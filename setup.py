from setuptools import setup

APP = ['Song Downloader.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'app_icon.icns',  # Path to your .icns file
    'packages': ['yt_dlp'],
    'includes': ['tkinter'],
    'excludes': ['PyInstaller', 'setuptools'],  # Explicitly exclude PyInstaller
    'plist': {
        'CFBundleName': 'YouTube to WAV Downloader',
        'CFBundleDisplayName': 'YouTube to WAV Downloader',
        'CFBundleGetInfoString': "Download YouTube videos as WAV files",
        'CFBundleIdentifier': "com.galfried.songdownloader",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'NSHumanReadableCopyright': "Copyright ©Gal Fried 2025",
    }
}

setup(
    app=APP,
    name='YouTube to WAV Downloader',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)