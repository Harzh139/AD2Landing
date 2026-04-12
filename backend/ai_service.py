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
        prompt = f"""You are an expert conversion copywriter and web strategist.
Given an advertisement analysis and current landing page content, generate high-converting landing page variations.

Ad Analysis:
{json.dumps(ad_analysis, indent=2)}

Original Landing Page Content (Scraped):
{json.dumps(scraped_data, indent=2)}

Tone requested: {tone_selector}

TASK:
1. Analyze the context: Industry (e-com, SaaS, etc), Intent (discount, premium, etc), Audience, and category (product, saas, or service).
2. Suggest a primary color hex code matching the tone and ad context.
3. Generate 2 to 3 structured variations of the landing page.

Rules for Variations:
- DO NOT repeat the ad headline exactly — improve it contextually.
- Hero: provide a badge, headline, subheadline, cta, and image_keyword (e.g., 'dashboard', 'fitness', 'product').
- Benefits: Provide 3-4 benefits. Each must have a 'title', 'description', and a simple keyword for 'icon'.
- Social Proof: Adapt to context type (B2C = testimonials, B2B = metrics/logos). 
- Pricing / Value: Adapt based on context type (discount = old vs new price; saas_plan = plan name/features; service_outcome = outcome title/desc).
- Product / Features: Adapt block (product_cards, feature_blocks, or transformations) with items.
- Final CTA: Urgency driven.

Output ONLY valid JSON in the exact following structure with NO markdown or explanations:
{{
  "mismatch_analysis": "Write a highly detailed, 3-4 sentence critical analysis explaining EXACTLY what the ad emphasizes versus what the original landing page is lacking or failing to communicate, and how these variations fix the message mismatch.",
  "context": {{
    "industry": "...",
    "intent": "...",
    "audience": "...",
    "category": "product|saas|service"
  }},
  "color_scheme": {{"primary": "#4f46e5", "bg": "#ffffff"}},
  "variations": [
    {{
      "hero": {{"badge": "...", "headline": "...", "subheadline": "...", "cta": "...", "image_keyword": "..."}},
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
