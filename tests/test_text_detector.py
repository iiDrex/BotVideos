"""
Tests para detector de texto
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from analyzer.text_detector import TextDetector

class TestTextDetector:
    """Tests para detector de texto"""
    
    def test_text_detector_init(self):
        """Test inicialización del detector"""
        detector = TextDetector(use_easyocr=False)
        
        # Verificar que se inicializa correctamente
        assert detector.confidence_threshold > 0
        assert detector.min_text_length > 0
    
    def test_get_detector_info(self):
        """Test obtener información del detector"""
        detector = TextDetector(use_easyocr=False)
        info = detector.get_detector_info()
        
        assert 'tesseract' in info
        assert 'easyocr' in info
        assert 'confidence_threshold' in info
        assert 'min_text_length' in info
    
    def test_preprocess_frame(self):
        """Test preprocesamiento de frame"""
        detector = TextDetector(use_easyocr=False)
        
        # Crear frame de prueba
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        processed = detector.preprocess_frame(frame)
        
        # Verificar que el frame procesado es diferente al original
        assert processed.shape != frame.shape or not np.array_equal(processed, frame)
        assert len(processed.shape) == 2  # Debe ser escala de grises
    
    def test_detect_text_with_tesseract_no_text(self):
        """Test detección con Tesseract sin texto"""
        detector = TextDetector(use_easyocr=False)
        
        # Crear frame sin texto (imagen negra)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        with patch('pytesseract.image_to_data') as mock_tesseract:
            mock_tesseract.return_value = {
                'level': [0],
                'conf': [0],
                'text': [''],
                'left': [0],
                'top': [0],
                'width': [0],
                'height': [0]
            }
            
            detections = detector.detect_text_with_tesseract(frame)
            assert detections == []
    
    def test_detect_text_with_tesseract_with_text(self):
        """Test detección con Tesseract con texto"""
        detector = TextDetector(use_easyocr=False)
        
        # Crear frame de prueba
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        with patch('pytesseract.image_to_data') as mock_tesseract:
            mock_tesseract.return_value = {
                'level': [0, 5],
                'conf': [0, 80],
                'text': ['', 'Hello World'],
                'left': [0, 100],
                'top': [0, 100],
                'width': [0, 200],
                'height': [0, 50]
            }
            
            detections = detector.detect_text_with_tesseract(frame)
            
            assert len(detections) == 1
            assert detections[0]['text'] == 'Hello World'
            assert detections[0]['method'] == 'tesseract'
            assert detections[0]['confidence'] == 0.8
    
    def test_detect_text_with_easyocr_no_text(self):
        """Test detección con EasyOCR sin texto"""
        detector = TextDetector(use_easyocr=True)
        
        # Crear frame sin texto
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        with patch.object(detector, 'easyocr_reader') as mock_reader:
            mock_reader.readtext.return_value = []
            
            detections = detector.detect_text_with_easyocr(frame)
            assert detections == []
    
    def test_detect_text_with_easyocr_with_text(self):
        """Test detección con EasyOCR con texto"""
        detector = TextDetector(use_easyocr=True)
        
        # Crear frame de prueba
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        with patch.object(detector, 'easyocr_reader') as mock_reader:
            mock_reader.readtext.return_value = [
                ([[100, 100], [300, 100], [300, 150], [100, 150]], 'Hello World', 0.9)
            ]
            
            detections = detector.detect_text_with_easyocr(frame)
            
            assert len(detections) == 1
            assert detections[0]['text'] == 'Hello World'
            assert detections[0]['method'] == 'easyocr'
            assert detections[0]['confidence'] == 0.9
            assert detections[0]['bbox'] == [100, 100, 200, 50]
    
    def test_detect_text_on_frame_combined(self):
        """Test detección combinada en frame"""
        detector = TextDetector(use_easyocr=True)
        
        # Crear frame de prueba
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        with patch.object(detector, 'detect_text_with_tesseract') as mock_tesseract:
            with patch.object(detector, 'detect_text_with_easyocr') as mock_easyocr:
                mock_tesseract.return_value = [{
                    'text': 'Tesseract Text',
                    'bbox': [100, 100, 200, 50],
                    'confidence': 0.8,
                    'method': 'tesseract'
                }]
                
                mock_easyocr.return_value = [{
                    'text': 'EasyOCR Text',
                    'bbox': [300, 300, 200, 50],
                    'confidence': 0.9,
                    'method': 'easyocr'
                }]
                
                detections = detector.detect_text_on_frame(frame)
                
                assert len(detections) == 2
                assert any(d['method'] == 'tesseract' for d in detections)
                assert any(d['method'] == 'easyocr' for d in detections)
    
    def test_remove_duplicate_detections(self):
        """Test eliminación de detecciones duplicadas"""
        detector = TextDetector(use_easyocr=False)
        
        detections = [
            {
                'text': 'Hello',
                'bbox': [100, 100, 200, 50],
                'confidence': 0.8,
                'method': 'tesseract'
            },
            {
                'text': 'Hello',
                'bbox': [110, 110, 190, 40],  # Superposición significativa
                'confidence': 0.9,
                'method': 'easyocr'
            },
            {
                'text': 'World',
                'bbox': [300, 300, 200, 50],  # No superposición
                'confidence': 0.8,
                'method': 'tesseract'
            }
        ]
        
        unique = detector._remove_duplicate_detections(detections)
        
        # Debe eliminar una de las detecciones superpuestas
        assert len(unique) == 2
        assert any(d['text'] == 'Hello' for d in unique)
        assert any(d['text'] == 'World' for d in unique)
    
    def test_calculate_sample_rate(self):
        """Test cálculo de tasa de muestreo"""
        detector = TextDetector(use_easyocr=False)
        
        sample_strategy = {
            'short': {'max_dur': 60, 'fps_factor': 0.5},
            'medium': {'max_dur': 300, 'fps_factor': 1.0},
            'long': {'fps_factor': 2.0}
        }
        
        # Video corto
        rate = detector._calculate_sample_rate(30, sample_strategy, 30)
        assert rate == 15  # 30 fps * 0.5
        
        # Video mediano
        rate = detector._calculate_sample_rate(120, sample_strategy, 30)
        assert rate == 30  # 30 fps * 1.0
        
        # Video largo
        rate = detector._calculate_sample_rate(400, sample_strategy, 30)
        assert rate == 60  # 30 fps * 2.0
    
    @patch('cv2.VideoCapture')
    def test_detect_text_on_video_success(self, mock_cap):
        """Test detección en video exitosa"""
        detector = TextDetector(use_easyocr=False)
        
        # Mock de VideoCapture
        mock_cap_instance = MagicMock()
        mock_cap_instance.isOpened.return_value = True
        mock_cap_instance.get.side_effect = lambda prop: {
            5: 30,  # FPS
            7: 900,  # FRAME_COUNT
            3: 640,  # FRAME_WIDTH
            4: 480   # FRAME_HEIGHT
        }.get(prop, 0)
        
        # Mock de frames
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cap_instance.read.side_effect = [(True, frame), (True, frame), (False, None)]
        mock_cap.return_value = mock_cap_instance
        
        with patch.object(detector, 'detect_text_on_frame') as mock_detect:
            mock_detect.return_value = []
            
            sample_strategy = {'short': {'max_dur': 60, 'fps_factor': 0.5}}
            detections = detector.detect_text_on_video('test.mp4', sample_strategy)
            
            assert detections == []
            mock_detect.assert_called()
    
    @patch('cv2.VideoCapture')
    def test_detect_text_on_video_with_text(self, mock_cap):
        """Test detección en video con texto"""
        detector = TextDetector(use_easyocr=False)
        
        # Mock de VideoCapture
        mock_cap_instance = MagicMock()
        mock_cap_instance.isOpened.return_value = True
        mock_cap_instance.get.side_effect = lambda prop: {
            5: 30,  # FPS
            7: 900,  # FRAME_COUNT
            3: 640,  # FRAME_WIDTH
            4: 480   # FRAME_HEIGHT
        }.get(prop, 0)
        
        # Mock de frames
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cap_instance.read.side_effect = [(True, frame), (False, None)]
        mock_cap.return_value = mock_cap_instance
        
        with patch.object(detector, 'detect_text_on_frame') as mock_detect:
            mock_detect.return_value = [{
                'text': 'Hello World',
                'bbox': [100, 100, 200, 50],
                'confidence': 0.8,
                'method': 'tesseract'
            }]
            
            sample_strategy = {'short': {'max_dur': 60, 'fps_factor': 0.5}}
            detections = detector.detect_text_on_video('test.mp4', sample_strategy)
            
            assert len(detections) == 1
            assert detections[0]['frame'] == 0
            assert detections[0]['text'] == 'Hello World'

if __name__ == '__main__':
    pytest.main([__file__])
