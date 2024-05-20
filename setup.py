from cx_Freeze import setup, Executable
#python setup.py build

executables = [Executable("App.py", base="Win32GUI", icon="AI判断ツール.ico")]

options = {
    "build_exe": {
        "packages": ["pygame","tkinter","sqlite3","datetime","json","calendar","random"],
        "include_files": ["play.png", "pause.png", "doraemon.mp3", "always.mp3", "yourname.mp3", "AI判断ツール.ico"],
        "excludes": ["multiprocessing"],
    },
}

setup(
    name="AI判断ツール",
    version="1.0",
    description="AI判断ツール",
    options=options,
    executables=executables
)
