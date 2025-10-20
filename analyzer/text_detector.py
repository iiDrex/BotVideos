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
            
            # Forzar GPU si está habilitado
            gpu = USE_GPU  # Forzar GPU si está habilitado
            if USE_GPU:
                console.print("    [green]✓ Forzando uso de GPU para EasyOCR[/green]")
                try:
                    import torch
                    if torch.cuda.is_available():
                        console.print("    [green]✓ GPU CUDA disponible para EasyOCR[/green]")
                    else:
                        console.print("    [yellow]⚠️  CUDA no disponible, pero forzando GPU para EasyOCR[/yellow]")
                except ImportError:
                    console.print("    [yellow]⚠️  PyTorch no disponible, pero forzando GPU para EasyOCR[/yellow]")
            else:
                console.print("    [yellow]⚠️  GPU deshabilitado para EasyOCR, usando CPU[/yellow]")
            
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
        Preprocesa un frame para mejorar la detección de texto - ULTRA RÁPIDO
        
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
            
            # Redimensionar para mejor detección (no tan agresivo)
            height, width = gray.shape
            if width > 640:  # Reducir a 640px para mejor detección
                scale = 640 / width
                new_width = 640
                new_height = int(height * scale)
                gray = cv2.resize(gray, (new_width, new_height))
            
            # PREPROCESAMIENTO MEJORADO para mejor detección
            # Aplicar filtro gaussiano para reducir ruido
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Usar umbralización adaptativa para mejor detección de texto
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
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
                # Filtrar por confianza MÁS ESTRICTO
                confidence = int(data['conf'][i])
                if confidence < self.confidence_threshold * 100:
                    continue
                
                # Obtener texto y coordenadas
                text = data['text'][i].strip()
                
                # Validación básica de longitud
                if len(text) < self.min_text_length:
                    continue
                
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                
                # Validar solo dimensiones básicas - SIN área mínima
                if w > 0 and h > 0:  # Cualquier tamaño de texto
                    detections.append({
                        'text': text,
                        'bbox': [x, y, w, h],
                        'confidence': float(confidence / 100.0),
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
                # Filtrar por confianza MÁS ESTRICTO
                if confidence < self.confidence_threshold:
                    continue
                
                text = text.strip()
                if len(text) < self.min_text_length:
                    continue
                
                # Convertir bbox a formato estándar
                x1, y1 = bbox[0]
                x2, y2 = bbox[2]
                x, y, w, h = int(x1), int(y1), int(x2-x1), int(y2-y1)
                
                # Validar solo dimensiones básicas - SIN área mínima
                if w > 0 and h > 0:  # Cualquier tamaño de texto
                    detections.append({
                        'text': text,
                        'bbox': [x, y, w, h],
                        'confidence': float(confidence),
                        'method': 'easyocr'
                    })
            
            return detections
            
        except Exception as e:
            console.print(f"    [red]Error con EasyOCR: {str(e)}[/red]")
            return []
    
    def _is_valid_text(self, text: str) -> bool:
        """
        FILTRO ULTRA PROFESIONAL - Detecta CUALQUIER texto visible
        Sistema de validación extremadamente estricto
        """
        text = text.strip()
        
        # Mínimo de caracteres
        if len(text) < self.min_text_length:
            return False
        
        # Filtrar solo espacios vacíos
        if not text or text.isspace():
            return False
        
        # ACEPTAR TODO LO DEMÁS - cualquier texto es válido para rechazar
        return True
    
    def _detect_text_patterns(self, frame: np.ndarray) -> List[Dict]:
        """
        Detección adicional de patrones de texto usando análisis visual
        """
        detections = []
        
        try:
            # Convertir a escala de grises
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame.copy()
            
            # Detectar contornos que podrían ser texto
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Filtrar contornos por área y aspecto
                area = cv2.contourArea(contour)
                if area > 50:  # Área mínima
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h if h > 0 else 0
                    
                    # Los caracteres de texto tienen proporciones específicas
                    if 0.1 < aspect_ratio < 10 and w > 5 and h > 5:
                        detections.append({
                            'text': f'PATTERN_{len(detections)}',
                            'bbox': [x, y, w, h],
                            'confidence': 0.8,
                            'method': 'pattern_detection'
                        })
        
        except Exception as e:
            console.print(f"    [yellow]Error en detección de patrones: {str(e)}[/yellow]")
        
        return detections
    
    def _detect_edge_text(self, frame: np.ndarray) -> List[Dict]:
        """
        Detección de texto basada en análisis de bordes
        """
        detections = []
        
        try:
            # Convertir a escala de grises
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame.copy()
            
            # Detectar bordes con múltiples métodos
            edges1 = cv2.Canny(gray, 30, 100)
            edges2 = cv2.Canny(gray, 50, 150)
            edges3 = cv2.Canny(gray, 100, 200)
            
            # Combinar bordes
            combined_edges = cv2.bitwise_or(edges1, cv2.bitwise_or(edges2, edges3))
            
            # Encontrar contornos
            contours, _ = cv2.findContours(combined_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 25:  # Área mínima muy pequeña
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Verificar si podría ser texto
                    if w > 3 and h > 3:  # Dimensiones mínimas muy pequeñas
                        detections.append({
                            'text': f'EDGE_{len(detections)}',
                            'bbox': [x, y, w, h],
                            'confidence': 0.7,
                            'method': 'edge_detection'
                        })
        
        except Exception as e:
            console.print(f"    [yellow]Error en detección de bordes: {str(e)}[/yellow]")
        
        return detections
    
    def _detect_any_font_text(self, frame: np.ndarray) -> List[Dict]:
        """
        Detección ULTRA AGRESIVA para CUALQUIER tipo de fuente
        Incluye fuentes estilizadas, decorativas, cursivas, etc.
        """
        detections = []
        
        try:
            # Convertir a escala de grises
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame.copy()
            
            # MÚLTIPLES MÉTODOS DE DETECCIÓN DE FUENTES
            
            # Método 1: Detección de gradientes (funciona con fuentes decorativas)
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            gradient_magnitude = np.uint8(gradient_magnitude)
            
            # Método 2: Detección de cambios de intensidad (fuentes con sombras)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            laplacian = np.uint8(np.absolute(laplacian))
            
            # Método 3: Detección de texturas (fuentes con patrones)
            texture = cv2.Laplacian(gray, cv2.CV_64F, ksize=5)
            texture = np.uint8(np.absolute(texture))
            
            # Combinar todos los métodos
            combined = cv2.addWeighted(gradient_magnitude, 0.4, laplacian, 0.3, 0)
            combined = cv2.addWeighted(combined, 0.7, texture, 0.3, 0)
            
            # Aplicar umbralización adaptativa múltiple
            thresh1 = cv2.adaptiveThreshold(combined, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
            thresh2 = cv2.adaptiveThreshold(combined, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            thresh3 = cv2.threshold(combined, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # Combinar umbralizaciones
            final_thresh = cv2.bitwise_or(thresh1, cv2.bitwise_or(thresh2, thresh3))
            
            # Encontrar contornos
            contours, _ = cv2.findContours(final_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 10:  # Área mínima extremadamente pequeña
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Verificar si podría ser cualquier tipo de texto
                    if w > 2 and h > 2:  # Dimensiones mínimas extremas
                        aspect_ratio = w / h if h > 0 else 0
                        
                        # Aceptar cualquier proporción (fuentes pueden ser muy variadas)
                        if 0.01 < aspect_ratio < 100:  # Rango extremadamente amplio
                            detections.append({
                                'text': f'FONT_{len(detections)}',
                                'bbox': [x, y, w, h],
                                'confidence': 0.9,
                                'method': 'any_font_detection'
                            })
        
        except Exception as e:
            console.print(f"    [yellow]Error en detección de fuentes: {str(e)}[/yellow]")
        
        return detections
    
    def _detect_stylized_text(self, frame: np.ndarray) -> List[Dict]:
        """
        Detección específica para texto estilizado y decorativo
        """
        detections = []
        
        try:
            # Convertir a escala de grises
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame.copy()
            
            # Detectar texto con sombras, gradientes y efectos
            # Aplicar filtros morfológicos para detectar formas de texto
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            
            # Operaciones morfológicas para detectar formas de texto
            opening = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
            closing = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            gradient = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)
            
            # Combinar operaciones
            combined = cv2.addWeighted(opening, 0.3, closing, 0.3, 0)
            combined = cv2.addWeighted(combined, 0.7, gradient, 0.3, 0)
            
            # Detectar bordes con múltiples escalas
            edges1 = cv2.Canny(combined, 10, 30)  # Muy sensible
            edges2 = cv2.Canny(combined, 20, 60)
            edges3 = cv2.Canny(combined, 40, 120)
            
            # Combinar bordes
            all_edges = cv2.bitwise_or(edges1, cv2.bitwise_or(edges2, edges3))
            
            # Encontrar contornos
            contours, _ = cv2.findContours(all_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 5:  # Área mínima extremadamente pequeña
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    if w > 1 and h > 1:  # Dimensiones mínimas extremas
                        detections.append({
                            'text': f'STYLIZED_{len(detections)}',
                            'bbox': [x, y, w, h],
                            'confidence': 0.8,
                            'method': 'stylized_text_detection'
                        })
        
        except Exception as e:
            console.print(f"    [yellow]Error en detección de texto estilizado: {str(e)}[/yellow]")
        
        return detections
    
    def _detect_rotated_text(self, frame: np.ndarray) -> List[Dict]:
        """
        Detección de texto rotado, inclinado o con orientación no estándar
        """
        detections = []
        
        try:
            # Convertir a escala de grises
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame.copy()
            
            # Probar múltiples rotaciones
            angles = [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255, 270, 285, 300, 315, 330, 345]
            
            for angle in angles:
                # Rotar la imagen
                if angle != 0:
                    h, w = gray.shape
                    center = (w // 2, h // 2)
                    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                    rotated = cv2.warpAffine(gray, rotation_matrix, (w, h))
                else:
                    rotated = gray.copy()
                
                # Detectar bordes en la imagen rotada
                edges = cv2.Canny(rotated, 10, 50)  # Muy sensible
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 3:  # Área mínima extremadamente pequeña
                        x, y, w, h = cv2.boundingRect(contour)
                        
                        if w > 1 and h > 1:  # Dimensiones mínimas extremas
                            detections.append({
                                'text': f'ROTATED_{len(detections)}',
                                'bbox': [x, y, w, h],
                                'confidence': 0.85,
                                'method': f'rotated_text_{angle}'
                            })
        
        except Exception as e:
            console.print(f"    [yellow]Error en detección de texto rotado: {str(e)}[/yellow]")
        
        return detections

    def detect_text_on_frame(self, frame: np.ndarray) -> List[Dict]:
        """
        DETECCIÓN ULTRA PROFESIONAL - Múltiples capas de detección
        Sistema extremadamente estricto para rechazar CUALQUIER texto
        
        Args:
            frame: Frame de video
            
        Returns:
            Lista de detecciones de texto
        """
        all_detections = []
        
        # CAPA 1: Tesseract OCR (siempre)
        tesseract_detections = self.detect_text_with_tesseract(frame)
        all_detections.extend(tesseract_detections)
        
        # CAPA 2: EasyOCR (siempre, no importa si Tesseract encuentra algo)
        if self.easyocr_reader is not None:
            easyocr_detections = self.detect_text_with_easyocr(frame)
            all_detections.extend(easyocr_detections)
        
        # CAPA 3: Detección de patrones visuales
        pattern_detections = self._detect_text_patterns(frame)
        all_detections.extend(pattern_detections)
        
        # CAPA 4: Análisis de bordes y contornos
        edge_detections = self._detect_edge_text(frame)
        all_detections.extend(edge_detections)
        
        # CAPA 5: Detección de CUALQUIER tipo de fuente
        font_detections = self._detect_any_font_text(frame)
        all_detections.extend(font_detections)
        
        # CAPA 6: Detección de texto estilizado y decorativo
        stylized_detections = self._detect_stylized_text(frame)
        all_detections.extend(stylized_detections)
        
        # CAPA 7: Detección de texto rotado e inclinado
        rotated_detections = self._detect_rotated_text(frame)
        all_detections.extend(rotated_detections)
        
        # Filtrar detecciones válidas (ULTRA PERMISIVO)
        valid_detections = [d for d in all_detections if self._is_valid_text(d['text'])]
        
        # Eliminar duplicados basados en proximidad espacial
        unique_detections = self._remove_duplicate_detections(valid_detections)
        
        return unique_detections
    
    def detect_text_on_video(self, path: str, sample_strategy: dict) -> List[Dict]:
        """
        Detecta texto en un video completo - ULTRA RÁPIDO Y OPTIMIZADO
        
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
            
            # MUESTREO EXTREMO para detectar TODO el texto
            sample_rate = max(1, int(fps * 1))  # Cada 1 segundo de video
            
            console.print(f"    [blue]Video: {duration:.1f}s, {total_frames} frames, {fps:.1f} fps[/blue]")
            console.print(f"    [blue]Muestreo: cada {sample_rate} frames[/blue]")
            
            detections = []
            frame_count = 0
            processed_frames = 0
            max_frames = 15  # OPTIMIZADO para velocidad masiva
            
            while processed_frames < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Aplicar muestreo ultra agresivo
                if frame_count % sample_rate == 0:
                    text_detections = self.detect_text_on_frame(frame)
                    
                    if text_detections:
                        for detection in text_detections:
                            detection['frame'] = frame_count
                            detection['timestamp'] = float(frame_count / fps if fps > 0 else 0)
                            detections.append(detection)
                        
                        # SALIDA TEMPRANA INMEDIATA - si detectamos texto, parar inmediatamente
                        console.print(f"    [yellow]⚠️  Texto detectado en frame {frame_count}[/yellow]")
                        break
                    
                    processed_frames += 1
                
                frame_count += 1
            
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
