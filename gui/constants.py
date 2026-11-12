# -*- coding: utf-8 -*-
"""
Stałe wyglądu okien wtyczki (GUI): okno do przeglądania zdjęć (Street View)
i karta z informacjami o zdjęciu rysowana na panoramie.

Kolory zgodne z identyfikacją EnviroSolutions (motyw jasny i ciemny), tak jak w plikach ui/*.ui.
Wymiary w pikselach logicznych (przy skalowaniu ekranu 125-150% Qt przelicza je sam).
"""

# ======================= Okno do przeglądania zdjęć (gui/ui_orbitalDialog.py) =======================

# Arkusz stylów okna; kolory zależą od właściwości "theme" ustawianej przez ThemeUtils
VIEWER_STYLE = """
QLabel#lbl_viewer_title { font-size: 14px; font-weight: 700; }
QLabel#lbl_viewer_subtitle { font-size: 11px; }
QToolButton#btn_viewer_close { border: none; border-radius: 6px; padding: 3px; }
QFrame#toolbar_frame QPushButton { border-radius: 6px; padding: 0px; }
QPushButton:focus, QToolButton:focus { outline: none; }

QDockWidget[theme="light"] QWidget#dockWidgetContents { background: #ffffff; }
QDockWidget[theme="light"] QFrame#header_frame { background: #ffffff; border: none; border-bottom: 2px solid #4c6e4f; }
QDockWidget[theme="light"] QLabel#lbl_viewer_title { color: #3b5a3e; }
QDockWidget[theme="light"] QLabel#lbl_viewer_subtitle { color: #6b7572; }
QDockWidget[theme="light"] QToolButton#btn_viewer_close:hover { background: #e8efe8; }
QDockWidget[theme="light"] QFrame#viewer_frame { background: #1f2122; border: none; }
QDockWidget[theme="light"] QFrame#toolbar_frame { background: #f6f8f6; border: none; border-top: 1px solid #d6ded6; }
QDockWidget[theme="light"] QFrame#toolbar_frame QPushButton { background: #ffffff; border: 1px solid #b9c7ba; }
QDockWidget[theme="light"] QFrame#toolbar_frame QPushButton:hover { background: #eef3ee; border-color: #4c6e4f; }
QDockWidget[theme="light"] QFrame#toolbar_frame QPushButton:pressed { background: #dfe8df; }
QDockWidget[theme="light"] QFrame[role="separator"] { background: #d6ded6; border: none; }

QDockWidget[theme="dark"] QWidget#dockWidgetContents { background: #2b2d2e; }
QDockWidget[theme="dark"] QFrame#header_frame { background: #2b2d2e; border: none; border-bottom: 2px solid #5b8260; }
QDockWidget[theme="dark"] QLabel#lbl_viewer_title { color: #a9cfac; }
QDockWidget[theme="dark"] QLabel#lbl_viewer_subtitle { color: #9aa4a0; }
QDockWidget[theme="dark"] QToolButton#btn_viewer_close:hover { background: #2c3a2d; }
QDockWidget[theme="dark"] QFrame#viewer_frame { background: #1f2122; border: none; }
QDockWidget[theme="dark"] QFrame#toolbar_frame { background: #303334; border: none; border-top: 1px solid #44494a; }
QDockWidget[theme="dark"] QFrame#toolbar_frame QPushButton { background: #262829; border: 1px solid #5a6162; }
QDockWidget[theme="dark"] QFrame#toolbar_frame QPushButton:hover { background: #2c3a2d; border-color: #6f9c73; }
QDockWidget[theme="dark"] QFrame#toolbar_frame QPushButton:pressed { background: #1f2a20; }
QDockWidget[theme="dark"] QFrame[role="separator"] { background: #44494a; border: none; }
"""

# Kolor ikon przycisków i ikona zamykania zależne od motywu
VIEWER_ICON_COLORS = {'light': '#3b5a3e', 'dark': '#cfe0d0'}
VIEWER_CLOSE_ICONS = {'light': 'close.svg', 'dark': 'close_dark.svg'}

# Wymiary okna i przycisków
VIEWER_DEFAULT_SIZE = (640, 480)          # rozmiar okna pływającego
VIEWER_OPEN_WIDTH_RATIO = 0.4             # szerokość okna zadokowanego przy pierwszym otwarciu (część okna QGIS)
VIEWER_BUTTON_SIZE = 34
VIEWER_ICON_SIZE = 20
VIEWER_HEADER_MARGINS = (12, 6, 8, 6)     # lewy, górny, prawy, dolny
VIEWER_HEADER_SPACING = 10
VIEWER_TITLE_SPACING = 1                  # odstęp między tytułem a nazwą zdjęcia
VIEWER_TOOLBAR_MARGINS = (10, 8, 10, 8)   # lewy, górny, prawy, dolny
VIEWER_TOOLBAR_SPACING = 6                # odstęp między przyciskami w grupie
VIEWER_SEPARATOR_SPACING = 4              # odstęp po obu stronach separatora grup
VIEWER_SEPARATOR_INSET = 10               # separator krótszy od przycisku o tyle pikseli

