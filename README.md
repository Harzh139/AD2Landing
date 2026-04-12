# AD2Landing 🚀

**AD2Landing** is a cutting-edge, AI-powered system designed to generate hyper-personalized, conversion-optimized landing pages dynamically tailored to ad creatives. By analyzing your ad copy or image alongside an existing landing page, the tool identifies mismatched messaging and actively remedies it by instantly generating highly stylistic structural variations of the landing page.

## Features ✨

*   **Multimodal Ad Insights**: Seamlessly pass text, image data (vision model), or video link contexts representing your ad creative.
*   **Context Match Intelligence**: The AI parses your baseline URL and natively targets gaps in audiences, intents, and offers between the origin ad and your baseline page.
*   **Dynamic UI Templating Engine**: Generates complete HTML templates that algorithmically adapt their structure to the detected industry. E-commerce sites gain Strikethrough Discount tags, SaaS domains get checkmark pricing grids, etc.
*   **Tone-Based Profiles**:
    *   **Professional & Direct**: Clean UI arrays focusing on product features.
    *   **Conversational & Friendly**: Visually softer layouts using rounded components and lighter colors.
    *   **Luxury & Premium**: Sharp corners, deeply rich dark modes, and serif web typography.
    *   **Urgent & Aggressive**: FOMO ticking banners, massive red layouts, strict calls to actions.
*   **Claude-Style Artifact Interface**: View and interact with 3 different variations of your landing page directly in a segmented Preview/Code modal, all inside your browser.

## Technologies Used 🛠

-   **Frontend**: Native HTML/CSS/JS (Lightweight, No external dependencies)
-   **Backend**: FastAPI (Python)
-   **AI Infrastructure**: Groq API powered by LLaMA Models (`llama-3.1-8b-instant` & `llama-3.2-11b-vision-preview`), processing at extraordinary speeds.
-   **HTML Processing**: `BeautifulSoup4` for contextual baseline parsing.

## Installation 💻

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Harzh139/AD2Landing.git
   cd AD2Landing
   ```

2. **Setup virtual environment & install requirements:**
   ```bash
   pip install fastapi uvicorn groq beautifulsoup4 requests python-multipart python-dotenv
   ```

3. **Configure API Keys:**
   Create a `.env` file within the `/backend` directory and add your Groq Key:
   ```env
   GROQ_API_KEY=gsk_your_api_key_here
   ```

4. **Run the fast-server:**
   ```bash
   python backend/main.py
   ```

5. **Open Frontend UI:**
   Simply double-click `index.html` to open it locally via your browser.

## Usage 🎯

1. Input a baseline Landing Page URL for analysis context.
2. Select your desired tone overriding theme.
3. Upload your ad payload (Image Mockup or Ad Copy).
4. Hit generate and observe the AI instantly generate and render 3 structural HTML variations resolving offer desyncs!
