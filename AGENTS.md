# Contributor guidance

- Keep image operations independent from Qt and operate on NumPy arrays.
- RGBA arrays use `uint8` and channel order RGBA; masks are grayscale `uint8`.
- Add focused, programmatically generated tests for editing behavior.
- Never write projects or exports directly to their final path: use an adjacent temporary file
  and atomic replacement.
- Run `ruff check .`, `ruff format --check .`, and `pytest` before committing.

