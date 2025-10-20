"""
Video Downloader usando yt-dlp
"""

import os
import subprocess
import tempfile
import time
from typing import Optional, Dict, Any
from rich.console import Console

from config import (
    TEMP_DIR, DOWNLOAD_TIMEOUT, MAX_DURATION, 
    YT_DLP_OPTIONS, REQUEST_DELAY
)

console = Console()

class VideoDownloader:
    """
    Descargador de videos usando yt-dlp
    """
    
    def __init__(self, temp_dir: str = TEMP_DIR):
        """
        Inicializa el descargador
        
        Args:
            temp_dir: Directorio temporal para descargas
        """
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)
        
    def download_temporal(self, url: str, max_duration: int = None) -> Optional[str]:
        """
        Descarga un video completo temporalmente
        
        Args:
            url: URL del video
            max_duration: Duración máxima en segundos
            
        Returns:
            Ruta al archivo descargado o None si falla
        """
        try:
            console.print(f"    [blue]Descargando: {url[:50]}...[/blue]")
            
            # Generar nombre de archivo único
            timestamp = int(time.time() * 1000)
            filename = f"temp_video_{timestamp}.%(ext)s"
            output_path = os.path.join(self.temp_dir, filename)
            
            # Construir comando yt-dlp ULTRA OPTIMIZADO para velocidad máxima
            cmd = [
                'yt-dlp',
                '--output', output_path,
                '--format', 'worst[height<=480]',  # ULTRA BAJA RESOLUCIÓN para velocidad máxima
                '--no-playlist',
                '--no-warnings',
                '--quiet',
                '--ignore-errors',
                '--no-check-certificate',
                '--concurrent-fragments', '1',  # Un fragmento a la vez para velocidad
                '--fragment-retries', '1',  # Menos reintentos
                '--retries', '1',  # Menos reintentos
                '--socket-timeout', '10',  # Timeout más corto
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            ]
            
            # Agregar límite de duración si se especifica
            if max_duration:
                cmd.extend(['--match-filter', f'duration <= {max_duration}'])
            else:
                cmd.extend(['--match-filter', f'duration <= {MAX_DURATION}'])
            
            cmd.append(url)
            
            # Ejecutar descarga
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=DOWNLOAD_TIMEOUT,
                check=True
            )
            
            # Buscar el archivo descargado
            downloaded_file = self._find_downloaded_file(output_path)
            if downloaded_file and os.path.exists(downloaded_file):
                console.print(f"    [green]OK - Descargado: {os.path.basename(downloaded_file)}[/green]")
                return downloaded_file
            else:
                console.print(f"    [red]ERROR - No se pudo encontrar el archivo descargado[/red]")
                return None
                
        except subprocess.TimeoutExpired:
            console.print(f"    [red]ERROR - Timeout en descarga[/red]")
            return None
        except subprocess.CalledProcessError as e:
            console.print(f"    [red]ERROR - Error en descarga: {e}[/red]")
            return None
        except Exception as e:
            console.print(f"    [red]ERROR - Error inesperado: {str(e)}[/red]")
            return None
        finally:
            # Delay entre descargas
            time.sleep(REQUEST_DELAY)
    
    def download_section(self, url: str, start: float, duration: float) -> Optional[str]:
        """
        Descarga una sección específica del video
        
        Args:
            url: URL del video
            start: Tiempo de inicio en segundos
            duration: Duración en segundos
            
        Returns:
            Ruta al archivo descargado o None si falla
        """
        try:
            console.print(f"    [blue]Descargando sección: {start}s-{start+duration}s[/blue]")
            
            # Generar nombre de archivo único
            timestamp = int(time.time() * 1000)
            filename = f"temp_section_{timestamp}.%(ext)s"
            output_path = os.path.join(self.temp_dir, filename)
            
            # Construir comando yt-dlp con segmento
            cmd = [
                'yt-dlp',
                '--output', output_path,
                '--format', 'best[height<=1080]',
                '--no-playlist',
                '--no-warnings',
                '--quiet',
                '--download-sections', f'*{start}:{start+duration}',
                url
            ]
            
            # Ejecutar descarga
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=DOWNLOAD_TIMEOUT,
                check=True
            )
            
            # Buscar el archivo descargado
            downloaded_file = self._find_downloaded_file(output_path)
            if downloaded_file and os.path.exists(downloaded_file):
                console.print(f"    [green]OK - Sección descargada: {os.path.basename(downloaded_file)}[/green]")
                return downloaded_file
            else:
                console.print(f"    [red]ERROR - No se pudo encontrar la sección descargada[/red]")
                return None
                
        except Exception as e:
            console.print(f"    [red]ERROR - Error descargando sección: {str(e)}[/red]")
            return None
    
    def download_thumbnail(self, url: str) -> Optional[str]:
        """
        Descarga solo el thumbnail del video
        
        Args:
            url: URL del video
            
        Returns:
            Ruta al thumbnail descargado o None si falla
        """
        try:
            console.print(f"    [blue]Descargando thumbnail: {url[:50]}...[/blue]")
            
            # Generar nombre de archivo único
            timestamp = int(time.time() * 1000)
            filename = f"temp_thumb_{timestamp}.%(ext)s"
            output_path = os.path.join(self.temp_dir, filename)
            
            # Construir comando yt-dlp para thumbnail
            cmd = [
                'yt-dlp',
                '--output', output_path,
                '--write-thumbnail',
                '--skip-download',
                '--no-playlist',
                '--no-warnings',
                '--quiet',
                url
            ]
            
            # Ejecutar descarga
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )
            
            # Buscar el thumbnail descargado
            thumbnail_file = self._find_downloaded_file(output_path)
            if thumbnail_file and os.path.exists(thumbnail_file):
                console.print(f"    [green]OK - Thumbnail descargado: {os.path.basename(thumbnail_file)}[/green]")
                return thumbnail_file
            else:
                console.print(f"    [red]ERROR - No se pudo encontrar el thumbnail[/red]")
                return None
                
        except Exception as e:
            console.print(f"    [red]ERROR - Error descargando thumbnail: {str(e)}[/red]")
            return None
    
    def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información del video sin descargarlo
        
        Args:
            url: URL del video
            
        Returns:
            Diccionario con información del video o None si falla
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
            
            import json
            return json.loads(result.stdout)
            
        except Exception as e:
            console.print(f"    [red]ERROR - Error obteniendo info: {str(e)}[/red]")
            return None
    
    def remove(self, file_path: str) -> bool:
        """
        Elimina un archivo temporal
        
        Args:
            file_path: Ruta del archivo a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                console.print(f"    [yellow]DELETED  Eliminado: {os.path.basename(file_path)}[/yellow]")
                return True
            return False
        except Exception as e:
            console.print(f"    [red]ERROR - Error eliminando archivo: {str(e)}[/red]")
            return False
    
    def cleanup(self) -> int:
        """
        Limpia todos los archivos temporales
        
        Returns:
            Número de archivos eliminados
        """
        try:
            count = 0
            for filename in os.listdir(self.temp_dir):
                if filename.startswith('temp_'):
                    file_path = os.path.join(self.temp_dir, filename)
                    try:
                        os.remove(file_path)
                        count += 1
                    except Exception:
                        continue
            
            if count > 0:
                console.print(f"    [yellow]DELETED  Limpiados {count} archivos temporales[/yellow]")
            
            return count
            
        except Exception as e:
            console.print(f"    [red]ERROR - Error en limpieza: {str(e)}[/red]")
            return 0
    
    def _find_downloaded_file(self, output_pattern: str) -> Optional[str]:
        """
        Busca el archivo descargado basado en el patrón de salida
        
        Args:
            output_pattern: Patrón de salida de yt-dlp
            
        Returns:
            Ruta al archivo encontrado o None
        """
        try:
            # Buscar archivos que coincidan con el patrón
            base_pattern = output_pattern.replace('%(ext)s', '*')
            import glob
            
            files = glob.glob(base_pattern)
            if files:
                # Retornar el archivo más reciente
                return max(files, key=os.path.getctime)
            
            return None
            
        except Exception:
            return None
    
    def get_temp_dir_size(self) -> int:
        """
        Obtiene el tamaño del directorio temporal en bytes
        
        Returns:
            Tamaño en bytes
        """
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(self.temp_dir):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
            return total_size
        except Exception:
            return 0
