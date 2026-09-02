LIGHT_QSS = """
QMainWindow, QWidget {
    background: #f6f7f9;
    color: #202124;
    font-family: "Segoe UI", "SF Pro Display", Arial;
    font-size: 13px;
}
QWidget#sidebar {
    background: #ffffff;
    border-right: 1px solid #e4e6eb;
}
QLabel#appTitle {
    font-size: 19px;
    font-weight: 700;
}
QLabel#sectionLabel {
    color: #777b84;
    font-size: 11px;
    font-weight: 700;
}
QPushButton {
    background: #ffffff;
    border: 1px solid #dfe2e8;
    border-radius: 9px;
    padding: 8px 12px;
}
QPushButton:hover {
    background: #f0f2f5;
}
QPushButton:pressed {
    background: #e6e8ec;
}
QPushButton#primary {
    background: #202124;
    color: white;
    border: none;
    font-weight: 600;
    padding: 9px 15px;
}
QPushButton#primary:hover {
    background: #303136;
}
QListWidget {
    background: transparent;
    border: none;
    outline: none;
}
QListWidget::item {
    border-radius: 9px;
    padding: 8px;
    margin: 2px 0;
}
QListWidget::item:selected {
    background: #eef0f4;
}
QFrame#pageArea {
    background: #f6f7f9;
    border: none;
}
QLabel#emptyTitle {
    font-size: 22px;
    font-weight: 700;
}
QLabel#emptyText {
    color: #777b84;
    font-size: 13px;
}
QFrame#dropZone {
    background: #ffffff;
    border: 1px dashed #cdd1d8;
    border-radius: 16px;
}
QLabel#dropIcon {
    font-size: 32px;
}
QStatusBar {
    background: #ffffff;
    border-top: 1px solid #e4e6eb;
}
"""

DARK_QSS = """
QMainWindow, QWidget {
    background: #17181b;
    color: #f1f2f4;
    font-family: "Segoe UI", "SF Pro Display", Arial;
    font-size: 13px;
}
QWidget#sidebar {
    background: #1d1f23;
    border-right: 1px solid #303238;
}
QLabel#appTitle {
    font-size: 19px;
    font-weight: 700;
}
QLabel#sectionLabel {
    color: #9297a1;
    font-size: 11px;
    font-weight: 700;
}
QPushButton {
    background: #24262b;
    border: 1px solid #363941;
    border-radius: 9px;
    padding: 8px 12px;
    color: #f1f2f4;
}
QPushButton:hover {
    background: #2d3036;
}
QPushButton:pressed {
    background: #34373e;
}
QPushButton#primary {
    background: #f1f2f4;
    color: #17181b;
    border: none;
    font-weight: 600;
    padding: 9px 15px;
}
QPushButton#primary:hover {
    background: #ffffff;
}
QListWidget {
    background: transparent;
    border: none;
    outline: none;
}
QListWidget::item {
    border-radius: 9px;
    padding: 8px;
    margin: 2px 0;
}
QListWidget::item:selected {
    background: #30333a;
}
QFrame#pageArea {
    background: #17181b;
    border: none;
}
QLabel#emptyTitle {
    font-size: 22px;
    font-weight: 700;
}
QLabel#emptyText {
    color: #9297a1;
    font-size: 13px;
}
QFrame#dropZone {
    background: #1d1f23;
    border: 1px dashed #464a54;
    border-radius: 16px;
}
QLabel#dropIcon {
    font-size: 32px;
}
QStatusBar {
    background: #1d1f23;
    border-top: 1px solid #303238;
}
"""
