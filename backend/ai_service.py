import os
import json
import base64
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class LlmService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key or self.api_key == 'your_groq_api_key_here':
            raise ValueError("GROQ_API_KEY is missing or invalid in .env file")
        self.client = Groq(api_key=self.api_key)

    def analyze_ad_text(self, text: str) -> dict:
        prompt = f"""You are an expert marketing strategist. Analyze the following ad text and extract the key information.
Return ONLY a valid JSON object with the following keys:
- headline (string)
- offer (string)
- audience (string)
- tone (string)
- pain_points (array of strings)
- cta (string)

Ad Text: "{text}"
"""
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        try:
            return json.loads(response.choices[0].message.content)
        except Exception:
            return {"error": "Failed to parse JSON"}

    def analyze_ad_image(self, image_base64: str) -> dict:
        prompt = """You are an expert marketing strategist. Analyze the provided ad image and extract the key information.
Return ONLY a valid JSON object with the following keys:
- headline (string)
- offer (string)
- audience (string)
- tone (string)
- pain_points (array of strings)
- cta (string)
"""
        try:
            response = self.client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": f"Failed to analyze image: {str(e)}"}

    def generate_landing_page(self, ad_analysis: dict, scraped_data: dict, tone_selector: str = "professional") -> dict:
        prompt = f"""You are an expert Conversion Rate Optimizer (CRO) and direct-response copywriter.
Your task is to take an EXISTING landing page and optimize/personalize it based on a specific Advertisement.

Ad Analysis:
{json.dumps(ad_analysis, indent=2)}

Existing Landing Page Content (Scraped Data):
{json.dumps(scraped_data, indent=2)}

Tone requested: {tone_selector}

CRITICAL GOAL:
Do NOT create a brand new page from scratch. Instead, ENHANCE the existing content. Improve headlines, adjust the tone to match the ad's intent, add urgency, and highlight the benefits that specifically appeal to the ad's audience.

TASK REQUIREMENTS:
1. Maintain the "Core Identity" of the existing page but improve every element for higher conversion.
2. Identify 3-4 specific "Optimized Variations" where each variation is an incremental improvement over the original.
3. For each variation, you MUST provide:
   - Updated content (Hero, Benefits, Social Proof, CTA, etc.) grounded in original data but improved.
   - If available in 'media' list, choose the most relevant media object (url, type, etc.) and save it in 'hero_media'.
   - A list of specific changes made (e.g., "Changed headline from 'Welcome' to 'Get 20% Off Now'").
   - CRO Reasoning for each change (e.g., "Aligns with the 'discount' intent of the ad creative").

Output ONLY valid JSON in the following structure:
{{
  "mismatch_analysis": "A critical 3-4 sentence analysis of why the CURRENT page fails to convert the AD traffic.",
  "context": {{
    "industry": "...",
    "intent": "...",
    "audience": "...",
    "category": "product|saas|service"
  }},
  "color_scheme": {{"primary": "#4f46e5", "bg": "#ffffff"}},
  "variations": [
    {{
      "variation_number": 1,
      "change_log": [
        {{"change": "...", "reason": "..."}}
      ],
      "hero": {{
        "badge": "...", 
        "headline": "...", 
        "subheadline": "...", 
        "cta": "...", 
        "image_keyword": "...",
        "hero_media": {{
           "url": "...",
           "type": "image|gif|video",
           "poster": "..."
        }}
      }},
      "benefits": [ {{"title": "...", "description": "...", "icon": "..."}} ],
      "social_proof": {{
        "type": "b2c|b2b",
        "testimonials": [{{"author": "...", "text": "..."}}],
        "metrics": "...",
        "logos": ["..."]
      }},
      "pricing_or_value": {{
        "type": "discount|saas_plan|service_outcome",
        "old_price": "...", "new_price": "...",
        "plan_name": "...", "plan_price": "...", "plan_features": ["..."],
        "outcome_title": "...", "outcome_desc": "..."
      }},
      "product_features": {{
        "type": "product_cards|feature_blocks|transformations",
        "items": [{{"title": "...", "desc": "..."}}]
      }},
      "final_cta": {{"headline": "...", "cta": "..."}}
    }}
  ]
}}
"""
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content.strip()
            return json.loads(content)
        except Exception as e:
            return {
                "error": str(e),
                "mismatch_analysis": "Failed to generate",
                "variations": []
            }
