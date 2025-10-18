"""
Tests para utilidades de ffprobe
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock

from utils.ffprobe_utils import (
    get_video_metadata,
    get_metadata_with_ytdlp,
    get_metadata_with_ffprobe,
    parse_ytdlp_metadata,
    parse_ffprobe_metadata,
    get_video_duration,
    get_video_dimensions,
    is_video_vertical
)

class TestFFProbeUtils:
    """Tests para utilidades de ffprobe"""
    
    def test_get_video_duration(self):
        """Test obtener duración de video"""
        # Mock de metadata
        with patch('utils.ffprobe_utils.get_video_metadata') as mock_get_metadata:
            mock_get_metadata.return_value = {'duration': 120.5}
            
            duration = get_video_duration('test_url')
            assert duration == 120.5
    
    def test_get_video_dimensions(self):
        """Test obtener dimensiones de video"""
        with patch('utils.ffprobe_utils.get_video_metadata') as mock_get_metadata:
            mock_get_metadata.return_value = {'width': 1920, 'height': 1080}
            
            width, height = get_video_dimensions('test_url')
            assert width == 1920
            assert height == 1080
    
    def test_is_video_vertical(self):
        """Test verificar si video es vertical"""
        with patch('utils.ffprobe_utils.get_video_dimensions') as mock_get_dimensions:
            # Video vertical
            mock_get_dimensions.return_value = (1080, 1920)
            assert is_video_vertical('test_url') == True
            
            # Video horizontal
            mock_get_dimensions.return_value = (1920, 1080)
            assert is_video_vertical('test_url') == False
    
    def test_parse_ytdlp_metadata(self):
        """Test parsear metadatos de yt-dlp"""
        ytdlp_data = {
            'duration': 120,
            'width': 1920,
            'height': 1080,
            'fps': 30,
            'format': 'mp4',
            'ext': 'mp4',
            'filesize': 1000000,
            'view_count': 5000,
            'uploader': 'test_user',
            'upload_date': '20240101',
            'title': 'Test Video',
            'description': 'Test Description',
            'tags': ['test', 'video'],
            'thumbnail': 'http://example.com/thumb.jpg',
            'webpage_url': 'http://example.com/video',
            'id': 'test123',
            'extractor': 'youtube'
        }
        
        result = parse_ytdlp_metadata(ytdlp_data)
        
        assert result['duration'] == 120
        assert result['width'] == 1920
        assert result['height'] == 1080
        assert result['fps'] == 30
        assert result['platform'] == 'youtube'
        assert result['title'] == 'Test Video'
    
    def test_parse_ffprobe_metadata(self):
        """Test parsear metadatos de ffprobe"""
        ffprobe_data = {
            'format': {
                'duration': '120.5',
                'format_name': 'mp4',
                'size': '1000000',
                'filename': 'test.mp4',
                'tags': {
                    'title': 'Test Video',
                    'comment': 'Test Description'
                }
            },
            'streams': [
                {
                    'codec_type': 'video',
                    'width': 1920,
                    'height': 1080,
                    'r_frame_rate': '30/1'
                }
            ]
        }
        
        result = parse_ffprobe_metadata(ffprobe_data)
        
        assert result['duration'] == 120.5
        assert result['width'] == 1920
        assert result['height'] == 1080
        assert result['fps'] == 30.0
        assert result['platform'] == 'local'
        assert result['title'] == 'Test Video'
    
    @patch('subprocess.run')
    def test_get_metadata_with_ytdlp_success(self, mock_run):
        """Test obtener metadatos con yt-dlp exitoso"""
        mock_result = MagicMock()
        mock_result.stdout = '{"duration": 120, "width": 1920, "height": 1080}'
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        result = get_metadata_with_ytdlp('http://example.com/video')
        
        assert result is not None
        assert result['duration'] == 120
        assert result['width'] == 1920
        assert result['height'] == 1080
    
    @patch('subprocess.run')
    def test_get_metadata_with_ytdlp_failure(self, mock_run):
        """Test obtener metadatos con yt-dlp fallido"""
        mock_run.side_effect = Exception("Command failed")
        
        result = get_metadata_with_ytdlp('http://example.com/video')
        
        assert result is None
    
    @patch('subprocess.run')
    def test_get_metadata_with_ffprobe_success(self, mock_run):
        """Test obtener metadatos con ffprobe exitoso"""
        mock_result = MagicMock()
        mock_result.stdout = '''
        {
            "format": {
                "duration": "120.5",
                "format_name": "mp4"
            },
            "streams": [
                {
                    "codec_type": "video",
                    "width": 1920,
                    "height": 1080,
                    "r_frame_rate": "30/1"
                }
            ]
        }
        '''
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        result = get_metadata_with_ffprobe('/path/to/video.mp4')
        
        assert result is not None
        assert result['duration'] == 120.5
        assert result['width'] == 1920
        assert result['height'] == 1080
    
    def test_get_video_metadata_url(self):
        """Test obtener metadatos de URL"""
        with patch('utils.ffprobe_utils.get_metadata_with_ytdlp') as mock_ytdlp:
            mock_ytdlp.return_value = {'duration': 120, 'width': 1920, 'height': 1080}
            
            result = get_video_metadata('http://example.com/video')
            
            assert result is not None
            assert result['duration'] == 120
            mock_ytdlp.assert_called_once_with('http://example.com/video')
    
    def test_get_video_metadata_file(self):
        """Test obtener metadatos de archivo local"""
        with patch('utils.ffprobe_utils.get_metadata_with_ffprobe') as mock_ffprobe:
            mock_ffprobe.return_value = {'duration': 120, 'width': 1920, 'height': 1080}
            
            result = get_video_metadata('/path/to/video.mp4')
            
            assert result is not None
            assert result['duration'] == 120
            mock_ffprobe.assert_called_once_with('/path/to/video.mp4')
    
    def test_get_video_info_summary(self):
        """Test obtener resumen de información del video"""
        with patch('utils.ffprobe_utils.get_video_metadata') as mock_get_metadata:
            mock_get_metadata.return_value = {
                'duration': 120.5,
                'width': 1920,
                'height': 1080,
                'fps': 30.0
            }
            
            summary = get_video_info_summary('test_url')
            
            assert '1920x1080' in summary
            assert '30.0fps' in summary
            assert '120.5s' in summary

if __name__ == '__main__':
    pytest.main([__file__])
