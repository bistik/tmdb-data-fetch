# AGENTS.md

## Toolchain
- Python 3.14, managed with `uv` (see `pyproject.toml`, `.python-version`, `uv.lock`).
- Install/sync: `uv sync`. Run the CLI: `uv run tmdbdf` (or `uv run python -m tmdbdf`).
- Entry point: `tmdbdf.app:main` (declared in `pyproject.toml` `[project.scripts]`).

## Architecture
- Package `tmdbdf/`:
  - `app.py` — `main()` entry: loads env, builds `Config`, calls `db.create_tables()`, then fetches movies (currently commented out).
  - `config.py` — `Config` frozen dataclass with `from_env()` classmethod; reads `SQLITE_DATABASE` (default `tmdbdf.db`) and `TMDB_AUTH_TOKEN` (default `""`).
  - `db.py` — sqlite schema + connection helpers: `get_connection()`, `create_tables()`, `has_request()`.
  - `api.py` — TMDB client (e.g. `fetch_top_movies()`).
  - `__init__.py` — empty.
- `load_dotenv()` runs in `app.main()`, **not** at package import.

## Environment
- `SQLITE_DATABASE` (path to sqlite file) — defaults to `tmdbdf.db` if unset.
- `TMDB_AUTH_TOKEN` — TMDB bearer token; if missing, `main()` prints a hint and exits 1.
- Loaded from `.env` via `python-dotenv` inside `app.main()`.
- `.env` is gitignored; `.env.example` is the tracked placeholder — keep new env vars documented there.

## Gotchas
- `sqlite3` API specifics (see `db.py`):
  - `cursor.execute()` runs **one statement only** — use `conn.executescript()` for multi-statement DDL (this is what `create_tables()` does).
  - `sqlite3.Connection`'s `__exit__` commits/rolls back but does **not** close the connection — wrap in `contextlib.closing(...)` to guarantee `close()` (pattern used across `db.py`).
  - `sqlite3.Cursor` has **no** context-manager protocol — do not write `with conn.cursor() as cursor:`. Prefer `conn.execute(...)` directly, which returns a cursor.

## Status
- No tests, lint, typecheck, or CI configured yet. Verify changes by running `uv run tmdbdf` and inspecting the sqlite DB.
