from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64

from scraper import scrape_landing_page
from ai_service import LlmService

from template_builder import build_landing_page_html

app = FastAPI(title="Ad to Landing Page Personalizer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = LlmService()

class GenerateRequest(BaseModel):
    landing_url: str
    ad_text: str = None
    ad_video: str = None
    tone: str = "professional"

@app.post("/api/generate")
async def generate_page(
    landing_url: str = Form(...),
    ad_text: str = Form(""),
    ad_video: str = Form(""),
    tone: str = Form("professional"),
    file: UploadFile = File(None)
):
    print("Received request for url:", landing_url)
    try:
        # 1. Analyze Ad
        ad_analysis = None
        if file and file.filename:
            contents = await file.read()
            base64_img = base64.b64encode(contents).decode('utf-8')
            ad_analysis = llm.analyze_ad_image(base64_img)
        elif ad_text.strip():
            ad_analysis = llm.analyze_ad_text(ad_text)
        elif ad_video.strip():
            ad_analysis = llm.analyze_ad_text(f"Ad is a video at this link: {ad_video}")
        else:
            raise HTTPException(status_code=400, detail="Must provide either Ad image, text, or video link.")
            
        if ad_analysis and 'error' in ad_analysis:
            raise HTTPException(status_code=500, detail=ad_analysis['error'])

        # 2. Scrape Landing Page
        scraped_data = scrape_landing_page(landing_url)

        # 3. Generate structured variations
        generation_data = llm.generate_landing_page(ad_analysis, scraped_data, tone)
        
        if "error" in generation_data:
            raise HTTPException(status_code=500, detail=generation_data["error"])

        # 4. Build HTML for each variation
        html_variations = []
        context = generation_data.get("context", {})
        colors = generation_data.get("color_scheme", {})
        
        for i, variation in enumerate(generation_data.get("variations", [])):
            html = build_landing_page_html(variation, tone, context, colors)
            html_variations.append({
                "variation_number": i + 1,
                "html": html,
                "mismatch_analysis": generation_data.get("mismatch_analysis", ""),
                "change_log": variation.get("change_log", [])
            })

        return {
            "success": True,
            "ad_analysis": ad_analysis,
            "variations": html_variations
        }

    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
