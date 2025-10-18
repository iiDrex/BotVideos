@echo off
echo ========================================
echo VideoFinder AI Bot - Instalacion Windows
echo ========================================
echo.

echo [1/5] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado
    echo Por favor instala Python 3.12 desde https://python.org
    pause
    exit /b 1
)

echo [2/5] Instalando dependencias de Python...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Fallo al instalar dependencias
    pause
    exit /b 1
)

echo [3/5] Instalando Playwright...
playwright install
if %errorlevel% neq 0 (
    echo ERROR: Fallo al instalar Playwright
    pause
    exit /b 1
)

echo [4/5] Verificando FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ADVERTENCIA: FFmpeg no encontrado
    echo Por favor instala FFmpeg desde https://ffmpeg.org
    echo O usa chocolatey: choco install ffmpeg
)

echo [5/5] Verificando Tesseract...
tesseract --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ADVERTENCIA: Tesseract no encontrado
    echo Por favor instala Tesseract OCR desde https://github.com/UB-Mannheim/tesseract/wiki
    echo O usa chocolatey: choco install tesseract
)

echo.
echo ========================================
echo Instalacion completada!
echo ========================================
echo.
echo Para ejecutar el bot:
echo   python final_bot.py
echo.
echo Para configurar variables de entorno:
echo   copy env.example .env
echo   (editar .env con tus rutas)
echo.
pause
