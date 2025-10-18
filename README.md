# VideoFinder AI Bot

Automatizador de contenido vertical sin rostros ni texto para YouTube, TikTok e Instagram.

## Características

- 🔍 Búsqueda automática por palabra clave
- 📱 Filtrado estricto: solo videos verticales, sin rostros, sin texto
- 🎯 Análisis optimizado del video completo
- 📊 Reportes detallados en JSON y listados enumerados
- 🖥️ Ejecución local en Windows 10

## Instalación

### Prerrequisitos del Sistema

#### 1. FFmpeg
```bash
# Descargar desde https://ffmpeg.org/download.html
# O usar chocolatey:
choco install ffmpeg

# Verificar instalación:
ffmpeg -version
ffprobe -version
```

#### 2. Tesseract OCR
```bash
# Descargar desde https://github.com/UB-Mannheim/tesseract/wiki
# Instalar en C:\Program Files\Tesseract-OCR\
# O usar chocolatey:
choco install tesseract
```

#### 3. Python 3.12
```bash
# Verificar versión:
python --version
```

### Instalación del Proyecto

1. **Clonar el repositorio:**
```bash
git clone <repository-url>
cd videofinder
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno:**
```bash
# Copiar archivo de ejemplo
copy .env.example .env

# Editar .env con tus rutas:
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

5. **Instalar Playwright (para TikTok/Instagram):**
```bash
playwright install
```

## Uso

### Ejecución básica:
```bash
python final_bot.py
```

### Ejemplo de sesión:
```
[VideoFinder AI Bot]
Ingrese palabra clave o búsqueda: Crochet y amigurumis
Ingrese rango de duración (segundos) MIN-MAX, ej 30-60: 30-60
Filtros a aplicar (separar por coma, 'todos' o 'none'): todos
Plataformas (youtube,instagram,tiktok): youtube,instagram
Máx resultados por plataforma [default 50]: 30

Resumen:
  - Keyword: Crochet y amigurumis
  - Duracion: 30-60 s
  - Filtros: vertical, faces, text
  - Plataformas: youtube, instagram
  - Max per platform: 30

Confirmar? (Y/n): Y
```

## Estructura del Proyecto

```
videofinder/
├─ README.md
├─ requirements.txt
├─ Dockerfile
├─ .env.example
├─ config.py
├─ final_bot.py          # CLI entrypoint
├─ orchestrator.py       # Lógica principal
├─ scrapers/             # Scrapers por plataforma
├─ downloader.py         # Descarga de videos
├─ analyzer/             # Análisis de video
├─ utils/                # Utilidades
├─ cleaners.py           # Limpieza de archivos
├─ outputs/              # Resultados
└─ tests/                # Tests
```

## Configuración

Edita `config.py` para ajustar parámetros:

- `FACE_CONFIDENCE`: Confianza mínima para detección de rostros (0.45)
- `OCR_CONFIDENCE`: Confianza mínima para detección de texto (0.5)
- `MIN_TEXT_LENGTH`: Longitud mínima de texto (2 caracteres)
- `USE_GPU`: Usar GPU si está disponible (False)

## Salidas

### JSON de Resultados (`outputs/results.json`)
Contiene todos los videos analizados con metadatos completos y razones de aceptación/rechazo.

### Lista Aceptada (`outputs/accepted_list.txt`)
Lista enumerada de videos que pasaron todos los filtros.

## Tests

```bash
# Ejecutar todos los tests:
pytest tests/

# Test específico:
pytest tests/test_integration.py
```

## Docker (Opcional)

```bash
# Construir imagen:
docker build -t videofinder .

# Ejecutar:
docker run -v $(pwd)/outputs:/app/outputs videofinder
```

## Notas Legales

Este software es para uso educativo y de investigación. Respeta los términos de servicio de las plataformas y las leyes de derechos de autor. El usuario es responsable del uso ético de esta herramienta.

## Troubleshooting

### Error: "tesseract not found"
- Verifica que Tesseract esté instalado
- Actualiza `TESSERACT_CMD` en `.env`

### Error: "ffmpeg not found"
- Instala FFmpeg y agrégalo al PATH
- Reinicia la terminal

### Error de memoria en análisis
- Reduce `max_results` en la configuración
- Aumenta `FPS_SAMPLE_FACTOR` para menos frames

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request
