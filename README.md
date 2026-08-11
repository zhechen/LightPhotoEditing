# LightEdit

LightEdit is a compact, local-first desktop raster editor for Python 3.11+. It works with
full-resolution RGBA layers and lossless `.ledit` projects; JPEG is deliberately a separate,
flattened export.

## Windows quick start

Open PowerShell in the downloaded/cloned LightPhotoEditing folder, then run:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\lightedit.exe
```

For later launches, open the same folder and run `.\.venv\Scripts\lightedit.exe`.

## Build a standalone Windows EXE

Build on Windows from PowerShell in the repository folder:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\pyinstaller.exe --clean --noconfirm LightEdit.spec
& .\dist\LightEdit.exe
```

The standalone application is `dist\LightEdit.exe`; the destination computer does not need
Python. Windows may show a SmartScreen prompt because a local build is not code-signed.

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
| Normal cursor / Zoom / Hand | V / Z / H |
| Zoom in / Zoom out | Ctrl++ / Ctrl+- |
| Fit canvas / Actual size | Ctrl+0 / Ctrl+1 |
| Return to normal cursor | Esc |
| Shortcut reference | Ctrl+/ |

Brush input is interpolated and one uninterrupted stroke is one undo operation. Blur, sharpen,
healing, clone stamping and liquify are destructive layer operations, so duplicate important
layers first. Masks are grayscale: white reveals and black hides.

The canvas starts at 1280 × 1280. Select several images in **File > Open**, or drag local PNG,
JPEG, WebP, or BMP files anywhere onto the window, to create one layer per image. Dropping a
`.ledit` file opens that project. Drag a layer to move it and drag its lower-right
handle to resize it. **Edit > Align to Grid** shows the grid and snaps transforms. Use **Set Canvas
Size** for a different canvas, and the Layers panel buttons to invert a mask or temporarily set it
to 50% while comparing layers.

Large canvases automatically fit inside the preview without changing their pixel dimensions.
Choose **View > Fit Canvas in Window** (`Ctrl+0`) to fit again, **Actual Size** (`Ctrl+1`) for 100%,
or use the visible Zoom In/Out menu commands. Press `Z` for the magnifying-glass cursor, then drag
right to zoom in or left to zoom out. Press `H` for the hand cursor, then hold the left mouse
button and drag to pan the preview. Press `V` or `Esc` to return to the normal cursor. The status
bar confirms every mode change and reports the current zoom percentage; zoom and pan affect only
the preview, never the document canvas or exported dimensions.

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

Run commands from the folder containing `pyproject.toml`. If installation fails after an update,
delete `.venv` and repeat the quick-start steps. On Linux test servers without a display, use
`QT_QPA_PLATFORM=offscreen pytest`.

## Contributing

Read `AGENTS.md`, keep Qt out of imaging modules, include generated tests, format with Ruff, and
run the full suite. Contributions should be focused and explain user-visible behavior, persistence
compatibility, and performance implications.
