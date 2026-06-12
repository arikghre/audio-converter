# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['build_tool.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='build',
    debug=False,
    strip=False,
    upx=False,
    console=True,
    icon='logo.ico',
)
