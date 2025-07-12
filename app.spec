# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Personal Documentation Assistant
This file defines how to package the application into a standalone executable.
"""

import os
import sys

# Get the directory containing this spec file
spec_dir = os.path.dirname(os.path.abspath(SPECPATH))

# Define paths
models_dir = os.path.join(spec_dir, 'models')
images_dir = os.path.join(spec_dir, 'images')
reports_dir = os.path.join(spec_dir, 'reports')

# Collect data files
datas = []

# Add model files if they exist
if os.path.exists(models_dir):
    for file in os.listdir(models_dir):
        if file.endswith('.gguf'):
            datas.append((os.path.join(models_dir, file), 'models'))

# Add sample images if they exist
if os.path.exists(images_dir):
    for file in os.listdir(images_dir):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            datas.append((os.path.join(images_dir, file), 'images'))

# Add any additional data files
additional_files = [
    ('README.md', '.'),
    ('requirements.txt', '.'),
]

for src, dst in additional_files:
    src_path = os.path.join(spec_dir, src)
    if os.path.exists(src_path):
        datas.append((src_path, dst))

# Hidden imports for dependencies that might not be auto-detected
hiddenimports = [
    'PIL._tkinter_finder',
    'PIL.Image',
    'PIL.ImageTk',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
    'gpt4all',
    'markdown2',
    'reportlab.platypus',
    'reportlab.lib.pagesizes',
    'reportlab.lib.styles',
    'reportlab.lib.units',
    'reportlab.lib.colors',
]

# Analysis configuration
a = Analysis(
    ['main.py'],
    pathex=[spec_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # Exclude heavy dependencies we don't need
        'numpy',       # Unless specifically required
        'scipy',
        'pandas',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate entries
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Executable configuration
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PersonalDocumentationAssistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True for debugging, False for release
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add path to .ico file here if you have one
)


# Collect all files into a directory
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PersonalDocumentationAssistant'
)

# Optional: Create a one-file executable (uncomment if preferred)
# Note: One-file mode is slower to start but creates a single .exe

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PersonalDocumentationAssistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
