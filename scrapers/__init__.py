"""
Scrapers para diferentes plataformas de video
"""

from .youtube_scraper import search_youtube
from .instagram_scraper import search_instagram
from .tiktok_scraper import search_tiktok

__all__ = ['search_youtube', 'search_instagram', 'search_tiktok']
