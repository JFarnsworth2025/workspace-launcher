# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("assets", "assets"),
        ("styles", "styles"),
        ("data/daily_verses.json", "data"),
        ("LICENSE", "."),
        ("README.md", "."),
        ("REBUILDING.md", "."),
        ("third-party-licenses", "third-party-licenses"),
        ("THIRD_PARTY_NOTICES.txt", "."),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["setuptools"],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

# Keep the Widgets app's plugins; omit unused PDF, QML and virtual-keyboard code.
qt_libraries = {"Qt6Core.dll", "Qt6Gui.dll", "Qt6Network.dll", "Qt6Widgets.dll", "Qt6OpenGL.dll", "Qt6Svg.dll"}
qt_plugins = {"qgif.dll", "qico.dll", "qjpeg.dll", "qsvg.dll", "qsvgicon.dll",
              "qwindows.dll", "qoffscreen.dll", "qminimal.dll", "qmodernwindowsstyle.dll",
              "qnetworklistmanager.dll", "qschannelbackend.dll", "qcertonlybackend.dll"}
release_binaries = []
for entry in a.binaries:
    name = entry[0].replace("\\", "/")
    filename = name.rsplit("/", 1)[-1]
    if name.startswith("PySide6/Qt6") and filename not in qt_libraries:
        continue
    if name.startswith("PySide6/plugins/") and filename not in qt_plugins:
        continue
    if filename == "opengl32sw.dll":
        continue
    release_binaries.append(entry)

exe = EXE(
    pyz,
    a.scripts,
    release_binaries,
    a.datas,
    [],
    name="Workspace Launcher",
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
    icon=["assets/icons/app.ico"],
    version="version_info.txt",
)
