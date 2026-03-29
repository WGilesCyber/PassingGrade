# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for PassingGrade (Windows)
# Run: pyinstaller PassingGrade.spec

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/common_passwords.txt', 'assets'),
        ('policy/policy.json',          'policy'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
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
    name='PassingGrade',
    debug=False,
    bootloader_ignore_signals=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,   # no console window
    disable_windowed_traceback=False,
    target_arch=None,
    icon='assets/icon.ico',
)
