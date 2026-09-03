from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .document import SourceDocument
from .page import PageRef


@dataclass
class WorkspaceSnapshot:
    pages: list[PageRef]


class Workspace:
    """
    Holds the current editable PDF workspace.

    The workspace contains:
        - imported source documents
        - one flattened ordered list of PageRef objects

    This allows pages from different PDFs to be freely rearranged.
    """

    def __init__(self):
        self.documents: list[SourceDocument] = []
        self.pages: list[PageRef] = []

    def add_document(self, document: SourceDocument):
        self.documents.append(document)

        for index in range(document.page_count):
            self.pages.append(
                PageRef(
                    source_path=document.path,
                    source_index=index,
                )
            )

    def remove_document(self, document: SourceDocument):
        self.documents.remove(document)

        self.pages = [
            page
            for page in self.pages
            if page.source_path != document.path
        ]

    def add_blank_page(
        self,
        index: int | None = None,
        width: float = 595.0,
        height: float = 842.0,
    ):
        page = PageRef(
            blank=True,
            width=width,
            height=height,
        )

        if index is None:
            self.pages.append(page)
        else:
            index = max(0, min(index, len(self.pages)))
            self.pages.insert(index, page)

    def insert_pages(
        self,
        pages: Iterable[PageRef],
        index: int,
    ):
        pages = list(pages)

        index = max(
            0,
            min(index, len(self.pages))
        )

        self.pages[index:index] = pages

    def delete_pages(self, indexes: Iterable[int]):
        indexes = sorted(
            set(indexes),
            reverse=True,
        )

        for index in indexes:
            if 0 <= index < len(self.pages):
                del self.pages[index]

    def duplicate_pages(self, indexes: Iterable[int]):
        indexes = sorted(set(indexes))

        copies = [
            self.pages[index].clone()
            for index in indexes
            if 0 <= index < len(self.pages)
        ]

        if not copies:
            return

        insert_at = indexes[-1] + 1

        self.pages[insert_at:insert_at] = copies

    def rotate_pages(
        self,
        indexes: Iterable[int],
        degrees: int,
    ):
        for index in indexes:
            if 0 <= index < len(self.pages):
                self.pages[index].rotate(degrees)

    def move_pages(
        self,
        indexes: Iterable[int],
        target_index: int,
    ):
        """
        Move selected pages as a group.

        target_index represents the insertion point in the original
        page list.
        """

        indexes = sorted(
            set(
                index
                for index in indexes
                if 0 <= index < len(self.pages)
            )
        )

        if not indexes:
            return

        selected = [
            self.pages[index]
            for index in indexes
        ]

        selected_ids = {
            page.uid
            for page in selected
        }

        remaining = [
            page
            for page in self.pages
            if page.uid not in selected_ids
        ]

        removed_before_target = sum(
            1
            for index in indexes
            if index < target_index
        )

        adjusted_target = target_index - removed_before_target

        adjusted_target = max(
            0,
            min(adjusted_target, len(remaining)),
        )

        remaining[
            adjusted_target:adjusted_target
        ] = selected

        self.pages = remaining

    def snapshot(self) -> WorkspaceSnapshot:
        return WorkspaceSnapshot(
            pages=[
                PageRef(
                    source_path=page.source_path,
                    source_index=page.source_index,
                    rotation=page.rotation,
                    blank=page.blank,
                    width=page.width,
                    height=page.height,
                    uid=page.uid,
                )
                for page in self.pages
            ]
        )

    def restore(self, snapshot: WorkspaceSnapshot):
        self.pages = [
            PageRef(
                source_path=page.source_path,
                source_index=page.source_index,
                rotation=page.rotation,
                blank=page.blank,
                width=page.width,
                height=page.height,
                uid=page.uid,
            )
            for page in snapshot.pages
        ]