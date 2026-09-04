from __future__ import annotations

import os
from pathlib import Path

import fitz

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QDialog,
    QScrollArea,
)

from easypdf.models import (
    SourceDocument,
    Workspace,
    WorkspaceSnapshot,
)
from easypdf.pdf import PDFRenderer
from easypdf.theme import (
    DARK_THEME,
    LIGHT_THEME,
    build_palette,
)
from easypdf.widgets import PageGrid


class PreviewDialog(QDialog):
    def __init__(
        self,
        pixmap,
        page_number: int,
        parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle(
            f"Page {page_number}"
        )

        self.resize(
            800,
            900,
        )

        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        label = QLabel()
        label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        label.setPixmap(pixmap)

        scroll.setWidget(label)

        layout.addWidget(scroll)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.workspace = Workspace()
        self.renderer = PDFRenderer()

        self.dark_mode = self._system_is_dark()

        self.undo_stack: list[
            WorkspaceSnapshot
        ] = []

        self.redo_stack: list[
            WorkspaceSnapshot
        ] = []

        self._building_document_list = False

        self.setWindowTitle(
            "EasyPDF"
        )

        self.resize(
            1400,
            900,
        )

        self.setAcceptDrops(True)

        self._build_menu()
        self._build_ui()
        self._apply_theme()

        self._update_actions()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------

    def _build_ui(self):
        root = QWidget()

        root_layout = QHBoxLayout(root)

        root_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        root_layout.setSpacing(0)

        # -----------------------------------------------------
        # Sidebar
        # -----------------------------------------------------

        self.sidebar = QFrame()
        self.sidebar.setObjectName(
            "Sidebar"
        )

        side_layout = QVBoxLayout(
            self.sidebar
        )

        side_layout.setContentsMargins(
            10,
            14,
            10,
            10,
        )

        side_layout.setSpacing(8)

        title = QLabel(
            "EasyPDF"
        )

        title.setObjectName(
            "SidebarTitle"
        )

        side_layout.addWidget(title)

        add_button = QPushButton(
            "＋  Add PDFs"
        )

        add_button.setObjectName(
            "PrimaryButton"
        )

        add_button.clicked.connect(
            self.add_pdfs
        )

        side_layout.addWidget(
            add_button
        )

        self.document_list = QListWidget()

        self.document_list.currentRowChanged.connect(
            self._document_selected
        )

        # This stretch is important.
        # It forces the theme button to the bottom.
        side_layout.addWidget(
            self.document_list,
            1,
        )

        self.theme_button = QPushButton(
            "☾  Dark Mode"
        )

        self.theme_button.clicked.connect(
            self.toggle_theme
        )

        side_layout.addWidget(
            self.theme_button
        )

        # -----------------------------------------------------
        # Main content
        # -----------------------------------------------------

        content = QWidget()

        content_layout = QVBoxLayout(content)

        content_layout.setContentsMargins(
            18,
            15,
            18,
            15,
        )

        content_layout.setSpacing(12)

        # Toolbar

        toolbar = QHBoxLayout()

        self.page_count_label = QLabel(
            "0 pages"
        )

        toolbar.addWidget(
            self.page_count_label
        )

        toolbar.addStretch()

        self.add_blank_button = QPushButton(
            "＋ Blank"
        )

        self.add_blank_button.clicked.connect(
            self.add_blank_page
        )

        toolbar.addWidget(
            self.add_blank_button
        )

        self.rotate_left_button = QPushButton(
            "↺ Rotate"
        )

        self.rotate_left_button.clicked.connect(
            lambda: self.rotate_pages(-90)
        )

        toolbar.addWidget(
            self.rotate_left_button
        )

        self.rotate_right_button = QPushButton(
            "↻ Rotate"
        )

        self.rotate_right_button.clicked.connect(
            lambda: self.rotate_pages(90)
        )

        toolbar.addWidget(
            self.rotate_right_button
        )

        self.duplicate_button = QPushButton(
            "⧉ Duplicate"
        )

        self.duplicate_button.clicked.connect(
            self.duplicate_pages
        )

        toolbar.addWidget(
            self.duplicate_button
        )

        self.delete_button = QPushButton(
            "Delete"
        )

        self.delete_button.clicked.connect(
            self.delete_pages
        )

        toolbar.addWidget(
            self.delete_button
        )

        self.export_button = QPushButton(
            "Export PDF"
        )

        self.export_button.setObjectName(
            "PrimaryButton"
        )

        self.export_button.clicked.connect(
            self.export_pdf
        )

        toolbar.addWidget(
            self.export_button
        )

        content_layout.addLayout(
            toolbar
        )

        self.page_grid = PageGrid(
            self.renderer
        )

        self.page_grid.selection_changed.connect(
            self._selection_changed
        )

        self.page_grid.pages_reordered.connect(
            self.reorder_pages
        )

        self.page_grid.page_double_clicked.connect(
            self.preview_page
        )

        content_layout.addWidget(
            self.page_grid,
            1,
        )

        root_layout.addWidget(
            self.sidebar
        )

        root_layout.addWidget(
            content,
            1,
        )

        self.setCentralWidget(root)

    # ---------------------------------------------------------
    # Menu
    # ---------------------------------------------------------

    def _build_menu(self):
        menu_bar = self.menuBar()

        # File

        file_menu = menu_bar.addMenu(
            "File"
        )

        add_action = QAction(
            "Add PDFs…",
            self,
        )

        add_action.setShortcut(
            QKeySequence.Open
        )

        add_action.triggered.connect(
            self.add_pdfs
        )

        file_menu.addAction(
            add_action
        )

        export_action = QAction(
            "Export PDF…",
            self,
        )

        export_action.setShortcut(
            QKeySequence.Save
        )

        export_action.triggered.connect(
            self.export_pdf
        )

        file_menu.addAction(
            export_action
        )

        file_menu.addSeparator()

        quit_action = QAction(
            "Quit",
            self,
        )

        quit_action.setShortcut(
            QKeySequence.Quit
        )

        quit_action.triggered.connect(
            self.close
        )

        file_menu.addAction(
            quit_action
        )

        # View

        view_menu = menu_bar.addMenu(
            "View"
        )

        undo_action = QAction(
            "Undo",
            self,
        )

        undo_action.setShortcut(
            QKeySequence.Undo
        )

        undo_action.triggered.connect(
            self.undo
        )

        self.undo_action = undo_action

        view_menu.addAction(
            undo_action
        )

        redo_action = QAction(
            "Redo",
            self,
        )

        redo_action.setShortcut(
            QKeySequence.Redo
        )

        redo_action.triggered.connect(
            self.redo
        )

        self.redo_action = redo_action

        view_menu.addAction(
            redo_action
        )

        view_menu.addSeparator()

        theme_action = QAction(
            "Toggle Dark Mode",
            self,
        )

        theme_action.triggered.connect(
            self.toggle_theme
        )

        view_menu.addAction(
            theme_action
        )

        # Help

        help_menu = menu_bar.addMenu(
            "Help"
        )

        guide_action = QAction(
            "Quick Guide",
            self,
        )

        guide_action.triggered.connect(
            self.show_quick_guide
        )

        help_menu.addAction(
            guide_action
        )

        about_action = QAction(
            "About EasyPDF",
            self,
        )

        about_action.triggered.connect(
            self.show_about
        )

        help_menu.addAction(
            about_action
        )

    # ---------------------------------------------------------
    # Theme
    # ---------------------------------------------------------

    def _system_is_dark(self) -> bool:
        """
        Detect the operating system's current color scheme.

        EasyPDF uses this only as its initial theme. Once the
        user explicitly chooses Dark Mode or Light Mode, the
        application controls its own appearance.
        """

        app = QApplication.instance()

        if app is None:
            return False

        color_scheme = app.styleHints().colorScheme()

        return (
            color_scheme
            == Qt.ColorScheme.Dark
        )


    def _apply_theme(self):
        app = QApplication.instance()

        if app is None:
            return

        if self.dark_mode:
            app.setPalette(
                build_palette(True)
            )

            app.setStyleSheet(
                DARK_THEME
            )

            self.theme_button.setText(
                "☀  Light Mode"
            )

        else:
            app.setPalette(
                build_palette(False)
            )

            app.setStyleSheet(
                LIGHT_THEME
            )

            self.theme_button.setText(
                "☾  Dark Mode"
            )


    def toggle_theme(self):
        self.dark_mode = not self.dark_mode

        self._apply_theme()

    # ---------------------------------------------------------
    # Documents
    # ---------------------------------------------------------

    def add_pdfs(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Add PDF files",
            "",
            "PDF Files (*.pdf)",
        )

        if not paths:
            return

        self._add_paths(paths)

    def _add_paths(self, paths):
        valid_documents = []

        for path in paths:
            try:
                document = SourceDocument.from_path(
                    path
                )

                if document.page_count == 0:
                    continue

                valid_documents.append(
                    document
                )

            except Exception as exc:
                QMessageBox.warning(
                    self,
                    "Unable to open PDF",
                    f"Could not open:\n\n{path}\n\n{exc}",
                )

        if not valid_documents:
            return

        for document in valid_documents:
            self.workspace.add_document(
                document
            )

        self._refresh_document_list()

        self._refresh_pages()

    def _refresh_document_list(self):
        self._building_document_list = True

        try:
            self.document_list.clear()

            for document in self.workspace.documents:
                item = QListWidgetItem(
                    document.name
                )

                item.setToolTip(
                    document.path
                )

                self.document_list.addItem(
                    item
                )

        finally:
            self._building_document_list = False

    def _document_selected(self, row: int):
        if self._building_document_list:
            return

        if row < 0:
            return

        if row >= len(
            self.workspace.documents
        ):
            return

        document = (
            self.workspace.documents[row]
        )

        indexes = [
            index
            for index, page in enumerate(
                self.workspace.pages
            )
            if page.source_path == document.path
        ]

        if not indexes:
            return

        self.page_grid.selected_indexes = set(
            indexes
        )

        self.page_grid.anchor_index = indexes[0]

        self.page_grid._update_selection_visuals()

        self.page_grid.selection_changed.emit(
            indexes
        )

    # ---------------------------------------------------------
    # Workspace history
    # ---------------------------------------------------------

    def _record_history(self):
        self.undo_stack.append(
            self.workspace.snapshot()
        )

        self.redo_stack.clear()

        # Prevent unlimited memory growth from
        # accidental Ctrl+Z archaeology.
        if len(self.undo_stack) > 100:
            self.undo_stack.pop(0)

        self._update_actions()

    def undo(self):
        if not self.undo_stack:
            return

        self.redo_stack.append(
            self.workspace.snapshot()
        )

        snapshot = self.undo_stack.pop()

        self.workspace.restore(
            snapshot
        )

        self._refresh_pages()

        self._update_actions()

    def redo(self):
        if not self.redo_stack:
            return

        self.undo_stack.append(
            self.workspace.snapshot()
        )

        snapshot = self.redo_stack.pop()

        self.workspace.restore(
            snapshot
        )

        self._refresh_pages()

        self._update_actions()

    # ---------------------------------------------------------
    # Page operations
    # ---------------------------------------------------------

    def _refresh_pages(self):
        self.page_grid.set_pages(
            self.workspace.pages,
            keep_selection=True,
        )

        self._update_page_count()
        self._update_actions()

    def _update_page_count(self):
        count = len(
            self.workspace.pages
        )

        self.page_count_label.setText(
            f"{count} page"
            + ("" if count == 1 else "s")
        )

    def _selection_changed(self, indexes):
        self._update_actions()

    def _update_actions(self):
        selected = self.page_grid.selected()

        has_selection = bool(selected)
        has_pages = bool(
            self.workspace.pages
        )

        self.rotate_left_button.setEnabled(
            has_selection
        )

        self.rotate_right_button.setEnabled(
            has_selection
        )

        self.duplicate_button.setEnabled(
            has_selection
        )

        self.delete_button.setEnabled(
            has_selection
        )

        self.add_blank_button.setEnabled(
            True
        )

        self.export_button.setEnabled(
            has_pages
        )

        self.undo_action.setEnabled(
            bool(self.undo_stack)
        )

        self.redo_action.setEnabled(
            bool(self.redo_stack)
        )

    def rotate_pages(
        self,
        degrees: int,
    ):
        indexes = self.page_grid.selected()

        if not indexes:
            return

        self._record_history()

        self.workspace.rotate_pages(
            indexes,
            degrees,
        )

        self._refresh_pages()

    def delete_pages(self):
        indexes = self.page_grid.selected()

        if not indexes:
            return

        self._record_history()

        self.workspace.delete_pages(
            indexes
        )

        self.page_grid.clear_selection()

        self._refresh_pages()

    def duplicate_pages(self):
        indexes = self.page_grid.selected()

        if not indexes:
            return

        self._record_history()

        self.workspace.duplicate_pages(
            indexes
        )

        self._refresh_pages()

    def add_blank_page(self):
        self._record_history()

        selected = self.page_grid.selected()

        if selected:
            insert_at = max(selected) + 1
        else:
            insert_at = len(
                self.workspace.pages
            )

        self.workspace.add_blank_page(
            index=insert_at
        )

        self._refresh_pages()

    def reorder_pages(
        self,
        selected_indexes: list[int],
        target_index: int,
    ):
        if not selected_indexes:
            return

        # Avoid pointless moves.
        if (
            len(selected_indexes) == 1
            and target_index in (
                selected_indexes[0],
                selected_indexes[0] + 1,
            )
        ):
            return

        self._record_history()

        selected_uids = [
            self.workspace.pages[index].uid
            for index in selected_indexes
        ]

        self.workspace.move_pages(
            selected_indexes,
            target_index,
        )

        new_selection = []

        for index, page in enumerate(
            self.workspace.pages
        ):
            if page.uid in selected_uids:
                new_selection.append(index)

        self.page_grid.selected_indexes = set(
            new_selection
        )

        self.page_grid.anchor_index = (
            new_selection[0]
            if new_selection
            else None
        )

        self._refresh_pages()

    # ---------------------------------------------------------
    # Preview
    # ---------------------------------------------------------

    def preview_page(self, index: int):
        if not (
            0 <= index
            < len(self.workspace.pages)
        ):
            return

        page = self.workspace.pages[index]

        pixmap = self.renderer.render(
            page,
            max_width=700,
            max_height=850,
        )

        dialog = PreviewDialog(
            pixmap,
            index + 1,
            self,
        )

        dialog.exec()

    # ---------------------------------------------------------
    # Export
    # ---------------------------------------------------------

    def export_pdf(self):
        if not self.workspace.pages:
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export PDF",
            "combined.pdf",
            "PDF Files (*.pdf)",
        )

        if not path:
            return

        path = str(
            Path(path).resolve()
        )

        source_paths = {
            page.source_path
            for page in self.workspace.pages
            if not page.blank
            and page.source_path
        }

        if path in source_paths:
            QMessageBox.warning(
                self,
                "Cannot overwrite source PDF",
                "The export location is one of the source PDFs.\n\n"
                "Choose a different filename so the original "
                "PDF remains untouched.",
            )

            return

        output = fitz.open()

        try:
            for page_ref in self.workspace.pages:

                if page_ref.blank:
                    new_page = output.new_page(
                        width=page_ref.width,
                        height=page_ref.height,
                    )

                    if page_ref.rotation:
                        new_page.set_rotation(
                            page_ref.rotation
                        )

                    continue

                if not page_ref.source_path:
                    continue

                source = fitz.open(
                    page_ref.source_path
                )

                try:
                    if not (
                        0 <= page_ref.source_index
                        < len(source)
                    ):
                        continue

                    output.insert_pdf(
                        source,
                        from_page=page_ref.source_index,
                        to_page=page_ref.source_index,
                    )

                    new_page = output[-1]

                    if page_ref.rotation:
                        new_page.set_rotation(
                            page_ref.rotation
                        )

                finally:
                    source.close()

            output.save(
                path,
                garbage=3,
                deflate=True,
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                "Export failed",
                f"Could not export the PDF.\n\n{exc}",
            )

            return

        finally:
            output.close()

        QMessageBox.information(
            self,
            "Export complete",
            f"PDF successfully exported to:\n\n{path}",
        )

    # ---------------------------------------------------------
    # Help
    # ---------------------------------------------------------

    def show_quick_guide(self):
        QMessageBox.information(
            self,
            "EasyPDF Quick Guide",
            """
<b>EasyPDF</b>

<b>Import PDFs</b>
<br>
Use <b>File → Add PDFs</b> or drag PDF files directly
into the application.

<br><br>

<b>Rearrange pages</b>
<br>
Select one or more pages and drag them to another
position. Pages can be moved between different PDFs.

<br><br>

<b>Select pages</b>
<br>
• Click: select one page
<br>
• Ctrl/Cmd + click: select multiple pages
<br>
• Shift + click: select a range

<br><br>

<b>Page operations</b>
<br>
• Rotate
<br>
• Delete
<br>
• Duplicate
<br>
• Add blank page
<br>
• Double-click a page for a larger preview

<br><br>

<b>Keyboard shortcuts</b>
<br>
• Ctrl/Cmd + O: Add PDFs
<br>
• Ctrl/Cmd + S: Export
<br>
• Ctrl/Cmd + Z: Undo
<br>
• Ctrl/Cmd + Shift + Z: Redo
<br>
• Delete: Delete selected pages

<br><br>

<b>Export</b>
<br>
Export creates a new PDF using the exact page order
currently shown in the workspace.
""",
        )

    def show_about(self):
        QMessageBox.about(
            self,
            "About EasyPDF",
            """
<b>EasyPDF</b><br>
Version 0.3.0<br><br>

A cross-platform PDF page organizer built with
PySide6 and PyMuPDF.

<br><br>

Designed for Windows and macOS.
""",
        )

    # ---------------------------------------------------------
    # Drag/drop PDFs
    # ---------------------------------------------------------

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            paths = [
                url.toLocalFile()
                for url in event.mimeData().urls()
                if url.isLocalFile()
            ]

            if any(
                path.lower().endswith(".pdf")
                for path in paths
            ):
                event.acceptProposedAction()
                return

        event.ignore()

    def dropEvent(self, event):
        paths = [
            url.toLocalFile()
            for url in event.mimeData().urls()
            if url.isLocalFile()
            and url.toLocalFile()
                .lower()
                .endswith(".pdf")
        ]

        if paths:
            self._add_paths(paths)

            event.acceptProposedAction()
        else:
            event.ignore()

    # ---------------------------------------------------------
    # Keyboard
    # ---------------------------------------------------------

    def keyPressEvent(self, event):
        if (
            event.key()
            == Qt.Key.Key_Delete
        ):
            self.delete_pages()
            return

        if event.key() == Qt.Key.Key_R:
            self.rotate_pages(90)
            return

        if (
            event.key() == Qt.Key.Key_Z
            and event.modifiers()
            & Qt.KeyboardModifier.ControlModifier
        ):
            if (
                event.modifiers()
                & Qt.KeyboardModifier.ShiftModifier
            ):
                self.redo()
            else:
                self.undo()

            return

        if (
            event.key() == Qt.Key.Key_Z
            and event.modifiers()
            & Qt.KeyboardModifier.MetaModifier
        ):
            if (
                event.modifiers()
                & Qt.KeyboardModifier.ShiftModifier
            ):
                self.redo()
            else:
                self.undo()

            return

        super().keyPressEvent(event)