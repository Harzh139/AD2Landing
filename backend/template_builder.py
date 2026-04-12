"""
template_builder.py
===================
PHILOSOPHY: We ENHANCE the real scraped HTML — we do NOT build new pages.

Approach:
1. Take the raw scraped HTML from the landing page
2. Parse it with BeautifulSoup
3. Surgically inject:
   - Ad-matched hero copy (h1, h2, subheadlines)
   - Personalized CTAs
   - Urgency banner (prepended to body)
   - Subtle CSS overlay for tone/color nudge
   - Sticky social-proof bar
4. Return the modified real HTML — preserving all layout, images, nav, footer
"""

from bs4 import BeautifulSoup
import re


# ─── Color palettes per tone ────────────────────────────────────────────────

TONE_STYLES = {
    "professional": {
        "accent":      "#2563eb",
        "accent_text": "#ffffff",
        "banner_bg":   "#1e3a8a",
        "banner_text": "#ffffff",
        "bar_bg":      "#f0f9ff",
        "bar_border":  "#2563eb",
        "bar_text":    "#1e3a8a",
    },
    "conversational": {
        "accent":      "#059669",
        "accent_text": "#ffffff",
        "banner_bg":   "#064e3b",
        "banner_text": "#ecfdf5",
        "bar_bg":      "#f0fdf4",
        "bar_border":  "#059669",
        "bar_text":    "#065f46",
    },
    "urgent": {
        "accent":      "#dc2626",
        "accent_text": "#ffffff",
        "banner_bg":   "#7f1d1d",
        "banner_text": "#fff7ed",
        "bar_bg":      "#fff1f2",
        "bar_border":  "#dc2626",
        "bar_text":    "#991b1b",
    },
    "luxury": {
        "accent":      "#b8972a",
        "accent_text": "#000000",
        "banner_bg":   "#1a1208",
        "banner_text": "#d4af37",
        "bar_bg":      "#0f0a00",
        "bar_border":  "#b8972a",
        "bar_text":    "#d4af37",
    },
}

FALLBACK = TONE_STYLES["professional"]


def get_tone_styles(tone: str) -> dict:
    for key in TONE_STYLES:
        if key in tone.lower():
            return TONE_STYLES[key]
    return FALLBACK


# ─── Main entry point ────────────────────────────────────────────────────────

def build_landing_page_html(
    variation_data: dict,
    tone: str,
    context: dict,
    colors: dict,
    raw_html: str = "",
) -> str:
    """
    If raw_html is available: enhance it in-place.
    Fallback: build a minimal standalone page (last resort only).
    """
    if raw_html and len(raw_html) > 500:
        return _enhance_existing_page(variation_data, tone, raw_html)
    else:
        return _build_fallback_page(variation_data, tone, colors)


# ─── Core: enhance the real page ────────────────────────────────────────────

