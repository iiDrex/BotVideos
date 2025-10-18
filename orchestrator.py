"""
Orchestrator - Lógica principal del VideoFinder AI Bot
Coordina scrapers, downloader y analyzer
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any
from rich.console import Console
from rich.progress import Progress, TaskID
from rich import print as rprint

from config import (
    TEMP_DIR, OUTPUT_JSON, ACCEPTED_LIST, 
    validate_config, OUTPUT_DIR
)
from scrapers.youtube_scraper import search_youtube
from scrapers.instagram_scraper import search_instagram
from scrapers.tiktok_scraper import search_tiktok
from downloader import VideoDownloader
from analyzer.video_analyzer import EnhancedVideoAnalyzer
from utils.ffprobe_utils import get_video_metadata, get_basic_duration_and_resolution
from cleaners import SimpleCleaner

console = Console()

def run_job(config: dict) -> List[Dict]:
    """
    Orquesta todo el flujo del VideoFinder AI Bot
    
    Args:
        config: Configuración del usuario
        
    Returns:
        Lista de resultados finales
    """
    console.print("[bold blue]Iniciando VideoFinder AI Bot[/bold blue]")
    
    # Crear directorios necesarios
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Inicializar componentes
    downloader = VideoDownloader(TEMP_DIR)
    analyzer = EnhancedVideoAnalyzer(config)
    cleaner = SimpleCleaner(TEMP_DIR)
    
    try:
        # Paso 1: Buscar candidatos en todas las plataformas
        console.print("\n[bold yellow]Buscando videos candidatos...[/bold yellow]")
        candidates = []
        
        for platform in config['platforms']:
            console.print(f"  Buscando en {platform}...")
            try:
                if platform == 'youtube':
                    platform_candidates = search_youtube(
                        config['keyword'], 
                        config['max_results']
                    )
                elif platform == 'instagram':
                    platform_candidates = search_instagram(
                        config['keyword'], 
                        config['max_results']
                    )
                elif platform == 'tiktok':
                    platform_candidates = search_tiktok(
                        config['keyword'], 
                        config['max_results']
                    )
                else:
                    console.print(f"  [red]Plataforma no soportada: {platform}[/red]")
                    continue
                
                candidates.extend(platform_candidates)
                console.print(f"  [green]OK {platform}: {len(platform_candidates)} candidatos encontrados[/green]")
                
            except Exception as e:
                console.print(f"  [red]ERROR {platform}: Error - {str(e)}[/red]")
                continue
        
        console.print(f"[green]Total candidatos encontrados: {len(candidates)}[/green]")
        
        if not candidates:
            console.print("[yellow]No se encontraron candidatos. Terminando.[/yellow]")
            return []
        
        # Paso 2: Pre-filtrar por metadatos (ligero primero)
        console.print("\n[bold yellow]Pre-filtrando por metadatos...[/bold yellow]")
        metadata_pass = []
        results = []
        
        with Progress() as progress:
            task = progress.add_task("Pre-filtrando...", total=len(candidates))
            
            for candidate in candidates:
                try:
                    url = candidate.get('url', '')
                    # 1) Ruta rápida: solo duración y resolución
                    basic = get_basic_duration_and_resolution(url)
                    # 2) Si falla o faltan datos, ruta completa
                    metadata = basic or get_video_metadata(url) or {}
                    if not metadata:
                        results.append(create_result(
                            candidate, metadata, "descartado", 
                            ["error obteniendo metadatos"]
                        ))
                        progress.update(task, advance=1)
                        continue
                    
                    # Verificar orientación vertical
                    if config['filters'].get('vertical', True):
                        if not is_vertical(metadata):
                            results.append(create_result(
                                candidate, metadata, "descartado",
                                ["orientacion horizontal"]
                            ))
                            progress.update(task, advance=1)
                            continue
                    
                    # Verificar duración
                    if not duration_in_range(metadata.get('duration', 0), config['duration_range']):
                        results.append(create_result(
                            candidate, metadata, "descartado",
                            ["duracion fuera de rango"]
                        ))
                        progress.update(task, advance=1)
                        continue
                    
                    # Pasar al siguiente paso
                    candidate_with_meta = {**candidate, **metadata}
                    metadata_pass.append(candidate_with_meta)
                    progress.update(task, advance=1)
                    
                except Exception as e:
                    console.print(f"[red]Error procesando candidato: {str(e)}[/red]")
                    results.append(create_result(
                        candidate, {}, "descartado",
                        [f"error: {str(e)}"]
                    ))
                    progress.update(task, advance=1)
        
        console.print(f"[green]Candidatos que pasaron pre-filtro: {len(metadata_pass)}[/green]")
        
        if not metadata_pass:
            console.print("[yellow]Ningún candidato pasó el pre-filtro. Terminando.[/yellow]")
            save_results(results)
            return results
        
        # Paso 3: Descargar y analizar videos
        console.print("\n[bold yellow]Descargando y analizando videos...[/bold yellow]")
        
        with Progress() as progress:
            task = progress.add_task("Analizando...", total=len(metadata_pass))
            
            for item in metadata_pass:
                try:
                    # Descargar video temporal
                    temp_path = downloader.download_temporal(item['url'])
                    if not temp_path:
                        results.append(create_result(
                            item, item, "descartado",
                            ["error descarga"]
                        ))
                        progress.update(task, advance=1)
                        continue
                    
                    # Analizar video
                    analysis = analyzer.analyze_video(temp_path)
                    
                    # Aplicar filtros
                    razones = []
                    
                    # Filtro de rostros
                    if config['filters'].get('faces', True) and analysis.get('has_face', False):
                        razones.append("rostro detectado")
                        results.append(create_result(
                            item, item, "descartado", razones, analysis
                        ))
                        downloader.remove(temp_path)
                        progress.update(task, advance=1)
                        continue
                    
                    # Filtro de texto
                    if config['filters'].get('text', True) and analysis.get('has_text', False):
                        razones.append("texto detectado")
                        results.append(create_result(
                            item, item, "descartado", razones, analysis
                        ))
                        downloader.remove(temp_path)
                        progress.update(task, advance=1)
                        continue
                    
                    # Video aceptado
                    results.append(create_result(
                        item, item, "aceptado", [], analysis
                    ))
                    downloader.remove(temp_path)
                    progress.update(task, advance=1)
                    
                except Exception as e:
                    console.print(f"[red]Error analizando video: {str(e)}[/red]")
                    results.append(create_result(
                        item, item, "descartado",
                        [f"error: {str(e)}"]
                    ))
                    if 'temp_path' in locals():
                        downloader.remove(temp_path)
                    progress.update(task, advance=1)
        
        # Paso 4: Guardar resultados
        console.print("\n[bold yellow]Guardando resultados...[/bold yellow]")
        save_results(results)
        
        # Paso 5: Mostrar resumen
        show_summary(results)
        
        return results
        
    except Exception as e:
        console.print(f"[bold red]Error en el orquestador: {str(e)}[/bold red]")
        raise
    finally:
        # Limpiar archivos temporales
        cleaner.cleanup()

def is_vertical(metadata: dict) -> bool:
    """Verifica si el video es vertical"""
    width = metadata.get('width', 0)
    height = metadata.get('height', 0)
    return height > width if width > 0 and height > 0 else False

def duration_in_range(duration: float, duration_range: tuple) -> bool:
    """Verifica si la duración está en el rango especificado"""
    min_dur, max_dur = duration_range
    return min_dur <= duration <= max_dur

def create_result(candidate: dict, metadata: dict, estado: str, razones: list, analysis: dict = None) -> dict:
    """Crea un resultado estructurado"""
    return {
        'titulo': candidate.get('title', 'Sin título'),
        'enlace': candidate.get('url', ''),
        'id': candidate.get('id', ''),
        'platform': candidate.get('platform', 'unknown'),
        'duracion_sec': int(metadata.get('duration', 0)),
        'width': metadata.get('width', 0),
        'height': metadata.get('height', 0),
        'resolution': f"{metadata.get('width', 0)}x{metadata.get('height', 0)}",
        'processed_at': datetime.now().isoformat() + 'Z',
        'estado': estado,
        'razones': razones,
        'raw_metadata': metadata,
        'analysis': analysis or {}
    }

def save_results(results: List[Dict]):
    """Guarda los resultados en JSON y genera lista aceptada"""
    # Guardar JSON completo
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Generar lista aceptada
    accepted = [r for r in results if r.get('estado') == 'aceptado']
    
    with open(ACCEPTED_LIST, 'w', encoding='utf-8') as f:
        f.write("==============================\n")
        f.write("✅ VIDEOS QUE PASARON LOS FILTROS\n")
        f.write("==============================\n\n")
        
        for i, video in enumerate(accepted, 1):
            f.write(f"{i}) \"{video['titulo']}\"\n")
            f.write(f"   • Enlace: {video['enlace']}\n")
            f.write(f"   • Duración: {video['duracion_sec']} s\n")
            f.write(f"   • Resolución: {video['resolution']}\n")
            f.write(f"   • Plataforma: {video['platform'].title()}\n\n")
    
    console.print(f"[green]Resultados guardados en: {OUTPUT_JSON}")
    console.print(f"[green]Lista aceptada guardada en: {ACCEPTED_LIST}")

def show_summary(results: List[Dict]):
    """Muestra resumen de resultados en consola"""
    accepted = [r for r in results if r.get('estado') == 'aceptado']
    discarded = [r for r in results if r.get('estado') == 'descartado']
    
    console.print("\n[bold green]==============================")
    console.print("VIDEOS QUE PASARON LOS FILTROS")
    console.print("==============================[/bold green]")
    
    if not accepted:
        console.print("[yellow]Ningún video pasó todos los filtros.[/yellow]")
    else:
        for i, video in enumerate(accepted, 1):
            console.print(f"[green]{i}) \"{video['titulo']}\"[/green]")
            console.print(f"   • Enlace: {video['enlace']}")
            console.print(f"   • Duración: {video['duracion_sec']} s")
            console.print(f"   • Resolución: {video['resolution']}")
            console.print(f"   • Plataforma: {video['platform'].title()}")
            console.print()
    
    # Mostrar estadísticas
    console.print(f"[blue]Total procesados: {len(results)}[/blue]")
    console.print(f"[green]Aceptados: {len(accepted)}[/green]")
    console.print(f"[red]Descartados: {len(discarded)}[/red]")
    
    # Mostrar razones de descarte
    if discarded:
        razones_count = {}
        for result in discarded:
            for razon in result.get('razones', []):
                razones_count[razon] = razones_count.get(razon, 0) + 1
        
        console.print("\n[bold yellow]Razones de descarte:[/bold yellow]")
        for razon, count in razones_count.items():
            console.print(f"  • {razon}: {count} videos")
