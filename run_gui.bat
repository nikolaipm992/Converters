@echo off
cd "%~dp0"
call venv\Scripts\activate
python run.py %1