def _enhance_existing_page(variation_data: dict, tone: str, raw_html: str) -> str:
    hero      = variation_data.get("hero", {})
    benefits  = variation_data.get("benefits", [])
    final_cta = variation_data.get("final_cta", {})
    ts        = get_tone_styles(tone)

    soup = BeautifulSoup(raw_html, "html.parser")

    # ── 1. Inject <base> so relative links/images still work ──────────────
    head = soup.find("head")
    if head and not soup.find("base"):
        base_tag = soup.new_tag("base", target="_blank")
        head.insert(0, base_tag)

    # ── 2. Inject our enhancement CSS ─────────────────────────────────────
    style_tag = soup.new_tag("style")
    style_tag.string = _enhancement_css(ts)
    if head:
        head.append(style_tag)

    body = soup.find("body")
    if not body:
        return raw_html   # can't parse, return as-is

    # ── 3. Prepend urgency/personalisation banner ─────────────────────────
    badge_text = hero.get("badge", "")
    headline   = hero.get("headline", "")
    subhl      = hero.get("subheadline", "")
    cta_text   = hero.get("cta", "")

    if badge_text or headline:
        banner = BeautifulSoup(_urgency_banner_html(badge_text, headline, subhl, cta_text, ts), "html.parser")
        body.insert(0, banner)

    # ── 4. Replace the most prominent H1 with the ad-matched headline ─────
    if headline:
        h1 = soup.find("h1")
        if h1:
            # Keep any child tags (e.g. <span>, <em>) but change the text node
            _replace_visible_text(h1, headline)

    # ── 5. Replace the first prominent H2/subheadline ─────────────────────
    if subhl:
        # Try an h2 near the top of the page
        candidates = soup.find_all("h2")
        if candidates:
            _replace_visible_text(candidates[0], subhl)

    # ── 6. Enhance CTAs — replace the first 2 primary CTAs ───────────────
    if cta_text:
        _enhance_ctas(soup, cta_text, ts)

    # ── 7. Inject social-proof / benefit bar before </body> ──────────────
    benefit_titles = [b.get("title", "") for b in benefits if b.get("title")]
    if benefit_titles:
        bar = BeautifulSoup(_benefit_bar_html(benefit_titles, ts), "html.parser")
        body.append(bar)

    # ── 8. Inject personalisation script (highlight, countdown if urgent) ─
    script_tag = soup.new_tag("script")
    script_tag.string = _personalisation_js(tone, ts)
    body.append(script_tag)

    return str(soup)


# ─── Text replacement helper ─────────────────────────────────────────────────

def _replace_visible_text(tag, new_text: str):
    """Replace a tag's visible text while preserving inner markup if simple."""
    # If it's a simple tag with no children tags, just set the string
    if not tag.find():
        tag.string = new_text
        return
    # Otherwise clear and re-insert as text (preserves tag but loses inner spans)
    for child in list(tag.children):
        child.extract()
    tag.append(new_text)


# ─── CTA enhancer ────────────────────────────────────────────────────────────

def _enhance_ctas(soup, cta_text: str, ts: dict):
    """
    Find anchor/button tags that look like CTAs (short text, prominent classes)
    and replace their text + add our accent class.
    Limit to first 3 so we don't over-change.
    """
    cta_keywords = {
        "shop", "buy", "get", "start", "try", "sign", "join",
        "learn", "explore", "discover", "order", "subscribe", "book",
    }
    changed = 0
    for tag in soup.find_all(["a", "button"]):
        if changed >= 3:
            break
        text = tag.get_text(strip=True).lower()
        if not text or len(text) > 60:
            continue
        if any(kw in text for kw in cta_keywords):
            # Replace text, keep href
            for child in list(tag.children):
                child.extract()
            tag.append(cta_text)
            # Add our class for styling
            existing = tag.get("class", [])
            tag["class"] = existing + ["ad2page-cta"]
            tag["style"] = (
                f"background:{ts['accent']} !important;"
                f"color:{ts['accent_text']} !important;"
                f"border-color:{ts['accent']} !important;"
                f"font-weight:700 !important;"
            )
            changed += 1


# ─── HTML fragments ──────────────────────────────────────────────────────────

def _urgency_banner_html(badge: str, headline: str, subhl: str, cta: str, ts: dict) -> str:
    badge_part = f'<span class="ad2p-badge">{badge}</span>' if badge else ""
    cta_part   = f'<a href="#" class="ad2p-banner-cta">{cta}</a>' if cta else ""
    hl_part    = f'<span class="ad2p-hl">{headline}</span>' if headline else ""
    sub_part   = f'<span class="ad2p-sub">{subhl}</span>' if subhl else ""

    return f"""
<div id="ad2page-banner">
  <div class="ad2p-inner">
    {badge_part}
    <div class="ad2p-copy">
      {hl_part}
      {sub_part}
    </div>
    {cta_part}
  </div>
</div>
"""


def _benefit_bar_html(titles: list, ts: dict) -> str:
    items = "".join(
        f'<div class="ad2p-bar-item"><span class="ad2p-check">✓</span>{t}</div>'
        for t in titles[:4]
    )
    return f"""
<div id="ad2page-bar">
  <div class="ad2p-bar-inner">
    {items}
  </div>
</div>
"""


