#!/usr/bin/env python3
"""
Script de prueba simple para VideoFinder AI Bot
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Prueba que todos los imports funcionen"""
    print("Probando imports...")
    
    try:
        from config import validate_config, USE_GPU
        print("  OK - Config importado")
        
        from analyzer.video_analyzer import EnhancedVideoAnalyzer
        print("  OK - Video Analyzer importado")
        
        from analyzer.face_detector import FaceDetector
        print("  OK - Face Detector importado")
        
        from analyzer.text_detector import TextDetector
        print("  OK - Text Detector importado")
        
        from downloader import VideoDownloader
        print("  OK - Video Downloader importado")
        
        from orchestrator import run_job
        print("  OK - Orchestrator importado")
        
        return True
        
    except Exception as e:
        print(f"  ERROR - Error en imports: {str(e)}")
        return False

def test_gpu_config():
    """Prueba la configuración de GPU"""
    print("\nProbando configuración de GPU...")
    
    try:
        from config import USE_GPU
        
        if USE_GPU:
            print("  OK - GPU habilitado en configuración")
            
            # Verificar PyTorch
            try:
                import torch
                if torch.cuda.is_available():
                    print(f"  OK - CUDA disponible: {torch.cuda.get_device_name(0)}")
                else:
                    print("  WARNING - CUDA no disponible")
            except ImportError:
                print("  WARNING - PyTorch no instalado")
        else:
            print("  WARNING - GPU deshabilitado")
            
        return True
        
    except Exception as e:
        print(f"  ERROR - Error en configuración GPU: {str(e)}")
        return False

def test_ytdlp():
    """Prueba yt-dlp"""
    print("\nProbando yt-dlp...")
    
    try:
        import subprocess
        result = subprocess.run(['yt-dlp', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"  OK - yt-dlp disponible: {version}")
            return True
        else:
            print("  ERROR - yt-dlp no funciona correctamente")
            return False
    except Exception as e:
        print(f"  ERROR - Error con yt-dlp: {str(e)}")
        return False

def main():
    """Función principal de prueba"""
    print("=" * 50)
    print("VideoFinder AI Bot - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("GPU Config", test_gpu_config),
        ("yt-dlp", test_ytdlp)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"ERROR en {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Mostrar resumen
    print("\n" + "=" * 50)
    print("Resumen de Pruebas:")
    print("=" * 50)
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("¡Todas las pruebas pasaron! El bot está listo para usar.")
        return True
    else:
        print("Algunas pruebas fallaron. Revisa los errores arriba.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
