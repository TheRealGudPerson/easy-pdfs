# EasyPDF

A modern cross-platform PDF page manager built with Python, PySide6, and PyMuPDF.

## App Installer (macOS and Windows)
The latest release can be found [here](https://github.com/TheRealGudPerson/easy-pdfs/releases/latest).

## Features

- Import multiple PDFs
- Combine any number of PDFs
- Visual page thumbnails
- Drag and drop page reordering
- Move pages between PDFs
- Multi-page selection
- Shift-click range selection
- Ctrl/Cmd-click multi-selection
- Rotate pages
- Delete pages
- Duplicate pages
- Add blank pages
- Undo/redo
- Page preview
- Drag PDFs directly into the app
- Light/dark mode
- Windows/macOS compatible

## Requirements

Current requirement is Python 3.14.

## Script Run (requires Python to be installed)

Run ```python installer.py```

## Manual Run (requires Python to be installed)

1. Create a virtual environment: ```python -m venv .venv```
2. Start the virtual environment:```.venv\Scripts\activate``` for Windows or ```source .venv/bin/activate``` for macOS
3. Install dependencies: ```pip install -r requirements.txt```
4. Run: ```python app.py```