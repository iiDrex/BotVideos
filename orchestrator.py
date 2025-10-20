"""
Orchestrator - Lógica principal del VideoFinder AI Bot
Coordina scrapers, downloader y analyzer
"""

import os
import json
import time
import numpy as np
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
    console.print("[bold cyan]Iniciando VideoFinder AI Bot[/bold cyan]")
    
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
        
        # Paso 2: Pre-filtrar por metadatos ULTRA RÁPIDO (sin llamadas a APIs)
        console.print("\n[bold yellow]Pre-filtrando por metadatos (ultra rápido)...[/bold yellow]")
        metadata_pass = []
        results = []
        
        # FILTRADO ULTRA RÁPIDO - sin barra de progreso
        for candidate in candidates:
            try:
                # USAR SOLO INFORMACIÓN YA DISPONIBLE DE LOS SCRAPERS
                # No hacer llamadas adicionales a APIs
                
                # Verificar orientación vertical usando información del scraper
                if config['filters'].get('vertical', True):
                    width = candidate.get('width', 0)
                    height = candidate.get('height', 0)
                    if width > 0 and height > 0:
                        if not (height > width):  # No es vertical
                            results.append(create_result(
                                candidate, candidate, "descartado",
                                ["orientacion horizontal"]
                            ))
                            continue
                
                # Verificar duración usando información del scraper
                duration = candidate.get('duration', 0)
                if duration > 0:
                    if not duration_in_range(duration, config['duration_range']):
                        results.append(create_result(
                            candidate, candidate, "descartado",
                            ["duracion fuera de rango"]
                        ))
                        continue
                
                # Si no tenemos información suficiente, pasar al siguiente paso
                # (se verificará durante el análisis de video)
                metadata_pass.append(candidate)
                
            except Exception as e:
                console.print(f"[red]Error procesando candidato: {str(e)}[/red]")
                results.append(create_result(
                    candidate, candidate, "descartado",
                    [f"error: {str(e)}"]
                ))
        
        console.print(f"[green]Candidatos que pasaron pre-filtro: {len(metadata_pass)}[/green]")
        
        if not metadata_pass:
            console.print("[yellow]Ningún candidato pasó el pre-filtro. Terminando.[/yellow]")
            save_results(results)
            return results
        
        # Paso 3: Descargar y analizar videos - PROCESAMIENTO EN PARALELO ULTRA RÁPIDO
        console.print("\n[bold yellow]Descargando y analizando videos (paralelo ultra rápido)...[/bold yellow]")
        
        # PROCESAMIENTO EN PARALELO para velocidad máxima
        import concurrent.futures
        import threading
        
        def process_single_video(item):
            """Procesa un solo video de forma optimizada"""
            try:
                # Descargar video temporal
                temp_path = downloader.download_temporal(item['url'])
                if not temp_path:
                    return create_result(
                        item, item, "descartado",
                        ["error descarga"]
                    )
                
                # Analizar video con filtros optimizados
                analysis = analyzer.analyze_video_optimized(temp_path, config['filters'])
                
                # Limpiar archivo temporal inmediatamente
                downloader.remove(temp_path)
                
                # Si el análisis retorna un resultado directo (descartado), usarlo
                if analysis.get('estado') == 'descartado':
                    return create_result(
                        item, item, "descartado", 
                        analysis.get('razones', []), analysis
                    )
                
                # Video aceptado
                return create_result(
                    item, item, "aceptado", [], analysis
                )
                
            except Exception as e:
                return create_result(
                    item, item, "descartado",
                    [f"error: {str(e)}"]
                )
        
        # PROCESAR EN PARALELO - máximo 8 videos simultáneos para búsqueda masiva
        max_workers = min(8, len(metadata_pass))
        results = []
        
        # LIMPIEZA DE MEMORIA antes del procesamiento paralelo
        import gc
        gc.collect()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Enviar todos los trabajos
            future_to_item = {
                executor.submit(process_single_video, item): item 
                for item in metadata_pass
            }
            
            # Recoger resultados conforme se completan
            with Progress() as progress:
                task = progress.add_task("Analizando...", total=len(metadata_pass))
                
                for future in concurrent.futures.as_completed(future_to_item):
                    try:
                        result = future.result()
                        results.append(result)
                        progress.update(task, advance=1)
                        
                        # LIMPIEZA DE MEMORIA después de cada video
                        gc.collect()
                        
                    except Exception as e:
                        console.print(f"[red]Error en procesamiento paralelo: {str(e)}[/red]")
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
    # Convertir todos los valores float32 a float para evitar errores de serialización
    def convert_float32(obj):
        if isinstance(obj, dict):
            return {k: convert_float32(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_float32(item) for item in obj]
        elif hasattr(obj, 'item'):  # numpy/torch tensors
            return float(obj.item())
        elif isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        else:
            return obj
    
    # Aplicar conversión a todos los resultados
    results_clean = convert_float32(results)
    
    # Guardar JSON completo
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(results_clean, f, indent=2, ensure_ascii=False)
    
    # Generar lista aceptada
    accepted = [r for r in results_clean if r.get('estado') == 'aceptado']
    
    with open(ACCEPTED_LIST, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("✅ VIDEOS ACEPTADOS - LISTA COMPLETA\n")
        f.write("=" * 60 + "\n\n")
        
        if not accepted:
            f.write("❌ No se encontraron videos que cumplan los criterios.\n")
        else:
            f.write(f"📊 Total de videos aceptados: {len(accepted)}\n\n")
            
            for i, video in enumerate(accepted, 1):
                f.write(f"{i:2d}) 📹 \"{video['titulo']}\"\n")
                f.write(f"     🔗 Enlace: {video['enlace']}\n")
                f.write(f"     ⏱️  Duración: {video['duracion_sec']} segundos\n")
                f.write(f"     📐 Resolución: {video['resolution']}\n")
                f.write(f"     🌐 Plataforma: {video['platform'].title()}\n")
                f.write(f"     📅 Procesado: {video['processed_at']}\n\n")
    
    console.print(f"[green]Resultados guardados en: {OUTPUT_JSON}")
    console.print(f"[green]Lista aceptada guardada en: {ACCEPTED_LIST}")
    console.print(f"[green]Total videos aceptados: {len(accepted)}")

def show_summary(results: List[Dict]):
    """Muestra resumen de resultados en consola"""
    accepted = [r for r in results if r.get('estado') == 'aceptado']
    discarded = [r for r in results if r.get('estado') == 'descartado']
    
    console.print("\n[bold green]==============================")
    console.print("[bold green]VIDEOS QUE PASARON LOS FILTROS[/bold green]")
    console.print("[bold green]==============================[/bold green]")
    
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
