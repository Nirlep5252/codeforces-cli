# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python CLI tool for competitive programming on Codeforces. Allows users to parse problems, run local test cases, and submit solutions with real-time verdict tracking from the terminal.

## Build & Development Commands

```bash
# Install dependencies and project (development)
uv sync

# Run CLI
uv run cf --help

# Build wheel
uv build

# Add a dependency
uv add <package>
```

There are no tests in this project.

## Architecture

**Entry Point**: `cf/__init__.py` - Click CLI group with custom `RichGroup` class for formatted help output. Commands registered via `commands.add_command()`.

**Command Modules** (each file = one Click command):
- `cf/config.py` - Store credentials in `~/.codeforces.uwu` (JSON)
- `cf/contests.py` - List contests or view problems in a specific contest
- `cf/parse.py` - Scrape problem statements and sample test cases, save as `.input.test`/`.output.test` files
- `cf/run.py` - Execute solutions locally against parsed test cases (Python, C, C++)
- `cf/submit.py` - Submit solutions and track verdicts via WebSocket (`wss://pubsub.codeforces.com/ws/`)
- `cf/unsolved.py` - List user's unsolved problems
- `cf/edit.py` - Open contest directories in VSCode/Vim/Neovim

**Core Utilities** (`utils.py`):
- `get_config()` - Load config from `~/.codeforces.uwu`
- `get_bp(lang)` - Load boilerplate templates from `~/cf_boilerplates/template.{lang}`
- `CFClient` - HTTP session handler with login and CSRF token management

**Key Dependencies**: Click (CLI), Rich (terminal UI), BeautifulSoup4 (HTML parsing), requests (HTTP), websocket-client (real-time updates)

## Code Patterns

- All web scraping uses BeautifulSoup on Codeforces HTML pages
- Commands verify they're running from a valid contest directory (subdirectory of configured `dir` with numeric name)
- Cross-platform path handling: `"/" if os.name == "posix" else "\\"`
- Language support in `submit.py:lang_ids` dict maps file extensions to Codeforces language IDs
