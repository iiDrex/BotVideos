"""
Face Detector usando YOLOv8 y modelos adicionales
"""

import cv2
import numpy as np
import time
from typing import List, Dict, Any, Optional
from rich.console import Console

from config import FACE_CONFIDENCE, USE_GPU, MODEL_CONFIGS

console = Console()

class FaceDetector:
    """
    Detector de rostros usando YOLOv8 y modelos adicionales
    """
    
    def __init__(self, model_path: str = None, use_gpu: bool = None):
        """
        Inicializa el detector de rostros
        
        Args:
            model_path: Ruta al modelo YOLO
            use_gpu: Usar GPU si está disponible
        """
        self.model_path = model_path or MODEL_CONFIGS['yolo_face']['model_path']
        self.use_gpu = use_gpu if use_gpu is not None else USE_GPU
        self.confidence_threshold = FACE_CONFIDENCE
        
        # Inicializar modelo YOLO
        self.model = None
        self._load_model()
        
    def _load_model(self):
        """Carga el modelo YOLO"""
        try:
            from ultralytics import YOLO
            
            console.print(f"    [blue]Cargando modelo YOLO: {self.model_path}[/blue]")
            self.model = YOLO(self.model_path)
            
            # Configurar dispositivo
            device = 'cuda' if self.use_gpu else 'cpu'
            self.model.to(device)
            
            console.print(f"    [green]✓ Modelo YOLO cargado en {device}[/green]")
            
        except Exception as e:
            console.print(f"    [red]✗ Error cargando modelo YOLO: {str(e)}[/red]")
            self.model = None
    
    def detect_faces_on_frame(self, frame: np.ndarray) -> List[Dict]:
        """
        Detecta rostros en un frame
        
        Args:
            frame: Frame de video como array numpy
            
        Returns:
            Lista de diccionarios con información de rostros detectados
        """
        if self.model is None:
            return []
        
        try:
            # Ejecutar detección
            results = self.model(frame, conf=self.confidence_threshold, verbose=False)
            
            faces = []
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        # Obtener coordenadas y confianza
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # Filtrar solo rostros (clase 0 en YOLO)
                        if class_id == 0 and confidence >= self.confidence_threshold:
                            faces.append({
                                'bbox': [int(x1), int(y1), int(x2-x1), int(y2-y1)],
                                'confidence': float(confidence),
                                'class': 'face'
                            })
            
            return faces
            
        except Exception as e:
            console.print(f"    [red]Error detectando rostros en frame: {str(e)}[/red]")
            return []
    
    def detect_faces_on_video(self, path: str, sample_strategy: dict) -> List[Dict]:
        """
        Detecta rostros en un video completo usando muestreo optimizado
        
        Args:
            path: Ruta al archivo de video
            sample_strategy: Estrategia de muestreo
            
        Returns:
            Lista de detecciones con información de frame
        """
        if self.model is None:
            return []
        
        try:
            console.print(f"    [blue]Analizando rostros en video: {os.path.basename(path)}[/blue]")
            
            # Abrir video
            cap = cv2.VideoCapture(path)
            if not cap.isOpened():
                console.print(f"    [red]✗ No se pudo abrir el video: {path}[/red]")
                return []
            
            # Obtener propiedades del video
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            # Calcular estrategia de muestreo
            sample_rate = self._calculate_sample_rate(duration, sample_strategy, fps)
            
            console.print(f"    [blue]Video: {duration:.1f}s, {total_frames} frames, {fps:.1f} fps[/blue]")
            console.print(f"    [blue]Muestreo: cada {sample_rate} frames[/blue]")
            
            detections = []
            frame_count = 0
            processed_frames = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Aplicar muestreo
                if frame_count % sample_rate == 0:
                    faces = self.detect_faces_on_frame(frame)
                    
                    if faces:
                        for face in faces:
                            face['frame'] = frame_count
                            face['timestamp'] = frame_count / fps if fps > 0 else 0
                            detections.append(face)
                        
                        # Si detectamos rostros, podemos parar aquí (optimización)
                        if len(detections) > 0:
                            console.print(f"    [yellow]⚠️  Rostros detectados en frame {frame_count}[/yellow]")
                            break
                    
                    processed_frames += 1
                
                frame_count += 1
            
            cap.release()
            
            console.print(f"    [green]✓ Procesados {processed_frames} frames, {len(detections)} rostros detectados[/green]")
            return detections
            
        except Exception as e:
            console.print(f"    [red]✗ Error analizando video: {str(e)}[/red]")
            return []
    
    def _calculate_sample_rate(self, duration: float, sample_strategy: dict, fps: float) -> int:
        """
        Calcula la tasa de muestreo basada en la duración del video
        
        Args:
            duration: Duración del video en segundos
            sample_strategy: Estrategia de muestreo
            fps: Frames por segundo del video
            
        Returns:
            Número de frames a saltar entre muestras
        """
        if duration <= sample_strategy.get('short', {}).get('max_dur', 60):
            fps_factor = sample_strategy.get('short', {}).get('fps_factor', 0.5)
        elif duration <= sample_strategy.get('medium', {}).get('max_dur', 300):
            fps_factor = sample_strategy.get('medium', {}).get('fps_factor', 1.0)
        else:
            fps_factor = sample_strategy.get('long', {}).get('fps_factor', 2.0)
        
        # Calcular frames a saltar
        sample_rate = max(1, int(fps * fps_factor))
        return sample_rate
    
    def detect_faces_with_confirmation(self, path: str, sample_strategy: dict) -> List[Dict]:
        """
        Detecta rostros con ventana de confirmación para reducir falsos positivos
        
        Args:
            path: Ruta al archivo de video
            sample_strategy: Estrategia de muestreo
            
        Returns:
            Lista de detecciones confirmadas
        """
        try:
            # Detección inicial
            initial_detections = self.detect_faces_on_video(path, sample_strategy)
            
            if not initial_detections:
                return []
            
            # Agrupar detecciones por proximidad temporal
            confirmed_detections = []
            window_size = 5  # Ventana de confirmación
            
            for detection in initial_detections:
                frame_num = detection['frame']
                
                # Verificar frames cercanos
                nearby_faces = self._check_nearby_frames(path, frame_num, window_size)
                
                if nearby_faces:
                    detection['confirmed'] = True
                    detection['nearby_count'] = len(nearby_faces)
                    confirmed_detections.append(detection)
            
            return confirmed_detections
            
        except Exception as e:
            console.print(f"    [red]Error en detección con confirmación: {str(e)}[/red]")
            return initial_detections
    
    def _check_nearby_frames(self, path: str, center_frame: int, window_size: int) -> List[Dict]:
        """
        Verifica frames cercanos para confirmar detecciones
        
        Args:
            path: Ruta al video
            center_frame: Frame central
            window_size: Tamaño de la ventana
            
        Returns:
            Lista de detecciones en frames cercanos
        """
        try:
            cap = cv2.VideoCapture(path)
            if not cap.isOpened():
                return []
            
            nearby_detections = []
            start_frame = max(0, center_frame - window_size)
            end_frame = center_frame + window_size
            
            # Saltar al frame inicial
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            for frame_num in range(start_frame, end_frame + 1):
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_num != center_frame:  # No revisar el frame central otra vez
                    faces = self.detect_faces_on_frame(frame)
                    if faces:
                        for face in faces:
                            face['frame'] = frame_num
                            nearby_detections.append(face)
            
            cap.release()
            return nearby_detections
            
        except Exception as e:
            console.print(f"    [yellow]Error verificando frames cercanos: {str(e)}[/yellow]")
            return []
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtiene información del modelo cargado
        
        Returns:
            Diccionario con información del modelo
        """
        if self.model is None:
            return {'loaded': False, 'error': 'Modelo no cargado'}
        
        try:
            return {
                'loaded': True,
                'model_path': self.model_path,
                'device': 'cuda' if self.use_gpu else 'cpu',
                'confidence_threshold': self.confidence_threshold,
                'model_type': 'YOLOv8'
            }
        except Exception as e:
            return {'loaded': False, 'error': str(e)}
