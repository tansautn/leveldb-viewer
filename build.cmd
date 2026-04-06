@echo off
setlocal enabledelayedexpansion

echo [0/10] Deactivate
call deactivate

echo [2/10] Xoa thu muc .pixi neu ton tai...
if exist "%~dp0.pixi" (
    rmdir /s /q "%~dp0.pixi"
)

timeout /t 2 /nobreak > nul
echo [2/10] Xoa thu muc .venv neu ton tai...
if exist "%~dp0.venv" (
    rmdir /s /q "%~dp0.venv"
)

timeout /t 2 /nobreak > nul
echo [2/10] Xoa thu muc dist neu ton tai...
if exist "%~dp0dist" (
    rmdir /s /q "%~dp0dist"
)
timeout /t 2 /nobreak > nul

echo [3/10] Tao virtualenv bang uv...
uv venv --python 3.12 --managed-python
timeout /t 2 /nobreak > nul

echo [4/10] Kich hoat virtualenv...
call .venv/Scripts/activate.bat
timeout /t 2 /nobreak > nul

echo [5/10] Cai dat dependencies...
uv pip install --refresh --strict --link-mode=copy zstandard pyside6 leveldb-py nuitka imageio
timeout /t 2 /nobreak > nul

echo [6/10] Build voi Nuitka...
python -m nuitka --onefile --output-dir=dist ^
--company-name="Zuko [@tansautn]"  ^
--product-name="LevelDB Viewer | Z U K O" ^
--file-version="2026.1.0.0" ^
--product-version="1.0.0" ^
--copyright="© 2026 (Z) Programing" ^
--trademarks="Z U K O ®" ^
--plugin-enable=pyside6 ^
--windows-console-mode=disable ^
--windows-icon-from-ico=assets/icon.png ./src/leveldb-viewer.py
timeout /t 2 /nobreak > nul

echo [8/10] Di chuyen vao dist ...
cd /d "%~dp0dist"
timeout /t 2 /nobreak > nul

echo [9/10] Chay file leveldb-viewer.exe...
Start leveldb-viewer.exe

echo [10/10] Ket thuc.
pause
