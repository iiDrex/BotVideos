"""
TikTok Scraper usando playwright y requests
"""

import time
import json
import re
from typing import List, Dict, Any
from rich.console import Console

from config import REQUEST_DELAY, MAX_RETRIES

console = Console()

def search_tiktok(keyword: str, max_results: int = 50) -> List[Dict]:
    """
    Busca videos en TikTok usando playwright
    
    Args:
        keyword: Palabra clave de búsqueda
        max_results: Máximo número de resultados
        
    Returns:
        Lista de diccionarios con metadatos de videos
    """
    console.print(f"  [blue]Buscando en TikTok: '{keyword}' (max: {max_results})[/blue]")
    
    try:
        videos = search_tiktok_with_playwright(keyword, max_results)
        
        if not videos:
            # Fallback a búsqueda con requests
            videos = search_tiktok_with_requests(keyword, max_results)
        
        console.print(f"  [green]✓ TikTok: {len(videos)} videos encontrados[/green]")
        return videos
        
    except Exception as e:
        console.print(f"  [red]✗ TikTok: Error - {str(e)}[/red]")
        return []

def search_tiktok_with_playwright(keyword: str, max_results: int) -> List[Dict]:
    """
    Busca videos en TikTok usando playwright
    
    Args:
        keyword: Palabra clave de búsqueda
        max_results: Máximo número de resultados
        
    Returns:
        Lista de videos encontrados
    """
    try:
        from playwright.sync_api import sync_playwright
        
        videos = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Configurar user agent
            page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            # Navegar a TikTok
            search_url = f"https://www.tiktok.com/search?q={keyword.replace(' ', '%20')}"
            page.goto(search_url)
            page.wait_for_load_state('networkidle')
            
            # Esperar a que carguen los videos
            page.wait_for_selector('[data-e2e="search-card-item"]', timeout=10000)
            
            # Buscar elementos de video
            video_elements = page.query_selector_all('[data-e2e="search-card-item"]')
            
            for i, video_elem in enumerate(video_elements[:max_results]):
                try:
                    video_data = extract_tiktok_video_data(page, video_elem, i)
                    if video_data:
                        videos.append(video_data)
                except Exception as e:
                    console.print(f"  [yellow]Error extrayendo video {i}: {str(e)}[/yellow]")
                    continue
                
                time.sleep(REQUEST_DELAY)
            
            browser.close()
        
        return videos
        
    except Exception as e:
        console.print(f"  [yellow]Error con playwright en TikTok: {str(e)}[/yellow]")
        return []

