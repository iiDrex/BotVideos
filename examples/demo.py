#!/usr/bin/env python3
"""
Demo de VideoFinder AI Bot
Ejemplo de uso programático
"""

import sys
import os
from datetime import datetime

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator import run_job
from analyzer.video_analyzer import EnhancedVideoAnalyzer
from downloader import VideoDownloader
from utils.ffprobe_utils import get_video_metadata

def demo_basic_usage():
    """Demo de uso básico"""
    print("=" * 60)
    print("🎬 VideoFinder AI Bot - Demo Básico")
    print("=" * 60)
    
    # Configuración de ejemplo
    config = {
        'keyword': 'nature landscape',
        'duration_range': (30, 120),
        'filters': {
            'vertical': True,
            'faces': True,
            'text': True
        },
        'platforms': ['youtube'],
        'max_results': 5
    }
    
    print(f"🔍 Buscando: '{config['keyword']}'")
    print(f"⏱️  Duración: {config['duration_range'][0]}-{config['duration_range'][1]}s")
    print(f"📱 Filtros: {', '.join([k for k, v in config['filters'].items() if v])}")
    print(f"🌐 Plataformas: {', '.join(config['platforms'])}")
    print(f"📊 Máximo: {config['max_results']} por plataforma")
    print()
    
    try:
        # Ejecutar análisis
        results = run_job(config)
        
        # Mostrar resultados
        print("📋 RESULTADOS:")
        print("-" * 40)
        
        accepted = [r for r in results if r.get('estado') == 'aceptado']
        discarded = [r for r in results if r.get('estado') == 'descartado']
        
        print(f"✅ Aceptados: {len(accepted)}")
        print(f"❌ Descartados: {len(discarded)}")
        print()
        
        if accepted:
            print("🎉 VIDEOS ACEPTADOS:")
            for i, video in enumerate(accepted, 1):
                print(f"{i}. {video['titulo']}")
                print(f"   🔗 {video['enlace']}")
                print(f"   ⏱️  {video['duracion_sec']}s")
                print(f"   📐 {video['resolution']}")
                print(f"   🌐 {video['platform'].title()}")
                print()
        
        if discarded:
            print("🚫 VIDEOS DESCARTADOS:")
            for i, video in enumerate(discarded, 1):
                print(f"{i}. {video['titulo']}")
                print(f"   ❌ Razones: {', '.join(video['razones'])}")
                print()
        
    except Exception as e:
        print(f"❌ Error en demo: {str(e)}")

def demo_video_analyzer():
    """Demo del analizador de video"""
    print("=" * 60)
    print("🔬 VideoFinder AI Bot - Demo Analizador")
    print("=" * 60)
    
    # Crear analizador
    analyzer = EnhancedVideoAnalyzer({})
    
    print("📊 Información del analizador:")
    info = analyzer.get_analyzer_info()
    
    print(f"  🤖 Detector de rostros: {'✓' if info['face_detector']['loaded'] else '✗'}")
    print(f"  📝 Detector de texto: {'✓' if info['text_detector']['tesseract']['available'] else '✗'}")
    print(f"  🔍 EasyOCR: {'✓' if info['text_detector']['easyocr']['available'] else '✗'}")
    print()

def demo_metadata_extraction():
    """Demo de extracción de metadatos"""
    print("=" * 60)
    print("📊 VideoFinder AI Bot - Demo Metadatos")
    print("=" * 60)
    
    # URLs de ejemplo (no funcionarán sin conexión)
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll
        "https://www.youtube.com/watch?v=9bZkp7q19f0",  # PSY - GANGNAM STYLE
    ]
    
    print("🔍 Extrayendo metadatos de URLs de ejemplo:")
    print()
    
    for url in test_urls:
        print(f"📺 {url}")
        try:
            metadata = get_video_metadata(url)
            if metadata:
                print(f"  ✅ Título: {metadata.get('title', 'N/A')}")
                print(f"  ⏱️  Duración: {metadata.get('duration', 0):.1f}s")
                print(f"  📐 Resolución: {metadata.get('width', 0)}x{metadata.get('height', 0)}")
                print(f"  🎬 FPS: {metadata.get('fps', 0):.1f}")
                print(f"  👤 Uploader: {metadata.get('uploader', 'N/A')}")
                print(f"  👀 Views: {metadata.get('view_count', 0):,}")
            else:
                print("  ❌ No se pudieron obtener metadatos")
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
        print()

def demo_configuration():
    """Demo de configuración"""
    print("=" * 60)
    print("⚙️  VideoFinder AI Bot - Demo Configuración")
    print("=" * 60)
    
    from config import (
        FACE_CONFIDENCE, OCR_CONFIDENCE, MIN_TEXT_LENGTH,
        USE_GPU, TEMP_DIR, OUTPUT_DIR, VIDEO_SAMPLE_STRATEGY
    )
    
    print("🔧 Configuración actual:")
    print(f"  🎯 Confianza rostros: {FACE_CONFIDENCE}")
    print(f"  📝 Confianza texto: {OCR_CONFIDENCE}")
    print(f"  📏 Longitud mínima texto: {MIN_TEXT_LENGTH}")
    print(f"  🖥️  Usar GPU: {USE_GPU}")
    print(f"  📁 Directorio temporal: {TEMP_DIR}")
    print(f"  📁 Directorio salida: {OUTPUT_DIR}")
    print()
    
    print("📊 Estrategia de muestreo:")
    for strategy, config in VIDEO_SAMPLE_STRATEGY.items():
        print(f"  {strategy}: {config}")
    print()

def main():
    """Función principal del demo"""
    print("🚀 VideoFinder AI Bot - Demostración")
    print("=" * 60)
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Demo de configuración
        demo_configuration()
        
        # Demo del analizador
        demo_video_analyzer()
        
        # Demo de metadatos
        demo_metadata_extraction()
        
        # Demo de uso básico (comentado para evitar requests reales)
        print("💡 Para probar el flujo completo, ejecuta:")
        print("   python final_bot.py")
        print()
        
        print("✅ Demo completado exitosamente!")
        
    except Exception as e:
        print(f"❌ Error en demo: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
