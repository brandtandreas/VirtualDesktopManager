#!/usr/bin/env python3
"""
NanoLike - A nano-inspired terminal text editor with customizable keyboard shortcuts.
"""

import curses
import os
import sys
import json
import re
from pathlib import Path
from typing import Optional


DEFAULT_KEYBINDINGS = {
    "quit": ["ctrl+x", "ctrl+q"],
    "save": ["ctrl+s", "ctrl+o"],
    "save_as": ["ctrl+shift+s"],
    "help": ["ctrl+g", "f1"],
    "cut_line": ["ctrl+k"],
    "paste": ["ctrl+u", "ctrl+v"],
    "copy_line": ["ctrl+c"],
    "search": ["ctrl+f", "ctrl+w"],
    "search_next": ["ctrl+n", "f3"],
    "search_prev": ["ctrl+p"],
    "replace": ["ctrl+r", "ctrl+h"],
    "goto_line": ["ctrl+l", "ctrl+_"],
    "page_up": ["ctrl+y", "pageup"],
    "page_down": ["ctrl+d", "pagedown"],
    "home": ["ctrl+a", "home"],
    "end": ["ctrl+e", "end"],
    "file_top": ["ctrl+home", "alt+\\"],
    "file_bottom": ["ctrl+end", "alt+/"],
    "undo": ["ctrl+z", "alt+u"],
    "redo": ["alt+e", "ctrl+y_redo"],
    "select_all": ["ctrl+shift+a"],
    "insert_tab": ["tab"],
    "delete_char": ["delete", "ctrl+d_del"],
    "backspace": ["backspace"],
    "new_file": ["ctrl+shift+n"],
    "open_file": ["ctrl+shift+o"],
    "next_word": ["alt+right", "ctrl+right"],
    "prev_word": ["alt+left", "ctrl+left"],
    "delete_word": ["ctrl+backspace", "alt+backspace"],
    "delete_to_eol": ["alt+d"],
    "toggle_line_numbers": ["alt+n"],
    "toggle_word_wrap": ["alt+w"],
    "toggle_auto_indent": ["alt+i"],
}

CONFIG_PATH = Path.home() / ".config" / "nanolike" / "config.json"
KEYBINDINGS_PATH = Path.home() / ".config" / "nanolike" / "keybindings.json"

KEY_NAMES = {
    curses.KEY_UP: "up",
    curses.KEY_DOWN: "down",
    curses.KEY_LEFT: "left",
    curses.KEY_RIGHT: "right",
    curses.KEY_HOME: "home",
    curses.KEY_END: "end",
    curses.KEY_PPAGE: "pageup",
    curses.KEY_NPAGE: "pagedown",
    curses.KEY_DC: "delete",
    curses.KEY_BACKSPACE: "backspace",
    curses.KEY_F1: "f1",
    curses.KEY_F2: "f2",
    curses.KEY_F3: "f3",
    curses.KEY_F4: "f4",
    curses.KEY_F5: "f5",
    curses.KEY_F6: "f6",
    curses.KEY_F7: "f7",
    curses.KEY_F8: "f8",
    curses.KEY_F9: "f9",
    curses.KEY_F10: "f10",
    curses.KEY_F11: "f11",
    curses.KEY_F12: "f12",
    127: "backspace",
    9: "tab",
    10: "enter",
    13: "enter",
    27: "escape",
    # Ctrl+Home / Ctrl+End (xterm sequences mapped via ncurses)
    curses.KEY_SHOME if hasattr(curses, "KEY_SHOME") else 0x152: "ctrl+home",
    curses.KEY_SEND if hasattr(curses, "KEY_SEND") else 0x168: "ctrl+end",
}


def ctrl(char: str) -> int:
    return ord(char.upper()) - ord("@")


CTRL_MAP = {ctrl(c): f"ctrl+{c.lower()}" for c in "abcdefghijklmnopqrstuvwxyz"}
CTRL_MAP[ctrl("_")] = "ctrl+_"


