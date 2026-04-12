"""
template_builder.py — ENHANCE the real page, never build new ones.

Strategy:
  1. Parse the scraped raw_html with BeautifulSoup
  2. Fix all relative URLs → absolute so images/CSS still load
  3. Inject personalisation banner at top of <body>
  4. Replace H1 text with ad-matched headline
  5. Replace first H2 text with ad-matched subheadline  
  6. Restyle + retextthe first 3 CTA buttons/links
  7. Append benefit bar before </body>
  8. If tone=urgent → inject countdown timer
  9. Fallback standalone page ONLY if raw_html is empty
"""

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


TONE_STYLES = {
    "professional": {
        "accent": "#2563eb", "accent_text": "#ffffff",
        "banner_bg": "#1e3a8a", "banner_text": "#ffffff",
        "bar_bg": "#eff6ff", "bar_border": "#2563eb", "bar_text": "#1e3a8a",
    },
    "conversational": {
        "accent": "#059669", "accent_text": "#ffffff",
        "banner_bg": "#064e3b", "banner_text": "#ecfdf5",
        "bar_bg": "#f0fdf4", "bar_border": "#059669", "bar_text": "#065f46",
    },
    "urgent": {
        "accent": "#dc2626", "accent_text": "#ffffff",
        "banner_bg": "#7f1d1d", "banner_text": "#fff7ed",
        "bar_bg": "#fff1f2", "bar_border": "#dc2626", "bar_text": "#991b1b",
    },
    "luxury": {
        "accent": "#b8972a", "accent_text": "#000000",
        "banner_bg": "#1a1208", "banner_text": "#d4af37",
        "bar_bg": "#0f0a00", "bar_border": "#b8972a", "bar_text": "#d4af37",
    },
}


def _ts(tone: str) -> dict:
    for k in TONE_STYLES:
        if k in tone.lower():
            return TONE_STYLES[k]
    return TONE_STYLES["professional"]


# ── Public entry point ────────────────────────────────────────────────────────

def build_landing_page_html(
    variation_data: dict,
    tone: str,
    context: dict,
    colors: dict,
    raw_html: str = "",
    base_url: str = "",
) -> str:
    if raw_html and len(raw_html.strip()) > 500:
        return _enhance(raw_html, variation_data, tone, base_url)
    return _fallback(variation_data, tone)


# ── Core enhancer ─────────────────────────────────────────────────────────────

def _enhance(raw_html: str, vd: dict, tone: str, base_url: str) -> str:
    ts   = _ts(tone)
    hero = vd.get("hero", {})
    benefits = vd.get("benefits", [])

    headline = hero.get("headline", "")
    subhl    = hero.get("subheadline", "")
    cta_text = hero.get("cta", "")
    badge    = hero.get("badge", "")

    soup = BeautifulSoup(raw_html, "html.parser")

    # 1. Fix <base> tag so relative URLs resolve against the original site
    head = soup.find("head")
    if head:
        existing_base = soup.find("base")
        if existing_base:
            existing_base.decompose()
        if base_url:
            base_tag = soup.new_tag("base", href=base_url)
            head.insert(0, base_tag)

        # Inject our CSS
        style = soup.new_tag("style")
        style.string = _css(ts)
        head.append(style)

    body = soup.find("body")
    if not body:
        # Wrap everything
        body = soup

    # 2. Prepend personalisation banner
    banner_soup = BeautifulSoup(_banner_html(badge, headline, subhl, cta_text, ts), "html.parser")
    body.insert(0, banner_soup)

    # 3. Replace H1
    if headline:
        h1 = soup.find("h1")
        if h1:
            _set_text(h1, headline)

    # 4. Replace first H2
    if subhl:
        for h2 in soup.find_all("h2"):
            txt = h2.get_text(strip=True)
            if txt and len(txt) > 2:
                _set_text(h2, subhl)
                break

    # 5. Restyle CTA buttons/links
    if cta_text:
        _inject_ctas(soup, cta_text, ts)

    # 6. Append benefit bar
    benefit_titles = [b.get("title", "") for b in benefits if b.get("title")]
    if benefit_titles:
        bar_soup = BeautifulSoup(_bar_html(benefit_titles, ts), "html.parser")
        body.append(bar_soup)

    # 7. Append JS (countdown if urgent)
    js = soup.new_tag("script")
    js.string = _js(tone, ts)
    body.append(js)

    return str(soup)


def _set_text(tag, new_text: str):
    """Clear a tag's content and set plain text."""
    for child in list(tag.children):
        child.extract()
    tag.append(new_text)


