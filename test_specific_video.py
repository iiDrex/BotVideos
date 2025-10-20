#!/usr/bin/env python3
"""
Script de prueba para un video específico
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator import run_job
from config import validate_config

def test_specific_video():
    """Prueba el bot con un video específico"""
    
    # Configuración de prueba
    config = {
        'keyword': 'test video',
        'platforms': ['youtube'],
        'max_results': 1,
        'duration_range': (10, 60),
        'filters': {
            'no_faces': True,
            'no_text': True,
            'min_duration': 10,
            'max_duration': 60
        }
    }
    
    # URL específica para probar
    test_url = "https://www.youtube.com/shorts/qYxxgkSvwto"
    
    print("=" * 60)
    print("PRUEBA DE FILTRO DE TEXTO ULTRA PROFESIONAL")
    print("=" * 60)
    print(f"Video de prueba: {test_url}")
    print("=" * 60)
    
    try:
        # Validar configuración
        validate_config()
        
        # Simular metadata del video
        test_metadata = [{
            'id': 'qYxxgkSvwto',
            'title': 'Test Video for Text Detection',
            'url': test_url,
            'platform': 'youtube',
            'duration': 30.0,
            'width': 1080,
            'height': 1920,
            'view_count': 1000,
            'uploader': 'Test Channel',
            'upload_date': '2024-01-01',
            'description': 'Test video for text detection',
            'tags': ['test'],
            'thumbnail': '',
            'raw_data': {}
        }]
        
        print("Iniciando análisis del video...")
        print("Configuración del filtro:")
        print(f"   • Confianza OCR: 0.1 (10%)")
        print(f"   • Longitud mínima: 1 carácter")
        print(f"   • Frames máximos: 20")
        print(f"   • Muestreo: cada 1 segundo")
        print(f"   • Capas de detección: 7")
        print("=" * 60)
        
        # Importar los módulos necesarios
        from downloader import VideoDownloader
        from analyzer.video_analyzer import EnhancedVideoAnalyzer
        from config import TEMP_DIR
        
        # Inicializar componentes
        downloader = VideoDownloader()
        analyzer = EnhancedVideoAnalyzer(config)
        
        print("Descargando video...")
        temp_path = downloader.download_temporal(test_url)
        
        if not temp_path:
            print("Error: No se pudo descargar el video")
            return
        
        print(f"Video descargado: {temp_path}")
        
        print("Analizando video con filtro ultra profesional...")
        print("   • CAPA 1: Tesseract OCR")
        print("   • CAPA 2: EasyOCR")
        print("   • CAPA 3: Patrones visuales")
        print("   • CAPA 4: Análisis de bordes")
        print("   • CAPA 5: Cualquier tipo de fuente")
        print("   • CAPA 6: Texto estilizado")
        print("   • CAPA 7: Texto rotado")
        
        # Analizar video
        analysis = analyzer.analyze_video(temp_path)
        
        print("=" * 60)
        print("RESULTADOS DEL ANALISIS:")
        print("=" * 60)
        
        if analysis.get('estado') == 'descartado':
            print("VIDEO RECHAZADO")
            razones = analysis.get('razones', [])
            print(f"Razones: {', '.join(razones)}")
            
            if 'texto detectado' in razones:
                print("DETALLES DE TEXTO DETECTADO:")
                text_details = analysis.get('text_details', [])
                for i, text in enumerate(text_details, 1):
                    print(f"   {i}) Texto: '{text.get('text', 'N/A')}'")
                    print(f"      Confianza: {text.get('confidence', 'N/A')}")
                    print(f"      Metodo: {text.get('method', 'N/A')}")
                    print(f"      Bbox: {text.get('bbox', 'N/A')}")
        else:
            print("VIDEO ACEPTADO")
            print("No se detecto texto en el video")
        
        print("=" * 60)
        print("Limpiando archivos temporales...")
        
        # Limpiar archivo temporal
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print("Archivo temporal eliminado")
        
        print("Prueba completada")
        
    except Exception as e:
        print(f"Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_specific_video()
