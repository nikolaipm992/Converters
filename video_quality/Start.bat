@echo off
chcp 1251 >nul
title Выбор действия

:menu
cls
echo ===============================
echo    Выберите действие:
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
python main.py
echo.
echo Нажмите любую клавишу для возврата в меню...
pause >nul
goto menu

:run_analysis
cls
echo Проведение видеоанализа...
python video_analysis.py
echo.
echo Нажмите любую клавишу для возврата в меню или 0 для выхода...
echo.
set /p exit_choice=Нажмите Enter для возврата или введите 0 для выхода: 
if "%exit_choice%"=="0" goto exit
goto menu

:exit
exit