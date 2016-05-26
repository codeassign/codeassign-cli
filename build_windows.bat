@echo off
pyinstaller cae.py --distpath windows --onefile
rmdir /S /Q build
del cae.spec
pause