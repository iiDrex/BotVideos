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

# Configuración de análisis de video - ULTRA MEGA VELOCIDAD
# Forzar valores ultra optimizados para velocidad máxima
VIDEO_SAMPLE_STRATEGY = {
    "short": {"max_dur": 60, "fps_factor": 10.0},  # ULTRA AGRESIVO
    "medium": {"max_dur": 300, "fps_factor": 15.0},  # ULTRA AGRESIVO
    "long": {"fps_factor": 20.0}  # MEGA AGRESIVO
}

# Configuración de detección
FACE_CONFIDENCE = float(os.getenv("FACE_CONFIDENCE", "0.45"))
OCR_CONFIDENCE = float(os.getenv("OCR_CONFIDENCE", "0.1"))  # EXTREMO - detecta TODO
MIN_TEXT_LENGTH = int(os.getenv("MIN_TEXT_LENGTH", "1"))  # Mínimo 1 carácter

# Configuración de GPU - FORZAR SIEMPRE GPU
def _check_gpu_availability():
    """Verifica si CUDA está disponible y fuerza GPU"""
    try:
        import torch
        if torch.cuda.is_available():
            print(f"[OK] GPU CUDA disponible: {torch.cuda.get_device_name(0)}")
            return True
        else:
            print("[WARN] CUDA no disponible, pero FORZANDO GPU...")
            return True  # Forzar GPU incluso si CUDA no está disponible
    except ImportError:
        print("[WARN] PyTorch no instalado, pero FORZANDO GPU...")
        return True  # Forzar GPU

# FORZAR SIEMPRE GPU - NO PERMITIR CPU
USE_GPU = True  # Forzar siempre GPU
_check_gpu_availability()

# Configuración de Tesseract
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "C:\\Program Files\\Tesseract-OCR\\tesseract.exe")

# Configuración de descarga - ULTRA RÁPIDO
DOWNLOAD_TIMEOUT = 30  # ULTRA REDUCIDO - forzar valor
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

# Configuración de análisis optimizado - ULTRA MEGA VELOCIDAD
ANALYSIS_CONFIG = {
    'enable_keyframe_boost': True,
    'enable_sliding_window': False,  # Deshabilitado para velocidad
    'enable_multi_scale_detection': False,  # Deshabilitado para velocidad
    'enable_early_exit': True,  # Salir temprano si detecta algo
    'max_frames_to_process': 15,  # OPTIMIZADO para velocidad masiva
    'preprocessing': {
        'resize_max': 320,  # ULTRA REDUCIDO para velocidad máxima
        'grayscale': True,
        'bilateral_filter': False,  # Deshabilitado para velocidad
        'adaptive_threshold': False  # Deshabilitado para velocidad
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
        'config': '--psm 13 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?@#$%^&*()_+-=[]{}|;:,.<>?/~`"\'\\/',
        'lang': 'eng+spa'
    }
}
