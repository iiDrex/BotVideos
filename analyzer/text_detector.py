"""
Text Detector usando EasyOCR y Tesseract
"""

import cv2
import numpy as np
import time
import os
from typing import List, Dict, Any, Optional
from rich.console import Console

from config import OCR_CONFIDENCE, MIN_TEXT_LENGTH, TESSERACT_CMD, USE_GPU, MODEL_CONFIGS

console = Console()

class TextDetector:
    """
    Detector de texto usando EasyOCR y Tesseract
    """
    
    def __init__(self, use_easyocr: bool = True):
        """
        Inicializa el detector de texto
        
        Args:
            use_easyocr: Usar EasyOCR además de Tesseract
        """
        self.use_easyocr = use_easyocr
        self.confidence_threshold = OCR_CONFIDENCE
        self.min_text_length = MIN_TEXT_LENGTH
        
        # Configurar Tesseract
        self.tesseract_cmd = TESSERACT_CMD
        self._setup_tesseract()
        
        # Inicializar EasyOCR si se solicita
        self.easyocr_reader = None
        if use_easyocr:
            self._setup_easyocr()
    
    def _setup_tesseract(self):
        """Configura Tesseract OCR"""
        try:
            import pytesseract
            
            # Configurar comando de Tesseract
            if os.path.exists(self.tesseract_cmd):
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
                console.print(f"    [green]✓ Tesseract configurado: {self.tesseract_cmd}[/green]")
            else:
                console.print(f"    [yellow]⚠️  Tesseract no encontrado en: {self.tesseract_cmd}[/yellow]")
                console.print("    [yellow]  Asegúrate de instalar Tesseract OCR[/yellow]")
                
        except Exception as e:
            console.print(f"    [red]✗ Error configurando Tesseract: {str(e)}[/red]")
    
    def _setup_easyocr(self):
        """Configura EasyOCR"""
        try:
            import easyocr
            
            console.print("    [blue]Inicializando EasyOCR...[/blue]")
            
            # Configurar idiomas
            languages = MODEL_CONFIGS['easyocr']['languages']
            gpu = MODEL_CONFIGS['easyocr']['gpu'] and USE_GPU
            model_dir = MODEL_CONFIGS['easyocr']['model_storage_directory']
            
            # Crear directorio de modelos si no existe
            os.makedirs(model_dir, exist_ok=True)
            
            self.easyocr_reader = easyocr.Reader(
                languages, 
                gpu=gpu,
                model_storage_directory=model_dir
            )
            
            console.print(f"    [green]✓ EasyOCR inicializado (GPU: {gpu})[/green]")
            
        except Exception as e:
            console.print(f"    [red]✗ Error inicializando EasyOCR: {str(e)}[/red]")
            self.easyocr_reader = None
    
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Preprocesa un frame para mejorar la detección de texto
        
        Args:
            frame: Frame de video
            
        Returns:
            Frame preprocesado
        """
        try:
            # Convertir a escala de grises
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame.copy()
            
            # Aplicar filtro bilateral para reducir ruido
            filtered = cv2.bilateralFilter(gray, 9, 75, 75)
            
            # Aplicar umbralización adaptativa
            thresh = cv2.adaptiveThreshold(
                filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Redimensionar si es muy grande
            height, width = thresh.shape
            if width > 1920:
                scale = 1920 / width
                new_width = 1920
                new_height = int(height * scale)
                thresh = cv2.resize(thresh, (new_width, new_height))
            
            return thresh
            
        except Exception as e:
            console.print(f"    [yellow]Error en preprocesamiento: {str(e)}[/yellow]")
            return frame
    
    def detect_text_with_tesseract(self, frame: np.ndarray) -> List[Dict]:
        """
        Detecta texto usando Tesseract
        
        Args:
            frame: Frame de video
            
        Returns:
            Lista de detecciones de texto
        """
        try:
            import pytesseract
            
            # Preprocesar frame
            processed_frame = self.preprocess_frame(frame)
            
            # Configuración de Tesseract
            config = MODEL_CONFIGS['tesseract']['config']
            lang = MODEL_CONFIGS['tesseract']['lang']
            
            # Obtener datos de texto con coordenadas
            data = pytesseract.image_to_data(
                processed_frame, 
                config=config,
                lang=lang,
                output_type=pytesseract.Output.DICT
            )
            
            detections = []
            n_boxes = len(data['level'])
            
            for i in range(n_boxes):
                # Filtrar por confianza
                confidence = int(data['conf'][i])
                if confidence < self.confidence_threshold * 100:
                    continue
                
                # Obtener texto y coordenadas
                text = data['text'][i].strip()
                if len(text) < self.min_text_length:
                    continue
                
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                
                if w > 0 and h > 0:  # Validar dimensiones
                    detections.append({
                        'text': text,
                        'bbox': [x, y, w, h],
                        'confidence': confidence / 100.0,
                        'method': 'tesseract'
                    })
            
            return detections
            
        except Exception as e:
            console.print(f"    [red]Error con Tesseract: {str(e)}[/red]")
            return []
    
    def detect_text_with_easyocr(self, frame: np.ndarray) -> List[Dict]:
        """
        Detecta texto usando EasyOCR
        
        Args:
            frame: Frame de video
            
        Returns:
            Lista de detecciones de texto
        """
        if self.easyocr_reader is None:
            return []
        
        try:
            # Preprocesar frame
            processed_frame = self.preprocess_frame(frame)
            
            # Ejecutar detección
            results = self.easyocr_reader.readtext(processed_frame)
            
            detections = []
            for (bbox, text, confidence) in results:
                # Filtrar por confianza y longitud
                if confidence < self.confidence_threshold:
                    continue
                
                if len(text.strip()) < self.min_text_length:
                    continue
                
                # Convertir bbox a formato estándar
                x1, y1 = bbox[0]
                x2, y2 = bbox[2]
                x, y, w, h = int(x1), int(y1), int(x2-x1), int(y2-y1)
                
                detections.append({
                    'text': text.strip(),
                    'bbox': [x, y, w, h],
                    'confidence': confidence,
                    'method': 'easyocr'
                })
            
            return detections
            
        except Exception as e:
            console.print(f"    [red]Error con EasyOCR: {str(e)}[/red]")
            return []
    
    def detect_text_on_frame(self, frame: np.ndarray) -> List[Dict]:
        """
        Detecta texto en un frame usando ambos métodos
        
        Args:
            frame: Frame de video
            
        Returns:
            Lista de detecciones de texto
        """
        all_detections = []
        
        # Detectar con Tesseract
        tesseract_detections = self.detect_text_with_tesseract(frame)
        all_detections.extend(tesseract_detections)
        
        # Detectar con EasyOCR si está disponible
        if self.easyocr_reader is not None:
            easyocr_detections = self.detect_text_with_easyocr(frame)
            all_detections.extend(easyocr_detections)
        
        # Eliminar duplicados basados en proximidad espacial
        unique_detections = self._remove_duplicate_detections(all_detections)
        
        return unique_detections
    
    def detect_text_on_video(self, path: str, sample_strategy: dict) -> List[Dict]:
        """
        Detecta texto en un video completo usando muestreo optimizado
        
        Args:
            path: Ruta al archivo de video
            sample_strategy: Estrategia de muestreo
            
        Returns:
            Lista de detecciones con información de frame
        """
        try:
            console.print(f"    [blue]Analizando texto en video: {os.path.basename(path)}[/blue]")
            
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
                    text_detections = self.detect_text_on_frame(frame)
                    
                    if text_detections:
                        for detection in text_detections:
                            detection['frame'] = frame_count
                            detection['timestamp'] = frame_count / fps if fps > 0 else 0
                            detections.append(detection)
                    
                    processed_frames += 1
                
                frame_count += 1
                
                # Limitar procesamiento para videos muy largos
                if processed_frames > 100:  # Máximo 100 frames procesados
                    break
            
            cap.release()
            
            console.print(f"    [green]✓ Procesados {processed_frames} frames, {len(detections)} textos detectados[/green]")
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
    
    def _remove_duplicate_detections(self, detections: List[Dict]) -> List[Dict]:
        """
        Elimina detecciones duplicadas basadas en proximidad espacial
        
        Args:
            detections: Lista de detecciones
            
        Returns:
            Lista de detecciones únicas
        """
        if not detections:
            return []
        
        unique_detections = []
        
        for detection in detections:
            is_duplicate = False
            bbox1 = detection['bbox']
            
            for unique_detection in unique_detections:
                bbox2 = unique_detection['bbox']
                
                # Calcular intersección
                x1, y1, w1, h1 = bbox1
                x2, y2, w2, h2 = bbox2
                
                # Calcular área de intersección
                x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
                y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
                overlap_area = x_overlap * y_overlap
                
                # Calcular áreas
                area1 = w1 * h1
                area2 = w2 * h2
                
                # Si hay superposición significativa, es duplicado
                if overlap_area > 0.5 * min(area1, area2):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_detections.append(detection)
        
        return unique_detections
    
    def get_detector_info(self) -> Dict[str, Any]:
        """
        Obtiene información de los detectores cargados
        
        Returns:
            Diccionario con información de los detectores
        """
        info = {
            'tesseract': {
                'available': os.path.exists(self.tesseract_cmd),
                'path': self.tesseract_cmd
            },
            'easyocr': {
                'available': self.easyocr_reader is not None,
                'gpu': USE_GPU
            },
            'confidence_threshold': self.confidence_threshold,
            'min_text_length': self.min_text_length
        }
        
        return info
