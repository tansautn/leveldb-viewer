# LevelDB Viewer

A visual tool to view and browse data in **LevelDB** databases.

## What is LevelDB and where is it usually found?

[LevelDB](https://github.com/google/leveldb) is an ultra-fast Key-Value storage library developed by Google that stores data as bytes. It is a simple and efficient open-source database library that provides fast read/write operations with built-in compression support.

You will frequently encounter LevelDB hidden within your computer's local data folders:
- **Browsers:** Google Chrome, Microsoft Edge, Brave, etc. (Local Storage or IndexedDB folders).
- **Electron Desktop Applications:** Slack, Discord, etc.
- **Blockchain:** Used as an internal database in nodes (e.g., Ethereum's Geth).
- **Games:** Minecraft (Bedrock Edition) uses technology similar to LevelDB to store world chunk data.

## Origin Story

*Searched everywhere for a viewer. Well, "If it doesn't exist, build it!"*

Because I couldn't find a truly good, simple yet powerful Viewer tool to view HEX code, text, and decode Key-Value pairs from LevelDB on Windows, I built this application myself.

## Install/Download

1. **Go to Release and download the latest automatically built version from the [Latest Release Page](//github.com/tansautn/leveldb-viewer/releases/latest)**
2. **Choose the version suitable for your operating system and download it (Supports: Windows, macOS, Linux)**
3. **Extract the package (if needed); Find the executable file and start viewing**

## Changelog

- Probably only one version exists. Changelog doesn't matter much

## Technologies Used
- Python 3.12+
- PySide6 (GUI framework)
- leveldb-py (Database interface)

## Build Instructions

This project uses [uv](https://github.com/astral-sh/uv) for ultra-fast package management and [Nuitka](https://nuitka.net/) to compile to executable.

### 1. On Windows (Using provided script)

Run the script file to get the build:
```cmd
build.cmd
```
This script will automatically: clear cache, set up `.venv` with Python 3.12, install dependencies, and compile to `.exe` in the `dist/` folder.

### 2. On other operating systems or manual run

```bash
# 1. Create venv using uv
uv venv --python 3.12 --managed-python

# 2. Activate venv
# Windows:
.venv\Scripts\activate.bat
# Linux/macOS:
source .venv/bin/activate

# 3. Install libraries
uv pip install zstandard pyside6 leveldb-py nuitka imageio

# 4. Run directly (Dev)
python src/leveldb-viewer.py

# 5. Build executable using Nuitka (Refer to build.cmd or .github/workflows/release.yml)
```