#!/usr/bin/env python3
"""
Búsqueda masiva completamente automática
Sin entrada del usuario - máxima velocidad
"""

import sys
import os
import time
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator import run_job
from config import validate_config

console = Console()

def get_auto_optimized_config():
    """
    Configuración automática ultra optimizada
    """
    return {
        'keyword': 'crochet amigurumi',
        'platforms': ['youtube'],
        'max_results': 300,  # Máximo razonable para velocidad
        'duration_range': (15, 60),
        'filters': {
            'no_faces': True,
            'no_text': True,
            'min_duration': 15,
            'max_duration': 60
        }
    }

def main():
    """Función principal completamente automática"""
    try:
        # Validar configuración
        console.print("\n[bold yellow]Validando configuración del sistema...[/bold yellow]")
        validate_config()
        
        # Mostrar configuración automática
        console.print("\n" + "="*80)
        console.print("[bold cyan]BUSQUEDA MASIVA AUTOMATICA - MAXIMA VELOCIDAD[/bold cyan]")
        console.print("="*80)
        
        config = get_auto_optimized_config()
        
        console.print(f"[bold green]Configuración automática:[/bold green]")
        console.print(f"  Palabra clave: {config['keyword']}")
        console.print(f"  Plataforma: {', '.join(config['platforms'])}")
        console.print(f"  Máximo videos: {config['max_results']}")
        console.print(f"  Duración: {config['duration_range'][0]}-{config['duration_range'][1]} segundos")
        console.print(f"  Filtros: Sin rostros, Sin texto")
        console.print(f"  Procesamiento: 8 videos simultáneos")
        console.print(f"  Análisis: 15 frames máximo por video")
        console.print("="*80)
        
        # Ejecutar búsqueda automática
        console.print("\n[bold green]Iniciando búsqueda masiva automática...[/bold green]")
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
            task = progress.add_task("Buscando videos masivamente (automático)...", total=100)
            
            # Ejecutar el trabajo
            results = run_job(config)
            
            # Completar progreso
            progress.update(task, completed=100)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Mostrar resultados
        console.print("\n" + "="*80)
        console.print("[bold green]BUSQUEDA MASIVA AUTOMATICA COMPLETADA[/bold green]")
        console.print("="*80)
        
        accepted_count = len([r for r in results if r.get('estado') == 'aceptado'])
        total_count = len(results)
        discarded_count = total_count - accepted_count
        
        # Estadísticas
        console.print(f"[green]Videos aceptados: {accepted_count}[/green]")
        console.print(f"[red]Videos descartados: {discarded_count}[/red]")
        console.print(f"[blue]Total procesados: {total_count}[/blue]")
        console.print(f"[yellow]Tiempo total: {duration:.1f} segundos[/yellow]")
        console.print(f"[cyan]Velocidad: {total_count/duration:.1f} videos/segundo[/cyan]")
        
        # Eficiencia
        if accepted_count > 0:
            efficiency = (accepted_count / total_count) * 100
            console.print(f"[bold green]Eficiencia: {efficiency:.1f}% de videos útiles[/bold green]")
        
        # Razones de descarte
        if discarded_count > 0:
            console.print(f"\n[bold yellow]Análisis de descartes:[/bold yellow]")
            reasons = {}
            for result in results:
                if result.get('estado') == 'descartado':
                    for reason in result.get('razones', []):
                        reasons[reason] = reasons.get(reason, 0) + 1
            
            for reason, count in reasons.items():
                percentage = (count / total_count) * 100
                console.print(f"  • {reason}: {count} videos ({percentage:.1f}%)")
        
        # Archivos generados
        console.print(f"\n[bold blue]Archivos generados:[/bold blue]")
        console.print(f"  Resultados completos: outputs/results.json")
        console.print(f"  Lista aceptada: outputs/accepted_list.txt")
        
        # Rendimiento
        if duration > 0:
            videos_per_minute = (total_count / duration) * 60
            console.print(f"\n[bold cyan]Rendimiento: {videos_per_minute:.1f} videos/minuto[/bold cyan]")
        
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
