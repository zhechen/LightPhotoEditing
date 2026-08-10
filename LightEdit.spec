# Checked-in PyInstaller recipe. Run from the repository root.
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files("lightedit")
a = Analysis(["lightedit_launcher.py"], pathex=["src"], datas=datas, hiddenimports=[],
             hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[])
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name="LightEdit", console=False,
          debug=False, bootloader_ignore_signals=False, strip=False, upx=True)
