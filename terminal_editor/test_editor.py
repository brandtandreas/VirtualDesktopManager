#!/usr/bin/env python3
"""Unit tests for NanoLike editor (non-curses logic only)."""

import sys
import os
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))

# Patch curses before importing editor so we can test without a terminal
import curses as _curses
import types

_mock_curses = types.ModuleType("curses")
_mock_curses.KEY_UP = 259
_mock_curses.KEY_DOWN = 258
_mock_curses.KEY_LEFT = 260
_mock_curses.KEY_RIGHT = 261
_mock_curses.KEY_HOME = 262
_mock_curses.KEY_END = 360
_mock_curses.KEY_PPAGE = 339
_mock_curses.KEY_NPAGE = 338
_mock_curses.KEY_DC = 330
_mock_curses.KEY_BACKSPACE = 263
_mock_curses.KEY_SHOME = 0x152
_mock_curses.KEY_SEND = 0x168
for i in range(1, 13):
    setattr(_mock_curses, f"KEY_F{i}", 265 + i - 1)
_mock_curses.error = Exception
sys.modules["curses"] = _mock_curses

from editor import (
    Editor, UndoStack, KeyBindings, Config, DEFAULT_KEYBINDINGS,
    key_to_name, ctrl
)


class MockStdscr:
    def getmaxyx(self): return (40, 80)
    def erase(self): pass
    def attron(self, *a): pass
    def attroff(self, *a): pass
    def addstr(self, *a): pass
    def refresh(self): pass
    def move(self, *a): pass
    def getch(self): return -1
    def keypad(self, *a): pass
    def timeout(self, *a): pass
    def color_pair(self, *a): return 0


def make_editor(content=""):
    e = Editor.__new__(Editor)
    e.config = Config.__new__(Config)
    e.config.tab_size = 4
    e.config.use_spaces = True
    e.config.auto_indent = True
    e.config.word_wrap = False
    e.config.line_numbers = True
    e.keybindings = KeyBindings()
    e.lines = content.splitlines() if content else [""]
    if not e.lines:
        e.lines = [""]
    e.cursor_row = 0
    e.cursor_col = 0
    e.scroll_row = 0
    e.scroll_col = 0
    e.filename = None
    e.modified = False
    e.status_msg = ""
    e.status_error = False
    e.clipboard = []
    e.undo_stack = UndoStack()
    e._last_saved_state = list(e.lines)
    e.search_term = ""
    e.search_matches = []
    e.search_idx = -1
    e.prev_key = None
    e.pending_escape = False
    e._selection_start = None
    e.stdscr = MockStdscr()
    return e


class TestUndoStack(unittest.TestCase):
    def test_push_undo(self):
        s = UndoStack()
        s.push(("state1", 0, 0))
        s.push(("state2", 1, 0))
        self.assertTrue(s.can_undo())
        result = s.undo()
        self.assertEqual(result[0], "state2")

    def test_undo_redo(self):
        s = UndoStack()
        s.push(("a", 0, 0))
        s.push(("b", 0, 0))
        s.undo()
        self.assertTrue(s.can_redo())
        r = s.redo()
        self.assertEqual(r[0], "b")

    def test_redo_cleared_on_push(self):
        s = UndoStack()
        s.push(("a", 0, 0))
        s.undo()
        self.assertTrue(s.can_redo())
        s.push(("c", 0, 0))
        self.assertFalse(s.can_redo())


class TestKeyBindings(unittest.TestCase):
    def test_default_bindings_present(self):
        kb = KeyBindings()
        self.assertIn("quit", kb.bindings)
        self.assertIn("save", kb.bindings)

    def test_get_action(self):
        kb = KeyBindings()
        self.assertEqual(kb.get_action("ctrl+x"), "quit")
        self.assertEqual(kb.get_action("ctrl+s"), "save")

    def test_first_key(self):
        kb = KeyBindings()
        self.assertEqual(kb.first_key("quit"), "ctrl+x")

    def test_unknown_key(self):
        kb = KeyBindings()
        self.assertIsNone(kb.get_action("ctrl+shift+z_unknown"))


