"""
Enhanced Video Analyzer - Análisis optimizado de videos completos
"""

import time
import os
from typing import Dict, List, Any
from rich.console import Console

from .face_detector import FaceDetector
from .text_detector import TextDetector
from config import VIDEO_SAMPLE_STRATEGY, ANALYSIS_CONFIG

console = Console()

class EnhancedVideoAnalyzer:
    """
    Analizador de video optimizado que combina detección de rostros y texto
    """
    
    def __init__(self, config: dict):
        """
        Inicializa el analizador de video
        
        Args:
            config: Configuración del usuario
        """
        self.config = config
        self.face_detector = FaceDetector()
        self.text_detector = TextDetector(use_easyocr=True)
        
        # Configuración de análisis
        self.sample_strategy = VIDEO_SAMPLE_STRATEGY
        self.analysis_config = ANALYSIS_CONFIG
        
        console.print("    [green]✓ Analizador de video inicializado[/green]")
    
    def analyze_video(self, path: str) -> Dict:
        """
        Analiza un video completo de forma optimizada
        
        Args:
            path: Ruta al archivo de video
            
        Returns:
            Diccionario con resultados del análisis
        """
        start_time = time.time()
        
        try:
            console.print(f"    [blue]Analizando video: {os.path.basename(path)}[/blue]")
            
            # Verificar que el archivo existe
            if not os.path.exists(path):
                return self._create_error_result("Archivo no encontrado")
            
            # Obtener información del video
            video_info = self._get_video_info(path)
            if not video_info:
                return self._create_error_result("No se pudo obtener información del video")
            
            # Calcular estrategia de muestreo
            sample_strategy = self._calculate_sample_strategy(video_info['duration'])
            
            # Análisis de rostros
            face_analysis = self._analyze_faces(path, sample_strategy)
            
            # Análisis de texto (solo si no hay rostros)
            text_analysis = {}
            if not face_analysis.get('has_face', False):
                text_analysis = self._analyze_text(path, sample_strategy)
            else:
                console.print("    [yellow]⚠️  Saltando análisis de texto (rostros detectados)[/yellow]")
            
            # Calcular tiempo de análisis
            analysis_time = int((time.time() - start_time) * 1000)
            
            # Crear resultado final
            result = {
                'has_face': face_analysis.get('has_face', False),
                'face_details': face_analysis.get('details', []),
                'has_text': text_analysis.get('has_text', False),
                'text_details': text_analysis.get('details', []),
                'analysis_time_ms': analysis_time,
                'video_info': video_info,
                'sample_strategy': sample_strategy
            }
            
            console.print(f"    [green]✓ Análisis completado en {analysis_time}ms[/green]")
            return result
            
        except Exception as e:
            console.print(f"    [red]✗ Error analizando video: {str(e)}[/red]")
            return self._create_error_result(str(e))
    
    def _get_video_info(self, path: str) -> Dict:
        """
        Obtiene información básica del video
        
        Args:
            path: Ruta al archivo de video
            
        Returns:
            Diccionario con información del video
        """
        try:
            import cv2
            
            cap = cv2.VideoCapture(path)
            if not cap.isOpened():
                return None
            
            # Obtener propiedades
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            return {
                'duration': duration,
                'fps': fps,
                'frame_count': frame_count,
                'width': width,
                'height': height,
                'resolution': f"{width}x{height}",
                'is_vertical': height > width
            }
            
        except Exception as e:
            console.print(f"    [yellow]Error obteniendo info del video: {str(e)}[/yellow]")
            return None
    
    def _calculate_sample_strategy(self, duration: float) -> Dict:
        """
        Calcula la estrategia de muestreo basada en la duración
        
        Args:
            duration: Duración del video en segundos
            
        Returns:
            Estrategia de muestreo
        """
        if duration <= self.sample_strategy['short']['max_dur']:
            return {
                'type': 'short',
                'max_duration': self.sample_strategy['short']['max_dur'],
                'fps_factor': self.sample_strategy['short']['fps_factor']
            }
        elif duration <= self.sample_strategy['medium']['max_dur']:
            return {
                'type': 'medium',
                'max_duration': self.sample_strategy['medium']['max_dur'],
                'fps_factor': self.sample_strategy['medium']['fps_factor']
            }
        else:
            return {
                'type': 'long',
                'fps_factor': self.sample_strategy['long']['fps_factor']
            }
    
    def _analyze_faces(self, path: str, sample_strategy: Dict) -> Dict:
        """
        Analiza rostros en el video
        
        Args:
            path: Ruta al archivo de video
            sample_strategy: Estrategia de muestreo
            
        Returns:
            Resultado del análisis de rostros
        """
        try:
            console.print("    [blue]Detectando rostros...[/blue]")
            
            # Usar detección con confirmación si está habilitada
            if self.analysis_config.get('enable_sliding_window', True):
                face_detections = self.face_detector.detect_faces_with_confirmation(path, sample_strategy)
            else:
                face_detections = self.face_detector.detect_faces_on_video(path, sample_strategy)
            
            has_face = len(face_detections) > 0
            
            return {
                'has_face': has_face,
                'details': face_detections,
                'count': len(face_detections)
            }
            
        except Exception as e:
            console.print(f"    [red]Error analizando rostros: {str(e)}[/red]")
            return {
                'has_face': False,
                'details': [],
                'count': 0,
                'error': str(e)
            }
    
    def _analyze_text(self, path: str, sample_strategy: Dict) -> Dict:
        """
        Analiza texto en el video
        
        Args:
            path: Ruta al archivo de video
            sample_strategy: Estrategia de muestreo
            
        Returns:
            Resultado del análisis de texto
        """
        try:
            console.print("    [blue]Detectando texto...[/blue]")
            
            text_detections = self.text_detector.detect_text_on_video(path, sample_strategy)
            has_text = len(text_detections) > 0
            
            return {
                'has_text': has_text,
                'details': text_detections,
                'count': len(text_detections)
            }
            
        except Exception as e:
            console.print(f"    [red]Error analizando texto: {str(e)}[/red]")
            return {
                'has_text': False,
                'details': [],
                'count': 0,
                'error': str(e)
            }
    
    def _create_error_result(self, error_message: str) -> Dict:
        """
        Crea un resultado de error
        
        Args:
            error_message: Mensaje de error
            
        Returns:
            Diccionario con resultado de error
        """
        return {
            'has_face': False,
            'face_details': [],
            'has_text': False,
            'text_details': [],
            'analysis_time_ms': 0,
            'error': error_message
        }
    
    def get_analyzer_info(self) -> Dict:
        """
        Obtiene información del analizador
        
        Returns:
            Diccionario con información del analizador
        """
        return {
            'face_detector': self.face_detector.get_model_info(),
            'text_detector': self.text_detector.get_detector_info(),
            'sample_strategy': self.sample_strategy,
            'analysis_config': self.analysis_config
        }
    
    def analyze_frame(self, frame_path: str) -> Dict:
        """
        Analiza un frame individual
        
        Args:
            frame_path: Ruta al archivo de imagen
            
        Returns:
            Resultado del análisis del frame
        """
        try:
            import cv2
            
            frame = cv2.imread(frame_path)
            if frame is None:
                return self._create_error_result("No se pudo cargar el frame")
            
            # Análisis de rostros
            face_detections = self.face_detector.detect_faces_on_frame(frame)
            
            # Análisis de texto
            text_detections = self.text_detector.detect_text_on_frame(frame)
            
            return {
                'has_face': len(face_detections) > 0,
                'face_details': face_detections,
                'has_text': len(text_detections) > 0,
                'text_details': text_detections,
                'analysis_time_ms': 0
            }
            
        except Exception as e:
            return self._create_error_result(str(e))
    
    def batch_analyze(self, video_paths: List[str]) -> List[Dict]:
        """
        Analiza múltiples videos en lote
        
        Args:
            video_paths: Lista de rutas de videos
            
        Returns:
            Lista de resultados de análisis
        """
        results = []
        
        for i, path in enumerate(video_paths, 1):
            console.print(f"    [blue]Analizando video {i}/{len(video_paths)}: {os.path.basename(path)}[/blue]")
            
            result = self.analyze_video(path)
            result['video_path'] = path
            result['batch_index'] = i
            
            results.append(result)
        
        return results
