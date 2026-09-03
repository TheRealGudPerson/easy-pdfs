from PySide6.QtCore import (
    QMimeData,
    QPoint,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QDrag,
    QMouseEvent,
    QPainter,
)
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
)

from easypdf.models.page import PageRef
from easypdf.pdf.renderer import PDFRenderer


MIME_TYPE = "application/x-easypdf-page"


class PageThumbnail(QFrame):
    clicked = Signal(int, object)
    double_clicked = Signal(int)

    def __init__(
        self,
        index: int,
        page_ref: PageRef,
        renderer: PDFRenderer,
        selected: bool = False,
        parent=None,
    ):
        super().__init__(parent)

        self.index = index
        self.page_ref = page_ref
        self.renderer = renderer

        self.drag_start_position = QPoint()

        self.setObjectName("PageThumbnail")
        self.setFixedSize(220, 300)

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        self._build_ui()

        self.set_selected(selected)

    def _build_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(
            10,
            10,
            10,
            8,
        )

        self.layout.setSpacing(6)

        self.preview = QLabel()
        self.preview.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.preview.setMinimumHeight(235)

        self.title = QLabel()
        self.title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.title.setWordWrap(True)

        self.layout.addWidget(
            self.preview,
            1,
        )

        self.layout.addWidget(
            self.title
        )

        self.refresh()

    def refresh(self):
        pixmap = self.renderer.render(
            self.page_ref,
            max_width=190,
            max_height=225,
        )

        self.preview.setPixmap(pixmap)

        if self.page_ref.blank:
            source = "Blank page"
        else:
            source = self.page_ref.source_name

        self.title.setText(
            f"{self.index + 1}  •  {source}"
        )

    def set_selected(self, selected: bool):
        self.setProperty(
            "selected",
            bool(selected),
        )

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def mousePressEvent(
        self,
        event: QMouseEvent,
    ):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.position().toPoint()

            modifiers = event.modifiers()

            self.clicked.emit(
                self.index,
                modifiers,
            )

        super().mousePressEvent(event)

    def mouseMoveEvent(
        self,
        event: QMouseEvent,
    ):
        if not (
            event.buttons()
            & Qt.MouseButton.LeftButton
        ):
            return

        distance = (
            event.position().toPoint()
            - self.drag_start_position
        ).manhattanLength()

        if distance < 10:
            return

        mime = QMimeData()

        mime.setData(
            MIME_TYPE,
            str(self.index).encode(),
        )

        drag = QDrag(self)

        drag.setMimeData(mime)

        drag.exec(
            Qt.DropAction.MoveAction
        )

    def mouseDoubleClickEvent(
        self,
        event: QMouseEvent,
    ):
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(
                self.index
            )

        super().mouseDoubleClickEvent(event)