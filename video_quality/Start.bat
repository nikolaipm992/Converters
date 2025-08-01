@echo off
chcp 1251 >nul
title Медиа конвертер

:menu
cls
echo ===============================
echo    Медиа конвертер
echo ===============================
echo 1. Запустить видео конвертер (main.py)
echo 2. Провести видеоанализ (video_analysis.py)
echo ===============================
echo 0. Выход
echo ===============================
echo Используйте клавиши 1, 2 или 0 для выбора

choice /c 120 /n /m "Выберите действие: "

if errorlevel 3 goto exit
if errorlevel 2 goto run_analysis
if errorlevel 1 goto run_converter

:run_converter
cls
echo Запуск видео конвертера...
echo ===============================
call python main.py
echo.
echo Нажмите любую клавишу для возврата в меню...
pause >nul
goto menu

:run_analysis
cls
echo Проведение видеоанализа...
echo ===============================
call python video_analysis.py
echo.
echo Нажмите любую клавишу для возврата в меню...
pause >nul
goto menu

:exit
echo.
echo До свидания!
timeout /t 1 >nul
exit