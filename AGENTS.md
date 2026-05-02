# AGENTS.md — Quick Context for Working on This Repo

## What This Is

- PyQt6 desktop app (Windows-first) for editing New World game config files (`rebindings_*.xml`, `usersettings.javsave`).
- Config files live in `%APPDATA%/AGS/New World/` (or Proton equivalent).
- Single external dependency: `PyQt6` (see `requirements.txt`).

## Entrypoints & Architecture

- **Run**: `python main.py` → `run_app()` → `MainWindow` + `ConfigParser`
- **Core modules**: `newworld_config_manager/config_parser.py`, `newworld_config_manager/main_window.py`
- **ConfigParser**: Finds configs, loads/saves XML, does full-folder backups
- **MainWindow**: Two tree views (rebindings vs user settings), color editor widget for RGBA values
- **Build**: PyInstaller via `build.bat` → `NewWorld Config Manager.spec`; outputs to `dist/`

## Key Behaviors That Trip Up Generic Agents

- **`resource_path()` in `main.py`**: Required for PyInstaller bundles. Uses `sys._MEIPASS` when bundled, falls back to `os.path.abspath(".")` in dev. Any file access (stylesheets, icons) must use this helper.
- **Config detection**: `ConfigParser._get_new_world_config_dir()` uses `APPDATA` on Windows. Fails cleanly if run outside Windows or without New World installed.
- **`usersettings.javsave` parsing**: Treated as XML but may not always be valid. `load_user_settings_config()` returns `(path, root|None)` — `None` means parse failure.
- **Rebindings file selection**: `_find_latest_rebindings_file()` picks newest `rebindings_b*.xml` by mtime, falls back to `rebindings.xml`.
- **Color editor widget**: Used for specific reticle colors + any field containing "color" with valid 4-float value. Slider values 0–255, stored as 0.0–1.0 floats.

## How to Test / Verify Changes

- **Run**: `python main.py` (requires PyQt6: `pip install -r requirements.txt`)
- **Build exe**: `build.bat` (Windows only; requires PyInstaller)
- **No unit tests** — verification is manual via GUI.

## File Layout Gotchas

- `newworld_config_manager/ui/assets/` contains icons and `appicon.png`
- `assets/stylesheet.qss` loaded via `resource_path("assets/stylesheet.qss")`
- `VERSION` read by `build.bat` for archive naming

## Framework / Toolchain Quirks

- **PyQt6**: `QTreeWidget` with `itemChanged` signals. `blockSignals(True)` used during tree population.
- **XML**: `xml.etree.ElementTree`; `ET.indent()` for pretty-print.
- **Windows paths**: `pathlib.Path` + `os.getenv("APPDATA")`. Proton paths noted but not implemented.
- **No lint/typecheck config enforced** (no ruff/mypy in CI, no `pyproject.toml`).

## Common Agent Mistakes to Avoid

- Don't bypass `resource_path()` for assets — breaks in bundled builds.
- Don't assume `usersettings.javsave` is always valid XML.
- Avoid touching `build/` or `dist/` (generated artifacts).
- Color values are space-separated floats (0.0–1.0), not hex.
- Rebindings edits update `input` attribute; defaults in `defaultInput` (read-only).
