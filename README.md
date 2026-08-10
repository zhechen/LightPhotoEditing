# LightEdit

LightEdit is a compact, local-first desktop raster editor for Python 3.11+. It works with
full-resolution RGBA layers and lossless `.ledit` projects; JPEG is deliberately a separate,
flattened export.

## Install and launch

Run the install commands from the repository root: the directory containing this `README.md`,
`pyproject.toml`, and `src`. On Windows PowerShell:

```powershell
if (-not (Test-Path .\pyproject.toml)) { throw "Open PowerShell in the LightPhotoEditing repository root" }
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\lightedit.exe
```

For later launches, open PowerShell in the same folder and run only
`.\.venv\Scripts\lightedit.exe`. Alternatively, activate the environment with
`.\.venv\Scripts\Activate.ps1` and then use the shorter `lightedit` command. In Windows Command
Prompt, activation is `.venv\Scripts\activate.bat`.

## Build a standalone Windows EXE

Build the EXE on Windows; PyInstaller cannot create a Windows executable from macOS or Linux.
Starting from a PowerShell prompt in the repository root:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\pyinstaller.exe --clean --noconfirm LightEdit.spec
& .\dist\LightEdit.exe
```

The finished application is `dist\LightEdit.exe`. It can be copied to another Windows computer
and launched without installing Python. Build on the same CPU architecture as the destination
(normally 64-bit), and distribute the EXE from a trusted location. Because local builds are not
code-signed, Windows SmartScreen may ask the recipient to confirm that they trust it. Re-run the
PyInstaller command after source changes to rebuild the application.

## macOS and Linux

Run these commands from the repository root:

```bash
cd /path/to/LightPhotoEditing
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
lightedit
```

On a headless machine use `QT_QPA_PLATFORM=offscreen lightedit`. Open PNG/JPEG or `.ledit` from
**File > Open**, edit with the toolbar, manage visibility in Layers, save editable work with
**Save Project**, and create a shareable image with **Export JPEG**.

## Workflow and shortcuts

| Action | Windows shortcut |
|---|---|
| Open / Save project | Ctrl+O / Ctrl+S |
| Export JPEG | Ctrl+Alt+Shift+S |
| Undo / Redo | Ctrl+Z / Ctrl+Shift+Z |
| Brush / Clone / Healing | B / S / J |
| Liquify | Ctrl+Shift+X |
| Cycle Blur and Sharpen | R |
| Shortcut reference | Ctrl+/ |

Brush input is interpolated and one uninterrupted stroke is one undo operation. Blur, sharpen,
healing, clone stamping and liquify are destructive layer operations, so duplicate important
layers first. Masks are grayscale: white reveals and black hides.

## Projects, recovery, and export

`.ledit` is a ZIP with a versioned `manifest.json` and lossless PNGs for every layer and mask.
Saving atomically replaces the destination. Recovery autosaves use the same validated format.
JPEG export composites visible layers at full resolution, supports resizing, quality, matte and
sRGB tagging, estimates output by encoding it, confirms overwrites, and never marks a project
saved. Metadata is removed by default for privacy.

## Development checks

```bash
ruff format --check .
ruff check .
pytest
```

Tests generate their own images and include headless Qt workflows; no personal photos or network
services are used.

## Privacy, performance, and limitations

All editing is local and LightEdit has no telemetry. Full-resolution layers consume roughly four
bytes per pixel each, plus masks and bounded changed-region history. Large filters and liquify can
be CPU-intensive. Version 0.1 has raster layers only: there are no adjustment/vector/text layers,
color-managed monitor proofing, RAW development, plugins, or cross-platform package signing.

## Troubleshooting

If Qt cannot find a display, set `QT_QPA_PLATFORM=offscreen` for tests (not interactive use).
If pip reports that a directory "does not appear to be a Python project", it is installing from
the wrong or an incomplete directory. In the same terminal, run `Get-Location` and
`Test-Path .\pyproject.toml` in PowerShell (or `cd` and `dir pyproject.toml` in Command Prompt).
The file check must succeed before running `python -m pip install -e ".[dev]"`. Change to the
repository root first; if the file is still absent, download or clone the complete repository
rather than an individual source file. Do not copy `pyproject.toml` into an unrelated working
directory, because the build also needs `README.md` and `src`.

Reinstall the editable package after moving the checkout. If `py` selects an older interpreter,
check installed versions with `py -0p` and recreate the environment explicitly with
`py -3.11 -m venv .venv`. If PowerShell blocks `Activate.ps1`, either use Command Prompt or run
`.\.venv\Scripts\python -m pip install -e ".[dev]"` and `.\.venv\Scripts\lightedit.exe` without
activation. If OpenCV/Qt wheels conflict, recreate the virtual environment. A rejected project
likely uses a newer manifest version; upgrade rather than editing the archive. Preserve a recovery
file before investigating a crash.

## Contributing

Read `AGENTS.md`, keep Qt out of imaging modules, include generated tests, format with Ruff, and
run the full suite. Contributions should be focused and explain user-visible behavior, persistence
compatibility, and performance implications.