def _inject_ctas(soup, cta_text: str, ts: dict):
    CTA_KW = {"shop","buy","get","start","try","sign","join","learn",
               "explore","discover","order","subscribe","book","apply","claim"}
    changed = 0
    for tag in soup.find_all(["a", "button"]):
        if changed >= 3:
            break
        txt = tag.get_text(strip=True).lower()
        if not txt or len(txt) > 80:
            continue
        if any(kw in txt for kw in CTA_KW):
            _set_text(tag, cta_text)
            tag["class"] = list(tag.get("class", [])) + ["ad2p-cta-injected"]
            tag["style"] = (
                f"background:{ts['accent']} !important;"
                f"color:{ts['accent_text']} !important;"
                f"border-color:{ts['accent']} !important;"
                f"font-weight:700 !important;"
                f"border-radius:6px !important;"
                f"padding:12px 28px !important;"
            )
            changed += 1


# ── HTML fragments ────────────────────────────────────────────────────────────

def _banner_html(badge, headline, subhl, cta, ts):
    badge_part = f'<span class="ad2p-badge">{badge}</span>' if badge else ""
    cta_part   = f'<a href="#" class="ad2p-bcta">{cta}</a>' if cta else ""
    hl_part    = f'<strong class="ad2p-hl">{headline}</strong>' if headline else ""
    sub_part   = f'<span class="ad2p-sub">{subhl}</span>' if subhl else ""
    return f"""<div id="ad2p-banner">
  <div class="ad2p-inner">
    {badge_part}
    <div class="ad2p-copy">{hl_part}{sub_part}</div>
    {cta_part}
  </div>
</div>"""


def _bar_html(titles, ts):
    items = "".join(
        f'<div class="ad2p-bar-item"><span class="ad2p-chk">✓</span>{t}</div>'
        for t in titles[:4]
    )
    return f'<div id="ad2p-bar"><div class="ad2p-bar-inner">{items}</div></div>'


# ── CSS ───────────────────────────────────────────────────────────────────────

def _css(ts):
    return f"""
/* ── Ad2Page Enhancement Layer ── */
#ad2p-banner{{
  width:100%;background:{ts['banner_bg']};color:{ts['banner_text']};
  padding:12px 20px;position:relative;z-index:2147483647;
  box-sizing:border-box;border-bottom:3px solid {ts['accent']};
  font-family:system-ui,sans-serif;
}}
.ad2p-inner{{
  max-width:1200px;margin:0 auto;display:flex;align-items:center;
  gap:16px;flex-wrap:wrap;justify-content:center;
}}
.ad2p-badge{{
  background:{ts['accent']};color:{ts['accent_text']};font-size:11px;
  font-weight:800;letter-spacing:.08em;text-transform:uppercase;
  padding:4px 12px;border-radius:20px;white-space:nowrap;flex-shrink:0;
}}
.ad2p-copy{{display:flex;flex-direction:column;gap:2px;text-align:center;}}
.ad2p-hl{{font-size:15px;font-weight:700;color:{ts['banner_text']};line-height:1.3;}}
.ad2p-sub{{font-size:12px;opacity:.8;color:{ts['banner_text']};}}
.ad2p-bcta{{
  background:{ts['accent']};color:{ts['accent_text']};font-size:13px;
  font-weight:700;padding:8px 20px;border-radius:6px;text-decoration:none;
  white-space:nowrap;flex-shrink:0;transition:filter .2s;
}}
.ad2p-bcta:hover{{filter:brightness(1.15);}}
#ad2p-bar{{
  width:100%;background:{ts['bar_bg']};border-top:2px solid {ts['bar_border']};
  padding:12px 20px;box-sizing:border-box;font-family:system-ui,sans-serif;
}}
.ad2p-bar-inner{{
  max-width:1100px;margin:0 auto;display:flex;gap:28px;
  flex-wrap:wrap;justify-content:center;
}}
.ad2p-bar-item{{
  font-size:13px;font-weight:600;color:{ts['bar_text']};
  display:flex;align-items:center;gap:7px;
}}
.ad2p-chk{{
  background:{ts['accent']};color:{ts['accent_text']};border-radius:50%;
  width:18px;height:18px;display:inline-flex;align-items:center;
  justify-content:center;font-size:10px;font-weight:800;flex-shrink:0;
}}
.ad2p-cta-injected{{animation:ad2p-pulse 2s ease infinite;}}
@keyframes ad2p-pulse{{
  0%,100%{{box-shadow:0 0 0 0 {ts['accent']}55;}}
  50%{{box-shadow:0 0 0 8px {ts['accent']}00;}}
}}
@media(max-width:600px){{
  .ad2p-inner{{flex-direction:column;text-align:center;}}
  .ad2p-bar-inner{{gap:14px;}}
}}
"""


