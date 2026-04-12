from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import base64

from scraper import scrape_landing_page
from ai_service import LlmService
from template_builder import build_landing_page_html

app = FastAPI(title="Ad2Page")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

llm = LlmService()


@app.post("/api/generate")
async def generate_page(
    landing_url: str = Form(...),
    ad_text: str = Form(""),
    ad_video: str = Form(""),
    tone: str = Form("professional"),
    file: UploadFile = File(None),
):
    print(f"[ad2page] url={landing_url} tone={tone}")

    # 1. Analyze ad
    ad_analysis = None
    if file and file.filename:
        contents = await file.read()
        ad_analysis = llm.analyze_ad_image(base64.b64encode(contents).decode())
    elif ad_text.strip():
        ad_analysis = llm.analyze_ad_text(ad_text)
    elif ad_video.strip():
        ad_analysis = llm.analyze_ad_text(f"Video ad at: {ad_video}")
    else:
        raise HTTPException(400, "Provide an ad image, text, or video link.")

    if ad_analysis and "error" in ad_analysis:
        raise HTTPException(500, ad_analysis["error"])

    # 2. Scrape real page
    scraped  = scrape_landing_page(landing_url)
    raw_html = scraped.get("raw_html", "")
    print(f"[ad2page] scraped html length: {len(raw_html)}")

    # 3. Generate 3 distinct variations via AI
    generation = llm.generate_landing_page(ad_analysis, scraped, tone)
    if "error" in generation:
        raise HTTPException(500, generation["error"])

    context  = generation.get("context", {})
    colors   = generation.get("color_scheme", {})
    mismatch = generation.get("mismatch_analysis", "")
    variations_raw = generation.get("variations", [])

    print(f"[ad2page] got {len(variations_raw)} variations from AI")

    # 4. Build HTML by ENHANCING real page (not building new one)
    html_variations = []
    for i, var in enumerate(variations_raw):
        html = build_landing_page_html(
            variation_data=var,
            tone=tone,
            context=context,
            colors=colors,
            raw_html=raw_html,
            base_url=landing_url,       # ← fixes relative URLs
        )
        html_variations.append({
            "variation_number": i + 1,
            "html": html,
            "mismatch_analysis": mismatch,
            "change_log": var.get("change_log", []),
        })

    return {
        "success": True,
        "ad_analysis": ad_analysis,
        "variations": html_variations,
        "original_html": raw_html,      # ← for Before/After toggle
    }


if __name__ == "__main__":
    import uvicorn
    # Use the string "main:app" format if you ever need reload=True
    # For production, we use the app object and reload=False
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)