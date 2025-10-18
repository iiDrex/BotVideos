"""
YouTube Scraper usando yt-dlp
"""

import json
import subprocess
import time
from typing import List, Dict, Any
from rich.console import Console

from config import YT_DLP_OPTIONS, REQUEST_DELAY

console = Console()

def search_youtube(keyword: str, max_results: int = 50) -> List[Dict]:
    """
    Busca videos en YouTube usando yt-dlp
    
    Args:
        keyword: Palabra clave de búsqueda
        max_results: Máximo número de resultados
        
    Returns:
        Lista de diccionarios con metadatos de videos
    """
    console.print(f"  [blue]Buscando en YouTube: '{keyword}' (max: {max_results})[/blue]")
    
    try:
        # Construir comando yt-dlp
        cmd = [
            'yt-dlp',
            '--dump-json',
            '--flat-playlist',
            '--playlist-end', str(max_results),
            f'ytsearch{max_results}:{keyword}',
            '--quiet',
            '--no-warnings'
        ]
        
        # Ejecutar comando
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            check=True
        )
        
        # Parsear resultados
        videos = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                try:
                    video_data = json.loads(line)
                    videos.append(parse_youtube_video(video_data))
                except json.JSONDecodeError:
                    continue
        
        console.print(f"  [green]✓ YouTube: {len(videos)} videos encontrados[/green]")
        return videos
        
    except subprocess.TimeoutExpired:
        console.print("  [red]✗ YouTube: Timeout en búsqueda[/red]")
        return []
    except subprocess.CalledProcessError as e:
        console.print(f"  [red]✗ YouTube: Error en búsqueda - {e}[/red]")
        return []
    except Exception as e:
        console.print(f"  [red]✗ YouTube: Error inesperado - {str(e)}[/red]")
        return []
    finally:
        # Delay entre requests
        time.sleep(REQUEST_DELAY)

def parse_youtube_video(video_data: Dict) -> Dict:
    """
    Parsea los datos de un video de YouTube
    
    Args:
        video_data: Datos raw del video de yt-dlp
        
    Returns:
        Diccionario estructurado con metadatos
    """
    return {
        'id': video_data.get('id', ''),
        'title': video_data.get('title', 'Sin título'),
        'url': video_data.get('webpage_url', ''),
        'platform': 'youtube',
        'duration': video_data.get('duration', 0),
        'width': video_data.get('width', 0),
        'height': video_data.get('height', 0),
        'view_count': video_data.get('view_count', 0),
        'uploader': video_data.get('uploader', ''),
        'upload_date': video_data.get('upload_date', ''),
        'description': video_data.get('description', ''),
        'tags': video_data.get('tags', []),
        'thumbnail': video_data.get('thumbnail', ''),
        'raw_data': video_data
    }

def get_youtube_video_metadata(video_id: str) -> Dict:
    """
    Obtiene metadatos detallados de un video específico de YouTube
    
    Args:
        video_id: ID del video de YouTube
        
    Returns:
        Diccionario con metadatos del video
    """
    try:
        cmd = [
            'yt-dlp',
            '--dump-json',
            f'https://www.youtube.com/watch?v={video_id}'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            check=True
        )
        
        video_data = json.loads(result.stdout)
        return parse_youtube_video(video_data)
        
    except Exception as e:
        console.print(f"  [red]Error obteniendo metadatos de YouTube: {str(e)}[/red]")
        return {}

def search_youtube_playlist(playlist_url: str, max_results: int = 50) -> List[Dict]:
    """
    Busca videos en una playlist de YouTube
    
    Args:
        playlist_url: URL de la playlist
        max_results: Máximo número de resultados
        
    Returns:
        Lista de diccionarios con metadatos de videos
    """
    console.print(f"  [blue]Buscando en playlist de YouTube: {playlist_url}[/blue]")
    
    try:
        cmd = [
            'yt-dlp',
            '--dump-json',
            '--flat-playlist',
            '--playlist-end', str(max_results),
            playlist_url
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            check=True
        )
        
        videos = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                try:
                    video_data = json.loads(line)
                    videos.append(parse_youtube_video(video_data))
                except json.JSONDecodeError:
                    continue
        
        console.print(f"  [green]✓ Playlist YouTube: {len(videos)} videos encontrados[/green]")
        return videos
        
    except Exception as e:
        console.print(f"  [red]✗ Error en playlist YouTube: {str(e)}[/red]")
        return []