def search_tiktok_with_requests(keyword: str, max_results: int) -> List[Dict]:
    """
    Búsqueda alternativa en TikTok usando requests
    
    Args:
        keyword: Palabra clave de búsqueda
        max_results: Máximo número de resultados
        
    Returns:
        Lista de videos encontrados
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        search_url = f"https://www.tiktok.com/search?q={keyword.replace(' ', '%20')}"
        
        response = requests.get(search_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        videos = []
        
        # Buscar elementos de video en el HTML
        video_links = soup.find_all('a', href=re.compile(r'/video/'))
        
        for i, link in enumerate(video_links[:max_results]):
            try:
                video_data = parse_tiktok_link(link, i)
                if video_data:
                    videos.append(video_data)
            except Exception as e:
                console.print(f"  [yellow]Error parseando link {i}: {str(e)}[/yellow]")
                continue
        
        return videos
        
    except Exception as e:
        console.print(f"  [yellow]Error con requests en TikTok: {str(e)}[/yellow]")
        return []

def extract_tiktok_video_data(page, video_elem, index: int) -> Dict:
    """
    Extrae datos de un elemento de video de TikTok
    
    Args:
        page: Página de playwright
        video_elem: Elemento de video
        index: Índice del video
        
    Returns:
        Diccionario con metadatos del video
    """
    try:
        # Obtener enlace del video
        link_elem = video_elem.query_selector('a')
        video_url = link_elem.get_attribute('href') if link_elem else ''
        
        if not video_url.startswith('http'):
            video_url = f"https://www.tiktok.com{video_url}"
        
        # Obtener información adicional
        title_elem = video_elem.query_selector('[data-e2e="search-card-desc"]')
        title = title_elem.inner_text() if title_elem else f'Video de TikTok {index}'
        
        user_elem = video_elem.query_selector('[data-e2e="search-card-user-unique-id"]')
        user = user_elem.inner_text() if user_elem else 'unknown'
        
        # Obtener thumbnail
        img_elem = video_elem.query_selector('img')
        thumbnail = img_elem.get_attribute('src') if img_elem else ''
        
        return {
            'id': f"tiktok_{index}",
            'title': title[:100] if title else f'Video de TikTok {index}',
            'url': video_url,
            'platform': 'tiktok',
            'duration': 0,  # No disponible sin análisis
            'width': 0,     # No disponible sin análisis
            'height': 0,    # No disponible sin análisis
            'view_count': 0,
            'uploader': user,
            'upload_date': '',
            'description': title,
            'tags': [],
            'thumbnail': thumbnail,
            'raw_data': {
                'index': index,
                'user': user
            }
        }
        
    except Exception as e:
        console.print(f"  [yellow]Error extrayendo datos de video TikTok: {str(e)}[/yellow]")
        return None

def parse_tiktok_link(link_elem, index: int) -> Dict:
    """
    Parsea un enlace de video de TikTok
    
    Args:
        link_elem: Elemento de enlace
        index: Índice del video
        
    Returns:
        Diccionario con metadatos del video
    """
    try:
        video_url = link_elem.get('href', '')
        if not video_url.startswith('http'):
            video_url = f"https://www.tiktok.com{video_url}"
        
        # Extraer ID del video de la URL
        video_id = video_url.split('/video/')[-1].split('?')[0] if '/video/' in video_url else f"tiktok_{index}"
        
        return {
            'id': video_id,
            'title': f'Video de TikTok {index}',
            'url': video_url,
            'platform': 'tiktok',
            'duration': 0,
            'width': 0,
            'height': 0,
            'view_count': 0,
            'uploader': 'unknown',
            'upload_date': '',
            'description': '',
            'tags': [],
            'thumbnail': '',
            'raw_data': {
                'index': index,
                'video_id': video_id
            }
        }
        
    except Exception as e:
        console.print(f"  [yellow]Error parseando enlace TikTok: {str(e)}[/yellow]")
        return None

def get_tiktok_video_metadata(url: str) -> Dict:
    """
    Obtiene metadatos de un video específico de TikTok
    
    Args:
        url: URL del video de TikTok
        
    Returns:
        Diccionario con metadatos del video
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extraer información del video
        title = soup.find('title')
        title_text = title.get_text() if title else 'Sin título'
        
        # Buscar metadatos en JSON-LD
        json_scripts = soup.find_all('script', type='application/ld+json')
        video_data = {}
        
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get('@type') == 'VideoObject':
                    video_data = data
                    break
            except json.JSONDecodeError:
                continue
        
        return {
            'id': url.split('/video/')[-1].split('?')[0] if '/video/' in url else 'unknown',
            'title': title_text,
            'url': url,
            'platform': 'tiktok',
            'duration': video_data.get('duration', 0),
            'width': video_data.get('width', 0),
            'height': video_data.get('height', 0),
            'view_count': 0,
            'uploader': video_data.get('author', {}).get('name', 'unknown'),
            'upload_date': video_data.get('uploadDate', ''),
            'description': video_data.get('description', ''),
            'tags': [],
            'thumbnail': video_data.get('thumbnailUrl', ''),
            'raw_data': video_data
        }
        
    except Exception as e:
        console.print(f"  [red]Error obteniendo metadatos de TikTok: {str(e)}[/red]")
        return {}