# ── JS ────────────────────────────────────────────────────────────────────────

def _js(tone, ts):
    countdown = ""
    if "urgent" in tone.lower():
        countdown = f"""
  var _end=Date.now()+15*60*1000,_el=document.createElement('div');
  _el.id='ad2p-cd';
  _el.style.cssText='position:fixed;bottom:20px;right:20px;background:{ts["accent"]};'
    +'color:{ts["accent_text"]};padding:12px 20px;border-radius:10px;font-size:14px;'
    +'font-weight:700;z-index:2147483646;box-shadow:0 4px 20px rgba(0,0,0,.3);'
    +'font-family:monospace;cursor:pointer;';
  document.body.appendChild(_el);
  (function _tick(){{
    var r=_end-Date.now();
    if(r<=0){{_el.textContent='⏰ Offer Expired';return;}}
    var m=Math.floor(r/60000),s=Math.floor((r%60000)/1000);
    _el.textContent='⚡ Ends: '+m+':'+(s<10?'0'+s:s);
    setTimeout(_tick,1000);
  }})();
"""
    return f"""(function(){{
  {countdown}
  document.querySelectorAll('.ad2p-bcta').forEach(function(a){{
    a.addEventListener('click',function(e){{
      e.preventDefault();
      var t=document.querySelector('form,[class*="cta"],[id*="cta"],h1');
      if(t)t.scrollIntoView({{behavior:'smooth'}});
    }});
  }});
}})();"""


# ── Fallback page (scraping failed) ──────────────────────────────────────────

def _fallback(vd, tone):
    hero  = vd.get("hero", {})
    bens  = vd.get("benefits", [])
    fcta  = vd.get("final_cta", {})
    ts    = _ts(tone)
    cards = "".join(
        f'<div class="card"><div class="icon">✦</div>'
        f'<h3>{b.get("title","")}</h3><p>{b.get("description","")}</p></div>'
        for b in bens
    )
    return f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{hero.get('headline','Landing Page')}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:system-ui,sans-serif;background:#fff;color:#111;line-height:1.6}}
.warn{{background:{ts['banner_bg']};color:{ts['banner_text']};text-align:center;
  padding:10px;font-size:12px;border-bottom:2px solid {ts['accent']}}}
.hero{{max-width:860px;margin:80px auto;text-align:center;padding:0 24px}}
.badge{{display:inline-block;background:{ts['accent']};color:{ts['accent_text']};
  padding:5px 16px;border-radius:20px;font-size:11px;font-weight:800;
  text-transform:uppercase;letter-spacing:.08em;margin-bottom:20px}}
h1{{font-size:clamp(28px,4vw,54px);line-height:1.1;margin-bottom:16px;font-weight:800}}
.sub{{font-size:18px;color:#555;margin-bottom:30px}}
.cta{{display:inline-block;background:{ts['accent']};color:{ts['accent_text']};
  padding:14px 36px;border-radius:8px;font-size:16px;font-weight:700;text-decoration:none}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
  gap:20px;max-width:860px;margin:50px auto;padding:0 24px}}
.card{{background:#f8f9fa;border-radius:10px;padding:28px;text-align:center}}
.icon{{font-size:24px;margin-bottom:10px;color:{ts['accent']}}}
.card h3{{font-size:16px;margin-bottom:6px}}
.card p{{font-size:13px;color:#666}}
.fcta{{text-align:center;padding:50px 24px;background:{ts['banner_bg']}}}
.fcta h2{{color:{ts['banner_text']};font-size:30px;margin-bottom:20px}}
</style></head><body>
<div class="warn">⚠ Fallback mode — target URL blocked bot scraping</div>
<div class="hero">
  <div class="badge">{hero.get('badge','Special Offer')}</div>
  <h1>{hero.get('headline','Your Personalized Headline')}</h1>
  <p class="sub">{hero.get('subheadline','')}</p>
  <a href="#" class="cta">{hero.get('cta','Get Started')}</a>
</div>
<div class="cards">{cards}</div>
<div class="fcta">
  <h2>{fcta.get('headline','Ready?')}</h2>
  <a href="#" class="cta">{fcta.get('cta','Take Action')}</a>
</div>
</body></html>"""