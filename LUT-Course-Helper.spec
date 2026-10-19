# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ["webui/launcher.py"],
    pathex=[],
    binaries=[],
    datas=[("webui/index.html", ".")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "PySide6",
        "qfluentwidgets",
        "scipy",
        "numpy",
        "pytest",
        "PIL",
        "webview",
        "clr",
        "pythonnet",
        "bottle",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="LUT-Course-Helper",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    icon="favicon.ico",
)
