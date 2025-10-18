"""
Simple Cleaner para limpieza de archivos temporales
"""

import os
import time
from typing import List, Optional
from rich.console import Console

from utils.file_utils import cleanup_files, get_directory_size, format_file_size

console = Console()

class SimpleCleaner:
    """
    Limpiador simple para archivos temporales
    """
    
    def __init__(self, temp_dir: str):
        """
        Inicializa el limpiador
        
        Args:
            temp_dir: Directorio temporal a limpiar
        """
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)
    
    def cleanup(self, max_age_hours: int = 1) -> int:
        """
        Limpia archivos temporales del directorio
        
        Args:
            max_age_hours: Edad máxima en horas para archivos temporales
            
        Returns:
            Número de archivos eliminados
        """
        try:
            console.print(f"    [blue]Limpiando archivos temporales en: {self.temp_dir}[/blue]")
            
            # Obtener tamaño antes de la limpieza
            size_before = get_directory_size(self.temp_dir)
            
            # Limpiar archivos temporales
            deleted_count = cleanup_files(
                self.temp_dir, 
                pattern="temp_*", 
                max_age_hours=max_age_hours
            )
            
            # Obtener tamaño después de la limpieza
            size_after = get_directory_size(self.temp_dir)
            size_freed = size_before - size_after
            
            if deleted_count > 0:
                console.print(f"    [green]✓ Limpieza completada: {deleted_count} archivos, {format_file_size(size_freed)} liberados[/green]")
            else:
                console.print(f"    [yellow]No se encontraron archivos temporales para limpiar[/yellow]")
            
            return deleted_count
            
        except Exception as e:
            console.print(f"    [red]Error en limpieza: {str(e)}[/red]")
            return 0
    
    def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """
        Limpia archivos antiguos del directorio
        
        Args:
            max_age_hours: Edad máxima en horas
            
        Returns:
            Número de archivos eliminados
        """
        try:
            console.print(f"    [blue]Limpiando archivos antiguos (>{max_age_hours}h) en: {self.temp_dir}[/blue]")
            
            deleted_count = 0
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for filename in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, filename)
                
                try:
                    if os.path.isfile(file_path):
                        file_age = current_time - os.path.getmtime(file_path)
                        if file_age > max_age_seconds:
                            os.remove(file_path)
                            deleted_count += 1
                            console.print(f"    [yellow]🗑️  Eliminado: {filename}[/yellow]")
                            
                except Exception as e:
                    console.print(f"    [yellow]Error eliminando {filename}: {str(e)}[/yellow]")
                    continue
            
            if deleted_count > 0:
                console.print(f"    [green]✓ Limpieza de archivos antiguos completada: {deleted_count} archivos[/green]")
            else:
                console.print(f"    [yellow]No se encontraron archivos antiguos para limpiar[/yellow]")
            
            return deleted_count
            
        except Exception as e:
            console.print(f"    [red]Error limpiando archivos antiguos: {str(e)}[/red]")
            return 0
    
    def cleanup_by_size(self, max_size_mb: int = 100) -> int:
        """
        Limpia archivos si el directorio excede un tamaño máximo
        
        Args:
            max_size_mb: Tamaño máximo en MB
            
        Returns:
            Número de archivos eliminados
        """
        try:
            current_size = get_directory_size(self.temp_dir)
            max_size_bytes = max_size_mb * 1024 * 1024
            
            if current_size <= max_size_bytes:
                console.print(f"    [yellow]Tamaño del directorio ({format_file_size(current_size)}) está dentro del límite[/yellow]")
                return 0
            
            console.print(f"    [blue]Tamaño del directorio ({format_file_size(current_size)}) excede el límite ({max_size_mb}MB)[/blue]")
            
            # Obtener lista de archivos ordenados por fecha de modificación
            files = []
            for filename in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, filename)
                if os.path.isfile(file_path):
                    files.append((file_path, os.path.getmtime(file_path)))
            
            # Ordenar por fecha de modificación (más antiguos primero)
            files.sort(key=lambda x: x[1])
            
            deleted_count = 0
            current_size = get_directory_size(self.temp_dir)
            
            for file_path, _ in files:
                if current_size <= max_size_bytes:
                    break
                
                try:
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    current_size -= file_size
                    deleted_count += 1
                    console.print(f"    [yellow]🗑️  Eliminado: {os.path.basename(file_path)} ({format_file_size(file_size)})[/yellow]")
                    
                except Exception as e:
                    console.print(f"    [yellow]Error eliminando {file_path}: {str(e)}[/yellow]")
                    continue
            
            if deleted_count > 0:
                console.print(f"    [green]✓ Limpieza por tamaño completada: {deleted_count} archivos, {format_file_size(get_directory_size(self.temp_dir))} restante[/green]")
            
            return deleted_count
            
        except Exception as e:
            console.print(f"    [red]Error en limpieza por tamaño: {str(e)}[/red]")
            return 0
    
    def get_status(self) -> dict:
        """
        Obtiene el estado del directorio temporal
        
        Returns:
            Diccionario con información del directorio
        """
        try:
            current_size = get_directory_size(self.temp_dir)
            file_count = len([f for f in os.listdir(self.temp_dir) if os.path.isfile(os.path.join(self.temp_dir, f))])
            
            return {
                'directory': self.temp_dir,
                'size_bytes': current_size,
                'size_formatted': format_file_size(current_size),
                'file_count': file_count,
                'exists': os.path.exists(self.temp_dir)
            }
            
        except Exception as e:
            console.print(f"    [red]Error obteniendo estado: {str(e)}[/red]")
            return {
                'directory': self.temp_dir,
                'size_bytes': 0,
                'size_formatted': '0 B',
                'file_count': 0,
                'exists': False,
                'error': str(e)
            }
    
    def force_cleanup(self) -> int:
        """
        Fuerza la limpieza de todos los archivos del directorio
        
        Returns:
            Número de archivos eliminados
        """
        try:
            console.print(f"    [blue]Forzando limpieza completa de: {self.temp_dir}[/blue]")
            
            deleted_count = 0
            
            for filename in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, filename)
                
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        deleted_count += 1
                        console.print(f"    [yellow]🗑️  Eliminado: {filename}[/yellow]")
                    elif os.path.isdir(file_path):
                        import shutil
                        shutil.rmtree(file_path)
                        deleted_count += 1
                        console.print(f"    [yellow]🗑️  Eliminado directorio: {filename}[/yellow]")
                        
                except Exception as e:
                    console.print(f"    [yellow]Error eliminando {filename}: {str(e)}[/yellow]")
                    continue
            
            if deleted_count > 0:
                console.print(f"    [green]✓ Limpieza forzada completada: {deleted_count} elementos[/green]")
            else:
                console.print(f"    [yellow]No se encontraron elementos para limpiar[/yellow]")
            
            return deleted_count
            
        except Exception as e:
            console.print(f"    [red]Error en limpieza forzada: {str(e)}[/red]")
            return 0
