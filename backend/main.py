from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import base64

from scraper import scrape_landing_page
from ai_service import LlmService
from template_builder import build_landing_page_html

app = FastAPI(title="Ad2Page — CRO Personalizer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = LlmService()


@app.post("/api/generate")
async def generate_page(
    landing_url: str = Form(...),
    ad_text: str = Form(""),
    ad_video: str = Form(""),
    tone: str = Form("professional"),
    file: UploadFile = File(None),
):
    print(f"Request: url={landing_url} tone={tone}")

    # 1. Analyze the ad creative
    ad_analysis = None
    if file and file.filename:
        contents = await file.read()
        b64 = base64.b64encode(contents).decode("utf-8")
        ad_analysis = llm.analyze_ad_image(b64)
    elif ad_text.strip():
        ad_analysis = llm.analyze_ad_text(ad_text)
    elif ad_video.strip():
        ad_analysis = llm.analyze_ad_text(f"Ad is a video at: {ad_video}")
    else:
        raise HTTPException(400, "Provide an ad image, text, or video link.")

    if ad_analysis and "error" in ad_analysis:
        raise HTTPException(500, ad_analysis["error"])

    # 2. Scrape the real landing page
    scraped = scrape_landing_page(landing_url)
    raw_html = scraped.get("raw_html", "")

    if not raw_html:
        print(f"Scrape failed for {landing_url}: {scraped.get('error')}")

    # 3. Ask AI for targeted modifications
    generation = llm.generate_landing_page(ad_analysis, scraped, tone)

    if "error" in generation:
        raise HTTPException(500, generation["error"])

    # 4. Apply modifications to the REAL HTML
    context  = generation.get("context", {})
    colors   = generation.get("color_scheme", {})
    mismatch = generation.get("mismatch_analysis", "")

    html_variations = []
    for i, variation in enumerate(generation.get("variations", [])):
        enhanced_html = build_landing_page_html(
            variation_data=variation,
            tone=tone,
            context=context,
            colors=colors,
            raw_html=raw_html,
        )
        html_variations.append({
            "variation_number": i + 1,
            "html": enhanced_html,
            "mismatch_analysis": mismatch,
            "change_log": variation.get("change_log", []),
        })

    return {
        "success": True,
        "ad_analysis": ad_analysis,
        "variations": html_variations,
        "original_html": raw_html,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)