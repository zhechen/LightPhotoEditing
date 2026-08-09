import numpy as np
from PIL import Image

from lightedit.core.document import Document, Layer
from lightedit.core.export import JPEGOptions, export_jpeg
from lightedit.core.history import History, RegionCommand
from lightedit.core.project import load_project, save_project
from lightedit.imaging.composite import blend_rgb
from lightedit.imaging.healing import inpaint
from lightedit.imaging.liquify import apply, identity_field, push
from lightedit.shortcuts import SHORTCUTS


def rgba(color, shape=(8, 8)):
    result = np.empty((*shape, 4), np.uint8)
    result[:] = color
    return result


def test_composite_opacity_mask_and_modes():
    black = rgba((0, 0, 0, 255))
    white = rgba((255, 255, 255, 255))
    mask = np.full((8, 8), 128, np.uint8)
    doc = Document(8, 8, [Layer(black), Layer(white, opacity=0.5, mask=mask)])
    assert 60 <= doc.composite()[0, 0, 0] <= 65
    for mode in ("normal", "multiply", "screen", "overlay"):
        result = blend_rgb(black[..., :3], white[..., :3], mode)
        assert result.shape == (8, 8, 3)


def test_history_region_is_reversible():
    target = np.zeros((10, 10), np.uint8)
    before = target[2:4, 3:6].copy()
    target[2:4, 3:6] = 9
    command = RegionCommand.capture(target, (3, 2, 3, 2), before)
    history = History()
    history.push(command)
    assert history.undo() and not target.any()
    assert history.redo() and target[2, 3] == 9


def test_project_round_trip_and_jpeg(tmp_path):
    doc = Document(8, 8, [Layer(rgba((10, 20, 30, 128)), "A", mask=np.full((8, 8), 200, np.uint8))])
    project = tmp_path / "x.ledit"
    save_project(doc, project)
    loaded = load_project(project)
    assert np.array_equal(loaded.layers[0].pixels, doc.layers[0].pixels)
    output = tmp_path / "x.jpg"
    export_jpeg(loaded, output, JPEGOptions(quality=80, matte=(1, 2, 3)))
    assert Image.open(output).mode == "RGB"
    try:
        export_jpeg(loaded, output, JPEGOptions())
    except FileExistsError:
        pass
    else:
        raise AssertionError("overwrite must require confirmation")


def test_liquify_and_healing():
    image = rgba((0, 0, 0, 255))
    image[4, 4, :3] = 255
    field = identity_field(8, 8)
    assert np.array_equal(apply(image, field), image)
    push(field, (4, 4), (1, 0), 3)
    assert field[4, 4, 0] == 3
    mask = np.zeros((8, 8), np.uint8)
    mask[4, 4] = 255
    assert inpaint(image, mask).shape == image.shape


def test_shortcuts_unique_and_expected():
    values = [value[1] for value in SHORTCUTS.values()]
    assert len(values) == len(set(values))
    assert SHORTCUTS["blur_sharpen"][1] == "R"
