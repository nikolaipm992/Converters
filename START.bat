@echo off
chcp 1251 >nul
title Медиа конвертер и утилиты

:: Определяем путь к папке, где находится этот bat-файл
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"  :: Убираем последний слэш

:: Путь к виртуальной среде (в той же папке, что и bat-файл)
set "VENV_PATH=%SCRIPT_DIR%\venv"

:: Путь к ffmpeg
set "FFMPEG_PATH=D:\codecs\ffmpeg"
set "FFMPEG_EXE=%FFMPEG_PATH%\ffmpeg.exe"

:: Добавляем путь к ffmpeg в переменную PATH
set "PATH=%FFMPEG_PATH%;%PATH%"

:: Проверяем, существует ли путь к ffmpeg
if not exist "%FFMPEG_PATH%" (
    echo Путь к ffmpeg не существует: %FFMPEG_PATH%
    echo Проверьте правильность пути к ffmpeg
    pause
    exit /b 1
)

:: Проверяем, доступен ли исполняемый файл ffmpeg
if not exist "%FFMPEG_EXE%" (
    echo Исполняемый файл ffmpeg.exe не найден по пути: %FFMPEG_EXE%
    echo Убедитесь, что ffmpeg установлен правильно и файл ffmpeg.exe находится в папке bin
    pause
    exit /b 1
)

:: Активируем виртуальную среду
if exist "%VENV_PATH%\Scripts\activate.bat" (
    call "%VENV_PATH%\Scripts\activate.bat"
    echo Виртуальная среда активирована: %VENV_PATH%
    echo Путь к ffmpeg добавлен: %FFMPEG_PATH%
) else (
    echo Виртуальная среда не найдена в папке: %VENV_PATH%
    echo Создайте её командой: python -m venv venv
    pause
    exit /b 1
)

:: Проверяем, работает ли ffmpeg
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ffmpeg не работает корректно
    echo Попробуйте добавить путь к ffmpeg в системную переменную PATH вручную
    pause
    exit /b 1
) else (
    echo ffmpeg найден и работает корректно
)

:menu
cls
echo ===============================
echo    Медиа конвертер и утилиты
echo ===============================
echo 1. Провести видеоанализ (app\video_analysis.py)
echo 2. Оценить качество видео (app\video_quality.py)
echo 3. Конвертировать PDF в JPG (app\pdf_in_jpg.py)
echo 4. Конвертировать JPG в PDF (app\jpg_in_pdf.py)
echo 5. Конвертировать PDF в Word (app\pdf_in_word.py)
echo 6. Конвертировать Word в PDF (app\word_in_pdf.py)
echo 7. Конвертировать XLSX в CSV (app\xlsx_in_csv.py)
echo 8. Извлечь email из Excel (app\extract_mail_of_exel.py)
echo ===============================
echo 0. Выход
echo ===============================
echo Используйте клавиши 0-8 для выбора

choice /c 123456780 /n /m "Выберите действие: "

if errorlevel 9 goto exit
if errorlevel 8 goto run_extract_mail
if errorlevel 7 goto run_xlsx_csv
if errorlevel 6 goto run_word_pdf
if errorlevel 5 goto run_pdf_word
if errorlevel 4 goto run_jpg_pdf
if errorlevel 3 goto run_pdf_jpg
if errorlevel 2 goto run_video_quality
if errorlevel 1 goto run_analysis

:run_analysis
cls
echo Проведение видеоанализа...
echo ===============================
if exist "app\video_analysis.py" (
    cd app
    python video_analysis.py
    cd ..
) else (
    echo Файл app\video_analysis.py не найден!
    timeout /t 2 /nobreak >nul
)
goto menu

:run_video_quality
cls
echo Оценка качества видео...
echo ===============================
if exist "app\video_quality.py" (
    cd app
    python video_quality.py
    cd ..
) else (
    echo Файл app\video_quality.py не найден!
    timeout /t 2 /nobreak >nul
)
goto menu

:run_pdf_jpg
cls
echo Конвертация PDF в JPG...
echo ===============================
if exist "app\pdf_in_jpg.py" (
    cd app
    python pdf_in_jpg.py
    cd ..
) else (
    echo Файл app\pdf_in_jpg.py не найден!
    timeout /t 2 /nobreak >nul
)
goto menu

:run_jpg_pdf
cls
echo Конвертация JPG в PDF...
echo ===============================
if exist "app\jpg_in_pdf.py" (
    cd app
    python jpg_in_pdf.py
    cd ..
) else (
    echo Файл app\jpg_in_pdf.py не найден!
    timeout /t 2 /nobreak >nul
)
goto menu

:run_pdf_word
cls
echo Конвертация PDF в Word...
echo ===============================
if exist "app\pdf_in_word.py" (
    cd app
    python pdf_in_word.py
    cd ..
) else (
    echo Файл app\pdf_in_word.py не найден!
    timeout /t 2 /nobreak >nul
)
goto menu

:run_word_pdf
cls
echo Конвертация Word в PDF...
echo ===============================
if exist "app\word_in_pdf.py" (
    cd app
    python word_in_pdf.py
    cd ..
) else (
    echo Файл app\word_in_pdf.py не найден!
    timeout /t 2 /nobreak >nul
)
goto menu

:run_xlsx_csv
cls
echo Конвертация XLSX в CSV...
echo ===============================
if exist "app\xlsx_in_csv.py" (
    cd app
    python xlsx_in_csv.py
    cd ..
) else (
    echo Файл app\xlsx_in_csv.py не найден!
    timeout /t 2 /nobreak >nul
)
goto menu

:run_extract_mail
cls
echo Извлечение email из Excel...
echo ===============================
if exist "app\extract_mail_of_exel.py" (
    cd app
    python extract_mail_of_exel.py
    cd ..
) else (
    echo Файл app\extract_mail_of_exel.py не найден!
    timeout /t 2 /nobreak >nul
)
goto menu

:exit
cls
echo ===============================
echo    До свидания!
echo ===============================
:: Деактивируем виртуальную среду
call "%VENV_PATH%\Scripts\deactivate.bat" >nul 2>&1
timeout /t 1 >nul
exit