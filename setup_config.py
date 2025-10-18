#!/usr/bin/env python3
"""
Script de configuración para VideoFinder AI Bot
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Verifica la versión de Python"""
    if sys.version_info < (3, 12):
        print("❌ Error: Se requiere Python 3.12 o superior")
        print(f"   Versión actual: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True

def check_ffmpeg():
    """Verifica si FFmpeg está instalado"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg - OK")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ FFmpeg no encontrado")
    print("   Instala desde: https://ffmpeg.org/download.html")
    print("   O usa chocolatey: choco install ffmpeg")
    return False

def check_tesseract():
    """Verifica si Tesseract está instalado"""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Tesseract OCR - OK")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ Tesseract OCR no encontrado")
    print("   Instala desde: https://github.com/UB-Mannheim/tesseract/wiki")
    print("   O usa chocolatey: choco install tesseract")
    return False

def create_env_file():
    """Crea el archivo .env si no existe"""
    env_file = Path('.env')
    env_example = Path('env.example')
    
    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("✅ Archivo .env creado desde env.example")
        else:
            # Crear .env básico
            with open(env_file, 'w') as f:
                f.write("""# Configuración de VideoFinder AI Bot
TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
TEMP_DIR=tmp
OUTPUT_DIR=outputs
FACE_CONFIDENCE=0.45
OCR_CONFIDENCE=0.5
MIN_TEXT_LENGTH=2
USE_GPU=False
DOWNLOAD_TIMEOUT=300
MAX_DURATION=600
REQUEST_DELAY=1.0
MAX_RETRIES=3
""")
            print("✅ Archivo .env creado con configuración básica")
    else:
        print("✅ Archivo .env ya existe")

def create_directories():
    """Crea directorios necesarios"""
    dirs = ['tmp', 'outputs', 'tests/sample_videos']
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directorio {dir_path} creado")

def install_dependencies():
    """Instala dependencias de Python"""
    try:
        print("📦 Instalando dependencias...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Dependencias instaladas")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error instalando dependencias")
        return False

def install_playwright():
    """Instala Playwright"""
    try:
        print("🎭 Instalando Playwright...")
        subprocess.run([sys.executable, '-m', 'playwright', 'install'], check=True)
        print("✅ Playwright instalado")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error instalando Playwright")
        return False

def main():
    """Función principal de configuración"""
    print("🚀 VideoFinder AI Bot - Configuración")
    print("=" * 50)
    
    # Verificar Python
    if not check_python_version():
        return 1
    
    # Crear directorios
    create_directories()
    
    # Crear archivo .env
    create_env_file()
    
    # Instalar dependencias
    if not install_dependencies():
        return 1
    
    # Instalar Playwright
    if not install_playwright():
        return 1
    
    # Verificar herramientas externas
    ffmpeg_ok = check_ffmpeg()
    tesseract_ok = check_tesseract()
    
    print("\n" + "=" * 50)
    print("📋 RESUMEN DE CONFIGURACIÓN")
    print("=" * 50)
    
    if ffmpeg_ok and tesseract_ok:
        print("🎉 ¡Configuración completada exitosamente!")
        print("\nPara ejecutar el bot:")
        print("  python final_bot.py")
    else:
        print("⚠️  Configuración parcialmente completada")
        print("\nInstala las herramientas faltantes y ejecuta:")
        print("  python final_bot.py")
    
    return 0

if __name__ == "__main__":
    exit(main())
