"""
Instagram Scraper usando instaloader y playwright
"""

import time
import json
from typing import List, Dict, Any
from rich.console import Console

from config import REQUEST_DELAY, MAX_RETRIES

console = Console()

def search_instagram(keyword: str, max_results: int = 50) -> List[Dict]:
    """
    Busca videos en Instagram usando instaloader
    
    Args:
        keyword: Palabra clave de búsqueda (hashtag)
        max_results: Máximo número de resultados
        
    Returns:
        Lista de diccionarios con metadatos de videos
    """
    console.print(f"  [blue]Buscando en Instagram: '{keyword}' (max: {max_results})[/blue]")
    
    try:
        # Limpiar keyword para hashtag
        hashtag = keyword.replace('#', '').replace(' ', '').lower()
        
        # Intentar con instaloader primero
        videos = search_instagram_hashtag(hashtag, max_results)
        
        if not videos:
            # Fallback a búsqueda general
            videos = search_instagram_general(keyword, max_results)
        
        console.print(f"  [green]✓ Instagram: {len(videos)} videos encontrados[/green]")
        return videos
        
    except Exception as e:
        console.print(f"  [red]✗ Instagram: Error - {str(e)}[/red]")
        return []

def search_instagram_hashtag(hashtag: str, max_results: int) -> List[Dict]:
    """
    Busca videos por hashtag en Instagram usando instaloader
    
    Args:
        hashtag: Hashtag a buscar
        max_results: Máximo número de resultados
        
    Returns:
        Lista de videos encontrados
    """
    try:
        import instaloader
        
        # Configurar instaloader
        loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )
        
        # Buscar por hashtag
        hashtag_obj = instaloader.Hashtag.from_name(loader.context, hashtag)
        videos = []
        
        count = 0
        for post in hashtag_obj.get_posts():
            if count >= max_results:
                break
                
            # Solo videos
            if post.is_video:
                video_data = parse_instagram_post(post)
                if video_data:
                    videos.append(video_data)
                    count += 1
            
            time.sleep(REQUEST_DELAY)
        
        return videos
        
    except Exception as e:
        console.print(f"  [yellow]Error con instaloader: {str(e)}[/yellow]")
        return []

def search_instagram_general(keyword: str, max_results: int) -> List[Dict]:
    """
    Búsqueda general en Instagram usando playwright
    
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
            
            # Navegar a Instagram
            page.goto(f"https://www.instagram.com/explore/tags/{keyword.replace(' ', '')}/")
            page.wait_for_load_state('networkidle')
            
            # Buscar videos en la página
            video_elements = page.query_selector_all('video')
            
            for i, video_elem in enumerate(video_elements[:max_results]):
                try:
                    # Obtener información del video
                    video_data = extract_instagram_video_data(page, video_elem, i)
                    if video_data:
                        videos.append(video_data)
                except Exception as e:
                    console.print(f"  [yellow]Error extrayendo video {i}: {str(e)}[/yellow]")
                    continue
            
            browser.close()
        
        return videos
        
    except Exception as e:
        console.print(f"  [yellow]Error con playwright: {str(e)}[/yellow]")
        return []

def parse_instagram_post(post) -> Dict:
    """
    Parsea un post de Instagram a formato estándar
    
    Args:
        post: Objeto post de instaloader
        
    Returns:
        Diccionario con metadatos del video
    """
    try:
        return {
            'id': post.shortcode,
            'title': post.caption[:100] if post.caption else 'Sin título',
            'url': f"https://www.instagram.com/p/{post.shortcode}/",
            'platform': 'instagram',
            'duration': post.video_duration or 0,
            'width': post.video_width or 0,
            'height': post.video_height or 0,
            'view_count': 0,  # No disponible en instaloader
            'uploader': post.owner_username,
            'upload_date': post.date_utc.isoformat() if post.date_utc else '',
            'description': post.caption or '',
            'tags': [],
            'thumbnail': post.url,
            'raw_data': {
                'shortcode': post.shortcode,
                'likes': post.likes,
                'comments': post.comments,
                'is_video': post.is_video
            }
        }
    except Exception as e:
        console.print(f"  [yellow]Error parseando post de Instagram: {str(e)}[/yellow]")
        return None

def extract_instagram_video_data(page, video_elem, index: int) -> Dict:
    """
    Extrae datos de un elemento de video de Instagram
    
    Args:
        page: Página de playwright
        video_elem: Elemento de video
        index: Índice del video
        
    Returns:
        Diccionario con metadatos del video
    """
    try:
        # Obtener información básica
        video_src = video_elem.get_attribute('src') or ''
        
        # Buscar información adicional en el DOM
        parent = video_elem.query_selector('xpath=..')
        caption_elem = parent.query_selector('[data-testid="post-caption"]') if parent else None
        caption = caption_elem.inner_text() if caption_elem else ''
        
        return {
            'id': f"instagram_{index}",
            'title': caption[:100] if caption else f'Video de Instagram {index}',
            'url': page.url,
            'platform': 'instagram',
            'duration': 0,  # No disponible sin análisis
            'width': 0,     # No disponible sin análisis
            'height': 0,    # No disponible sin análisis
            'view_count': 0,
            'uploader': 'unknown',
            'upload_date': '',
            'description': caption,
            'tags': [],
            'thumbnail': video_src,
            'raw_data': {
                'video_src': video_src,
                'index': index
            }
        }
        
    except Exception as e:
        console.print(f"  [yellow]Error extrayendo datos de video: {str(e)}[/yellow]")
        return None

def get_instagram_video_metadata(url: str) -> Dict:
    """
    Obtiene metadatos de un video específico de Instagram
    
    Args:
        url: URL del video de Instagram
        
    Returns:
        Diccionario con metadatos del video
    """
    try:
        import instaloader
        
        loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )
        
        # Extraer shortcode de la URL
        shortcode = url.split('/p/')[-1].split('/')[0]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        
        return parse_instagram_post(post)
        
    except Exception as e:
        console.print(f"  [red]Error obteniendo metadatos de Instagram: {str(e)}[/red]")
        return {}