# Przyciski paska narzędzi: grupy oddzielone separatorem -> (nazwa obiektu, plik ikony, podpowiedź)
VIEWER_BUTTON_GROUPS = (
    (("btn_look_up", "look_up.svg", "Look up"),
     ("btn_look_down", "look_down.svg", "Look down")),
    (("btn_turn_left", "turn_left.svg", "Turn left"),
     ("btn_turn_right", "turn_right.svg", "Turn right")),
    (("btn_zoom_in", "zoom_in.svg", "Zoom in"),
     ("btn_zoom_out", "zoom_out.svg", "Zoom out")),
    (("btn_screenshot", "camera.svg", "Save view as image"),
     ("btn_fullscreen", "full_screen.svg", "Full screen")),
)

# ======================= Karta z informacjami o zdjęciu (modules/description_card.py) =======================

CARD_PLUGIN_ICON = 'ikona_wtyczki.svg'
CARD_TITLE = 'PhotoViewer360'
CARD_SUBTITLE = 'by EnviroSolutions · v%s'   # %s - wersja wtyczki

# Karta
CARD_MARGIN = 10              # odstęp karty od krawędzi widoku
CARD_WIDTH = 320
CARD_RADIUS = 8
CARD_SHADOW_OFFSET = 2
CARD_SHADOW_ALPHA = 40        # przezroczystość cienia (0-255)

# Nagłówek karty
CARD_HEADER_HEIGHT = 60
CARD_HEADER_PADDING = 14      # odstęp ikony i przycisku zwijania od boków karty
CARD_ICON_SIZE = 36
CARD_ICON_TEXT_GAP = 12       # odstęp tekstu od ikony
CARD_TITLE_RECT = (9, 24)     # (y, wysokość) tytułu
CARD_SUBTITLE_RECT = (33, 16)  # (y, wysokość) podtytułu
CARD_ACCENT_HEIGHT = 2        # zielona linia pod nagłówkiem

# Przycisk zwijania (okrąg ze strzałką)
CARD_COLLAPSE_SIZE = 24
CARD_COLLAPSE_PEN = 1.6
CARD_CHEVRON_HALF_WIDTH = 5
CARD_CHEVRON_HALF_HEIGHT = 2.5

# Tabela "Informacje o zdjęciu"
CARD_PANEL_MARGIN = 10
CARD_PANEL_RADIUS = 6
CARD_PANEL_TITLE_HEIGHT = 30
CARD_ROW_HEIGHT = 29
CARD_TEXT_PADDING = 10        # odstęp tekstu od lewej krawędzi tabeli
CARD_LABEL_COLUMN = 108       # minimalna szerokość kolumny z nazwami pól
CARD_LABEL_GAP = 24           # odstęp najdłuższej nazwy pola od wartości

# Czcionki: (rozmiar w pikselach, pogrubienie)
CARD_FONT_TITLE = (18, True)
CARD_FONT_SUBTITLE = (11, False)
CARD_FONT_SECTION = (13, True)
CARD_FONT_LABEL = (12, False)
CARD_FONT_VALUE = (12, True)

CARD_COLORS = {
    'light': {
        'card': '#ffffff', 'card_border': '#d6ded6', 'title': '#3b5a3e', 'subtitle': '#6b7572',
        'accent': '#4c6e4f', 'panel_border': '#c9d5c9', 'panel_title_bg': '#b9c7b9', 'panel_title': '#23282a',
        'row': '#ffffff', 'row_alt': '#f3f6f3', 'label': '#5a6460', 'value': '#23282a', 'icon': '#3b5a3e',
    },
    'dark': {
        'card': '#2b2d2e', 'card_border': '#44494a', 'title': '#a9cfac', 'subtitle': '#9aa4a0',
        'accent': '#5b8260', 'panel_border': '#4c6e4f', 'panel_title_bg': '#4c6e4f', 'panel_title': '#ffffff',
        'row': '#262829', 'row_alt': '#303334', 'label': '#9aa4a0', 'value': '#e6e9e7', 'icon': '#a9cfac',
    },
}
