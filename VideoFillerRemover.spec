# -*- mode: python ; coding: utf-8 -*-

# Block cipher can be None for basic cases
block_cipher = None

a = Analysis(
    ['C:/Users/brevi/Desktop/VideoFillerRemover/VideoFillerRemover.py'],
    pathex=['C:/Users/brevi/Desktop/VideoFillerRemover'],
    binaries=[
        ('C:/ProgramData/chocolatey/bin/ffmpeg.exe', 'ffmpeg/'), # FFmpeg binary
    ],
    datas=[
        ('C:/Users/brevi/Desktop/VideoFillerRemover/azure.tcl', '.'),  # TCL file
        ('C:/Users/brevi/Desktop/VideoFillerRemover/BrevengineeringIcon.jpg', '.'),  # Icon file
        ('C:/Users/brevi/Desktop/VideoFillerRemover/theme', 'theme/'),  # Theme folder
        ('C:/Users/brevi/AppData/Local/Programs/Python/Python38/Lib/site-packages/moviepy', 'moviepy/'),  # MoviePy folder
        ('C:/Users/brevi/Desktop/VideoFillerRemover/ART-0001 logo.png', '.'),  # Add the splash image
        ('C:/Users/brevi/Desktop/VideoFillerRemover/VideoFillerremoverVenv/Lib/site-packages/whisper/assets', 'whisper/assets/'),  # Include whole whisper/assets folder
        ('C:/Users/brevi/Desktop/VideoFillerRemover/VideoFillerremoverVenv/Lib/site-packages/whisper/assets/mel_filters.npz','whisper/assets/'),
        ('C:/Users/brevi/Desktop/VideoFillerRemover/VideoFillerremoverVenv/Lib/site-packages/whisper/assets/multilingual.tiktoken','whisper/assets/'),
        ('C:/Users/brevi/Desktop/VideoFillerRemover/VideoFillerremoverVenv/Lib/site-packages/whisper/assets/gpt2.tiktoken','whisper/assets/'),
    ],
    hiddenimports=['moviepy.editor', 'moviepy', 'imageio_ffmpeg', 'Pillow'],
    hookspath=[],  # Specify any custom hooks if needed
    runtime_hooks=[],  # Any custom runtime hooks
    excludes=[],  # Exclude unwanted modules
    noarchive=False,  # Keep the archives for better performance (default is False)
    optimize=0,  # Optimization level (0 = no optimization)
)

# Create the PYZ archive (compressed Python modules)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Splash screen setup (ensure splash image path is correct)
splash = Splash(
    'C:/Users/brevi/Desktop/VideoFillerRemover/ART-0001 logo.png',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    text_size=12,
    minify_script=True,
    always_on_top=True,
)

# EXE configuration (turn on onefile mode here)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    splash=splash,
    exclude_binaries=True,  # This makes sure we are using the one-file build
    name='Video Filler Remover',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Console mode (set to False for a windowed app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,  # Set to 'x86_64' for 64-bit targets, if needed
    codesign_identity=None,  # Optional for macOS
    entitlements_file=None,  # Optional entitlements for macOS
    icon='C:\\Users\\brevi\\Downloads\\BrevengineeringIcon.ico',  # Icon for the app
    onefile=True,  # This flag explicitly tells PyInstaller to bundle everything into a single file
)

# Collect all files into the final build output
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    splash.binaries,
    strip=False,  # Don't strip files, as that can cause issues with debugging
    upx=True,  # Use UPX compression
    upx_exclude=[],  # Exclude specific files from UPX compression, if necessary
    name='Video Filler Remover',
)
