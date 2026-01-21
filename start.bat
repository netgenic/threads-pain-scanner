@echo off
chcp 65001 >nul
title Threads Pain Scanner

echo.
echo ╔══════════════════════════════════════════╗
echo ║     🔍 Threads Pain Scanner              ║
echo ╚══════════════════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo.
    echo Установите Python: winget install Python.Python.3.12
    echo.
    pause
    exit /b 1
)

echo ✓ Python найден

:: Check/Install dependencies
cd /d "%~dp0backend"

echo.
echo 📦 Проверка зависимостей...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo    Установка зависимостей...
    pip install -r requirements.txt -q
)
echo ✓ Зависимости установлены

:: Check Ollama
echo.
ollama --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Ollama не найден - AI-анализ будет недоступен
    echo    Для установки: winget install Ollama.Ollama
    echo    Затем: ollama pull qwen2.5:7b
) else (
    echo ✓ Ollama найден
)

echo.
echo ════════════════════════════════════════════
echo 🚀 Запуск сервера...
echo    Откройте в браузере: http://localhost:8000
echo    Для остановки: Ctrl+C
echo ════════════════════════════════════════════
echo.

python main.py

pause
