# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['converter.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pillow_heif', 'PIL', 'pydub'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AGsMediaConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon='logo.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='AGsMediaConverter',
)
