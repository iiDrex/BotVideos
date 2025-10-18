"""
Utilidades para manejo de archivos
"""

import os
import shutil
import time
from typing import List, Optional
from rich.console import Console

console = Console()

def ensure_directory(path: str) -> bool:
    """
    Asegura que un directorio existe, lo crea si no existe
    
    Args:
        path: Ruta del directorio
        
    Returns:
        True si el directorio existe o se creó correctamente
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        console.print(f"    [red]Error creando directorio {path}: {str(e)}[/red]")
        return False

def cleanup_files(directory: str, pattern: str = "temp_*", max_age_hours: int = 24) -> int:
    """
    Limpia archivos temporales de un directorio
    
    Args:
        directory: Directorio a limpiar
        pattern: Patrón de archivos a eliminar
        max_age_hours: Edad máxima en horas
        
    Returns:
        Número de archivos eliminados
    """
    try:
        if not os.path.exists(directory):
            return 0
        
        import glob
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        deleted_count = 0
        
        # Buscar archivos que coincidan con el patrón
        search_pattern = os.path.join(directory, pattern)
        files = glob.glob(search_pattern)
        
        for file_path in files:
            try:
                # Verificar edad del archivo
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > max_age_seconds:
                    os.remove(file_path)
                    deleted_count += 1
                    console.print(f"    [yellow]🗑️  Eliminado: {os.path.basename(file_path)}[/yellow]")
            except Exception as e:
                console.print(f"    [yellow]Error eliminando {file_path}: {str(e)}[/yellow]")
                continue
        
        if deleted_count > 0:
            console.print(f"    [green]✓ Limpiados {deleted_count} archivos temporales[/green]")
        
        return deleted_count
        
    except Exception as e:
        console.print(f"    [red]Error en limpieza: {str(e)}[/red]")
        return 0

def get_file_size(file_path: str) -> int:
    """
    Obtiene el tamaño de un archivo en bytes
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        Tamaño en bytes o 0 si no existe
    """
    try:
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0
    except Exception:
        return 0

def get_directory_size(directory: str) -> int:
    """
    Obtiene el tamaño total de un directorio en bytes
    
    Args:
        directory: Ruta del directorio
        
    Returns:
        Tamaño total en bytes
    """
    try:
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
        return total_size
    except Exception:
        return 0

def format_file_size(size_bytes: int) -> str:
    """
    Formatea el tamaño de archivo en una cadena legible
    
    Args:
        size_bytes: Tamaño en bytes
        
    Returns:
        String formateado (ej: "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    i = 0
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def find_files_by_extension(directory: str, extensions: List[str]) -> List[str]:
    """
    Busca archivos por extensión en un directorio
    
    Args:
        directory: Directorio a buscar
        extensions: Lista de extensiones (ej: ['.mp4', '.avi'])
        
    Returns:
        Lista de rutas de archivos encontrados
    """
    try:
        import glob
        
        files = []
        for ext in extensions:
            pattern = os.path.join(directory, f"*{ext}")
            files.extend(glob.glob(pattern))
        
        return files
        
    except Exception as e:
        console.print(f"    [red]Error buscando archivos: {str(e)}[/red]")
        return []

def move_file(source: str, destination: str) -> bool:
    """
    Mueve un archivo de una ubicación a otra
    
    Args:
        source: Ruta de origen
        destination: Ruta de destino
        
    Returns:
        True si se movió correctamente
    """
    try:
        # Asegurar que el directorio de destino existe
        dest_dir = os.path.dirname(destination)
        ensure_directory(dest_dir)
        
        shutil.move(source, destination)
        return True
        
    except Exception as e:
        console.print(f"    [red]Error moviendo archivo: {str(e)}[/red]")
        return False

def copy_file(source: str, destination: str) -> bool:
    """
    Copia un archivo de una ubicación a otra
    
    Args:
        source: Ruta de origen
        destination: Ruta de destino
        
    Returns:
        True si se copió correctamente
    """
    try:
        # Asegurar que el directorio de destino existe
        dest_dir = os.path.dirname(destination)
        ensure_directory(dest_dir)
        
        shutil.copy2(source, destination)
        return True
        
    except Exception as e:
        console.print(f"    [red]Error copiando archivo: {str(e)}[/red]")
        return False

def delete_file(file_path: str) -> bool:
    """
    Elimina un archivo
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        True si se eliminó correctamente
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
        
    except Exception as e:
        console.print(f"    [red]Error eliminando archivo: {str(e)}[/red]")
        return False

def get_file_info(file_path: str) -> Optional[dict]:
    """
    Obtiene información detallada de un archivo
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        Diccionario con información del archivo o None si no existe
    """
    try:
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        
        return {
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'size_formatted': format_file_size(stat.st_size),
            'created': time.ctime(stat.st_ctime),
            'modified': time.ctime(stat.st_mtime),
            'accessed': time.ctime(stat.st_atime),
            'is_file': os.path.isfile(file_path),
            'is_directory': os.path.isdir(file_path)
        }
        
    except Exception as e:
        console.print(f"    [red]Error obteniendo info del archivo: {str(e)}[/red]")
        return None

def create_temp_file(prefix: str = "temp_", suffix: str = ".tmp") -> str:
    """
    Crea un archivo temporal
    
    Args:
        prefix: Prefijo del archivo
        suffix: Sufijo del archivo
        
    Returns:
        Ruta del archivo temporal creado
    """
    try:
        import tempfile
        
        # Crear archivo temporal
        fd, path = tempfile.mkstemp(prefix=prefix, suffix=suffix)
        os.close(fd)  # Cerrar el descriptor de archivo
        
        return path
        
    except Exception as e:
        console.print(f"    [red]Error creando archivo temporal: {str(e)}[/red]")
        return ""

def cleanup_temp_files(temp_dir: str) -> int:
    """
    Limpia todos los archivos temporales de un directorio
    
    Args:
        temp_dir: Directorio temporal
        
    Returns:
        Número de archivos eliminados
    """
    try:
        if not os.path.exists(temp_dir):
            return 0
        
        deleted_count = 0
        
        for filename in os.listdir(temp_dir):
            if filename.startswith('temp_'):
                file_path = os.path.join(temp_dir, filename)
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception:
                    continue
        
        if deleted_count > 0:
            console.print(f"    [green]✓ Limpiados {deleted_count} archivos temporales[/green]")
        
        return deleted_count
        
    except Exception as e:
        console.print(f"    [red]Error limpiando archivos temporales: {str(e)}[/red]")
        return 0
