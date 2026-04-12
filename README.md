# AD2Landing 🚀

**AD2Landing** is a cutting-edge, AI-powered system designed to resolve one of the most expensive leaks in digital marketing: the disconnect between ad creatives and landing page experiences.

---

## 🛑 The Problem: Message Mismatch

When users click an ad, they expect the landing page to directly reflect the exact offer, tone, and visual urgency that earned their click. 
However, most campaigns drive highly segmented ad traffic to a **generic, static landing page**. 

* **High Bounce Rates:** Users leave when they don't immediately see the specific offer or product highlighted in the ad.
* **Wasted Ad Spend:** The mismatch in urgency, tone, or audience framing causes a massive drop-off in conversions.
* **Inflexible Architecture:** It is too time-consuming for developers and marketers to manually code dozens of landing page variations tailored to every micro-campaign.

---

## ⚡ The Solution: Intelligent Generation

AD2Landing solves this by acting as an autonomous, expert conversion copywriter and web developer. By simply uploading your Ad Creative (Image or Text) alongside your baseline URL, the system dynamically bridges the gap:

1. **Multimodal Analysis:** The system uses vision models (`llama-3.2-11b-vision-preview`) and fast text models (`llama-3.1-8b-instant`) to extract the core intent, audience, and offer mechanics of your ad.
2. **Contextual Scraping:** It parses the target URL to establish baseline data.
3. **Adaptive HTML Generation:** It generates structured JSON that maps to a dynamic, production-ready UI templating engine. The system actually changes layout paradigms based on the backend context (e.g., rendering "Client Logos" for SaaS B2B, and "Testimonial Grids" for B2C).
4. **Tone Mapping:** The UI physically transforms based on the desired tone. 
   - *Luxury* -> Deep blacks, gold accents, and serif typography.
   - *Urgent* -> Stark red action colors, warning badges, and bold headers.

---

## 🏆 The Outcome: Maximized ROI

By utilizing AD2Landing, marketers and developers achieve:

* **Frictionless Conversions:** The user experiences a seamless transition from the Ad to the Landing page, keeping the offer and tone completely unified.
* **Instant A/B Testing:** The engine generates **3 distinct structural HTML variations** simultaneously.
* **Zero-Code Deployment:** The Claude-inspired user interface allows you to instantly toggle between variations and copy the production-ready raw HTML straight to your clipboard with a single click.
* **Higher Profit Margins:** Lower bounce rates directly translate to cheaper acquisition costs and significantly higher campaign returns.

---

## 🛠 Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Harzh139/AD2Landing.git
   cd AD2Landing
   ```

2. **Setup virtual environment & requirements:**
   ```bash
   pip install fastapi uvicorn groq beautifulsoup4 requests python-multipart python-dotenv
   ```

3. **Configure API Keys:**
   Create a `.env` file within the `/backend` directory and add your Groq Key:
   ```env
   GROQ_API_KEY=gsk_your_groq_key
   ```

4. **Run the Server:**
   ```bash
   python backend/main.py
   ```

5. **Open Frontend UI:**
   Double-click `index.html` to open it locally in your browser.
