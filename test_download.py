#!/usr/bin/env python3
"""
Script de prueba para verificar que las descargas funcionen
"""

import sys
import os
from rich.console import Console

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

console = Console()

def test_download():
    """Prueba la descarga de un video específico"""
    console.print("[blue]Probando descarga de video...[/blue]")
    
    try:
        from downloader import VideoDownloader
        
        # Crear downloader
        downloader = VideoDownloader("tmp")
        
        # URL de prueba
        test_url = "https://www.youtube.com/shorts/Fa8-K1UFKyE"
        
        console.print(f"[blue]Descargando: {test_url}[/blue]")
        
        # Intentar descarga
        result = downloader.download_temporal(test_url, max_duration=60)
        
        if result:
            console.print(f"[green]OK - Descarga exitosa: {result}[/green]")
            
            # Verificar que el archivo existe
            if os.path.exists(result):
                file_size = os.path.getsize(result)
                console.print(f"[green]OK - Archivo existe: {file_size} bytes[/green]")
                
                # Limpiar archivo de prueba
                downloader.remove(result)
                console.print("[yellow]Archivo de prueba eliminado[/yellow]")
                
                return True
            else:
                console.print("[red]ERROR - Archivo no encontrado[/red]")
                return False
        else:
            console.print("[red]ERROR - Error en descarga[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]ERROR - Error: {str(e)}[/red]")
        return False

def test_gpu_status():
    """Verifica el estado de GPU"""
    console.print("\n[blue]Verificando estado de GPU...[/blue]")
    
    try:
        from config import USE_GPU
        console.print(f"[blue]USE_GPU configurado: {USE_GPU}[/blue]")
        
        if USE_GPU:
            try:
                import torch
                if torch.cuda.is_available():
                    console.print(f"[green]OK - CUDA disponible: {torch.cuda.get_device_name(0)}[/green]")
                    return True
                else:
                    console.print("[yellow]WARNING  CUDA no disponible, pero GPU forzado[/yellow]")
                    return True
            except ImportError:
                console.print("[yellow]WARNING  PyTorch no disponible, pero GPU forzado[/yellow]")
                return True
        else:
            console.print("[yellow]WARNING  GPU deshabilitado[/yellow]")
            return False
            
    except Exception as e:
        console.print(f"[red]ERROR - Error verificando GPU: {str(e)}[/red]")
        return False

def main():
    """Función principal de prueba"""
    console.print("=" * 50)
    console.print("Prueba de Descarga y GPU")
    console.print("=" * 50)
    
    # Probar descarga
    download_ok = test_download()
    
    # Probar GPU
    gpu_ok = test_gpu_status()
    
    # Resumen
    console.print("\n" + "=" * 50)
    console.print("Resumen:")
    console.print("=" * 50)
    
    if download_ok:
        console.print("[green]OK - Descargas funcionando correctamente[/green]")
    else:
        console.print("[red]ERROR - Problemas con descargas[/red]")
    
    if gpu_ok:
        console.print("[green]OK - GPU configurado correctamente[/green]")
    else:
        console.print("[yellow]WARNING  GPU no disponible, usando CPU[/yellow]")
    
    if download_ok:
        console.print("\n[bold green]¡El bot está listo para usar![/bold green]")
        console.print("[blue]Ejecuta: python final_bot.py[/blue]")
        return True
    else:
        console.print("\n[bold red]Hay problemas que resolver[/bold red]")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