# ─── CSS ─────────────────────────────────────────────────────────────────────

def _enhancement_css(ts: dict) -> str:
    return f"""
/* ═══ Ad2Page Enhancement Layer ═══ */
#ad2page-banner {{
  width: 100%;
  background: {ts['banner_bg']};
  color: {ts['banner_text']};
  padding: 14px 20px;
  position: relative;
  z-index: 99999;
  box-sizing: border-box;
  border-bottom: 2px solid {ts['accent']};
}}
.ad2p-inner {{
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
  justify-content: center;
}}
.ad2p-badge {{
  background: {ts['accent']};
  color: {ts['accent_text']};
  font-size: 11px;
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
  padding: 4px 12px;
  border-radius: 20px;
  white-space: nowrap;
  flex-shrink: 0;
}}
.ad2p-copy {{
  display: flex;
  flex-direction: column;
  gap: 2px;
  text-align: center;
}}
.ad2p-hl {{
  font-size: 15px;
  font-weight: 700;
  color: {ts['banner_text']};
  line-height: 1.3;
}}
.ad2p-sub {{
  font-size: 12px;
  opacity: 0.75;
  color: {ts['banner_text']};
}}
.ad2p-banner-cta {{
  background: {ts['accent']};
  color: {ts['accent_text']};
  font-size: 13px;
  font-weight: 700;
  padding: 8px 20px;
  border-radius: 6px;
  text-decoration: none;
  white-space: nowrap;
  flex-shrink: 0;
  transition: filter .2s;
}}
.ad2p-banner-cta:hover {{ filter: brightness(1.15); }}

/* Benefit bar */
#ad2page-bar {{
  width: 100%;
  background: {ts['bar_bg']};
  border-top: 2px solid {ts['bar_border']};
  padding: 14px 20px;
  box-sizing: border-box;
  margin-top: 40px;
}}
.ad2p-bar-inner {{
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  gap: 32px;
  flex-wrap: wrap;
  justify-content: center;
}}
.ad2p-bar-item {{
  font-size: 13px;
  font-weight: 600;
  color: {ts['bar_text']};
  display: flex;
  align-items: center;
  gap: 7px;
}}
.ad2p-check {{
  background: {ts['accent']};
  color: {ts['accent_text']};
  border-radius: 50%;
  width: 18px;
  height: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 800;
  flex-shrink: 0;
}}

/* CTA pulse on urgent */
.ad2page-cta {{
  animation: ad2p-pulse 2s ease infinite;
}}
@keyframes ad2p-pulse {{
  0%, 100% {{ box-shadow: 0 0 0 0 {ts['accent']}55; }}
  50%       {{ box-shadow: 0 0 0 8px {ts['accent']}00; }}
}}

@media (max-width: 600px) {{
  .ad2p-inner {{ flex-direction: column; text-align: center; }}
  .ad2p-bar-inner {{ gap: 16px; }}
}}
"""


# ─── JS ──────────────────────────────────────────────────────────────────────

def _personalisation_js(tone: str, ts: dict) -> str:
    countdown_code = ""
    if "urgent" in tone.lower():
        countdown_code = """
  // Countdown timer injected by Ad2Page
  var end = Date.now() + 15 * 60 * 1000; // 15 min
  var el  = document.createElement('div');
  el.id   = 'ad2p-countdown';
  el.style.cssText = 'position:fixed;bottom:20px;right:20px;background:#dc2626;color:#fff;'
    + 'padding:12px 20px;border-radius:10px;font-size:14px;font-weight:700;z-index:99999;'
    + 'box-shadow:0 4px 20px rgba(220,38,38,.4);font-family:monospace;';
  document.body.appendChild(el);
  (function tick() {
    var rem = end - Date.now();
    if (rem <= 0) { el.textContent = '⏰ Offer Expired'; return; }
    var m = Math.floor(rem/60000), s = Math.floor((rem%60000)/1000);
    el.textContent = '⚡ Offer ends: ' + m + ':' + (s<10?'0'+s:s);
    setTimeout(tick, 1000);
  })();
"""

    return f"""
(function() {{
  // Ad2Page personalisation layer
  {countdown_code}

  // Smooth-scroll all ad2p CTAs
  document.querySelectorAll('.ad2p-banner-cta').forEach(function(a) {{
    a.addEventListener('click', function(e) {{
      e.preventDefault();
      var target = document.querySelector('form, .cta-section, [data-section="cta"], #cta');
      if (target) target.scrollIntoView({{ behavior:'smooth' }});
      else window.scrollTo({{ top: document.body.scrollHeight, behavior:'smooth' }});
    }});
  }});
}})();
"""


