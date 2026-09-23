# Repository Guidelines

## Project Structure & Module Organization

`mkdocs_ai_summary/` contains the Python package: `plugin.py` implements the plugin, `chatgpt_api.py` and `tongyi_api.py` integrate providers, and `cache.py` handles shared caching. `docs/` and root `mkdocs.yml` define the documentation site. `readme.md` is the README; `assets/` holds its image. `test/` contains the automated configuration suite and demo Markdown; unrelated legacy contents there remain ignored. `build/`, `dist/`, and `site/` are generated artifacts.

## Build, Test, and Development Commands

- `python -m pip install -e '.[chatgpt]'` installs the package in editable mode with the OpenAI-compatible provider dependency. Use `.[tongyi]` when working on Tongyi support.
- `mkdocs serve` runs the configured documentation site locally with live reload. Provider API calls require the appropriate environment key if a page opts into summaries.
- `mkdocs build` builds the documentation site into `site/` and checks the MkDocs configuration.
- `python -m build` creates distributable archives in `dist/` (install `build` first if needed).

Run the configuration suite with `python -m pip install -e '.[test]'` followed by `python -m unittest discover -s test -p 'test_*.py'`. It builds the demo Markdown pages with provider requests intercepted, so no credentials or network calls are needed.

## Coding Style & Naming Conventions

Use four spaces, `snake_case` for modules/functions/variables, and `PascalCase` for classes. Keep provider request logic in its provider module and shared cache behavior in `cache.py`. Preserve Python 3.10 compatibility and declare dependencies in `pyproject.toml`.

## Testing Guidelines

Configuration tests and demo Markdown fixtures live in `test/`. The suite intercepts provider calls and checks the arguments passed by the plugin; keep it independent of live API credentials and billing.

## Commit & Pull Request Guidelines

Recent history uses short, imperative or descriptive subjects, such as `bug fix, dashscope import error` and `Update readme.md`; keep the subject concise and focused. Pull requests should explain the user-visible change, list relevant configuration or provider impact, link related issues when applicable, and include a documentation/build check for changes that affect the site. Never include API keys or generated build output in a change.

## Security & Configuration Tips

Read API credentials from environment variables (`OPENAI_API_KEY`, `DASHSCOPE_API_KEY`, or `DEEPSEEK_API_KEY`) and do not commit credentials. Cache JSON files are runtime data; the repository ignores generated cache files by default.
