from functools import lru_cache

import fitz

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap

from easypdf.models.page import PageRef


class PDFRenderer:
    def __init__(self):
        pass

    @staticmethod
    def _pixmap_from_page(
        page: fitz.Page,
        rotation: int,
        max_width: int,
        max_height: int,
    ) -> QPixmap:

        rect = page.rect

        scale = min(
            max_width / max(rect.width, 1),
            max_height / max(rect.height, 1),
        )

        scale = max(scale, 0.05)

        matrix = fitz.Matrix(
            scale,
            scale,
        )

        pix = page.get_pixmap(
            matrix=matrix,
            alpha=False,
            annots=True,
        )

        image = QImage(
            pix.samples,
            pix.width,
            pix.height,
            pix.stride,
            QImage.Format.Format_RGB888,
        ).copy()

        result = QPixmap.fromImage(image)

        if rotation:
            transform = result.transformed(
                __import__(
                    "PySide6.QtGui",
                    fromlist=["QTransform"],
                ).QTransform().rotate(rotation),
                Qt.TransformationMode.SmoothTransformation,
            )
            result = transform

        return result

    def render(
        self,
        page_ref: PageRef,
        max_width: int = 180,
        max_height: int = 240,
    ) -> QPixmap:

        if page_ref.blank:
            return self._render_blank(
                max_width,
                max_height,
                page_ref.rotation,
                page_ref.width,
                page_ref.height,
            )

        if not page_ref.source_path:
            return QPixmap()

        document = fitz.open(page_ref.source_path)

        try:
            if not (
                0 <= page_ref.source_index < len(document)
            ):
                return QPixmap()

            page = document.load_page(
                page_ref.source_index
            )

            return self._pixmap_from_page(
                page,
                page_ref.rotation,
                max_width,
                max_height,
            )

        finally:
            document.close()

    @staticmethod
    def _render_blank(
        max_width: int,
        max_height: int,
        rotation: int,
        width: float,
        height: float,
    ) -> QPixmap:

        scale = min(
            max_width / max(width, 1),
            max_height / max(height, 1),
        )

        pixel_width = max(
            20,
            int(width * scale),
        )

        pixel_height = max(
            20,
            int(height * scale),
        )

        image = QImage(
            pixel_width,
            pixel_height,
            QImage.Format.Format_RGB32,
        )

        image.fill(Qt.GlobalColor.white)

        pixmap = QPixmap.fromImage(image)

        if rotation:
            from PySide6.QtGui import QTransform

            pixmap = pixmap.transformed(
                QTransform().rotate(rotation),
                Qt.TransformationMode.SmoothTransformation,
            )

        return pixmap