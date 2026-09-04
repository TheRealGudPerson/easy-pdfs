# EasyPDF.spec

import sys

from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files


hiddenimports = collect_submodules("pymupdf")

datas = collect_data_files("pymupdf")


if sys.platform == "win32":
    app_icon = "assets/easypdf.ico"
elif sys.platform == "darwin":
    app_icon = "assets/easypdf.icns"
else:
    app_icon = None


a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)


pyz = PYZ(
    a.pure
)


exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="EasyPDF",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon=app_icon,
)


if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="EasyPDF.app",
        icon=app_icon,
        bundle_identifier="com.easypdf.app",
    )