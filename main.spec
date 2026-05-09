# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=['config.settings', 'core.utils', 'scripts.audio.audio_synthesis_2_audio_by_url_and_text', 'scripts.audio.audio_translate_with_menu_2_audio', 'scripts.audio.default_audio_2_audio', 'scripts.audio.local_audio_2_audio', 'scripts.image.image_to_answer', 'scripts.image.image_to_text', 'scripts.image.image_to_understand', 'scripts.multimodal.text_to_text_and_audio', 'scripts.multimodal.video_synthesis_by_video_and_image', 'scripts.text.parse_sse', 'scripts.text.text2picture_by_qwen', 'scripts.text.text2text_chat', 'scripts.text.text2video_by_async', 'scripts.text.text_and_audio_prompt_2_audio', 'scripts.text.text_to_speech_synthesis', 'scripts.text.text2picture_by_wan', 'scripts.video.video_to_understand_with_menu', 'scripts.video.video_to_understand_by_pictures_list'],
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
    a.binaries,
    a.datas,
    [],
    name='main',
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
