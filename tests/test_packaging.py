import ast
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_pyinstaller_entry_point_imports_app_as_package():
    launcher = REPOSITORY_ROOT / "lightedit_launcher.py"
    tree = ast.parse(launcher.read_text(encoding="utf-8"))

    imports = [node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    assert any(
        node.level == 0
        and node.module == "lightedit.app"
        and any(alias.name == "main" for alias in node.names)
        for node in imports
    )


def test_pyinstaller_spec_builds_package_aware_launcher():
    spec = (REPOSITORY_ROOT / "LightEdit.spec").read_text(encoding="utf-8")

    assert 'Analysis(["lightedit_launcher.py"]' in spec
    assert 'Analysis(["src/lightedit/app.py"]' not in spec
