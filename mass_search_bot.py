#!/usr/bin/env python3
"""
Bot de búsqueda masiva optimizado
Busca la máxima cantidad de videos en el menor tiempo posible
"""

import sys
import os
import time
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich import print as rprint

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator import run_job
from config import validate_config

console = Console()

def get_optimized_config():
    """
    Configuración optimizada para búsqueda masiva
    Busca la máxima cantidad de videos en el menor tiempo
    """
    return {
        'keyword': 'crochet amigurumi',  # Palabra clave optimizada
        'platforms': ['youtube'],  # Solo YouTube para velocidad
        'max_results': 200,  # MÁXIMO de videos por plataforma
        'duration_range': (15, 60),  # Rango optimizado para shorts
        'filters': {
            'no_faces': True,
            'no_text': True,
            'min_duration': 15,
            'max_duration': 60
        }
    }

def display_optimization_info():
    """Muestra información sobre las optimizaciones aplicadas"""
    console.print("\n" + "="*80)
    console.print("[bold cyan]🚀 BOT DE BÚSQUEDA MASIVA ULTRA OPTIMIZADO[/bold cyan]")
    console.print("="*80)
    
    optimizations = [
        "✅ Búsqueda automática sin entrada del usuario",
        "✅ Máximo 200 videos por plataforma",
        "✅ Procesamiento paralelo ultra rápido (8 videos simultáneos)",
        "✅ Filtro de texto ultra profesional (7 capas)",
        "✅ Análisis optimizado (20 frames máximo)",
        "✅ Muestreo cada 1 segundo",
        "✅ Solo YouTube (más rápido que múltiples plataformas)",
        "✅ Duración optimizada (15-60 segundos)",
        "✅ GPU forzada para máxima velocidad",
        "✅ Limpieza automática de archivos temporales"
    ]
    
    for opt in optimizations:
        console.print(f"  {opt}")
    
    console.print("="*80)

def main():
    """Función principal optimizada para búsqueda masiva"""
    try:
        # Validar configuración del sistema
        console.print("\n[bold yellow]Validando configuración del sistema...[/bold yellow]")
        validate_config()
        
        # Mostrar información de optimización
        display_optimization_info()
        
        # Configuración automática optimizada
        config = get_optimized_config()
        
        # Mostrar configuración
        console.print(f"\n[bold green]Configuración de búsqueda masiva:[/bold green]")
        console.print(f"  🔍 Palabra clave: {config['keyword']}")
        console.print(f"  📺 Plataforma: {', '.join(config['platforms'])}")
        console.print(f"  📊 Máximo videos: {config['max_results']}")
        console.print(f"  ⏱️  Duración: {config['duration_range'][0]}-{config['duration_range'][1]} segundos")
        console.print(f"  🎯 Filtros: Sin rostros, Sin texto")
        
        # Confirmar ejecución
        console.print(f"\n[bold yellow]¿Iniciar búsqueda masiva? (Sí/No):[/bold yellow] ", end="")
        response = input().lower().strip()
        
        if response not in ['sí', 'si', 's', 'yes', 'y']:
            console.print("[yellow]Búsqueda cancelada.[/yellow]")
            return
        
        # Ejecutar búsqueda masiva
        console.print("\n[bold green]🚀 Iniciando búsqueda masiva ultra optimizada...[/bold green]")
        start_time = datetime.now()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
            expand=True
        ) as progress:
            
            # Crear tarea de progreso
            task = progress.add_task("Buscando videos masivamente...", total=100)
            
            # Ejecutar el trabajo
            results = run_job(config)
            
            # Completar progreso
            progress.update(task, completed=100)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Mostrar resultados finales
        console.print("\n" + "="*80)
        console.print("[bold green]🎉 BÚSQUEDA MASIVA COMPLETADA[/bold green]")
        console.print("="*80)
        
        accepted_count = len([r for r in results if r.get('estado') == 'aceptado'])
        total_count = len(results)
        discarded_count = total_count - accepted_count
        
        # Estadísticas detalladas
        console.print(f"[green]✅ Videos aceptados: {accepted_count}[/green]")
        console.print(f"[red]❌ Videos descartados: {discarded_count}[/red]")
        console.print(f"[blue]📊 Total procesados: {total_count}[/blue]")
        console.print(f"[yellow]⏱️  Tiempo total: {duration:.1f} segundos[/yellow]")
        console.print(f"[cyan]🚀 Velocidad: {total_count/duration:.1f} videos/segundo[/cyan]")
        
        # Razones de descarte
        if discarded_count > 0:
            console.print(f"\n[bold yellow]Razones de descarte:[/bold yellow]")
            reasons = {}
            for result in results:
                if result.get('estado') == 'descartado':
                    for reason in result.get('razones', []):
                        reasons[reason] = reasons.get(reason, 0) + 1
            
            for reason, count in reasons.items():
                console.print(f"  • {reason}: {count} videos")
        
        # Archivos generados
        console.print(f"\n[bold blue]📁 Archivos generados:[/bold blue]")
        console.print(f"  📄 Resultados completos: outputs/results.json")
        console.print(f"  📋 Lista aceptada: outputs/accepted_list.txt")
        
        # Eficiencia
        if accepted_count > 0:
            efficiency = (accepted_count / total_count) * 100
            console.print(f"\n[bold green]📈 Eficiencia: {efficiency:.1f}% de videos útiles[/bold green]")
        
        console.print("="*80)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Búsqueda cancelada por el usuario.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error durante la búsqueda masiva: {str(e)}[/bold red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
