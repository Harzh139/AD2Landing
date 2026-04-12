import os, json
from groq import Groq
from dotenv import load_dotenv
load_dotenv()


class LlmService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key or self.api_key == "your_groq_api_key_here":
            raise ValueError("GROQ_API_KEY missing or invalid")
        self.client = Groq(api_key=self.api_key)

    def analyze_ad_text(self, text: str) -> dict:
        r = self.client.chat.completions.create(
            messages=[{"role": "user", "content": f"""Analyze this ad. Return ONLY valid JSON with keys:
headline, offer, audience, tone, pain_points (array), cta
Ad: "{text}" """}],
            model="llama-3.1-8b-instant",
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        try:
            return json.loads(r.choices[0].message.content)
        except Exception:
            return {"error": "Failed to parse ad analysis"}

    def analyze_ad_image(self, image_base64: str) -> dict:
        try:
            r = self.client.chat.completions.create(
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": """Analyze this ad image. Return ONLY valid JSON with keys:
headline, offer, audience, tone, pain_points (array), cta"""},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
                ]}],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            return json.loads(r.choices[0].message.content)
        except Exception as e:
            return {"error": f"Image analysis failed: {e}"}

    def generate_landing_page(self, ad_analysis: dict, scraped: dict, tone: str = "professional") -> dict:
        lean = {
            "title":      scraped.get("title", ""),
            "headings":   scraped.get("headings", [])[:8],
            "ctas":       scraped.get("ctas", [])[:6],
            "paragraphs": scraped.get("paragraphs", [])[:4],
        }

        prompt = f"""You are a senior CRO (Conversion Rate Optimization) specialist.

TASK: Generate 3 DISTINCT copy variations to personalize an existing landing page based on an ad.
You are NOT building new pages — you are rewriting specific copy elements of the existing page.

Ad Analysis:
{json.dumps(ad_analysis, indent=2)}

Existing Page Content:
{json.dumps(lean, indent=2)}

Tone: {tone}

CRITICAL RULES:
1. Each variation MUST have clearly different angles:
   - Variation 1: OFFER-FOCUSED (lead with discount/deal, "50% OFF" in headline)
   - Variation 2: BENEFIT-FOCUSED (lead with the outcome/transformation, emotional)
   - Variation 3: URGENCY-FOCUSED (scarcity, FOMO, time pressure, "Today Only")
2. hero.headline replaces the existing page H1 — make it punchy, direct, ≤10 words
3. hero.subheadline replaces first H2 — 1 sentence, supports the headline
4. hero.cta replaces existing CTA buttons — action verb + specific benefit
5. hero.badge = short urgency label shown in a banner (e.g. "50% Off Today Only")
6. benefits = exactly 3 items relevant to the ad offer
7. change_log MUST list what changed vs the original page headings/CTAs above

Return ONLY valid JSON (no markdown, no explanation):
{{
  "mismatch_analysis": "2-3 sentences: what mismatch exists between the ad offer and existing page",
  "context": {{"industry":"...","intent":"...","audience":"...","category":"product|saas|service"}},
  "color_scheme": {{"primary":"#hex","bg":"#hex"}},
  "variations": [
    {{
      "variation_number": 1,
      "angle": "offer-focused",
      "change_log": [
        {{"change":"Replaced H1 '...' with offer headline","reason":"Original H1 ignores the 50% discount"}},
        {{"change":"Changed CTA from '...' to '...'","reason":"More specific to the deal"}}
      ],
      "hero": {{
        "badge":"50% Off — Today Only",
        "headline":"...",
        "subheadline":"...",
        "cta":"...",
        "image_keyword":"sneakers sale"
      }},
      "benefits":[
        {{"title":"...","description":"...","icon":"star"}},
        {{"title":"...","description":"...","icon":"shield"}},
        {{"title":"...","description":"...","icon":"bolt"}}
      ],
      "final_cta":{{"headline":"...","cta":"..."}}
    }},
    {{
      "variation_number": 2,
      "angle": "benefit-focused",
      "change_log": [{{"change":"...","reason":"..."}}],
      "hero": {{"badge":"...","headline":"...","subheadline":"...","cta":"...","image_keyword":"..."}},
      "benefits":[{{"title":"...","description":"...","icon":"star"}}],
      "final_cta":{{"headline":"...","cta":"..."}}
    }},
    {{
      "variation_number": 3,
      "angle": "urgency-focused",
      "change_log": [{{"change":"...","reason":"..."}}],
      "hero": {{"badge":"...","headline":"...","subheadline":"...","cta":"...","image_keyword":"..."}},
      "benefits":[{{"title":"...","description":"...","icon":"star"}}],
      "final_cta":{{"headline":"...","cta":"..."}}
    }}
  ]
}}"""

        try:
            r = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                temperature=0.85,   # higher = more variation between outputs
                response_format={"type": "json_object"},
            )
            result = json.loads(r.choices[0].message.content.strip())
            # Validate we got 3 distinct variations
            variations = result.get("variations", [])
            print(f"[ai_service] angles: {[v.get('angle','?') for v in variations]}")
            return result
        except Exception as e:
            return {"error": str(e), "mismatch_analysis": "Generation failed", "variations": []}