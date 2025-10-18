"""
Configuración central del VideoFinder AI Bot
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Directorios
TEMP_DIR = os.getenv("TEMP_DIR", "tmp")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "results.json")
ACCEPTED_LIST = os.path.join(OUTPUT_DIR, "accepted_list.txt")

# Configuración de análisis de video
VIDEO_SAMPLE_STRATEGY = {
    "short": {"max_dur": 60, "fps_factor": float(os.getenv("FPS_SAMPLE_FACTOR_SHORT", "0.5"))},
    "medium": {"max_dur": 300, "fps_factor": float(os.getenv("FPS_SAMPLE_FACTOR_MEDIUM", "1.0"))},
    "long": {"fps_factor": float(os.getenv("FPS_SAMPLE_FACTOR_LONG", "2.0"))}
}

# Configuración de detección
FACE_CONFIDENCE = float(os.getenv("FACE_CONFIDENCE", "0.45"))
OCR_CONFIDENCE = float(os.getenv("OCR_CONFIDENCE", "0.5"))
MIN_TEXT_LENGTH = int(os.getenv("MIN_TEXT_LENGTH", "2"))

# Configuración de GPU
USE_GPU = os.getenv("USE_GPU", "False").lower() == "true"

# Configuración de Tesseract
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "C:\\Program Files\\Tesseract-OCR\\tesseract.exe")

# Configuración de descarga
DOWNLOAD_TIMEOUT = int(os.getenv("DOWNLOAD_TIMEOUT", "300"))
MAX_DURATION = int(os.getenv("MAX_DURATION", "600"))

# Configuración de scraping
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "1.0"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Configuración de filtros
REJECT_ON_PERSON_CLASS = False
FRAME_CONFIRMATION_WINDOW = 2

# Límites por defecto
DEFAULT_MAX_RESULTS = 50
FINAL_RESULTS_LIMIT = None  # None => list all accepted

# Configuración de yt-dlp
YT_DLP_OPTIONS = {
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    'writeinfojson': False,
    'writesubtitles': False,
    'writeautomaticsub': False,
    'ignoreerrors': True,
    'no_check_certificate': True,
    'prefer_insecure': False,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Configuración de scraping por plataforma
PLATFORM_CONFIGS = {
    'youtube': {
        'enabled': True,
        'max_results': DEFAULT_MAX_RESULTS,
        'search_type': 'video',
        'order': 'relevance'
    },
    'instagram': {
        'enabled': True,
        'max_results': DEFAULT_MAX_RESULTS,
        'hashtag_search': True
    },
    'tiktok': {
        'enabled': True,
        'max_results': DEFAULT_MAX_RESULTS,
        'search_type': 'video'
    }
}

# Configuración de logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Configuración de análisis optimizado
ANALYSIS_CONFIG = {
    'enable_keyframe_boost': True,
    'enable_sliding_window': True,
    'enable_multi_scale_detection': True,
    'preprocessing': {
        'resize_max': 1920,
        'grayscale': True,
        'bilateral_filter': True,
        'adaptive_threshold': True
    }
}

# Configuración de salida
OUTPUT_CONFIG = {
    'include_raw_metadata': False,
    'include_analysis_timing': True,
    'include_confidence_scores': True,
    'save_individual_results': False
}

# Validación de configuración
def validate_config():
    """Valida la configuración y crea directorios necesarios"""
    import os
    
    # Crear directorios si no existen
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Validar Tesseract
    if not os.path.exists(TESSERACT_CMD):
        print(f"⚠️  Advertencia: Tesseract no encontrado en {TESSERACT_CMD}")
        print("   Asegúrate de instalar Tesseract OCR y configurar TESSERACT_CMD en .env")
    
    # Validar FFmpeg
    import subprocess
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        subprocess.run(['ffprobe', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Advertencia: FFmpeg no encontrado en PATH")
        print("   Asegúrate de instalar FFmpeg y agregarlo al PATH")
    
    return True

# Configuración de modelos
MODEL_CONFIGS = {
    'yolo_face': {
        'model_path': 'yolov8n.pt',
        'confidence_threshold': FACE_CONFIDENCE,
        'device': 'cuda' if USE_GPU else 'cpu'
    },
    'easyocr': {
        'languages': ['en', 'es'],
        'gpu': USE_GPU,
        'model_storage_directory': os.path.join(TEMP_DIR, 'easyocr_models')
    },
    'tesseract': {
        'config': '--psm 6 --oem 3',
        'lang': 'eng+spa'
    }
}
