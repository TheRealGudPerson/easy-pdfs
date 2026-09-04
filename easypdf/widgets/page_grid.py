from PySide6.QtCore import (
    QPoint,
    QRect,
    Signal,
    Qt,
)
from PySide6.QtGui import (
    QDragEnterEvent,
    QDropEvent,
    QPainter,
    QPen,
)
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QScrollArea,
    QSizePolicy,
    QWidget,
)

from easypdf.models.page import PageRef
from easypdf.pdf.renderer import PDFRenderer
from easypdf.widgets.page_thumbnail import (
    MIME_TYPE,
    PageThumbnail,
)


class PageGrid(QScrollArea):
    selection_changed = Signal(list)
    pages_reordered = Signal(list, int)
    page_double_clicked = Signal(int)

    def __init__(
        self,
        renderer: PDFRenderer,
        parent=None,
    ):
        super().__init__(parent)

        self.renderer = renderer

        self.pages: list[PageRef] = []

        self.selected_indexes: set[int] = set()

        self.anchor_index: int | None = None

        # Index where dragged pages would be inserted.
        self.drag_target_index: int | None = None

        self.is_dragging_pages = False

        self.setAcceptDrops(True)
        self.setWidgetResizable(True)

        self.container = QWidget()

        self.container = QWidget()
        self.container.setObjectName(
            "PageGridContainer"
        )

        self.grid = QGridLayout(
            self.container
        )

        self.grid.setContentsMargins(
            20,
            20,
            20,
            30,
        )

        self.grid.setHorizontalSpacing(18)
        self.grid.setVerticalSpacing(18)

        self.setWidget(
            self.container
        )

        self.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        # Allow the insertion indicator to repaint smoothly.
        self.viewport().setAttribute(
            Qt.WidgetAttribute.WA_OpaquePaintEvent,
            False,
        )

        self.viewport().setObjectName(
            "PageGridViewport"
        )

    # ---------------------------------------------------------
    # Page management
    # ---------------------------------------------------------

    def set_pages(
        self,
        pages: list[PageRef],
        keep_selection: bool = False,
    ):
        if keep_selection:
            old_uids = {
                self.pages[index].uid
                for index in self.selected_indexes
                if 0 <= index < len(self.pages)
            }
        else:
            old_uids = set()

        self.pages = pages

        self._rebuild(
            old_uids=old_uids
        )

    def _clear(self):
        while self.grid.count():
            item = self.grid.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def _columns(self) -> int:
        width = max(
            1,
            self.viewport().width(),
        )

        # Approximate card width plus spacing.
        card_width = 238

        return max(
            1,
            width // card_width,
        )

    def _rebuild(
        self,
        old_uids=None,
    ):
        self._clear()

        if old_uids is None:
            old_uids = set()

        self.selected_indexes = set()

        columns = self._columns()

        for index, page in enumerate(
            self.pages
        ):
            selected = (
                page.uid in old_uids
            )

            if selected:
                self.selected_indexes.add(
                    index
                )

            card = PageThumbnail(
                index=index,
                page_ref=page,
                renderer=self.renderer,
                selected=selected,
            )

            card.clicked.connect(
                self._page_clicked
            )

            card.double_clicked.connect(
                self.page_double_clicked
            )

            row = index // columns
            column = index % columns

            self.grid.addWidget(
                card,
                row,
                column,
            )

        rows = (
            (len(self.pages) - 1) // columns + 1
            if self.pages
            else 0
        )

        self.grid.setRowStretch(
            rows,
            1,
        )

        self.selection_changed.emit(
            sorted(
                self.selected_indexes
            )
        )

        self.viewport().update()

    def resizeEvent(self, event):
        old_uids = {
            self.pages[index].uid
            for index in self.selected_indexes
            if 0 <= index < len(self.pages)
        }

        super().resizeEvent(event)

        self._rebuild(
            old_uids=old_uids
        )

    # ---------------------------------------------------------
    # Selection
    # ---------------------------------------------------------

    def _page_clicked(
        self,
        index: int,
        modifiers,
    ):
        ctrl = bool(
            modifiers
            & Qt.KeyboardModifier.ControlModifier
        )

        meta = bool(
            modifiers
            & Qt.KeyboardModifier.MetaModifier
        )

        shift = bool(
            modifiers
            & Qt.KeyboardModifier.ShiftModifier
        )

        multi = ctrl or meta

        if shift and self.anchor_index is not None:
            start = min(
                self.anchor_index,
                index,
            )

            end = max(
                self.anchor_index,
                index,
            )

            self.selected_indexes = set(
                range(
                    start,
                    end + 1,
                )
            )

        elif multi:
            if index in self.selected_indexes:
                self.selected_indexes.remove(
                    index
                )
            else:
                self.selected_indexes.add(
                    index
                )

            self.anchor_index = index

        else:
            self.selected_indexes = {
                index
            }

            self.anchor_index = index

        self._update_selection_visuals()

        self.selection_changed.emit(
            sorted(
                self.selected_indexes
            )
        )

    def _update_selection_visuals(self):
        for i in range(
            self.grid.count()
        ):
            item = self.grid.itemAt(i)

            widget = item.widget()

            if isinstance(
                widget,
                PageThumbnail,
            ):
                widget.set_selected(
                    widget.index
                    in self.selected_indexes
                )

    def clear_selection(self):
        self.selected_indexes.clear()

        self.anchor_index = None

        self._update_selection_visuals()

        self.selection_changed.emit([])

    def selected(self) -> list[int]:
        return sorted(
            self.selected_indexes
        )

    # ---------------------------------------------------------
    # Drag insertion calculation
    # ---------------------------------------------------------

    def _card_widgets(self):
        """
        Return all page cards in page order.
        """
        cards = []

        for i in range(
            self.grid.count()
        ):
            item = self.grid.itemAt(i)

            widget = item.widget()

            if isinstance(
                widget,
                PageThumbnail,
            ):
                cards.append(widget)

        cards.sort(
            key=lambda widget: widget.index
        )

        return cards

    def drop_target_index(
        self,
        position: QPoint,
    ) -> int:
        """
        Calculate the insertion point.

        The result represents an insertion position between pages:

            0 | Page 1 | 1 | Page 2 | 2 | Page 3 | 3

        This is more useful than simply returning the page
        underneath the cursor.
        """

        cards = self._card_widgets()

        if not cards:
            return 0

        # Convert viewport coordinates to container coordinates.
        container_position = self.container.mapFrom(
            self.viewport(),
            position,
        )

        for index, card in enumerate(cards):

            rect = card.geometry()

            if not rect.contains(
                container_position
            ):
                continue

            center = rect.center()

            columns = self._columns()

            column = index % columns

            # For cards that aren't in the final column,
            # use the horizontal midpoint as the insertion
            # boundary.
            if (
                container_position.x()
                < center.x()
            ):
                return index

            return index + 1

        # If the cursor isn't directly over a card, find
        # the nearest card center.
        closest_index = len(cards)

        closest_distance = None

        for index, card in enumerate(cards):
            rect = card.geometry()

            center = rect.center()

            dx = (
                container_position.x()
                - center.x()
            )

            dy = (
                container_position.y()
                - center.y()
            )

            distance = (
                dx * dx
                + dy * dy
            )

            if (
                closest_distance is None
                or distance < closest_distance
            ):
                closest_distance = distance
                closest_index = (
                    index
                    if container_position.x()
                    < center.x()
                    else index + 1
                )

        return max(
            0,
            min(
                closest_index,
                len(cards),
            ),
        )

    # ---------------------------------------------------------
    # Insertion indicator
    # ---------------------------------------------------------

    def _indicator_rect(
        self,
        target_index: int,
    ) -> QRect | None:
        """
        Calculate the visible insertion indicator rectangle
        in viewport coordinates.
        """

        cards = self._card_widgets()

        if not cards:
            # Empty workspace.
            viewport_rect = self.viewport().rect()

            x = viewport_rect.width() // 2

            return QRect(
                x - 2,
                25,
                4,
                max(
                    30,
                    viewport_rect.height() - 50,
                ),
            )

        target_index = max(
            0,
            min(
                target_index,
                len(cards),
            ),
        )

        columns = self._columns()

        # -----------------------------------------------------
        # Before first page
        # -----------------------------------------------------

        if target_index == 0:
            card = cards[0]

            point = self.container.mapTo(
                self.viewport(),
                card.geometry().topLeft(),
            )

            return QRect(
                point.x() - 5,
                point.y() - 5,
                4,
                card.height() + 10,
            )

        # -----------------------------------------------------
        # After last page
        # -----------------------------------------------------

        if target_index >= len(cards):
            card = cards[-1]

            point = self.container.mapTo(
                self.viewport(),
                card.geometry().topRight(),
            )

            return QRect(
                point.x() + 1,
                point.y() - 5,
                4,
                card.height() + 10,
            )

        # -----------------------------------------------------
        # Between two pages
        # -----------------------------------------------------

        before = cards[target_index - 1]
        after = cards[target_index]

        before_rect = before.geometry()
        after_rect = after.geometry()

        before_point = self.container.mapTo(
            self.viewport(),
            before_rect.topRight(),
        )

        after_point = self.container.mapTo(
            self.viewport(),
            after_rect.topLeft(),
        )

        # If the two pages are on the same row,
        # draw a vertical line between them.
        if (
            before_rect.center().y()
            == after_rect.center().y()
        ):
            x = (
                before_point.x()
                + after_point.x()
            ) // 2

            top = min(
                before_point.y(),
                after_point.y(),
            )

            height = max(
                before.height(),
                after.height(),
            )

            return QRect(
                x - 2,
                top - 5,
                4,
                height + 10,
            )

        # -----------------------------------------------------
        # Between rows
        # -----------------------------------------------------

        before_bottom = self.container.mapTo(
            self.viewport(),
            before_rect.bottomLeft(),
        )

        after_top = self.container.mapTo(
            self.viewport(),
            after_rect.topLeft(),
        )

        y = (
            before_bottom.y()
            + after_top.y()
        ) // 2

        left = min(
            before_bottom.x(),
            after_top.x(),
        )

        right = max(
            before_bottom.x()
            + before.width(),
            after_top.x()
            + after.width(),
        )

        return QRect(
            left - 5,
            y - 2,
            max(
                30,
                right - left + 10,
            ),
            4,
        )

    def _set_drag_target(
        self,
        target_index: int | None,
    ):
        if (
            target_index is not None
            and self.pages
        ):
            target_index = max(
                0,
                min(
                    target_index,
                    len(self.pages),
                ),
            )

        if (
            self.drag_target_index
            == target_index
        ):
            return

        self.drag_target_index = target_index

        self.viewport().update()

    def paintEvent(self, event):
        super().paintEvent(event)

        if (
            not self.is_dragging_pages
            or self.drag_target_index is None
        ):
            return

        rect = self._indicator_rect(
            self.drag_target_index
        )

        if rect is None:
            return

        painter = QPainter(
            self.viewport()
        )

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        # Use the application's standard accent-ish
        # highlight without requiring a hard-coded stylesheet
        # dependency.
        pen = QPen(
            self.palette().highlight()
        )

        pen.setWidth(4)
        pen.setCapStyle(
            Qt.PenCapStyle.RoundCap
        )

        painter.setPen(pen)

        if rect.width() <= 6:
            x = rect.center().x()

            painter.drawLine(
                x,
                rect.top(),
                x,
                rect.bottom(),
            )
        else:
            y = rect.center().y()

            painter.drawLine(
                rect.left(),
                y,
                rect.right(),
                y,
            )

        painter.end()

    # ---------------------------------------------------------
    # Drag/drop
    # ---------------------------------------------------------

    def dragEnterEvent(
        self,
        event: QDragEnterEvent,
    ):
        if event.mimeData().hasFormat(
            MIME_TYPE
        ):
            self.is_dragging_pages = True

            raw = event.mimeData().data(
                MIME_TYPE
            )

            try:
                source_index = int(
                    bytes(raw).decode()
                )
            except ValueError:
                event.ignore()
                return

            if (
                source_index
                not in self.selected_indexes
            ):
                self.selected_indexes = {
                    source_index
                }

                self.anchor_index = (
                    source_index
                )

                self._update_selection_visuals()

                self.selection_changed.emit(
                    [source_index]
                )

            self._set_drag_target(
                None
            )

            event.acceptProposedAction()

            return

        event.ignore()

    def dragMoveEvent(self, event):
        if not event.mimeData().hasFormat(
            MIME_TYPE
        ):
            event.ignore()
            return

        target = self.drop_target_index(
            event.position().toPoint()
        )

        self._set_drag_target(
            target
        )

        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.is_dragging_pages = False

        self._set_drag_target(
            None
        )

        super().dragLeaveEvent(
            event
        )

    def dropEvent(
        self,
        event: QDropEvent,
    ):
        if not event.mimeData().hasFormat(
            MIME_TYPE
        ):
            event.ignore()
            return

        raw = event.mimeData().data(
            MIME_TYPE
        )

        try:
            source_index = int(
                bytes(raw).decode()
            )
        except ValueError:
            self.is_dragging_pages = False
            self._set_drag_target(None)
            event.ignore()
            return

        selected = self.selected()

        if source_index not in selected:
            selected = [
                source_index
            ]

        # Recalculate the final target from the
        # actual drop position.
        target = self.drop_target_index(
            event.position().toPoint()
        )

        self.is_dragging_pages = False

        self._set_drag_target(
            None
        )

        self.pages_reordered.emit(
            selected,
            target,
        )

        event.acceptProposedAction()