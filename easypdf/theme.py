from PySide6.QtGui import QColor, QPalette


LIGHT_THEME = """
QMainWindow,
QWidget {
    background: #f5f5f7;
    color: #222222;
}

QScrollArea {
    background: #f5f5f7;
    border: none;
}

QWidget#PageGridContainer,
QWidget#PageGridViewport {
    background: #f5f5f7;
    color: #222222;
}

QMenuBar {
    background: #ffffff;
    color: #222222;
    padding: 4px;
}

QMenuBar::item {
    padding: 7px 10px;
    border-radius: 6px;
}

QMenuBar::item:selected {
    background: #e8e8ed;
}

QMenu {
    background: #ffffff;
    color: #222222;
    border: 1px solid #d7d7dc;
    padding: 5px;
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 5px;
}

QMenu::item:selected {
    background: #e9e9ef;
}

QFrame#Sidebar {
    background: #ededf0;
    border-right: 1px solid #d8d8dc;
}

QLabel#SidebarTitle {
    font-size: 17px;
    font-weight: 700;
    color: #222222;
}

QListWidget {
    background: transparent;
    color: #222222;
    border: none;
    outline: none;
}

QListWidget::item {
    padding: 10px;
    margin: 2px 6px;
    border-radius: 8px;
}

QListWidget::item:selected {
    background: #dcdce3;
}

QPushButton {
    border: 1px solid #d0d0d5;
    background: #ffffff;
    color: #222222;
    padding: 8px 13px;
    border-radius: 8px;
}

QPushButton:hover {
    background: #f0f0f3;
}

QPushButton:pressed {
    background: #e5e5e9;
}

QPushButton:disabled {
    color: #999999;
    background: #eeeeef;
}

QPushButton#PrimaryButton {
    background: #222222;
    color: #ffffff;
    border: none;
}

QPushButton#PrimaryButton:hover {
    background: #3b3b3b;
}

QFrame#PageThumbnail {
    background: #ffffff;
    color: #222222;
    border: 1px solid #d7d7dc;
    border-radius: 12px;
}

QFrame#PageThumbnail QLabel {
    background: transparent;
    color: #222222;
}

QFrame#PageThumbnail[selected="true"] {
    border: 3px solid #3478f6;
}

QLabel#EmptyState {
    background: transparent;
    color: #777777;
    font-size: 16px;
}
"""


DARK_THEME = """
QMainWindow,
QWidget {
    background: #1c1c1e;
    color: #f5f5f7;
}

QScrollArea {
    background: #1c1c1e;
    border: none;
}

QWidget#PageGridContainer,
QWidget#PageGridViewport {
    background: #1c1c1e;
    color: #f5f5f7;
}

QMenuBar {
    background: #242426;
    color: #f5f5f7;
    padding: 4px;
}

QMenuBar::item {
    padding: 7px 10px;
    border-radius: 6px;
}

QMenuBar::item:selected {
    background: #3a3a3c;
}

QMenu {
    background: #2c2c2e;
    color: #f5f5f7;
    border: 1px solid #444448;
    padding: 5px;
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 5px;
}

QMenu::item:selected {
    background: #414143;
}

QFrame#Sidebar {
    background: #242426;
    border-right: 1px solid #3b3b3d;
}

QLabel#SidebarTitle {
    font-size: 17px;
    font-weight: 700;
    color: #f5f5f7;
}

QListWidget {
    background: transparent;
    color: #f5f5f7;
    border: none;
    outline: none;
}

QListWidget::item {
    padding: 10px;
    margin: 2px 6px;
    border-radius: 8px;
}

QListWidget::item:selected {
    background: #3a3a3c;
}

QPushButton {
    border: 1px solid #49494d;
    background: #303032;
    color: #f5f5f7;
    padding: 8px 13px;
    border-radius: 8px;
}

QPushButton:hover {
    background: #3b3b3d;
}

QPushButton:pressed {
    background: #454547;
}

QPushButton:disabled {
    color: #777777;
    background: #29292b;
}

QPushButton#PrimaryButton {
    background: #f5f5f7;
    color: #18181a;
    border: none;
}

QPushButton#PrimaryButton:hover {
    background: #dddddf;
}

QFrame#PageThumbnail {
    background: #29292b;
    color: #f5f5f7;
    border: 1px solid #454549;
    border-radius: 12px;
}

QFrame#PageThumbnail QLabel {
    background: transparent;
    color: #f5f5f7;
}

QFrame#PageThumbnail[selected="true"] {
    border: 3px solid #5b9bff;
}

QLabel#EmptyState {
    background: transparent;
    color: #999999;
    font-size: 16px;
}
"""


def build_palette(dark: bool) -> QPalette:
    """
    Build a complete application palette.

    This prevents Qt from falling back to the operating
    system's palette for widgets that aren't completely
    controlled by the stylesheet.
    """

    palette = QPalette()

    if dark:
        window = QColor("#1c1c1e")
        base = QColor("#1c1c1e")
        alternate_base = QColor("#242426")
        text = QColor("#f5f5f7")
        button = QColor("#303032")
        button_text = QColor("#f5f5f7")
        highlight = QColor("#3478f6")
        highlighted_text = QColor("#ffffff")
        disabled_text = QColor("#777777")

    else:
        window = QColor("#f5f5f7")
        base = QColor("#ffffff")
        alternate_base = QColor("#ededf0")
        text = QColor("#222222")
        button = QColor("#ffffff")
        button_text = QColor("#222222")
        highlight = QColor("#3478f6")
        highlighted_text = QColor("#ffffff")
        disabled_text = QColor("#999999")

    palette.setColor(
        QPalette.ColorRole.Window,
        window,
    )

    palette.setColor(
        QPalette.ColorRole.Base,
        base,
    )

    palette.setColor(
        QPalette.ColorRole.AlternateBase,
        alternate_base,
    )

    palette.setColor(
        QPalette.ColorRole.Text,
        text,
    )

    palette.setColor(
        QPalette.ColorRole.WindowText,
        text,
    )

    palette.setColor(
        QPalette.ColorRole.Button,
        button,
    )

    palette.setColor(
        QPalette.ColorRole.ButtonText,
        button_text,
    )

    palette.setColor(
        QPalette.ColorRole.Highlight,
        highlight,
    )

    palette.setColor(
        QPalette.ColorRole.HighlightedText,
        highlighted_text,
    )

    palette.setColor(
        QPalette.ColorGroup.Disabled,
        QPalette.ColorRole.Text,
        disabled_text,
    )

    palette.setColor(
        QPalette.ColorGroup.Disabled,
        QPalette.ColorRole.WindowText,
        disabled_text,
    )

    palette.setColor(
        QPalette.ColorGroup.Disabled,
        QPalette.ColorRole.ButtonText,
        disabled_text,
    )

    return palette