"""
Utilidades para obtener metadatos de video usando ffprobe y yt-dlp
"""

import json
import subprocess
import time
from typing import Dict, Any, Optional
from rich.console import Console

from config import REQUEST_DELAY

console = Console()

def get_video_metadata(url_or_path: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene metadatos de un video usando yt-dlp y ffprobe
    
    Args:
        url_or_path: URL o ruta del archivo de video
        
    Returns:
        Diccionario con metadatos del video o None si falla
    """
    try:
        # Intentar con yt-dlp primero (para URLs)
        if url_or_path.startswith(('http://', 'https://')):
            metadata = get_metadata_with_ytdlp(url_or_path)
            if metadata:
                return metadata
        
        # Fallback a ffprobe (para archivos locales)
        metadata = get_metadata_with_ffprobe(url_or_path)
        if metadata:
            return metadata
        
        console.print(f"    [yellow]⚠️  No se pudieron obtener metadatos para: {url_or_path[:50]}...[/yellow]")
        return None
        
    except Exception as e:
        console.print(f"    [red]✗ Error obteniendo metadatos: {str(e)}[/red]")
        return None
    finally:
        # Delay entre requests
        time.sleep(REQUEST_DELAY)

def get_basic_duration_and_resolution(url: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene SOLO duración y resolución de forma ligera usando yt-dlp --print

    Args:
        url: URL del video (preferible YouTube/TikTok/Instagram)

    Returns:
        Diccionario con 'duration', 'width', 'height' o None si falla
    """
    try:
        if not (url.startswith('http://') or url.startswith('https://')):
            return None

        # yt-dlp permite imprimir campos específicos rápidamente
        cmd = [
            'yt-dlp',
            '--skip-download',
            '--no-warnings',
            '--quiet',
            '--print', '%(duration)s|%(width)s|%(height)s',
            url
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=20,
            check=True
        )

        line = result.stdout.strip().split('\n')[0] if result.stdout else ''
        if not line:
            return None

        parts = line.split('|')
        if len(parts) != 3:
            return None

        # Parsear valores con tolerancia a vacíos
        def _to_float(v):
            try:
                return float(v)
            except Exception:
                return 0.0

        def _to_int(v):
            try:
                return int(float(v))
            except Exception:
                return 0

        duration = _to_float(parts[0])
        width = _to_int(parts[1])
        height = _to_int(parts[2])

        # Si no se obtuvo nada útil, fallback a None
        if duration <= 0 and (width == 0 or height == 0):
            return None

        return {
            'duration': duration if duration > 0 else 0,
            'width': width,
            'height': height
        }

    except Exception:
        return None

def get_metadata_with_ytdlp(url: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene metadatos usando yt-dlp
    
    Args:
        url: URL del video
        
    Returns:
        Diccionario con metadatos o None si falla
    """
    try:
        cmd = [
            'yt-dlp',
            '--dump-json',
            '--no-warnings',
            '--quiet',
            url
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            check=True
        )
        
        if result.stdout.strip():
            data = json.loads(result.stdout)
            return parse_ytdlp_metadata(data)
        
        return None
        
    except subprocess.TimeoutExpired:
        console.print(f"    [yellow]Timeout obteniendo metadatos con yt-dlp[/yellow]")
        return None
    except subprocess.CalledProcessError as e:
        console.print(f"    [yellow]Error con yt-dlp: {e}[/yellow]")
        return None
    except json.JSONDecodeError:
        console.print(f"    [yellow]Error parseando JSON de yt-dlp[/yellow]")
        return None
    except Exception as e:
        console.print(f"    [yellow]Error inesperado con yt-dlp: {str(e)}[/yellow]")
        return None

def get_metadata_with_ffprobe(path: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene metadatos usando ffprobe
    
    Args:
        path: Ruta al archivo de video
        
    Returns:
        Diccionario con metadatos o None si falla
    """
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            check=True
        )
        
        if result.stdout.strip():
            data = json.loads(result.stdout)
            return parse_ffprobe_metadata(data)
        
        return None
        
    except subprocess.TimeoutExpired:
        console.print(f"    [yellow]Timeout obteniendo metadatos con ffprobe[/yellow]")
        return None
    except subprocess.CalledProcessError as e:
        console.print(f"    [yellow]Error con ffprobe: {e}[/yellow]")
        return None
    except json.JSONDecodeError:
        console.print(f"    [yellow]Error parseando JSON de ffprobe[/yellow]")
        return None
    except Exception as e:
        console.print(f"    [yellow]Error inesperado con ffprobe: {str(e)}[/yellow]")
        return None

def parse_ytdlp_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parsea metadatos de yt-dlp a formato estándar
    
    Args:
        data: Datos raw de yt-dlp
        
    Returns:
        Diccionario con metadatos parseados
    """
    try:
        # Obtener stream de video
        video_stream = None
        if 'formats' in data:
            for fmt in data['formats']:
                if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                    video_stream = fmt
                    break
        
        # Extraer información básica
        duration = data.get('duration', 0)
        width = data.get('width', 0)
        height = data.get('height', 0)
        
        # Si no hay width/height en el nivel superior, buscar en streams
        if not width or not height:
            if video_stream:
                width = video_stream.get('width', 0)
                height = video_stream.get('height', 0)
        
        return {
            'duration': float(duration) if duration else 0,
            'width': int(width) if width else 0,
            'height': int(height) if height else 0,
            'fps': data.get('fps', 0),
            'format': data.get('format', ''),
            'ext': data.get('ext', ''),
            'filesize': data.get('filesize', 0),
            'view_count': data.get('view_count', 0),
            'uploader': data.get('uploader', ''),
            'upload_date': data.get('upload_date', ''),
            'title': data.get('title', ''),
            'description': data.get('description', ''),
            'tags': data.get('tags', []),
            'thumbnail': data.get('thumbnail', ''),
            'webpage_url': data.get('webpage_url', ''),
            'id': data.get('id', ''),
            'platform': data.get('extractor', 'unknown'),
            'raw_data': data
        }
        
    except Exception as e:
        console.print(f"    [yellow]Error parseando metadatos de yt-dlp: {str(e)}[/yellow]")
        return {}

def parse_ffprobe_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parsea metadatos de ffprobe a formato estándar
    
    Args:
        data: Datos raw de ffprobe
        
    Returns:
        Diccionario con metadatos parseados
    """
    try:
        # Obtener información del formato
        format_info = data.get('format', {})
        duration = float(format_info.get('duration', 0))
        
        # Buscar stream de video
        video_stream = None
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'video':
                video_stream = stream
                break
        
        # Extraer dimensiones
        width = 0
        height = 0
        fps = 0
        
        if video_stream:
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            
            # Calcular FPS
            fps_str = video_stream.get('r_frame_rate', '0/1')
            if '/' in fps_str:
                num, den = fps_str.split('/')
                if int(den) > 0:
                    fps = float(num) / float(den)
        
        return {
            'duration': duration,
            'width': width,
            'height': height,
            'fps': fps,
            'format': format_info.get('format_name', ''),
            'ext': format_info.get('filename', '').split('.')[-1] if '.' in format_info.get('filename', '') else '',
            'filesize': int(format_info.get('size', 0)),
            'view_count': 0,
            'uploader': '',
            'upload_date': '',
            'title': format_info.get('tags', {}).get('title', ''),
            'description': format_info.get('tags', {}).get('comment', ''),
            'tags': [],
            'thumbnail': '',
            'webpage_url': '',
            'id': '',
            'platform': 'local',
            'raw_data': data
        }
        
    except Exception as e:
        console.print(f"    [yellow]Error parseando metadatos de ffprobe: {str(e)}[/yellow]")
        return {}

def get_video_duration(url_or_path: str) -> float:
    """
    Obtiene solo la duración de un video
    
    Args:
        url_or_path: URL o ruta del archivo
        
    Returns:
        Duración en segundos o 0 si falla
    """
    metadata = get_video_metadata(url_or_path)
    return metadata.get('duration', 0) if metadata else 0

def get_video_dimensions(url_or_path: str) -> tuple:
    """
    Obtiene las dimensiones de un video
    
    Args:
        url_or_path: URL o ruta del archivo
        
    Returns:
        Tupla (width, height) o (0, 0) si falla
    """
    metadata = get_video_metadata(url_or_path)
    if metadata:
        return (metadata.get('width', 0), metadata.get('height', 0))
    return (0, 0)

def is_video_vertical(url_or_path: str) -> bool:
    """
    Verifica si un video es vertical
    
    Args:
        url_or_path: URL o ruta del archivo
        
    Returns:
        True si es vertical, False en caso contrario
    """
    width, height = get_video_dimensions(url_or_path)
    return height > width if width > 0 and height > 0 else False

def get_video_info_summary(url_or_path: str) -> str:
    """
    Obtiene un resumen de información del video
    
    Args:
        url_or_path: URL o ruta del archivo
        
    Returns:
        String con resumen del video
    """
    metadata = get_video_metadata(url_or_path)
    if not metadata:
        return "Información no disponible"
    
    duration = metadata.get('duration', 0)
    width = metadata.get('width', 0)
    height = metadata.get('height', 0)
    fps = metadata.get('fps', 0)
    
    return f"{width}x{height} @ {fps:.1f}fps, {duration:.1f}s"
