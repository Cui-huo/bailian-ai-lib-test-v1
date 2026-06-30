# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 配置 - Gradio Web 前端版
# 构建命令: pyinstaller app.spec

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

# 收集 assets 目录下的所有测试资源文件
assets_dir = Path('assets')
assets_datas = []
if assets_dir.exists():
    for f in assets_dir.iterdir():
        if f.is_file():
            assets_datas.append((str(f), 'assets'))

# 收集 Gradio 及其依赖的静态资源（模板/CSS/JS/version.txt），否则打包后闪崩
assets_datas += collect_data_files('gradio')
assets_datas += collect_data_files('gradio_client')
assets_datas += collect_data_files('safehttpx')
assets_datas += collect_data_files('groovy')

a = Analysis(
    ['app.py'],
    pathex=['.'],
    binaries=[],
    datas=assets_datas,
    hiddenimports=[
        'config.settings',
        'core.utils',
        'dashscope',
        'dashscope.audio.tts_v2',
        'dashscope.aigc.image_generation',
        'dashscope.aigc.video_synthesis',
        'dashscope.api_entities.dashscope_response',
        'gradio.themes',
        'gradio.themes.soft',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols.http.auto',
        'uvicorn.lifespan',
        'fastapi',
        'starlette',
        'soundfile',
        'numpy',
        'dotenv',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    module_collection_mode={'gradio': 'py'},
    excludes=[
        'matplotlib',
        'matplotlib.backends',
        'matplotlib.pyplot',
        'openpyxl',
        'xlrd',
        'IPython',
        'ipykernel',
        'jupyter_client',
        'nbconvert',
        'nbformat',
        'notebook',
        'pandas.tests',
        'numpy.tests',
        'scipy',
        'PIL.ImageQt',
        'PIL.ImageTk',
        'tkinter',
        'PyQt5',
        'PySide2',
        'PySide6',
        'PyQt6',
        'wx',
        'curses',
        'sqlalchemy',
        'alembic',
        'pytest',
        'setuptools',
        'pip',
        'wheel',
        'pkg_resources',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AI工具箱',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Windows GUI 子系统 (console=False) 与 uvicorn 不兼容
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
