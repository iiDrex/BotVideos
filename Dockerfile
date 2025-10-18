# Dockerfile para VideoFinder AI Bot
FROM python:3.12-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-spa \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración
COPY requirements.txt .
COPY .env.example .env

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Playwright
RUN playwright install chromium
RUN playwright install-deps

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p tmp outputs

# Configurar variables de entorno
ENV TESSERACT_CMD=/usr/bin/tesseract
ENV TEMP_DIR=tmp
ENV OUTPUT_DIR=outputs
ENV USE_GPU=False

# Exponer puerto (opcional para web interface)
EXPOSE 8000

# Comando por defecto
CMD ["python", "final_bot.py"]
