from dataclasses import dataclass
from typing import Optional
import uuid


@dataclass
class PageRef:
    """
    Represents one page in the workspace.

    A page can either come from an imported PDF or be a blank page.
    """

    source_path: Optional[str] = None
    source_index: int = 0
    rotation: int = 0
    blank: bool = False

    width: float = 595.0
    height: float = 842.0

    uid: str = ""

    def __post_init__(self):
        if not self.uid:
            self.uid = str(uuid.uuid4())

        self.rotation %= 360

    @property
    def source_name(self) -> str:
        if self.blank:
            return "Blank Page"

        if not self.source_path:
            return "Unknown"

        from pathlib import Path

        return Path(self.source_path).name

    def rotate(self, degrees: int = 90):
        self.rotation = (self.rotation + degrees) % 360

    def clone(self) -> "PageRef":
        return PageRef(
            source_path=self.source_path,
            source_index=self.source_index,
            rotation=self.rotation,
            blank=self.blank,
            width=self.width,
            height=self.height,
        )