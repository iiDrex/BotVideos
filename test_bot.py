#!/usr/bin/env python3
"""
Script de prueba para VideoFinder AI Bot
Verifica que todos los componentes funcionen correctamente
"""

import sys
import os
from rich.console import Console
from rich.panel import Panel

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

console = Console()

def test_imports():
    """Prueba que todos los imports funcionen"""
    console.print("[blue]Probando imports...[/blue]")
    
    try:
        from config import validate_config, USE_GPU
        console.print("    [green]✓ Config importado[/green]")
        
        from analyzer.video_analyzer import EnhancedVideoAnalyzer
        console.print("    [green]✓ Video Analyzer importado[/green]")
        
        from analyzer.face_detector import FaceDetector
        console.print("    [green]✓ Face Detector importado[/green]")
        
        from analyzer.text_detector import TextDetector
        console.print("    [green]✓ Text Detector importado[/green]")
        
        from downloader import VideoDownloader
        console.print("    [green]✓ Video Downloader importado[/green]")
        
        from orchestrator import run_job
        console.print("    [green]✓ Orchestrator importado[/green]")
        
        return True
        
    except Exception as e:
        console.print(f"    [red]✗ Error en imports: {str(e)}[/red]")
        return False

def test_gpu_config():
    """Prueba la configuración de GPU"""
    console.print("\n[blue]Probando configuración de GPU...[/blue]")
    
    try:
        from config import USE_GPU
        
        if USE_GPU:
            console.print("    [green]✓ GPU habilitado en configuración[/green]")
            
            # Verificar PyTorch
            try:
                import torch
                if torch.cuda.is_available():
                    console.print(f"    [green]✓ CUDA disponible: {torch.cuda.get_device_name(0)}[/green]")
                else:
                    console.print("    [yellow]⚠️  CUDA no disponible[/yellow]")
            except ImportError:
                console.print("    [yellow]⚠️  PyTorch no instalado[/yellow]")
        else:
            console.print("    [yellow]⚠️  GPU deshabilitado[/yellow]")
            
        return True
        
    except Exception as e:
        console.print(f"    [red]✗ Error en configuración GPU: {str(e)}[/red]")
        return False

def test_components():
    """Prueba la inicialización de componentes"""
    console.print("\n[blue]Probando componentes...[/blue]")
    
    try:
        # Probar configuración
        from config import validate_config
        validate_config()
        console.print("    [green]✓ Configuración validada[/green]")
        
        # Probar Face Detector
        from analyzer.face_detector import FaceDetector
        face_detector = FaceDetector()
        console.print("    [green]✓ Face Detector inicializado[/green]")
        
        # Probar Text Detector
        from analyzer.text_detector import TextDetector
        text_detector = TextDetector()
        console.print("    [green]✓ Text Detector inicializado[/green]")
        
        # Probar Video Analyzer
        from analyzer.video_analyzer import EnhancedVideoAnalyzer
        config = {'filters': {'vertical': True, 'faces': True, 'text': True}}
        analyzer = EnhancedVideoAnalyzer(config)
        console.print("    [green]✓ Video Analyzer inicializado[/green]")
        
        # Probar Downloader
        from downloader import VideoDownloader
        downloader = VideoDownloader()
        console.print("    [green]✓ Video Downloader inicializado[/green]")
        
        return True
        
    except Exception as e:
        console.print(f"    [red]✗ Error en componentes: {str(e)}[/red]")
        return False

def test_ytdlp():
    """Prueba yt-dlp"""
    console.print("\n[blue]Probando yt-dlp...[/blue]")
    
    try:
        import subprocess
        result = subprocess.run(['yt-dlp', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            console.print(f"    [green]✓ yt-dlp disponible: {version}[/green]")
            return True
        else:
            console.print("    [red]✗ yt-dlp no funciona correctamente[/red]")
            return False
    except Exception as e:
        console.print(f"    [red]✗ Error con yt-dlp: {str(e)}[/red]")
        return False

def main():
    """Función principal de prueba"""
    console.print(Panel(
        "VideoFinder AI Bot - Test Suite",
        style="bold cyan"
    ))
    
    tests = [
        ("Imports", test_imports),
        ("GPU Config", test_gpu_config),
        ("Components", test_components),
        ("yt-dlp", test_ytdlp)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            console.print(f"[red]✗ Error en {test_name}: {str(e)}[/red]")
            results.append((test_name, False))
    
    # Mostrar resumen
    console.print("\n[bold]Resumen de Pruebas:[/bold]")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        color = "green" if result else "red"
        console.print(f"  [{color}]{status}[/{color}] {test_name}")
        if result:
            passed += 1
    
    console.print(f"\n[bold]Resultado: {passed}/{total} pruebas pasaron[/bold]")
    
    if passed == total:
        console.print("[bold green]¡Todas las pruebas pasaron! El bot está listo para usar.[/bold green]")
        return True
    else:
        console.print("[bold red]Algunas pruebas fallaron. Revisa los errores arriba.[/bold red]")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