class TestEditorInsert(unittest.TestCase):
    def test_insert_char(self):
        e = make_editor()
        e.insert_char("H")
        e.insert_char("i")
        self.assertEqual(e.lines[0], "Hi")
        self.assertEqual(e.cursor_col, 2)

    def test_insert_newline(self):
        e = make_editor("Hello")
        e.cursor_col = 3
        e.insert_newline()
        self.assertEqual(e.lines[0], "Hel")
        self.assertEqual(e.lines[1], "lo")
        self.assertEqual(e.cursor_row, 1)

    def test_auto_indent(self):
        e = make_editor("    hello")
        e.cursor_col = 9
        e.insert_newline()
        self.assertEqual(e.lines[2] if len(e.lines) > 2 else e.lines[1], "    ")

    def test_backspace_within_line(self):
        e = make_editor("Hello")
        e.cursor_col = 3
        e.backspace()
        self.assertEqual(e.lines[0], "Helo")
        self.assertEqual(e.cursor_col, 2)

    def test_backspace_join_lines(self):
        e = make_editor("Hello\nWorld")
        e.cursor_row = 1
        e.cursor_col = 0
        e.backspace()
        self.assertEqual(len(e.lines), 1)
        self.assertEqual(e.lines[0], "HelloWorld")

    def test_delete_char(self):
        e = make_editor("Hello")
        e.cursor_col = 0
        e.delete_char()
        self.assertEqual(e.lines[0], "ello")

    def test_delete_char_join_lines(self):
        e = make_editor("Hello\nWorld")
        e.cursor_row = 0
        e.cursor_col = 5
        e.delete_char()
        self.assertEqual(e.lines[0], "HelloWorld")
        self.assertEqual(len(e.lines), 1)


class TestEditorCutPaste(unittest.TestCase):
    def test_cut_line(self):
        e = make_editor("Line 1\nLine 2\nLine 3")
        e.cursor_row = 1
        e.cut_line()
        self.assertEqual(len(e.lines), 2)
        self.assertEqual(e.clipboard, ["Line 2"])

    def test_paste(self):
        e = make_editor("Line 1\nLine 3")
        e.clipboard = ["Line 2"]
        e.cursor_row = 0
        e.paste()
        self.assertIn("Line 2", e.lines)

    def test_copy_line(self):
        e = make_editor("Hello")
        e.copy_line()
        self.assertEqual(e.clipboard, ["Hello"])


class TestEditorNavigation(unittest.TestCase):
    def test_move_next_word(self):
        e = make_editor("hello world foo")
        e.cursor_col = 0
        e.move_next_word()
        self.assertEqual(e.cursor_col, 6)

    def test_move_prev_word(self):
        e = make_editor("hello world")
        e.cursor_col = 11
        e.move_prev_word()
        self.assertEqual(e.cursor_col, 6)

    def test_delete_to_eol(self):
        e = make_editor("hello world")
        e.cursor_col = 5
        e.delete_to_eol()
        self.assertEqual(e.lines[0], "hello")


class TestEditorSearch(unittest.TestCase):
    def test_build_search_matches(self):
        e = make_editor("foo bar foo\nbaz foo")
        e.search_term = "foo"
        e._build_search_matches()
        self.assertEqual(len(e.search_matches), 3)

    def test_search_case_insensitive(self):
        e = make_editor("Hello HELLO hello")
        e.search_term = "hello"
        e._build_search_matches()
        self.assertEqual(len(e.search_matches), 3)


class TestEditorUndo(unittest.TestCase):
    def test_undo_insert(self):
        e = make_editor()
        e.insert_char("A")
        e.insert_char("B")
        e._do_undo()
        # After undo, state is restored to after first insert
        # (each insert pushes separately)
        self.assertIn(e.lines[0], ["A", ""])

    def test_delete_word_before(self):
        e = make_editor("hello world")
        e.cursor_col = 11
        e.delete_word_before()
        self.assertEqual(e.lines[0], "hello ")


class TestSaveLoad(unittest.TestCase):
    def test_save_and_reload(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test content\n")
            fname = f.name
        try:
            e = make_editor("new content")
            e.filename = fname
            e.save_file()
            self.assertFalse(e.modified)
            with open(fname) as f:
                data = f.read()
            self.assertIn("new content", data)
        finally:
            os.unlink(fname)


class TestKeyToName(unittest.TestCase):
    def test_ctrl_chars(self):
        self.assertEqual(key_to_name(ctrl("x")), "ctrl+x")
        self.assertEqual(key_to_name(ctrl("s")), "ctrl+s")

    def test_alt_sequence(self):
        self.assertEqual(key_to_name(ord("u"), 27), "alt+u")
        self.assertEqual(key_to_name(ord("n"), 27), "alt+n")

    def test_printable(self):
        self.assertEqual(key_to_name(ord("a")), "a")

    def test_special_keys(self):
        self.assertEqual(key_to_name(9), "tab")
        self.assertEqual(key_to_name(127), "backspace")


if __name__ == "__main__":
    unittest.main(verbosity=2)