def key_to_name(key: int, prev_key: Optional[int] = None) -> str:
    if prev_key == 27:
        if key in range(ord("a"), ord("z") + 1):
            return f"alt+{chr(key)}"
        if key == ord("\\"):
            return "alt+\\"
        if key == ord("/"):
            return "alt+/"
        if key == curses.KEY_LEFT:
            return "alt+left"
        if key == curses.KEY_RIGHT:
            return "alt+right"
        if key == curses.KEY_BACKSPACE or key == 127:
            return "alt+backspace"
        if key == ord("d") or key == ord("D"):
            return "alt+d"
        if key == ord("u") or key == ord("U"):
            return "alt+u"
        if key == ord("e") or key == ord("E"):
            return "alt+e"
        if key == ord("n") or key == ord("N"):
            return "alt+n"
        if key == ord("w") or key == ord("W"):
            return "alt+w"
        if key == ord("i") or key == ord("I"):
            return "alt+i"

    if key in KEY_NAMES:
        return KEY_NAMES[key]
    if key in CTRL_MAP:
        return CTRL_MAP[key]
    if 32 <= key <= 126:
        return chr(key)
    return f"key:{key}"


class Config:
    def __init__(self):
        self.tab_size = 4
        self.use_spaces = True
        self.auto_indent = True
        self.word_wrap = False
        self.line_numbers = True
        self.syntax_highlight = False
        self.color_scheme = "default"
        self.load()

    def load(self):
        if CONFIG_PATH.exists():
            try:
                data = json.loads(CONFIG_PATH.read_text())
                self.tab_size = data.get("tab_size", self.tab_size)
                self.use_spaces = data.get("use_spaces", self.use_spaces)
                self.auto_indent = data.get("auto_indent", self.auto_indent)
                self.word_wrap = data.get("word_wrap", self.word_wrap)
                self.line_numbers = data.get("line_numbers", self.line_numbers)
                self.color_scheme = data.get("color_scheme", self.color_scheme)
            except (json.JSONDecodeError, OSError):
                pass

    def save(self):
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "tab_size": self.tab_size,
            "use_spaces": self.use_spaces,
            "auto_indent": self.auto_indent,
            "word_wrap": self.word_wrap,
            "line_numbers": self.line_numbers,
            "color_scheme": self.color_scheme,
        }
        CONFIG_PATH.write_text(json.dumps(data, indent=2))


class KeyBindings:
    def __init__(self):
        self.bindings: dict[str, list[str]] = dict(DEFAULT_KEYBINDINGS)
        self.load()
        self._reverse: dict[str, str] = {}
        self._build_reverse()

    def _build_reverse(self):
        self._reverse = {}
        for action, keys in self.bindings.items():
            for key in keys:
                self._reverse[key] = action

    def load(self):
        if KEYBINDINGS_PATH.exists():
            try:
                data = json.loads(KEYBINDINGS_PATH.read_text())
                for action, keys in data.items():
                    if isinstance(keys, list):
                        self.bindings[action] = keys
                    elif isinstance(keys, str):
                        self.bindings[action] = [keys]
                self._build_reverse()
            except (json.JSONDecodeError, OSError):
                pass

    def save(self):
        KEYBINDINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        KEYBINDINGS_PATH.write_text(json.dumps(self.bindings, indent=2))

    def save_defaults(self):
        KEYBINDINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        KEYBINDINGS_PATH.write_text(json.dumps(DEFAULT_KEYBINDINGS, indent=2))

    def get_action(self, key_name: str) -> Optional[str]:
        return self._reverse.get(key_name)

    def get_keys_for(self, action: str) -> list[str]:
        return self.bindings.get(action, [])

    def first_key(self, action: str) -> str:
        keys = self.get_keys_for(action)
        return keys[0] if keys else ""


class UndoStack:
    def __init__(self, max_size=200):
        self._undo: list[tuple] = []
        self._redo: list[tuple] = []
        self._max = max_size

    def push(self, state: tuple):
        self._undo.append(state)
        if len(self._undo) > self._max:
            self._undo.pop(0)
        self._redo.clear()

    def undo(self) -> Optional[tuple]:
        if self._undo:
            state = self._undo.pop()
            self._redo.append(state)
            return state
        return None

    def redo(self) -> Optional[tuple]:
        if self._redo:
            state = self._redo.pop()
            self._undo.append(state)
            return state
        return None

    def can_undo(self) -> bool:
        return bool(self._undo)

    def can_redo(self) -> bool:
        return bool(self._redo)


