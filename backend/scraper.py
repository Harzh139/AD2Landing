import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

def scrape_landing_page(url: str) -> dict:
    try:
        if not url.startswith('http'):
            url = 'https://' + url
            
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        response = requests.get(url, headers=headers, timeout=15)
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

        # Extract Media (Images, GIFs, Videos)
        media = []
        
        # 1. Image Search (including sources, data-src, etc)
        img_tags = soup.find_all(['img', 'source'])
        for img in img_tags:
            src = img.get('src') or img.get('data-src') or img.get('srcset', '').split(' ')[0]
            if src:
                absolute_url = urljoin(url, src)
                if not absolute_url.startswith('http'): continue
                
                is_gif = absolute_url.lower().endswith('.gif')
                media.append({
                    "type": "gif" if is_gif else "image",
                    "url": absolute_url,
                    "alt": img.get('alt', '')
                })

        # 2. Video Search
        video_tags = soup.find_all(['video', 'iframe', 'source'])
        for v in video_tags:
            # If it's a source, only if parent is video
            if v.name == 'source' and v.parent.name != 'video':
                continue
                
            src = v.get('src') or v.get('data-src')
            if src:
                absolute_url = urljoin(url, src)
                if absolute_url.startswith('http'):
                    # Basic check if it's likely a video file or embed
                    if any(ext in absolute_url.lower() for ext in ['.mp4', '.webm', '.ogg', 'youtube', 'vimeo']):
                        media.append({
                            "type": "video",
                            "url": absolute_url,
                            "poster": urljoin(url, v.get('poster', '')) if v.name == 'video' else ""
                        })

        return {
            "title": soup.title.string if soup.title else "",
            "headings": headings[:20],
            "paragraphs": paragraphs[:20],
            "ctas": list(set(ctas))[:10],
            "media": media[:30]
        }
    except Exception as e:
        print(f"Scrape error for {url}: {e}")
        return {"error": str(e), "title": "", "headings": [], "paragraphs": [], "ctas": [], "media": []}
