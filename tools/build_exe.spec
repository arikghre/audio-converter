# -*- mode: python ; coding: utf-8 -*-
import os

ROOT = os.path.dirname(SPECPATH)  # parent of tools/ = repo root

a = Analysis(
    [os.path.join(ROOT, 'tools', 'build_tool.py')],
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
    name='AgsMediaConverter',
    debug=False,
    strip=False,
    upx=False,
    console=True,
    icon=os.path.join(ROOT, 'src', 'logo.ico'),
)
