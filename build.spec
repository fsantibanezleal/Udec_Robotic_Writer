# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Udec_Robotic_Writer.

Build with:
    pyinstaller build.spec --clean --noconfirm

Or use the PowerShell script:
    .\\Build_PyInstaller.ps1
"""
import pkgutil
from pathlib import Path

APP_NAME = "Udec_Robotic_Writer"
ENTRY_POINT = "run_app.py"

# Hidden imports: uvicorn internals + dash submodules
hidden_imports = [
    # Uvicorn internals
    "uvicorn.lifespan.on",
    "uvicorn.lifespan.off",
    "uvicorn.lifespan",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.protocols.http.httptools_impl",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.protocols.websockets.wsproto_impl",
    "uvicorn.protocols.websockets.websockets_impl",
    "uvicorn.loops.auto",
    "uvicorn.loops.asyncio",
]

# Dynamically discover all dash submodules
try:
    import dash
    for importer, modname, ispkg in pkgutil.walk_packages(
        dash.__path__, prefix="dash."
    ):
        hidden_imports.append(modname)
except ImportError:
    pass

hidden_imports.extend([
    "dash_bootstrap_components",
    "plotly",
    "plotly.graph_objects",
    "plotly.express",
])

# Data files: Dash frontend assets
datas = []
assets_dir = Path("src/frontend/assets")
if assets_dir.exists():
    datas.append((str(assets_dir), "src/frontend/assets"))

a = Analysis(
    [ENTRY_POINT],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "IPython", "jupyter"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)
