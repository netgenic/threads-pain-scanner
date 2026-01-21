@echo off
chcp 65001 >nul
title Установка Threads Pain Scanner

echo.
echo ╔══════════════════════════════════════════╗
echo ║  📦 Установка Threads Pain Scanner       ║
echo ╚══════════════════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo.
    echo Установите Python командой:
    echo   winget install Python.Python.3.12
    echo.
    echo После установки перезапустите этот скрипт.
    pause
    exit /b 1
)

echo ✓ Python найден
python --version

:: Install Python dependencies
echo.
echo 📦 Установка Python зависимостей...
cd /d "%~dp0backend"
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Ошибка установки зависимостей
    pause
    exit /b 1
)

echo.
echo ✓ Python зависимости установлены

:: Check/Install Ollama
echo.
echo ════════════════════════════════════════════
echo 🤖 Ollama (локальная нейросеть)
echo ════════════════════════════════════════════
echo.

ollama --version >nul 2>&1
if errorlevel 1 (
    echo Ollama не установлен. Хотите установить? (Y/N)
    set /p INSTALL_OLLAMA=
    if /i "%INSTALL_OLLAMA%"=="Y" (
        echo.
        echo Установка Ollama...
        winget install Ollama.Ollama
        echo.
        echo ✓ Ollama установлен
        echo.
        echo Скачивание модели Qwen 2.5 (5GB)...
        ollama pull qwen2.5:7b
    ) else (
        echo.
        echo ⚠️  Ollama пропущен - AI-анализ будет недоступен
        echo    Вы можете установить его позже:
        echo    winget install Ollama.Ollama
        echo    ollama pull qwen2.5:7b
    )
) else (
    echo ✓ Ollama уже установлен
    
    :: Check if model exists
    ollama list | findstr "qwen2.5" >nul 2>&1
    if errorlevel 1 (
        echo.
        echo Модель qwen2.5:7b не найдена. Скачать? (Y/N)
        set /p DOWNLOAD_MODEL=
        if /i "%DOWNLOAD_MODEL%"=="Y" (
            echo Скачивание модели (5GB)...
            ollama pull qwen2.5:7b
        )
    ) else (
        echo ✓ Модель qwen2.5 найдена
    )
)

echo.
echo ════════════════════════════════════════════
echo ✅ Установка завершена!
echo ════════════════════════════════════════════
echo.
echo Для запуска используйте: start.bat
echo.
pause
