# Ad2Page: AI Landing Page Personalizer
## Brief Explanation & System Flow

Ad2Page is an AI-powered Conversion Rate Optimization (CRO) engine that surgically personalizes existing landing pages based on specific ad creatives. Instead of building new pages from scratch, it bridges the gap between what a user sees in an ad and what they experience on the page.

### System Flow:
1.  **Ad Intelligence Phase**: The system analyzes the ad (image, text, or video) to extract the "Offer Core," "Audience Intent," and "Visual Tone."
2.  **Context Extraction Phase**: The Scraper retrieves the real-time structure and copy of the target landing page (Headlines, CTAs, Benefits).
3.  **CRO Mapping Phase**: The AI Agent compares the Ad intent vs. the Page content to find "Message Mismatches."
4.  **Surgical Injection Phase**: The Template Builder takes the AI's optimized copy and injects it into a branded, high-performance layout that inherits the original site's context.

---

## Key Components & Agent Design

The system is designed as a modular pipeline of specialized "agents":

*   **Analysis Agent (Vision/Text)**: Uses Llama 3.2 Vision and 3.1 Text to deconstruct marketing psychological triggers from ad mockups.
*   **Scraper Agent**: A robust crawler that captures raw HTML and structured data, resolving relative URLs and capturing brand-specific media (videos/gifs).
*   **CRO Strategy Agent**: The "Brain" that identifies incremental optimization angles (Offer-focused, Benefit-focused, Urgency-focused).
*   **Template Logic Engine**: A deterministic builder that converts AI-generated JSON into production-ready HTML/CSS, ensuring the layout never "breaks" regardless of the AI's output.

---

## Reliability & Governance
### How we handle common AI challenges:

#### 1. Random Changes & Inconsistent Outputs
*   **Constraint-Based Prompting**: We force the LLM into a strict JSON-Schema response format. By defining exactly what fields are allowed (and locking the count to exactly 3 variations), we prevent the AI from "wandering" or adding unnecessary elements.
*   **Temperature Tuning**: We use a higher temperature (0.85) to ensure diversity *between* variations (so Var 1 and Var 2 aren't identical), but keep a low sequence penalty to ensure each individual variation stays coherent.

#### 2. Broken UI 
*   **Decoupled Architecture**: The AI never generates CSS or Layout code directly. It only generates **Copy and Intent**. Our `template_builder.py` handles the rendering. This ensures that even if the AI gives a $1,000,000$ word headline, our CSS handles it gracefully without breaking the layout.
*   **CSS Variable Injection**: System-wide styles (colors, fonts, radius) are controlled by deterministic CSS variables based on the "Tone Selection," not AI hallucination.

#### 3. Hallucinations
*   **Context Grounding**: We inject the `scraped_data` (the real page content) directly into the AI's prompt as the "Grounded Truth." The AI is explicitly told it is a "CRO Specialist," not a creator; it is penalized if it ignores the original brand data.
*   **Asset Inheritance**: The system is forced to pick images/videos from the `media` list extracted from the real website, preventing it from inventing non-existent product features.

#### 4. UI/UX Consistency
*   **Stateful Frontend**: The script.js manages variation states, ensuring that "Var 1" always represents the same logic for that session. 
*   **Original HTML Preservation**: By returning the `original_html` in the API, we give the user a source of truth to compare against, making any AI-driven changes transparent and verifiable.
