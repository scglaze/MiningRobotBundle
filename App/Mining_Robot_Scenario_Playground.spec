# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=[('Mining_Domain_Scenario1_Graphic.png', '.'), ('Mining_Domain_Scenario2_Graphic.png', '.'), ('Mining_Domain_Scenario3_Graphic.png', '.'), ('Mining_Domain_Scenario4_Graphic.png', '.'), ('Mining_Domain_Scenario5_Graphic.png', '.'), ('Mining_Domain_Scenario6_Graphic.png', '.'), ('Mining_Domain_Scenario7_Graphic.png', '.'), ('Mining_Domain_Scenario8_Graphic.png', '.'), ('Mining_Domain_Scenario9_Graphic.png', '.'), ('Mining_Domain_Scenario10_Graphic.png', '.'), ('Mining_Robot_Planning_Domain.txt', '.'), ('Mining_Robot_Policies.txt', '.'), ('Mining_Robot_Scenario1.txt', '.'), ('Mining_Robot_Scenario2.txt', '.'), ('Mining_Robot_Scenario3.txt', '.'), ('Mining_Robot_Scenario4.txt', '.'), ('Mining_Robot_Scenario5.txt', '.'), ('Mining_Robot_Scenario6.txt', '.'), ('Mining_Robot_Scenario7.txt', '.'), ('Mining_Robot_Scenario8.txt', '.'), ('Mining_Robot_Scenario9.txt', '.'), ('Mining_Robot_Scenario10.txt', '.'), ('Normal_BMode.txt', '.'), ('Safe_BMode.txt', '.'), ('Risky_BMode.txt', '.')],
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
    name='Mining_Robot_Scenario_Playground',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
