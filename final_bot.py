#!/usr/bin/env python3
"""
VideoFinder AI Bot - CLI Entry Point
Automatizador de contenido vertical sin rostros ni texto
"""

import sys
import os
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

# Agregar el directorio actual al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import validate_config, DEFAULT_MAX_RESULTS, PLATFORM_CONFIGS
from orchestrator import run_job

console = Console()

def print_banner():
    """Muestra el banner de bienvenida"""
    banner = """============================================================
                    VideoFinder AI Bot                       
              Automatizador de Contenido Vertical            
                    Sin Rostros ni Texto                     
============================================================"""
    console.print(Panel(banner, style="bold cyan"))

def validate_keyword(keyword: str) -> str:
    """Valida la palabra clave de búsqueda"""
    if not keyword or not keyword.strip():
        raise ValueError("La palabra clave no puede estar vacía")
    return keyword.strip()

def validate_duration_range(duration_str: str) -> tuple:
    """Valida y parsea el rango de duración"""
    try:
        if '-' not in duration_str:
            raise ValueError("Formato inválido. Use MIN-MAX (ej: 30-60)")
        
        min_str, max_str = duration_str.split('-', 1)
        min_sec = int(min_str.strip())
        max_sec = int(max_str.strip())
        
        if min_sec <= 0:
            raise ValueError("La duración mínima debe ser mayor a 0")
        if max_sec < min_sec:
            raise ValueError("La duración máxima debe ser mayor o igual a la mínima")
        
        return (min_sec, max_sec)
    except ValueError as e:
        if "invalid literal" in str(e):
            raise ValueError("Las duraciones deben ser números enteros")
        raise

def validate_filters(filters_str: str) -> dict:
    """Valida y parsea los filtros"""
    if not filters_str or filters_str.lower() == 'none':
        return {'vertical': False, 'faces': False, 'text': False}
    
    if filters_str.lower() == 'todos':
        return {'vertical': True, 'faces': True, 'text': True}
    
    filters = {}
    filter_options = ['vertical', 'faces', 'text']
    
    for option in filters_str.split(','):
        option = option.strip().lower()
        if option in filter_options:
            filters[option] = True
        else:
            raise ValueError(f"Filtro inválido: {option}. Opciones válidas: {', '.join(filter_options)}")
    
    # Validar que al menos un filtro esté activo
    if not any(filters.values()):
        raise ValueError("Debe seleccionar al menos un filtro")
    
    return filters

def validate_platforms(platforms_str: str) -> list:
    """Valida las plataformas"""
    if not platforms_str:
        return ['youtube', 'instagram', 'tiktok']
    
    valid_platforms = ['youtube', 'instagram', 'tiktok']
    platforms = [p.strip().lower() for p in platforms_str.split(',')]
    
    for platform in platforms:
        if platform not in valid_platforms:
            raise ValueError(f"Plataforma inválida: {platform}. Opciones válidas: {', '.join(valid_platforms)}")
    
    return platforms

def validate_max_results(max_str: str) -> int:
    """Valida el máximo de resultados"""
    if not max_str:
        return DEFAULT_MAX_RESULTS
    
    try:
        max_results = int(max_str)
        if max_results <= 0:
            raise ValueError("El máximo de resultados debe ser mayor a 0")
        return max_results
    except ValueError:
        raise ValueError("El máximo de resultados debe ser un número entero")

def cli_prompt_user() -> dict:
    """Interfaz CLI para obtener configuración del usuario"""
    print_banner()
    
    console.print("\n[bold green]Configuración de búsqueda:[/bold green]")
    
    # Palabra clave
    while True:
        keyword_input = Prompt.ask(
            "Ingrese palabra clave o búsqueda",
            default=""
        )
        try:
            keyword = validate_keyword(keyword_input)
            break
        except Exception as e:
            console.print(f"[red]{e}[/red]")
    
    # Rango de duración
    while True:
        duration_input = Prompt.ask(
            "Ingrese rango de duración (segundos) MIN-MAX, ej 30-60",
            default="30-60"
        )
        try:
            duration_range = validate_duration_range(duration_input)
            break
        except Exception as e:
            console.print(f"[red]{e}[/red]")
    
    # Filtros
    while True:
        filters_input = Prompt.ask(
            "Filtros a aplicar (separar por coma, 'todos' o 'none')",
            default="todos"
        )
        try:
            filters = validate_filters(filters_input)
            break
        except Exception as e:
            console.print(f"[red]{e}[/red]")
    
    # Plataformas
    while True:
        platforms_input = Prompt.ask(
            "Plataformas (youtube,instagram,tiktok)",
            default="youtube,instagram,tiktok"
        )
        try:
            platforms = validate_platforms(platforms_input)
            break
        except Exception as e:
            console.print(f"[red]{e}[/red]")
    
    # Máximo de resultados
    while True:
        max_input = Prompt.ask(
            f"Máx resultados por plataforma [default {DEFAULT_MAX_RESULTS}]",
            default=str(DEFAULT_MAX_RESULTS)
        )
        try:
            max_results = validate_max_results(max_input)
            break
        except Exception as e:
            console.print(f"[red]{e}[/red]")
    
    return {
        'keyword': keyword,
        'duration_range': duration_range,
        'filters': filters,
        'platforms': platforms,
        'max_results': max_results
    }

def display_config_summary(config: dict):
    """Muestra un resumen de la configuración"""
    table = Table(title="Resumen de Configuración")
    table.add_column("Parámetro", style="cyan")
    table.add_column("Valor", style="magenta")
    
    table.add_row("Palabra clave", config['keyword'])
    table.add_row("Duración", f"{config['duration_range'][0]}-{config['duration_range'][1]} s")
    
    filter_names = []
    if config['filters'].get('vertical', False):
        filter_names.append("vertical")
    if config['filters'].get('faces', False):
        filter_names.append("faces")
    if config['filters'].get('text', False):
        filter_names.append("text")
    
    table.add_row("Filtros", ", ".join(filter_names) if filter_names else "ninguno")
    table.add_row("Plataformas", ", ".join(config['platforms']))
    table.add_row("Max por plataforma", str(config['max_results']))
    
    console.print(table)

def main():
    """Función principal del CLI"""
    try:
        # Validar configuración del sistema
        console.print("\n[bold yellow]Validando configuración del sistema...[/bold yellow]")
        validate_config()
        
        # Obtener configuración del usuario
        config = cli_prompt_user()
        
        # Mostrar resumen
        console.print("\n")
        display_config_summary(config)
        
        # Confirmar ejecución
        console.print("\n")
        if not Confirm.ask("Confirmar?", default=True):
            console.print("[yellow]Operación cancelada por el usuario.[/yellow]")
            return
        
        # Ejecutar el trabajo
        console.print("\n[bold green]Iniciando análisis...[/bold green]")
        start_time = datetime.now()
        
        results = run_job(config)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Mostrar resultados
        console.print(f"\n[bold green]✅ Análisis completado en {duration:.1f} segundos[/bold green]")
        
        accepted_count = len([r for r in results if r.get('estado') == 'aceptado'])
        total_count = len(results)
        
        console.print(f"[green]Videos aceptados: {accepted_count}/{total_count}[/green]")
        console.print(f"[blue]Resultados guardados en: outputs/results.json[/blue]")
        console.print(f"[blue]Lista aceptada en: outputs/accepted_list.txt[/blue]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Operación cancelada por el usuario.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