# ─── Fallback standalone page (only if no raw_html) ─────────────────────────

def _build_fallback_page(variation_data: dict, tone: str, colors: dict) -> str:
    """Minimal, clean standalone page — used ONLY when scraping fails."""
    hero      = variation_data.get("hero", {})
    benefits  = variation_data.get("benefits", [])
    final_cta = variation_data.get("final_cta", {})
    ts        = get_tone_styles(tone)

    benefits_html = "".join(
        f"""<div class="card">
              <div class="icon">✦</div>
              <h3>{b.get('title','')}</h3>
              <p>{b.get('description','')}</p>
           </div>"""
        for b in benefits
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{hero.get('headline','Landing Page')}</title>
<style>
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{font-family:system-ui,sans-serif;background:#fff;color:#111;line-height:1.6}}
  .banner{{background:{ts['banner_bg']};color:{ts['banner_text']};text-align:center;padding:10px 20px;font-size:13px;font-weight:700;letter-spacing:.05em}}
  .hero{{max-width:900px;margin:80px auto;text-align:center;padding:0 24px}}
  .badge{{display:inline-block;background:{ts['accent']};color:{ts['accent_text']};padding:6px 18px;border-radius:20px;font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.08em;margin-bottom:24px}}
  h1{{font-size:clamp(32px,5vw,60px);line-height:1.1;margin-bottom:20px;font-weight:800}}
  .sub{{font-size:20px;color:#555;margin-bottom:36px}}
  .cta{{display:inline-block;background:{ts['accent']};color:{ts['accent_text']};padding:16px 40px;border-radius:8px;font-size:17px;font-weight:700;text-decoration:none;letter-spacing:.02em}}
  .cta:hover{{filter:brightness(1.1)}}
  .cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:24px;max-width:900px;margin:60px auto;padding:0 24px}}
  .card{{background:#f8f9fa;border-radius:12px;padding:32px;text-align:center}}
  .icon{{font-size:28px;margin-bottom:12px;color:{ts['accent']}}}
  .card h3{{font-size:18px;margin-bottom:8px}}
  .card p{{font-size:14px;color:#666}}
  .fcta{{text-align:center;padding:60px 24px;background:{ts['banner_bg']}}}
  .fcta h2{{color:{ts['banner_text']};font-size:36px;margin-bottom:24px}}
  .note{{font-size:11px;color:#aaa;text-align:center;padding:12px;border-top:1px solid #eee}}
</style>
</head>
<body>
<div class="banner">⚡ Personalized page — scraping unavailable for this URL</div>
<div class="hero">
  <div class="badge">{hero.get('badge','Special Offer')}</div>
  <h1>{hero.get('headline','Your Personalized Headline')}</h1>
  <p class="sub">{hero.get('subheadline','')}</p>
  <a href="#" class="cta">{hero.get('cta','Get Started')}</a>
</div>
<div class="cards">{benefits_html}</div>
<div class="fcta">
  <h2>{final_cta.get('headline','Ready to get started?')}</h2>
  <a href="#" class="cta">{final_cta.get('cta','Take Action Now')}</a>
</div>
<p class="note">Ad2Page fallback mode — target URL could not be scraped (bot protection, auth wall, etc.)</p>
</body>
</html>"""