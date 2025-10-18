"""
Tests para detector de rostros
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from analyzer.face_detector import FaceDetector

class TestFaceDetector:
    """Tests para detector de rostros"""
    
    def test_face_detector_init(self):
        """Test inicialización del detector"""
        detector = FaceDetector()
        
        # Verificar que se inicializa correctamente
        assert detector.confidence_threshold > 0
        assert detector.model_path is not None
    
    def test_get_model_info(self):
        """Test obtener información del modelo"""
        detector = FaceDetector()
        info = detector.get_model_info()
        
        assert 'loaded' in info
        assert 'model_path' in info
        assert 'device' in info
    
    def test_detect_faces_on_frame_no_faces(self):
        """Test detección en frame sin rostros"""
        detector = FaceDetector()
        
        # Crear frame de prueba (imagen negra)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        with patch.object(detector, 'model') as mock_model:
            mock_model.return_value = [MagicMock(boxes=None)]
            
            faces = detector.detect_faces_on_frame(frame)
            assert faces == []
    
    def test_detect_faces_on_frame_with_faces(self):
        """Test detección en frame con rostros"""
        detector = FaceDetector()
        
        # Crear frame de prueba
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        with patch.object(detector, 'model') as mock_model:
            # Mock de detección con rostro
            mock_box = MagicMock()
            mock_box.xyxy = [np.array([100, 100, 200, 200])]
            mock_box.conf = [np.array([0.8])]
            mock_box.cls = [np.array([0])]  # Clase 0 = rostro
            
            mock_result = MagicMock()
            mock_result.boxes = [mock_box]
            mock_model.return_value = [mock_result]
            
            faces = detector.detect_faces_on_frame(frame)
            
            assert len(faces) == 1
            assert faces[0]['confidence'] == 0.8
            assert faces[0]['class'] == 'face'
            assert faces[0]['bbox'] == [100, 100, 100, 100]
    
    def test_calculate_sample_rate_short_video(self):
        """Test cálculo de tasa de muestreo para video corto"""
        detector = FaceDetector()
        
        sample_strategy = {
            'short': {'max_dur': 60, 'fps_factor': 0.5},
            'medium': {'max_dur': 300, 'fps_factor': 1.0},
            'long': {'fps_factor': 2.0}
        }
        
        # Video corto (30 segundos)
        sample_rate = detector._calculate_sample_rate(30, sample_strategy, 30)
        assert sample_rate == 15  # 30 fps * 0.5 = 15
    
    def test_calculate_sample_rate_medium_video(self):
        """Test cálculo de tasa de muestreo para video mediano"""
        detector = FaceDetector()
        
        sample_strategy = {
            'short': {'max_dur': 60, 'fps_factor': 0.5},
            'medium': {'max_dur': 300, 'fps_factor': 1.0},
            'long': {'fps_factor': 2.0}
        }
        
        # Video mediano (120 segundos)
        sample_rate = detector._calculate_sample_rate(120, sample_strategy, 30)
        assert sample_rate == 30  # 30 fps * 1.0 = 30
    
    def test_calculate_sample_rate_long_video(self):
        """Test cálculo de tasa de muestreo para video largo"""
        detector = FaceDetector()
        
        sample_strategy = {
            'short': {'max_dur': 60, 'fps_factor': 0.5},
            'medium': {'max_dur': 300, 'fps_factor': 1.0},
            'long': {'fps_factor': 2.0}
        }
        
        # Video largo (400 segundos)
        sample_rate = detector._calculate_sample_rate(400, sample_strategy, 30)
        assert sample_rate == 60  # 30 fps * 2.0 = 60
    
    @patch('cv2.VideoCapture')
    def test_detect_faces_on_video_success(self, mock_cap):
        """Test detección en video exitosa"""
        detector = FaceDetector()
        
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
        
        with patch.object(detector, 'detect_faces_on_frame') as mock_detect:
            mock_detect.return_value = []
            
            sample_strategy = {'short': {'max_dur': 60, 'fps_factor': 0.5}}
            detections = detector.detect_faces_on_video('test.mp4', sample_strategy)
            
            assert detections == []
            mock_detect.assert_called()
    
    @patch('cv2.VideoCapture')
    def test_detect_faces_on_video_with_faces(self, mock_cap):
        """Test detección en video con rostros"""
        detector = FaceDetector()
        
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
        
        with patch.object(detector, 'detect_faces_on_frame') as mock_detect:
            mock_detect.return_value = [{
                'bbox': [100, 100, 200, 200],
                'confidence': 0.8,
                'class': 'face'
            }]
            
            sample_strategy = {'short': {'max_dur': 60, 'fps_factor': 0.5}}
            detections = detector.detect_faces_on_video('test.mp4', sample_strategy)
            
            assert len(detections) == 1
            assert detections[0]['frame'] == 0
            assert detections[0]['confidence'] == 0.8
    
    def test_detect_faces_with_confirmation(self):
        """Test detección con confirmación"""
        detector = FaceDetector()
        
        with patch.object(detector, 'detect_faces_on_video') as mock_detect:
            mock_detect.return_value = [{
                'frame': 10,
                'bbox': [100, 100, 200, 200],
                'confidence': 0.8,
                'class': 'face'
            }]
            
            with patch.object(detector, '_check_nearby_frames') as mock_check:
                mock_check.return_value = [{
                    'bbox': [110, 110, 190, 190],
                    'confidence': 0.7,
                    'class': 'face'
                }]
                
                sample_strategy = {'short': {'max_dur': 60, 'fps_factor': 0.5}}
                detections = detector.detect_faces_with_confirmation('test.mp4', sample_strategy)
                
                assert len(detections) == 1
                assert detections[0]['confirmed'] == True
                assert detections[0]['nearby_count'] == 1
    
    def test_check_nearby_frames(self):
        """Test verificación de frames cercanos"""
        detector = FaceDetector()
        
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap_instance = MagicMock()
            mock_cap_instance.isOpened.return_value = True
            mock_cap_instance.set.return_value = True
            mock_cap_instance.read.side_effect = [(True, np.zeros((480, 640, 3))), (True, np.zeros((480, 640, 3)))]
            mock_cap.return_value = mock_cap_instance
            
            with patch.object(detector, 'detect_faces_on_frame') as mock_detect:
                mock_detect.return_value = [{
                    'bbox': [100, 100, 200, 200],
                    'confidence': 0.8,
                    'class': 'face'
                }]
                
                nearby = detector._check_nearby_frames('test.mp4', 10, 5)
                
                assert len(nearby) > 0
                assert nearby[0]['frame'] in [5, 6, 7, 8, 9, 11, 12, 13, 14, 15]

if __name__ == '__main__':
    pytest.main([__file__])
