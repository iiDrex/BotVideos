#!/usr/bin/env python3
"""
Script para verificar configuración de GPU
"""

def check_pytorch():
    """Verifica si PyTorch está instalado"""
    try:
        import torch
        print(f"OK - PyTorch instalado: {torch.__version__}")
        return True
    except ImportError:
        print("ERROR - PyTorch no instalado")
        return False

def check_cuda():
    """Verifica si CUDA está disponible"""
    try:
        import torch
        if torch.cuda.is_available():
            print(f"OK - CUDA disponible: {torch.cuda.get_device_name(0)}")
            print(f"OK - Número de GPUs: {torch.cuda.device_count()}")
            print(f"OK - Versión CUDA: {torch.version.cuda}")
            return True
        else:
            print("ERROR - CUDA no disponible")
            return False
    except ImportError:
        print("ERROR - PyTorch no instalado")
        return False

def check_ultralytics():
    """Verifica si Ultralytics está instalado"""
    try:
        from ultralytics import YOLO
        print("OK - Ultralytics instalado")
        return True
    except ImportError:
        print("ERROR - Ultralytics no instalado")
        return False

def check_easyocr():
    """Verifica si EasyOCR está instalado"""
    try:
        import easyocr
        print("OK - EasyOCR instalado")
        return True
    except ImportError:
        print("ERROR - EasyOCR no instalado")
        return False

def main():
    print("=" * 50)
    print("Verificación de GPU y Dependencias")
    print("=" * 50)
    
    pytorch_ok = check_pytorch()
    cuda_ok = check_cuda()
    ultralytics_ok = check_ultralytics()
    easyocr_ok = check_easyocr()
    
    print("\n" + "=" * 50)
    print("Resumen:")
    print("=" * 50)
    
    if pytorch_ok and cuda_ok:
        print("OK - GPU está listo para usar")
    elif pytorch_ok:
        print("WARNING - PyTorch instalado pero CUDA no disponible")
        print("   Instala PyTorch con soporte CUDA:")
        print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    else:
        print("ERROR - PyTorch no instalado")
        print("   Instala PyTorch con soporte CUDA:")
        print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    
    if ultralytics_ok:
        print("OK - Ultralytics listo")
    else:
        print("ERROR - Instala Ultralytics: pip install ultralytics")
    
    if easyocr_ok:
        print("OK - EasyOCR listo")
    else:
        print("ERROR - Instala EasyOCR: pip install easyocr")

if __name__ == "__main__":
    main()
