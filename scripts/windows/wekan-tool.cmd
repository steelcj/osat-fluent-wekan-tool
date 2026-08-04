@echo off
REM Generated from scripts/windows/wekan-tool.cmd by install-wekan.py -- do not edit by hand.
REM Re-running the installer regenerates this file.
set "WRITABLE_PATH=__WEKAN_DATA_DIR__"
if not defined WEKAN_ROOT_URL set "WEKAN_ROOT_URL=http://localhost:2000"
if not defined WEKAN_PORT set "WEKAN_PORT=2000"
set "ROOT_URL=%WEKAN_ROOT_URL%"
set "PORT=%WEKAN_PORT%"
cd /d "__WEKAN_BUNDLE_DIR__"
call start-wekan.bat %*
