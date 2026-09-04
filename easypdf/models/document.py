from dataclasses import dataclass
from pathlib import Path

import pymupdf


@dataclass
class SourceDocument:
    path: str
    name: str
    page_count: int

    @classmethod
    def from_path(cls, path: str) -> "SourceDocument":
        document = pymupdf.open(path)

        try:
            page_count = len(document)
        finally:
            document.close()

        return cls(
            path=str(Path(path).resolve()),
            name=Path(path).name,
            page_count=page_count,
        )