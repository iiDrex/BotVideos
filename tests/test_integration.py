"""
Tests de integración para VideoFinder AI Bot
"""

import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock

from orchestrator import run_job
from analyzer.video_analyzer import EnhancedVideoAnalyzer
from downloader import VideoDownloader
from scrapers.youtube_scraper import search_youtube
from scrapers.instagram_scraper import search_instagram
from scrapers.tiktok_scraper import search_tiktok

class TestIntegration:
    """Tests de integración"""
    
    def test_orchestrator_run_job_basic(self):
        """Test ejecución básica del orquestador"""
        config = {
            'keyword': 'test video',
            'duration_range': (30, 60),
            'filters': {'vertical': True, 'faces': True, 'text': True},
            'platforms': ['youtube'],
            'max_results': 5
        }
        
        with patch('scrapers.youtube_scraper.search_youtube') as mock_search:
            mock_search.return_value = [
                {
                    'id': 'test1',
                    'title': 'Test Video 1',
                    'url': 'https://youtube.com/watch?v=test1',
                    'platform': 'youtube',
                    'duration': 45,
                    'width': 1080,
                    'height': 1920
                }
            ]
            
            with patch('utils.ffprobe_utils.get_video_metadata') as mock_metadata:
                mock_metadata.return_value = {
                    'duration': 45,
                    'width': 1080,
                    'height': 1920,
                    'fps': 30
                }
                
                with patch('downloader.VideoDownloader.download_temporal') as mock_download:
                    mock_download.return_value = '/tmp/test_video.mp4'
                    
                    with patch('analyzer.video_analyzer.EnhancedVideoAnalyzer.analyze_video') as mock_analyze:
                        mock_analyze.return_value = {
                            'has_face': False,
                            'face_details': [],
                            'has_text': False,
                            'text_details': [],
                            'analysis_time_ms': 1000
                        }
                        
                        results = run_job(config)
                        
                        assert len(results) == 1
                        assert results[0]['estado'] == 'aceptado'
                        assert results[0]['titulo'] == 'Test Video 1'
    
    def test_orchestrator_run_job_with_rejection(self):
        """Test ejecución con rechazo por rostros"""
        config = {
            'keyword': 'test video',
            'duration_range': (30, 60),
            'filters': {'vertical': True, 'faces': True, 'text': True},
            'platforms': ['youtube'],
            'max_results': 5
        }
        
        with patch('scrapers.youtube_scraper.search_youtube') as mock_search:
            mock_search.return_value = [
                {
                    'id': 'test1',
                    'title': 'Test Video 1',
                    'url': 'https://youtube.com/watch?v=test1',
                    'platform': 'youtube',
                    'duration': 45,
                    'width': 1080,
                    'height': 1920
                }
            ]
            
            with patch('utils.ffprobe_utils.get_video_metadata') as mock_metadata:
                mock_metadata.return_value = {
                    'duration': 45,
                    'width': 1080,
                    'height': 1920,
                    'fps': 30
                }
                
                with patch('downloader.VideoDownloader.download_temporal') as mock_download:
                    mock_download.return_value = '/tmp/test_video.mp4'
                    
                    with patch('analyzer.video_analyzer.EnhancedVideoAnalyzer.analyze_video') as mock_analyze:
                        mock_analyze.return_value = {
                            'has_face': True,
                            'face_details': [{'frame': 10, 'bbox': [100, 100, 200, 200], 'confidence': 0.8}],
                            'has_text': False,
                            'text_details': [],
                            'analysis_time_ms': 1000
                        }
                        
                        results = run_job(config)
                        
                        assert len(results) == 1
                        assert results[0]['estado'] == 'descartado'
                        assert 'rostro detectado' in results[0]['razones']
    
    def test_orchestrator_run_job_with_text_rejection(self):
        """Test ejecución con rechazo por texto"""
        config = {
            'keyword': 'test video',
            'duration_range': (30, 60),
            'filters': {'vertical': True, 'faces': True, 'text': True},
            'platforms': ['youtube'],
            'max_results': 5
        }
        
        with patch('scrapers.youtube_scraper.search_youtube') as mock_search:
            mock_search.return_value = [
                {
                    'id': 'test1',
                    'title': 'Test Video 1',
                    'url': 'https://youtube.com/watch?v=test1',
                    'platform': 'youtube',
                    'duration': 45,
                    'width': 1080,
                    'height': 1920
                }
            ]
            
            with patch('utils.ffprobe_utils.get_video_metadata') as mock_metadata:
                mock_metadata.return_value = {
                    'duration': 45,
                    'width': 1080,
                    'height': 1920,
                    'fps': 30
                }
                
                with patch('downloader.VideoDownloader.download_temporal') as mock_download:
                    mock_download.return_value = '/tmp/test_video.mp4'
                    
                    with patch('analyzer.video_analyzer.EnhancedVideoAnalyzer.analyze_video') as mock_analyze:
                        mock_analyze.return_value = {
                            'has_face': False,
                            'face_details': [],
                            'has_text': True,
                            'text_details': [{'frame': 10, 'text': 'Hello World', 'confidence': 0.8}],
                            'analysis_time_ms': 1000
                        }
                        
                        results = run_job(config)
                        
                        assert len(results) == 1
                        assert results[0]['estado'] == 'descartado'
                        assert 'texto detectado' in results[0]['razones']
    
    def test_orchestrator_run_job_metadata_filtering(self):
        """Test filtrado por metadatos"""
        config = {
            'keyword': 'test video',
            'duration_range': (30, 60),
            'filters': {'vertical': True, 'faces': True, 'text': True},
            'platforms': ['youtube'],
            'max_results': 5
        }
        
        with patch('scrapers.youtube_scraper.search_youtube') as mock_search:
            mock_search.return_value = [
                {
                    'id': 'test1',
                    'title': 'Test Video 1',
                    'url': 'https://youtube.com/watch?v=test1',
                    'platform': 'youtube',
                    'duration': 45,
                    'width': 1920,  # Horizontal
                    'height': 1080
                }
            ]
            
            with patch('utils.ffprobe_utils.get_video_metadata') as mock_metadata:
                mock_metadata.return_value = {
                    'duration': 45,
                    'width': 1920,
                    'height': 1080,
                    'fps': 30
                }
                
                results = run_job(config)
                
                assert len(results) == 1
                assert results[0]['estado'] == 'descartado'
                assert 'orientacion horizontal' in results[0]['razones']
    
    def test_orchestrator_run_job_duration_filtering(self):
        """Test filtrado por duración"""
        config = {
            'keyword': 'test video',
            'duration_range': (30, 60),
            'filters': {'vertical': True, 'faces': True, 'text': True},
            'platforms': ['youtube'],
            'max_results': 5
        }
        
        with patch('scrapers.youtube_scraper.search_youtube') as mock_search:
            mock_search.return_value = [
                {
                    'id': 'test1',
                    'title': 'Test Video 1',
                    'url': 'https://youtube.com/watch?v=test1',
                    'platform': 'youtube',
                    'duration': 120,  # Fuera de rango
                    'width': 1080,
                    'height': 1920
                }
            ]
            
            with patch('utils.ffprobe_utils.get_video_metadata') as mock_metadata:
                mock_metadata.return_value = {
                    'duration': 120,
                    'width': 1080,
                    'height': 1920,
                    'fps': 30
                }
                
                results = run_job(config)
                
                assert len(results) == 1
                assert results[0]['estado'] == 'descartado'
                assert 'duracion fuera de rango' in results[0]['razones']
    
    def test_enhanced_video_analyzer_analyze_video(self):
        """Test análisis de video"""
        analyzer = EnhancedVideoAnalyzer({})
        
        with patch('analyzer.face_detector.FaceDetector.detect_faces_on_video') as mock_faces:
            with patch('analyzer.text_detector.TextDetector.detect_text_on_video') as mock_text:
                mock_faces.return_value = []
                mock_text.return_value = []
                
                with patch('cv2.VideoCapture') as mock_cap:
                    mock_cap_instance = MagicMock()
                    mock_cap_instance.isOpened.return_value = True
                    mock_cap_instance.get.side_effect = lambda prop: {
                        5: 30,  # FPS
                        7: 900,  # FRAME_COUNT
                        3: 640,  # FRAME_WIDTH
                        4: 480   # FRAME_HEIGHT
                    }.get(prop, 0)
                    mock_cap_instance.read.side_effect = [(True, None), (False, None)]
                    mock_cap.return_value = mock_cap_instance
                    
                    result = analyzer.analyze_video('/tmp/test.mp4')
                    
                    assert 'has_face' in result
                    assert 'has_text' in result
                    assert 'analysis_time_ms' in result
    
    def test_video_downloader_download_temporal(self):
        """Test descarga temporal de video"""
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = VideoDownloader(temp_dir)
            
            with patch('subprocess.run') as mock_run:
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = ''
                mock_run.return_value = mock_result
                
                with patch('glob.glob') as mock_glob:
                    mock_glob.return_value = ['/tmp/test_video.mp4']
                    
                    with patch('os.path.exists') as mock_exists:
                        mock_exists.return_value = True
                        
                        result = downloader.download_temporal('https://example.com/video')
                        
                        assert result == '/tmp/test_video.mp4'
    
    def test_scrapers_integration(self):
        """Test integración de scrapers"""
        # Test YouTube scraper
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = json.dumps({
                'id': 'test1',
                'title': 'Test Video',
                'webpage_url': 'https://youtube.com/watch?v=test1',
                'duration': 45,
                'width': 1080,
                'height': 1920
            })
            mock_run.return_value = mock_result
            
            videos = search_youtube('test', 5)
            assert len(videos) == 1
            assert videos[0]['platform'] == 'youtube'
        
        # Test Instagram scraper
        with patch('instaloader.Instaloader') as mock_loader:
            mock_instance = MagicMock()
            mock_loader.return_value = mock_instance
            
            with patch('instaloader.Hashtag.from_name') as mock_hashtag:
                mock_hashtag_obj = MagicMock()
                mock_hashtag.return_value = mock_hashtag_obj
                
                mock_post = MagicMock()
                mock_post.is_video = True
                mock_post.shortcode = 'test123'
                mock_post.caption = 'Test caption'
                mock_post.video_duration = 45
                mock_post.video_width = 1080
                mock_post.video_height = 1920
                mock_post.owner_username = 'testuser'
                mock_post.date_utc.isoformat.return_value = '2024-01-01T00:00:00Z'
                mock_post.url = 'https://example.com/video.mp4'
                
                mock_hashtag_obj.get_posts.return_value = [mock_post]
                
                videos = search_instagram('test', 5)
                assert len(videos) == 1
                assert videos[0]['platform'] == 'instagram'
        
        # Test TikTok scraper
        with patch('playwright.sync_api.sync_playwright') as mock_playwright:
            mock_p = MagicMock()
            mock_playwright.return_value.__enter__.return_value = mock_p
            
            mock_browser = MagicMock()
            mock_p.chromium.launch.return_value = mock_browser
            
            mock_page = MagicMock()
            mock_browser.new_page.return_value = mock_page
            
            mock_elem = MagicMock()
            mock_elem.query_selector.return_value = MagicMock()
            mock_elem.get_attribute.return_value = 'https://tiktok.com/video/123'
            mock_elem.inner_text.return_value = 'Test video'
            
            mock_page.query_selector_all.return_value = [mock_elem]
            
            videos = search_tiktok('test', 5)
            assert len(videos) == 1
            assert videos[0]['platform'] == 'tiktok'
    
    def test_end_to_end_workflow(self):
        """Test flujo completo end-to-end"""
        config = {
            'keyword': 'test video',
            'duration_range': (30, 60),
            'filters': {'vertical': True, 'faces': True, 'text': True},
            'platforms': ['youtube'],
            'max_results': 3
        }
        
        # Mock de todos los componentes
        with patch('scrapers.youtube_scraper.search_youtube') as mock_search:
            mock_search.return_value = [
                {
                    'id': 'test1',
                    'title': 'Test Video 1',
                    'url': 'https://youtube.com/watch?v=test1',
                    'platform': 'youtube',
                    'duration': 45,
                    'width': 1080,
                    'height': 1920
                },
                {
                    'id': 'test2',
                    'title': 'Test Video 2',
                    'url': 'https://youtube.com/watch?v=test2',
                    'platform': 'youtube',
                    'duration': 45,
                    'width': 1920,  # Horizontal
                    'height': 1080
                }
            ]
            
            with patch('utils.ffprobe_utils.get_video_metadata') as mock_metadata:
                def metadata_side_effect(url):
                    if 'test1' in url:
                        return {
                            'duration': 45,
                            'width': 1080,
                            'height': 1920,
                            'fps': 30
                        }
                    elif 'test2' in url:
                        return {
                            'duration': 45,
                            'width': 1920,
                            'height': 1080,
                            'fps': 30
                        }
                    return None
                
                mock_metadata.side_effect = metadata_side_effect
                
                with patch('downloader.VideoDownloader.download_temporal') as mock_download:
                    mock_download.return_value = '/tmp/test_video.mp4'
                    
                    with patch('analyzer.video_analyzer.EnhancedVideoAnalyzer.analyze_video') as mock_analyze:
                        mock_analyze.return_value = {
                            'has_face': False,
                            'face_details': [],
                            'has_text': False,
                            'text_details': [],
                            'analysis_time_ms': 1000
                        }
                        
                        results = run_job(config)
                        
                        # Debe haber 2 resultados: 1 aceptado, 1 descartado
                        assert len(results) == 2
                        
                        accepted = [r for r in results if r['estado'] == 'aceptado']
                        discarded = [r for r in results if r['estado'] == 'descartado']
                        
                        assert len(accepted) == 1
                        assert len(discarded) == 1
                        
                        assert accepted[0]['titulo'] == 'Test Video 1'
                        assert 'orientacion horizontal' in discarded[0]['razones']

if __name__ == '__main__':
    pytest.main([__file__])
