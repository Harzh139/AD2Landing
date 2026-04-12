import requests
from bs4 import BeautifulSoup
import re

def scrape_landing_page(url: str) -> dict:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        if not url.startswith('http'):
            url = 'https://' + url
            
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Clean script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        headings = []
        for tag in ['h1', 'h2', 'h3']:
            for h in soup.find_all(tag):
                text = h.get_text(strip=True)
                if text:
                    headings.append(text)
        
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if text and len(text) > 20: 
                paragraphs.append(text)
                
        ctas = []
        for btn in soup.find_all(['a', 'button']):
            text = btn.get_text(strip=True)
            if text and len(text) < 30:
                ctas.append(text)

        # Extract media (images, gifs, videos)
        media = []
        from urllib.parse import urljoin
        
        # 1. Images and GIFs
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                # Resolve URL
                absolute_url = urljoin(url, src)
                if not absolute_url.startswith('http'): continue
                
                # Check for GIF
                is_gif = absolute_url.lower().endswith('.gif')
                
                # Filter out small icons if not a GIF
                if not is_gif:
                    width = img.get('width', '100')
                    height = img.get('height', '100')
                    try:
                        if int(width.replace('px','')) < 50 or int(height.replace('px','')) < 50:
                            continue
                    except: pass
                
                media.append({
                    "type": "gif" if is_gif else "image",
                    "url": absolute_url,
                    "alt": img.get('alt', '')
                })

        # 2. Videos
        for video in soup.find_all('video'):
            v_src = video.get('src')
            if not v_src:
                source = video.find('source')
                if source: v_src = source.get('src')
            
            if v_src:
                absolute_url = urljoin(url, v_src)
                if absolute_url.startswith('http'):
                    media.append({
                        "type": "video",
                        "url": absolute_url,
                        "poster": urljoin(url, video.get('poster', ''))
                    })

        return {
            "title": soup.title.string if soup.title else "",
            "headings": headings[:20],
            "paragraphs": paragraphs[:20],
            "ctas": list(set(ctas))[:10],
            "media": media[:20]
        }
    except Exception as e:
        return {"error": str(e), "title": "", "headings": [], "paragraphs": [], "ctas": []}
