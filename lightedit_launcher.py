"""PyInstaller entry point that preserves ``lightedit`` as a package."""

from lightedit.app import main


if __name__ == "__main__":
    raise SystemExit(main())