class Editor:
    def __init__(self, stdscr, filename: Optional[str] = None):
        self.stdscr = stdscr
        self.config = Config()
        self.keybindings = KeyBindings()
        self.lines: list[str] = [""]
        self.cursor_row = 0
        self.cursor_col = 0
        self.scroll_row = 0
        self.scroll_col = 0
        self.filename: Optional[str] = filename
        self.modified = False
        self.status_msg = ""
        self.status_error = False
        self.clipboard: list[str] = []
        self.undo_stack = UndoStack()
        self._last_saved_state: Optional[list[str]] = None
        self.search_term = ""
        self.search_matches: list[tuple[int, int]] = []
        self.search_idx = -1
        self.prev_key: Optional[int] = None
        self.pending_escape = False
        self._selection_start: Optional[tuple[int, int]] = None

        if filename and os.path.exists(filename):
            self._load_file(filename)
        elif filename:
            self.set_status(f"New file: {filename}")

        self._last_saved_state = [l for l in self.lines]
        self._setup_colors()

    def _setup_colors(self):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)   # status bar
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)    # title bar
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_CYAN)    # help bar
        curses.init_pair(4, curses.COLOR_YELLOW, -1)                  # line numbers
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # search highlight
        curses.init_pair(6, curses.COLOR_RED, -1)                     # error status
        curses.init_pair(7, curses.COLOR_GREEN, -1)                   # ok status
        curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLACK)   # normal text

    def _load_file(self, filename: str):
        try:
            with open(filename, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            self.lines = content.splitlines(keepends=False)
            if not self.lines:
                self.lines = [""]
            self.set_status(f"Read {len(self.lines)} lines")
        except OSError as e:
            self.set_status(f"Error: {e}", error=True)
            self.lines = [""]

    def set_status(self, msg: str, error: bool = False):
        self.status_msg = msg
        self.status_error = error

    def _line_number_width(self) -> int:
        if not self.config.line_numbers:
            return 0
        return len(str(len(self.lines))) + 1

    @property
    def height(self) -> int:
        h, _ = self.stdscr.getmaxyx()
        return h - 3  # title + status + help bar

    @property
    def width(self) -> int:
        _, w = self.stdscr.getmaxyx()
        return w

    def _draw_title_bar(self):
        h, w = self.stdscr.getmaxyx()
        name = self.filename or "New Buffer"
        modified = " [Modified]" if self.modified else ""
        title = f" NanoLike - {name}{modified} "
        title = title[:w]
        self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
        self.stdscr.addstr(0, 0, title.center(w))
        self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

    def _draw_status_bar(self):
        h, w = self.stdscr.getmaxyx()
        col_info = f"Ln {self.cursor_row + 1}, Col {self.cursor_col + 1}"
        if self.status_msg:
            msg = self.status_msg[:w - len(col_info) - 2]
            attr = curses.color_pair(6) if self.status_error else curses.color_pair(7)
        else:
            msg = ""
            attr = curses.color_pair(1)
        line = f" {msg:<{w - len(col_info) - 3}}{col_info} "
        self.stdscr.attron(curses.color_pair(1))
        try:
            self.stdscr.addstr(h - 2, 0, line[:w])
        except curses.error:
            pass
        if self.status_msg:
            self.stdscr.attron(attr | curses.A_BOLD)
            try:
                self.stdscr.addstr(h - 2, 1, msg)
            except curses.error:
                pass
            self.stdscr.attroff(attr | curses.A_BOLD)
        self.stdscr.attroff(curses.color_pair(1))

    def _draw_help_bar(self):
        h, w = self.stdscr.getmaxyx()
        kb = self.keybindings
        shortcuts = [
            (kb.first_key("quit"), "Quit"),
            (kb.first_key("save"), "Save"),
            (kb.first_key("search"), "Search"),
            (kb.first_key("replace"), "Replace"),
            (kb.first_key("goto_line"), "Go To"),
            (kb.first_key("cut_line"), "Cut Line"),
            (kb.first_key("paste"), "Paste"),
            (kb.first_key("help"), "Help"),
            (kb.first_key("undo"), "Undo"),
            (kb.first_key("redo"), "Redo"),
        ]
        bar = ""
        for key, label in shortcuts:
            entry = f" {key} {label} "
            if len(bar) + len(entry) + 1 > w:
                break
            bar += entry
        self.stdscr.attron(curses.color_pair(3))
        try:
            self.stdscr.addstr(h - 1, 0, bar.ljust(w)[:w])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(3))

    def _draw_text_area(self):
        h, w = self.stdscr.getmaxyx()
        lnw = self._line_number_width()
        text_w = w - lnw

        search_positions: set[tuple[int, int, int]] = set()
        if self.search_term:
            for row, col in self.search_matches:
                for i in range(len(self.search_term)):
                    search_positions.add((row, col + i, 0))

        for screen_row in range(self.height):
            file_row = screen_row + self.scroll_row
            y = screen_row + 1  # +1 for title bar

            # Draw line number
            if self.config.line_numbers:
                if file_row < len(self.lines):
                    lnum = str(file_row + 1).rjust(lnw - 1) + " "
                else:
                    lnum = " " * lnw
                self.stdscr.attron(curses.color_pair(4))
                try:
                    self.stdscr.addstr(y, 0, lnum[:lnw])
                except curses.error:
                    pass
                self.stdscr.attroff(curses.color_pair(4))

            # Draw text
            if file_row < len(self.lines):
                line = self.lines[file_row]
                visible = line[self.scroll_col:self.scroll_col + text_w]
                try:
                    self.stdscr.addstr(y, lnw, " " * text_w)
                except curses.error:
                    pass
                for col_offset, ch in enumerate(visible):
                    col_in_file = self.scroll_col + col_offset
                    screen_col = lnw + col_offset
                    if screen_col >= w - 1:
                        break
                    if (file_row, col_in_file, 0) in search_positions:
                        attr = curses.color_pair(5) | curses.A_BOLD
                    else:
                        attr = 0
                    try:
                        self.stdscr.addstr(y, screen_col, ch, attr)
                    except curses.error:
                        pass
            else:
                try:
                    self.stdscr.addstr(y, 0, "~".ljust(w - 1))
                except curses.error:
                    pass

    def _update_scroll(self):
        lnw = self._line_number_width()
        text_w = self.width - lnw
        if self.cursor_row < self.scroll_row:
            self.scroll_row = self.cursor_row
        elif self.cursor_row >= self.scroll_row + self.height:
            self.scroll_row = self.cursor_row - self.height + 1
        if self.cursor_col < self.scroll_col:
            self.scroll_col = self.cursor_col
        elif self.cursor_col >= self.scroll_col + text_w:
            self.scroll_col = self.cursor_col - text_w + 1

    def _draw_cursor(self):
        lnw = self._line_number_width()
        screen_row = self.cursor_row - self.scroll_row + 1
        screen_col = self.cursor_col - self.scroll_col + lnw
        h, w = self.stdscr.getmaxyx()
        if 1 <= screen_row < h - 2 and 0 <= screen_col < w:
            try:
                self.stdscr.move(screen_row, screen_col)
            except curses.error:
                pass

    def draw(self):
        self.stdscr.erase()
        self._update_scroll()
        self._draw_title_bar()
        self._draw_text_area()
        self._draw_status_bar()
        self._draw_help_bar()
        self._draw_cursor()
        self.stdscr.refresh()

    def _clamp_cursor(self):
        self.cursor_row = max(0, min(self.cursor_row, len(self.lines) - 1))
        line_len = len(self.lines[self.cursor_row])
        self.cursor_col = max(0, min(self.cursor_col, line_len))

    def _save_undo(self):
        state = ([l for l in self.lines], self.cursor_row, self.cursor_col)
        self.undo_stack.push(state)

    def _do_undo(self):
        state = self.undo_stack.undo()
        if state:
            saved = ([l for l in self.lines], self.cursor_row, self.cursor_col)
            self.undo_stack._redo.append(saved)
            self.undo_stack._undo.pop()  # remove duplicate
            lines, row, col = state
            self.lines = lines
            self.cursor_row = row
            self.cursor_col = col
            self._clamp_cursor()
            self.modified = self.lines != self._last_saved_state
            self.set_status("Undone")
        else:
            self.set_status("Nothing to undo")

    def _do_redo(self):
        state = self.undo_stack.redo()
        if state:
            lines, row, col = state
            self.lines = lines
            self.cursor_row = row
            self.cursor_col = col
            self._clamp_cursor()
            self.modified = self.lines != self._last_saved_state
            self.set_status("Redone")
        else:
            self.set_status("Nothing to redo")

    def insert_char(self, ch: str):
        self._save_undo()
        line = self.lines[self.cursor_row]
        self.lines[self.cursor_row] = line[:self.cursor_col] + ch + line[self.cursor_col:]
        self.cursor_col += len(ch)
        self.modified = True

    def insert_newline(self):
        self._save_undo()
        line = self.lines[self.cursor_row]
        before = line[:self.cursor_col]
        after = line[self.cursor_col:]
        indent = ""
        if self.config.auto_indent:
            indent = re.match(r"^(\s*)", before).group(1)
        self.lines[self.cursor_row] = before
        self.lines.insert(self.cursor_row + 1, indent + after)
        self.cursor_row += 1
        self.cursor_col = len(indent)
        self.modified = True

    def backspace(self):
        if self.cursor_col > 0:
            self._save_undo()
            line = self.lines[self.cursor_row]
            self.lines[self.cursor_row] = line[:self.cursor_col - 1] + line[self.cursor_col:]
            self.cursor_col -= 1
            self.modified = True
        elif self.cursor_row > 0:
            self._save_undo()
            prev_line = self.lines[self.cursor_row - 1]
            curr_line = self.lines[self.cursor_row]
            self.cursor_col = len(prev_line)
            self.lines[self.cursor_row - 1] = prev_line + curr_line
            self.lines.pop(self.cursor_row)
            self.cursor_row -= 1
            self.modified = True

    def delete_char(self):
        line = self.lines[self.cursor_row]
        if self.cursor_col < len(line):
            self._save_undo()
            self.lines[self.cursor_row] = line[:self.cursor_col] + line[self.cursor_col + 1:]
            self.modified = True
        elif self.cursor_row < len(self.lines) - 1:
            self._save_undo()
            next_line = self.lines[self.cursor_row + 1]
            self.lines[self.cursor_row] = line + next_line
            self.lines.pop(self.cursor_row + 1)
            self.modified = True

    def cut_line(self):
        self._save_undo()
        self.clipboard = [self.lines.pop(self.cursor_row)]
        if not self.lines:
            self.lines = [""]
        self.cursor_row = min(self.cursor_row, len(self.lines) - 1)
        self.cursor_col = min(self.cursor_col, len(self.lines[self.cursor_row]))
        self.modified = True
        self.set_status("Line cut")

    def copy_line(self):
        self.clipboard = [self.lines[self.cursor_row]]
        self.set_status("Line copied")

    def paste(self):
        if not self.clipboard:
            self.set_status("Clipboard empty")
            return
        self._save_undo()
        for i, text in enumerate(self.clipboard):
            self.lines.insert(self.cursor_row + i + 1, text)
        self.cursor_row += len(self.clipboard)
        self.modified = True
        self.set_status(f"Pasted {len(self.clipboard)} line(s)")

    def delete_word_before(self):
        self._save_undo()
        line = self.lines[self.cursor_row]
        if self.cursor_col == 0:
            return
        left = line[:self.cursor_col]
        stripped = left.rstrip()
        if stripped == left:
            # delete last word
            new_left = re.sub(r"\S+\s*$", "", left)
        else:
            new_left = stripped
        self.lines[self.cursor_row] = new_left + line[self.cursor_col:]
        self.cursor_col = len(new_left)
        self.modified = True

    def delete_to_eol(self):
        self._save_undo()
        line = self.lines[self.cursor_row]
        self.lines[self.cursor_row] = line[:self.cursor_col]
        self.modified = True

    def move_next_word(self):
        line = self.lines[self.cursor_row]
        col = self.cursor_col
        while col < len(line) and line[col].isalnum():
            col += 1
        while col < len(line) and not line[col].isalnum():
            col += 1
        self.cursor_col = col

    def move_prev_word(self):
        line = self.lines[self.cursor_row]
        col = self.cursor_col
        while col > 0 and not line[col - 1].isalnum():
            col -= 1
        while col > 0 and line[col - 1].isalnum():
            col -= 1
        self.cursor_col = col

    def save_file(self, filename: Optional[str] = None) -> bool:
        target = filename or self.filename
        if not target:
            target = self._prompt("Save As: ")
            if not target:
                self.set_status("Save cancelled")
                return False
            self.filename = target
        try:
            with open(target, "w", encoding="utf-8") as f:
                f.write("\n".join(self.lines))
                if self.lines and self.lines[-1] != "":
                    f.write("\n")
            self.modified = False
            self._last_saved_state = [l for l in self.lines]
            self.set_status(f"Saved: {target}")
            return True
        except OSError as e:
            self.set_status(f"Save error: {e}", error=True)
            return False

    def _prompt(self, prompt: str, default: str = "") -> str:
        h, w = self.stdscr.getmaxyx()
        curses.echo()
        curses.curs_set(1)
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        try:
            self.stdscr.addstr(h - 2, 0, (prompt + default).ljust(w - 1)[:w - 1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
        self.stdscr.refresh()
        buf = default
        self.stdscr.move(h - 2, len(prompt))
        while True:
            try:
                key = self.stdscr.getch()
            except curses.error:
                break
            if key in (10, 13):
                break
            if key == 27:
                buf = ""
                break
            if key in (curses.KEY_BACKSPACE, 127):
                buf = buf[:-1]
            elif 32 <= key <= 126:
                buf += chr(key)
            try:
                self.stdscr.addstr(h - 2, len(prompt), (buf + " " * 20)[:w - len(prompt) - 1])
                self.stdscr.move(h - 2, len(prompt) + len(buf))
            except curses.error:
                pass
            self.stdscr.refresh()
        curses.noecho()
        return buf

    def do_search(self, forward: bool = True):
        term = self._prompt("Search: ", self.search_term)
        if not term:
            self.set_status("Search cancelled")
            return
        self.search_term = term
        self._build_search_matches()
        if not self.search_matches:
            self.set_status(f"Not found: {term}", error=True)
            return
        self._next_match(forward)

    def _build_search_matches(self):
        self.search_matches = []
        if not self.search_term:
            return
        try:
            pattern = re.compile(re.escape(self.search_term), re.IGNORECASE)
            for row, line in enumerate(self.lines):
                for m in pattern.finditer(line):
                    self.search_matches.append((row, m.start()))
        except re.error:
            pass

    def _next_match(self, forward: bool = True):
        if not self.search_matches:
            return
        cursor_pos = (self.cursor_row, self.cursor_col)
        if forward:
            for i, (row, col) in enumerate(self.search_matches):
                if (row, col) > cursor_pos:
                    self.search_idx = i
                    self.cursor_row, self.cursor_col = row, col
                    self.set_status(f"Match {i + 1}/{len(self.search_matches)}: {self.search_term}")
                    return
            self.search_idx = 0
            self.cursor_row, self.cursor_col = self.search_matches[0]
            self.set_status(f"Wrapped. Match 1/{len(self.search_matches)}: {self.search_term}")
        else:
            for i in range(len(self.search_matches) - 1, -1, -1):
                row, col = self.search_matches[i]
                if (row, col) < cursor_pos:
                    self.search_idx = i
                    self.cursor_row, self.cursor_col = row, col
                    self.set_status(f"Match {i + 1}/{len(self.search_matches)}: {self.search_term}")
                    return
            self.search_idx = len(self.search_matches) - 1
            self.cursor_row, self.cursor_col = self.search_matches[-1]
            self.set_status(f"Wrapped. Match {len(self.search_matches)}/{len(self.search_matches)}: {self.search_term}")

    def do_replace(self):
        term = self._prompt("Search: ", self.search_term)
        if not term:
            self.set_status("Replace cancelled")
            return
        replacement = self._prompt("Replace with: ")
        self.search_term = term
        self._build_search_matches()
        if not self.search_matches:
            self.set_status(f"Not found: {term}", error=True)
            return
        choice = self._prompt(f"Replace all? (y/n): ")
        if choice.lower() == "y":
            self._save_undo()
            count = 0
            for i in range(len(self.lines)):
                new_line = self.lines[i].replace(term, replacement)
                if new_line != self.lines[i]:
                    count += len(self.lines[i].split(term)) - 1
                    self.lines[i] = new_line
            self.modified = count > 0
            self.search_matches = []
            self.set_status(f"Replaced {count} occurrence(s)")
        else:
            self._next_match()

    def do_goto_line(self):
        num_str = self._prompt("Go to line: ")
        try:
            n = int(num_str) - 1
            if 0 <= n < len(self.lines):
                self.cursor_row = n
                self.cursor_col = 0
                self.set_status(f"Jumped to line {n + 1}")
            else:
                self.set_status(f"Line {n + 1} out of range", error=True)
        except ValueError:
            self.set_status("Invalid line number", error=True)

    def show_help(self):
        h, w = self.stdscr.getmaxyx()
        kb = self.keybindings
        lines = [
            "NanoLike Help - Keyboard Shortcuts",
            "=" * 40,
            "",
        ]
        for action, keys in kb.bindings.items():
            label = action.replace("_", " ").title()
            keys_str = " / ".join(keys)
            lines.append(f"  {keys_str:<20} {label}")
        lines += [
            "",
            "Config files:",
            f"  {CONFIG_PATH}",
            f"  {KEYBINDINGS_PATH}",
            "",
            "Press any key to close...",
        ]
        self.stdscr.erase()
        self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
        try:
            self.stdscr.addstr(0, 0, " NanoLike Help ".center(w))
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
        for i, line in enumerate(lines[:h - 2]):
            try:
                self.stdscr.addstr(i + 1, 0, line[:w - 1])
            except curses.error:
                pass
        self.stdscr.attron(curses.color_pair(3))
        try:
            self.stdscr.addstr(h - 1, 0, " Press any key to close ".ljust(w)[:w])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(3))
        self.stdscr.refresh()
        self.stdscr.getch()

    def _confirm_quit(self) -> bool:
        if not self.modified:
            return True
        choice = self._prompt("Save before quit? (y/n/cancel): ")
        if choice.lower() == "y":
            return self.save_file()
        elif choice.lower() == "n":
            return True
        return False

    def handle_key(self, key: int) -> bool:
        """Return False to quit."""
        # Handle escape sequences
        if self.pending_escape:
            self.pending_escape = False
            key_name = key_to_name(key, 27)
        else:
            if key == 27:
                self.pending_escape = True
                return True
            key_name = key_to_name(key)

        action = self.keybindings.get_action(key_name)

        # Navigation (always handle even without action mapping)
        if key == curses.KEY_UP or key_name == "up":
            self.cursor_row = max(0, self.cursor_row - 1)
            self._clamp_cursor()
            return True
        if key == curses.KEY_DOWN or key_name == "down":
            self.cursor_row = min(len(self.lines) - 1, self.cursor_row + 1)
            self._clamp_cursor()
            return True
        if key == curses.KEY_LEFT or key_name == "left":
            if self.cursor_col > 0:
                self.cursor_col -= 1
            elif self.cursor_row > 0:
                self.cursor_row -= 1
                self.cursor_col = len(self.lines[self.cursor_row])
            return True
        if key == curses.KEY_RIGHT or key_name == "right":
            if self.cursor_col < len(self.lines[self.cursor_row]):
                self.cursor_col += 1
            elif self.cursor_row < len(self.lines) - 1:
                self.cursor_row += 1
                self.cursor_col = 0
            return True
        if key in (10, 13) or key_name == "enter":
            self.insert_newline()
            return True

        if action:
            return self._dispatch_action(action, key_name)

        # Printable character
        if isinstance(key, int) and 32 <= key <= 126:
            self.insert_char(chr(key))
        elif key_name == "tab":
            if self.config.use_spaces:
                self.insert_char(" " * self.config.tab_size)
            else:
                self.insert_char("\t")
        elif key_name == "backspace":
            self.backspace()

        return True

    def _dispatch_action(self, action: str, key_name: str) -> bool:
        if action == "quit":
            return not self._confirm_quit()
        elif action == "save":
            self.save_file()
        elif action == "save_as":
            new_name = self._prompt("Save As: ", self.filename or "")
            if new_name:
                self.save_file(new_name)
        elif action == "help":
            self.show_help()
        elif action == "cut_line":
            self.cut_line()
        elif action == "copy_line":
            self.copy_line()
        elif action == "paste":
            self.paste()
        elif action == "search":
            self.do_search()
        elif action == "search_next":
            if self.search_term:
                self._build_search_matches()
                self._next_match(forward=True)
            else:
                self.do_search()
        elif action == "search_prev":
            if self.search_term:
                self._build_search_matches()
                self._next_match(forward=False)
            else:
                self.do_search(forward=False)
        elif action == "replace":
            self.do_replace()
        elif action == "goto_line":
            self.do_goto_line()
        elif action == "page_up":
            self.cursor_row = max(0, self.cursor_row - self.height)
            self._clamp_cursor()
        elif action == "page_down":
            self.cursor_row = min(len(self.lines) - 1, self.cursor_row + self.height)
            self._clamp_cursor()
        elif action == "home":
            line = self.lines[self.cursor_row]
            indent = len(line) - len(line.lstrip())
            self.cursor_col = indent if self.cursor_col != indent else 0
        elif action == "end":
            self.cursor_col = len(self.lines[self.cursor_row])
        elif action == "file_top":
            self.cursor_row = 0
            self.cursor_col = 0
        elif action == "file_bottom":
            self.cursor_row = len(self.lines) - 1
            self.cursor_col = len(self.lines[-1])
        elif action == "undo":
            self._do_undo()
        elif action == "redo":
            self._do_redo()
        elif action == "delete_char":
            self.delete_char()
        elif action == "backspace":
            self.backspace()
        elif action == "next_word":
            self.move_next_word()
        elif action == "prev_word":
            self.move_prev_word()
        elif action == "delete_word":
            self.delete_word_before()
        elif action == "delete_to_eol":
            self.delete_to_eol()
        elif action == "toggle_line_numbers":
            self.config.line_numbers = not self.config.line_numbers
            self.config.save()
            self.set_status(f"Line numbers {'on' if self.config.line_numbers else 'off'}")
        elif action == "toggle_word_wrap":
            self.config.word_wrap = not self.config.word_wrap
            self.config.save()
            self.set_status(f"Word wrap {'on' if self.config.word_wrap else 'off'}")
        elif action == "toggle_auto_indent":
            self.config.auto_indent = not self.config.auto_indent
            self.config.save()
            self.set_status(f"Auto-indent {'on' if self.config.auto_indent else 'off'}")
        elif action == "insert_tab":
            if self.config.use_spaces:
                self.insert_char(" " * self.config.tab_size)
            else:
                self.insert_char("\t")
        return True

    def run(self):
        curses.curs_set(1)
        curses.cbreak()
        self.stdscr.keypad(True)
        self.stdscr.timeout(100)
        running = True
        while running:
            self.draw()
            key = self.stdscr.getch()
            if key == -1:
                continue
            if not self.handle_key(key):
                running = False
            self.status_msg = self.status_msg  # persist until next action


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else None

    if "--export-keybindings" in sys.argv:
        kb = KeyBindings()
        kb.save_defaults()
        print(f"Default keybindings exported to: {KEYBINDINGS_PATH}")
        return

    if "--export-config" in sys.argv:
        cfg = Config()
        cfg.save()
        print(f"Default config exported to: {CONFIG_PATH}")
        return

    if "--help" in sys.argv or "-h" in sys.argv:
        print("NanoLike - A nano-inspired terminal editor")
        print("")
        print("Usage: editor.py [OPTIONS] [FILE]")
        print("")
        print("Options:")
        print("  --export-keybindings  Write default keybindings to config dir and exit")
        print("  --export-config       Write default config to config dir and exit")
        print("  --help, -h            Show this help message")
        print("")
        print(f"Config:      {CONFIG_PATH}")
        print(f"Keybindings: {KEYBINDINGS_PATH}")
        return

    def _run(stdscr):
        editor = Editor(stdscr, filename)
        editor.run()

    curses.wrapper(_run)


if __name__ == "__main__":
    main()
