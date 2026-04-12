# Deployment Guide: Ad-to-Landing Page Personalizer

Since this project consists of a **Static Frontend** (HTML/JS/CSS) and a **Python Backend** (FastAPI), you can deploy them separately to keep things simple and cost-effective.

---

## 🚀 Step 1: Deploy the Backend (Python FastAPI)

The backend handles the AI logic, scraping, and template building.

### Option A: Railway (Highly Recommended)
1.  **Create a Account:** Go to [Railway.app](https://railway.app/).
2.  **New Project:** Select "Deploy from GitHub repo" and pick your `AD2Landing` repo.
3.  **Root Directory:** Set the root directory to `backend/`.
4.  **Environment Variables:** Add your `GROQ_API_KEY` in the Railway dashboard.
5.  **Build Command:** Railway will automatically detect the `requirements.txt` we moved into the `backend/` folder and install everything.
6.  **Start Command:** If needed, set the start command to:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port $PORT
    ```
7.  **Get your URL:** Once deployed, Railway will give you a public URL (e.g., `https://backend-production.up.railway.app`). **Copy this URL.**

---

## 🎨 Step 2: Update and Deploy the Frontend

Now you need to tell your frontend to talk to the new backend URL instead of your local computer.

### 1. Update `script.js`
Open `script.js` and find the line where it fetches data:
```javascript
const response = await fetch('http://localhost:8000/api/generate', { ... });
```
Replace `http://localhost:8000` with your **Railway Backend URL**:
```javascript
const response = await fetch('https://your-backend-url.up.railway.app/api/generate', { ... });
```

### 2. Deploy to Vercel or Netlify
1.  **Vercel:** Go to [Vercel.com](https://vercel.com/).
2.  **Import Repo:** Connect your GitHub and import the repo.
3.  **Settings:** Vercel will automatically detect the `index.html` in the root and host it as a static site.
4.  **Deploy:** Click Deploy! Your frontend is now live.

---

## 🛠 Step 3: Handling CORS (Security)

By default, browse security might block your frontend on `vercel.app` from Talking to your backend on `railway.app`.

I have already pre-configured the backend to handle CORS in `main.py`. However, for production, you should update the `allow_origins` list in `backend/main.py`:

```python
# In backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-url.vercel.app"], # Replace with your real frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📦 Alternative: Deploying Both Together (VPS)

If you have a Linux VPS (DigitalOcean, AWS EC2):
1.  **Install Nginx**: Use Nginx to serve the `index.html` and other static files.
2.  **Run Backend with Systemd**: Run the FastAPI app in the background using `gunicorn` or `uvicorn`.
3.  **Reverse Proxy**: Configure Nginx to forward requests to `/api` to your FastAPI server running on port 8000.

---

## ✅ Summary Checklist
1. [ ] Backend deployed to Railway/Render.
2. [ ] `GROQ_API_KEY` added to environment variables.
3. [ ] `script.js` updated with the new backend URL.
4. [ ] Frontend deployed to Vercel/Netlify.
5. [ ] (Optional) CORS updated in `main.py` for extra security.
