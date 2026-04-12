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

        return {
            "title": soup.title.string if soup.title else "",
            "headings": headings[:20],
            "paragraphs": paragraphs[:20],
            "ctas": list(set(ctas))[:10]
        }
    except Exception as e:
        return {"error": str(e), "title": "", "headings": [], "paragraphs": [], "ctas": []}
