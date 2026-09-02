from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog, QFrame, QMessageBox,
    QSpacerItem, QSizePolicy
)

from .theme import LIGHT_QSS, DARK_QSS


class DropZone(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 35, 40, 35)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel("＋")
        icon.setObjectName("dropIcon")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Drop PDF files here")
        title.setObjectName("emptyTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text = QLabel("or use the Add PDF button")
        text.setObjectName("emptyText")
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(text)

        self.on_files = None

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        paths = []
        for url in event.mimeData().urls():
            if url.isLocalFile() and Path(url.toLocalFile()).suffix.lower() == ".pdf":
                paths.append(url.toLocalFile())
        if paths and self.on_files:
            self.on_files(paths)
        event.acceptProposedAction()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.documents = []
        self.dark_mode = False

        self.setWindowTitle("PDF Manager")
        self.resize(1280, 800)
        self.setMinimumSize(900, 600)
        self.setAcceptDrops(True)

        self.build_ui()
        self.build_menu()
        self.apply_theme()
        self.statusBar().showMessage("Ready")

    def build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        main = QHBoxLayout(root)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(18, 20, 18, 18)
        side.setSpacing(12)

        title = QLabel("◈  PDF Manager")
        title.setObjectName("appTitle")
        side.addWidget(title)

        add_btn = QPushButton("+  Add PDF")
        add_btn.setObjectName("primary")
        add_btn.clicked.connect(self.add_pdfs)
        side.addWidget(add_btn)

        label = QLabel("DOCUMENTS")
        label.setObjectName("sectionLabel")
        side.addWidget(label)

        self.document_list = QListWidget()
        self.document_list.itemClicked.connect(self.document_clicked)
        side.addWidget(self.document_list)

        side.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        settings = QPushButton("⚙  Settings")
        settings.clicked.connect(self.toggle_theme)
        side.addWidget(settings)

        # Main area
        content = QWidget()
        content.setObjectName("pageArea")
        center = QVBoxLayout(content)
        center.setContentsMargins(28, 24, 28, 24)
        center.setSpacing(18)

        top = QHBoxLayout()
        self.page_count = QLabel("0 pages")
        self.page_count.setStyleSheet("font-size: 15px; font-weight: 600;")
        top.addWidget(self.page_count)
        top.addStretch()

        self.zoom_label = QLabel("100%")
        top.addWidget(self.zoom_label)
        center.addLayout(top)

        center.addStretch()

        self.empty_title = QLabel("Your workspace is empty")
        self.empty_title.setObjectName("emptyTitle")
        self.empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center.addWidget(self.empty_title)

        self.drop_zone = DropZone()
        self.drop_zone.setMaximumWidth(520)
        self.drop_zone.setMinimumHeight(190)
        self.drop_zone.on_files = self.add_pdf_paths
        center.addWidget(self.drop_zone, alignment=Qt.AlignmentFlag.AlignCenter)

        center.addStretch()

        # Bottom toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(7)

        for text in ("↶  Undo", "↷  Redo", "↺  Rotate", "↻  Rotate", "⧉  Duplicate", "+  Blank", "🗑  Delete"):
            btn = QPushButton(text)
            btn.setEnabled(False)
            toolbar.addWidget(btn)

        toolbar.addStretch()

        export = QPushButton("Export PDF  →")
        export.setObjectName("primary")
        export.setEnabled(False)
        toolbar.addWidget(export)

        center.addLayout(toolbar)

        main.addWidget(sidebar)
        main.addWidget(content, 1)

        self.sidebar = sidebar
        self.content = content

    def build_menu(self):
        file_menu = self.menuBar().addMenu("&File")

        add = QAction("Add PDF…", self)
        add.setShortcut("Ctrl+O")
        add.triggered.connect(self.add_pdfs)
        file_menu.addAction(add)

        file_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        view_menu = self.menuBar().addMenu("&View")
        theme = QAction("Toggle Light / Dark Mode", self)
        theme.setShortcut("Ctrl+Shift+D")
        theme.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme)

    def apply_theme(self):
        self.setStyleSheet(DARK_QSS if self.dark_mode else LIGHT_QSS)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def add_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Add PDF files",
            "",
            "PDF files (*.pdf)"
        )
        if files:
            self.add_pdf_paths(files)

    def add_pdf_paths(self, paths):
        added = 0
        for path in paths:
            path = str(Path(path).resolve())
            if path.lower().endswith(".pdf") and path not in self.documents:
                self.documents.append(path)
                item = QListWidgetItem(Path(path).name)
                item.setToolTip(path)
                self.document_list.addItem(item)
                added += 1

        if added:
            self.page_count.setText(
                f"{len(self.documents)} PDF" + ("" if len(self.documents) == 1 else "s")
            )
            self.empty_title.setText("PDFs added")
            self.statusBar().showMessage(
                f"Added {added} PDF" + ("" if added == 1 else "s")
            )

    def document_clicked(self, item):
        QMessageBox.information(
            self,
            "PDF loaded",
            f"Loaded:\n{item.toolTip()}\n\n"
            "Page thumbnails and editing will be added in the next phase."
        )

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        paths = [
            url.toLocalFile()
            for url in event.mimeData().urls()
            if url.isLocalFile() and Path(url.toLocalFile()).suffix.lower() == ".pdf"
        ]
        if paths:
            self.add_pdf_paths(paths)
        event.acceptProposedAction()
