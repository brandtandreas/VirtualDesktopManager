// ==UserScript==
// @name         Metal Archives — Mobile-Friendly CSS
// @namespace    https://www.metal-archives.com/
// @version      1.0.0
// @description  Injects a responsive, mobile-friendly stylesheet into metal-archives.com
// @author       VirtualDesktopManager project
// @match        https://www.metal-archives.com/*
// @grant        GM_addStyle
// @run-at       document-start
// ==/UserScript==

/* global GM_addStyle */

GM_addStyle(`
/*
 * ─── VIEWPORT / BOX MODEL RESET ─────────────────────────────────────────────
 */
html {
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
  overflow-x: hidden;
}
body {
  min-width: 0 !important;
  max-width: 100% !important;
  width: 100% !important;
  overflow-x: hidden;
  margin: 0 !important;
  padding: 0 !important;
  font-size: 15px;
  line-height: 1.5;
}
* { box-sizing: border-box; }

/*
 * ─── WRAPPER / LAYOUT CONTAINERS ─────────────────────────────────────────────
 */
@media (max-width: 768px) {
  #wrapper, #page, #main, #mainContent, #content, .wrapper, .container {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    margin: 0 auto !important;
    padding: 0 8px !important;
  }
  #content_wrapper, #left_column, #right_column {
    width: 100% !important;
    float: none !important;
    margin: 0 !important;
    padding: 0 !important;
  }
}

/*
 * ─── HEADER ──────────────────────────────────────────────────────────────────
 */
@media (max-width: 768px) {
  #header, #header_wrapper {
    width: 100% !important;
    min-width: 0 !important;
    padding: 8px !important;
    text-align: center;
  }
  #logoContainer, .logoContainer, #header img, #header_wrapper img {
    max-width: 240px !important;
    width: 100% !important;
    height: auto !important;
    display: block;
    margin: 0 auto 8px !important;
  }
  #header form, #searchContent form, #search_form {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    justify-content: center;
    margin: 8px 0;
  }
  #header input[type="text"], #header input[type="search"],
  #searchContent input[type="text"], #search_form input[type="text"] {
    width: 100%;
    max-width: 340px;
    font-size: 16px;
    padding: 8px 10px;
    border-radius: 4px;
  }
  #header select, #searchContent select, #search_form select {
    font-size: 16px;
    padding: 8px 6px;
    width: 100%;
    max-width: 220px;
  }
  #header input[type="submit"], #header button,
  #searchContent input[type="submit"], #search_form input[type="submit"] {
    padding: 8px 16px;
    font-size: 15px;
    touch-action: manipulation;
    min-height: 44px;
  }
}

/*
 * ─── MAIN NAVIGATION ─────────────────────────────────────────────────────────
 */
@media (max-width: 768px) {
  #navContent, #nav, nav, .nav, .navigation {
    width: 100% !important;
    min-width: 0 !important;
    background: #1a1a1a;
  }
  #navContent ul, #nav ul, nav ul {
    display: flex !important;
    flex-wrap: wrap;
    list-style: none;
    margin: 0;
    padding: 0;
    gap: 2px;
    background: #1a1a1a;
  }
  #navContent ul li, #nav ul li, nav ul li {
    flex: 1 1 auto;
    text-align: center;
    min-width: 70px;
  }
  #navContent ul li a, #nav ul li a, nav ul li a {
    display: block;
    padding: 10px 8px;
    font-size: 13px;
    white-space: nowrap;
    text-decoration: none;
    min-height: 44px;
    line-height: 24px;
    touch-action: manipulation;
  }
  #navContent ul li ul, #nav ul li ul, nav ul li ul {
    position: static !important;
    display: none;
    flex-direction: column;
    width: 100%;
    background: #222;
    box-shadow: none;
  }
  #navContent ul li:hover ul, #navContent ul li:focus-within ul,
  #nav ul li:hover ul, #nav ul li:focus-within ul,
  nav ul li:hover ul, nav ul li:focus-within ul {
    display: flex !important;
  }
  #navContent ul li ul li, #nav ul li ul li, nav ul li ul li {
    width: 100%;
    min-width: 0;
  }
}

/*
 * ─── DATA TABLES (jQuery DataTables) ─────────────────────────────────────────
 */
@media (max-width: 768px) {
  table.display, table.datatable, .display_table, table {
    display: block;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    width: 100% !important;
    min-width: 0 !important;
    max-width: 100%;
    border-collapse: collapse;
  }
  .dataTables_wrapper, .dataTable_wrapper {
    width: 100% !important;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  .dataTables_length, .dataTables_filter,
  .dataTables_info, .dataTables_paginate {
    display: block !important;
    width: 100% !important;
    text-align: left !important;
    margin: 6px 0 !important;
    font-size: 13px;
  }
  .dataTables_filter input {
    font-size: 16px;
    padding: 6px 8px;
    width: 100%;
    max-width: 260px;
  }
  .dataTables_paginate .paginate_button {
    padding: 6px 10px !important;
    min-height: 36px;
    font-size: 13px;
    display: inline-block;
  }
  table td, table th {
    padding: 6px 8px !important;
    font-size: 13px;
    white-space: nowrap;
  }
}

/*
 * ─── BAND / ARTIST PAGES ─────────────────────────────────────────────────────
 */
@media (max-width: 768px) {
  #band_info, #band_stats, #band_tab_album, .band_header {
    width: 100% !important;
    float: none !important;
    display: block !important;
    margin: 0 0 12px !important;
    padding: 8px !important;
  }
  #band_logo, .band_logo img {
    max-width: 200px !important;
    width: 100% !important;
    height: auto !important;
    display: block;
    margin: 0 auto 12px !important;
    float: none !important;
  }
  #band_tab_members img, .member_img {
    max-width: 100px !important;
    height: auto !important;
  }
  #band_info h1, .band_name {
    font-size: 1.5em !important;
    word-break: break-word;
    text-align: center;
  }
  #band_stats dl, .band_stats dl {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 4px 12px;
    padding: 0;
    margin: 0;
  }
  #band_stats dt, .band_stats dt { font-weight: bold; text-align: right; }
  #band_stats dd, .band_stats dd { margin: 0; text-align: left; }
}

/*
 * ─── ALBUM / RELEASE PAGES ───────────────────────────────────────────────────
 */
@media (max-width: 768px) {
  #album_info, .album_info {
    width: 100% !important;
    float: none !important;
    display: block !important;
    padding: 8px !important;
  }
  #album_info #cover, .album_cover, #cover img {
    max-width: 220px !important;
    width: 100% !important;
    height: auto !important;
    display: block;
    margin: 0 auto 12px !important;
    float: none !important;
  }
  #album_tab_tracklist table { font-size: 13px; }
  #album_tab_reviews .reviewBox {
    width: 100% !important;
    float: none !important;
    margin: 0 0 16px !important;
  }
}

/*
 * ─── TABS (jQuery UI Tabs) ────────────────────────────────────────────────────
 */
@media (max-width: 768px) {
  .ui-tabs .ui-tabs-nav {
    display: flex !important;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    flex-wrap: nowrap !important;
    white-space: nowrap;
    padding: 0 !important;
    gap: 4px;
  }
  .ui-tabs .ui-tabs-nav li { flex: 0 0 auto; }
  .ui-tabs .ui-tabs-nav li a {
    font-size: 13px;
    padding: 8px 12px !important;
    display: block;
    min-height: 40px;
    line-height: 24px;
    touch-action: manipulation;
  }
  .ui-tabs-panel { padding: 8px !important; }
}

/*
 * ─── SEARCH / LISTING PAGES ──────────────────────────────────────────────────
 */
@media (max-width: 768px) {
  #alpha_list, .alpha_list {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    justify-content: center;
    padding: 8px 0;
  }
  #alpha_list a, .alpha_list a {
    padding: 6px 10px;
    font-size: 15px;
    display: inline-block;
    min-width: 36px;
    text-align: center;
    min-height: 36px;
    line-height: 24px;
    touch-action: manipulation;
  }
  #bandListFilters, .band_filters, #searchForm {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 8px 0;
  }
  #bandListFilters select, .band_filters select, #searchForm select {
    font-size: 16px;
    padding: 8px 6px;
    width: 100%;
  }
  #bandListFilters input[type="submit"], .band_filters input[type="submit"],
  #searchForm input[type="submit"] {
    font-size: 15px;
    padding: 10px;
    min-height: 44px;
    width: 100%;
    touch-action: manipulation;
  }
}

/*
 * ─── HOMEPAGE ────────────────────────────────────────────────────────────────
 */
@media (max-width: 768px) {
  #homepage_additions, .homepage_additions, #newsBanner, .newsBanner {
    width: 100% !important;
    float: none !important;
    margin: 0 0 16px !important;
    padding: 8px !important;
  }
  #stats_wrapper, .stats_wrapper {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
  }
  .stat_box, .statBox { flex: 1 1 120px; text-align: center; padding: 8px; }
  #recent_additions table, .recent_additions table { font-size: 12px; }
}

/*
 * ─── IMAGES ──────────────────────────────────────────────────────────────────
 */
@media (max-width: 768px) {
  img { max-width: 100%; height: auto; }
}

/*
 * ─── TOUCH TARGETS ───────────────────────────────────────────────────────────
 */
@media (max-width: 768px) {
  a { touch-action: manipulation; }
  input[type="button"], input[type="submit"], button, .btn, .button {
    min-height: 44px;
    min-width: 44px;
    touch-action: manipulation;
    padding: 8px 14px;
  }
  .ui-autocomplete {
    max-width: calc(100vw - 16px) !important;
    overflow-x: hidden;
    font-size: 14px;
  }
  .ui-autocomplete li { padding: 10px 12px !important; min-height: 44px; line-height: 24px; }
}

/*
 * ─── FOOTER ──────────────────────────────────────────────────────────────────
 */
@media (max-width: 768px) {
  #footer, .footer {
    width: 100% !important;
    min-width: 0 !important;
    padding: 12px 8px !important;
    font-size: 12px;
    text-align: center;
  }
  #footer a, .footer a { padding: 4px 6px; display: inline-block; min-height: 36px; line-height: 28px; }
}

/*
 * ─── LIGHTBOX ────────────────────────────────────────────────────────────────
 */
@media (max-width: 768px) {
  #fancybox-wrap, .fancybox-wrap, .fancybox-inner {
    max-width: 100vw !important;
    width: 100vw !important;
    left: 0 !important;
    right: 0 !important;
    margin: 0 auto !important;
  }
  .fancybox-inner img { max-width: 100% !important; height: auto !important; }
}

/*
 * ─── TYPOGRAPHY ──────────────────────────────────────────────────────────────
 */
@media (max-width: 480px) {
  body { font-size: 14px; }
  h1 { font-size: 1.4em; }
  h2 { font-size: 1.2em; }
  h3 { font-size: 1.1em; }
  h1, h2, h3, h4, .band_name, .album_name {
    word-break: break-word;
    overflow-wrap: break-word;
    hyphens: auto;
  }
}

/*
 * ─── FORUM ───────────────────────────────────────────────────────────────────
 */
@media (max-width: 768px) {
  .postContainer, .forumPost {
    display: flex !important;
    flex-direction: column !important;
  }
  .postContainer .postInfo, .forumPost .postInfo {
    width: 100% !important;
    float: none !important;
    border-bottom: 1px solid #444;
    margin-bottom: 8px;
  }
  .postContainer .postContent, .forumPost .postContent {
    width: 100% !important;
    float: none !important;
  }
  #forumPosts table, .forumTable { font-size: 13px; }
}

/*
 * ─── MISC ────────────────────────────────────────────────────────────────────
 */
@media (max-width: 768px) {
  .spacer, .clear { height: 8px !important; display: block; }
  p, td, li, dd { word-break: break-word; overflow-wrap: break-word; }
  table.display::before, table.datatable::before {
    content: "← Scroll →";
    display: block;
    font-size: 11px;
    color: #888;
    text-align: center;
    padding: 2px 0 4px;
    font-style: italic;
  }
}
`);
