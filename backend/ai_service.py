import os, json, base64
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class LlmService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key or self.api_key == "your_groq_api_key_here":
            raise ValueError("GROQ_API_KEY missing or invalid in .env")
        self.client = Groq(api_key=self.api_key)

    # ── Ad analysis ─────────────────────────────────────────────────────

    def analyze_ad_text(self, text: str) -> dict:
        prompt = f"""You are an expert marketing strategist.
Analyze this ad and return ONLY valid JSON with keys:
- headline (string)
- offer (string) — the specific deal/discount/benefit
- audience (string)
- tone (string)
- pain_points (array of strings)
- cta (string) — exact call-to-action text

Ad: "{text}"
"""
        r = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        try:
            return json.loads(r.choices[0].message.content)
        except Exception:
            return {"error": "Failed to parse ad analysis"}

    def analyze_ad_image(self, image_base64: str) -> dict:
        prompt = """You are an expert marketing strategist.
Analyze this ad image and return ONLY valid JSON with keys:
- headline (string)
- offer (string)
- audience (string)
- tone (string)
- pain_points (array of strings)
- cta (string)
"""
        try:
            r = self.client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }},
                    ],
                }],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            return json.loads(r.choices[0].message.content)
        except Exception as e:
            return {"error": f"Image analysis failed: {e}"}

    # ── Landing page enhancement ─────────────────────────────────────────

    def generate_landing_page(
        self, ad_analysis: dict, scraped_data: dict, tone_selector: str = "professional"
    ) -> dict:
        # Keep scraped_data lean — only send text content to save tokens
        lean_scraped = {
            "title":    scraped_data.get("title", ""),
            "headings": scraped_data.get("headings", [])[:10],
            "ctas":     scraped_data.get("ctas", [])[:8],
            "paragraphs": scraped_data.get("paragraphs", [])[:5],
        }

        prompt = f"""You are an expert Conversion Rate Optimizer (CRO) and direct-response copywriter.

CRITICAL TASK:
You are given an EXISTING landing page (already scraped). Your job is to:
1. IDENTIFY the mismatch between the ad and the landing page
2. SUGGEST surgical copy changes (headline, subheadline, CTAs) to match the ad's offer
3. Generate 3 variations of these targeted changes

You are NOT building a new page. You are a CRO specialist enhancing existing copy.

Ad Analysis:
{json.dumps(ad_analysis, indent=2)}

Existing Page Content:
{json.dumps(lean_scraped, indent=2)}

Requested tone: {tone_selector}

RULES:
- hero.headline = the new H1 for the page (replaces the existing H1)
- hero.subheadline = improved subheading that directly references the ad offer
- hero.cta = action-oriented CTA text that matches the ad
- hero.badge = short urgency label (e.g. "Limited Time", "50% Off Today")
- benefits = 3 concise bullets showing WHY the offer is relevant
- change_log = list of specific changes made and why (for the audit panel)
- Each variation should differ in angle: Var1=offer-focused, Var2=benefit-focused, Var3=urgency-focused

Return ONLY valid JSON:
{{
  "mismatch_analysis": "2-3 sentences on what the original page is missing vs the ad.",
  "context": {{
    "industry": "...",
    "intent": "...",
    "audience": "...",
    "category": "product|saas|service"
  }},
  "color_scheme": {{"primary": "#hex", "bg": "#hex"}},
  "variations": [
    {{
      "variation_number": 1,
      "change_log": [
        {{"change": "Replaced H1 with offer-specific headline", "reason": "Original H1 does not mention the 50% discount"}}
      ],
      "hero": {{
        "badge": "Limited Time Offer",
        "headline": "...",
        "subheadline": "...",
        "cta": "...",
        "image_keyword": "...",
        "hero_media": {{
          "url": "",
          "type": "image",
          "poster": ""
        }}
      }},
      "benefits": [
        {{"title": "...", "description": "...", "icon": "star"}}
      ],
      "social_proof": {{
        "type": "b2c",
        "testimonials": [{{"author": "...", "text": "..."}}],
        "metrics": "",
        "logos": []
      }},
      "pricing_or_value": {{
        "type": "discount",
        "old_price": "",
        "new_price": "",
        "plan_name": "",
        "plan_price": "",
        "plan_features": [],
        "outcome_title": "",
        "outcome_desc": ""
      }},
      "product_features": {{
        "type": "feature_blocks",
        "items": [{{"title": "...", "desc": "..."}}]
      }},
      "final_cta": {{"headline": "...", "cta": "..."}}
    }}
  ]
}}
"""
        try:
            r = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            return json.loads(r.choices[0].message.content.strip())
        except Exception as e:
            return {"error": str(e), "mismatch_analysis": "Generation failed", "variations": []}