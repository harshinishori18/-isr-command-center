# ISR Command Center — Deployment Guide

## What's included
- Flask web app (production-ready)
- Gunicorn WSGI server
- PWA support (installs as a native app on Android & iOS)
- Service Worker (offline caching)
- Railway-ready (free hosting, no credit card needed)

---

## Option A — Deploy to Railway (Recommended — Free, Live URL in 5 min)

Railway gives you a live HTTPS URL that works on every device instantly.

### Step 1 — Push to GitHub
```bash
cd isr_command_center
git init
git add .
git commit -m "Initial commit"
# Create a new repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/isr-command-center.git
git push -u origin main
```

### Step 2 — Deploy on Railway
1. Go to **https://railway.app** → Sign in with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your `isr-command-center` repo
4. Railway auto-detects Python + `Procfile` — click **Deploy**
5. Go to **Settings → Networking → Generate Domain**
6. Your app is live at `https://isr-command-center-xxx.railway.app`

### Step 3 — Set Environment Variables (on Railway dashboard)
```
SECRET_KEY = any-long-random-string-here
```
(Railway auto-sets PORT — you don't need to set that)

### Optional — Add PostgreSQL (so data persists across deploys)
1. In Railway → **New** → **Database** → **PostgreSQL**
2. Railway automatically sets `DATABASE_URL` — your app picks it up automatically

---

## Option B — Run Locally

```bash
cd isr_command_center
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open http://localhost:5000

---

## Option C — Run on your Local Network (phone + laptop together)

```bash
python app.py
```
Then on your phone, open: `http://YOUR_LAPTOP_IP:5000`
Find your IP with `ipconfig` (Windows) or `ifconfig` (Mac/Linux)

---

## Install as a Mobile App (PWA)

Once deployed to Railway:

**Android (Chrome):**
1. Open the Railway URL in Chrome
2. Tap the menu (⋮) → "Add to Home Screen"
3. App installs with the ISR icon — opens fullscreen, no browser bar

**iPhone (Safari):**
1. Open the Railway URL in Safari
2. Tap the Share button → "Add to Home Screen"
3. App installs with the ISR icon — opens fullscreen

---

## File Structure
```
isr_command_center/
├── app.py               ← Flask routes (production-ready)
├── models.py            ← Database models
├── gamification.py      ← Points, levels, badges logic
├── requirements.txt     ← Python dependencies
├── Procfile             ← Gunicorn start command for Railway
├── runtime.txt          ← Python 3.11
├── .gitignore
├── static/
│   ├── css/style.css    ← Full luxury CSS
│   ├── js/main.js
│   ├── manifest.json    ← PWA manifest
│   ├── sw.js            ← Service worker
│   └── icons/
│       ├── icon-192.png
│       └── icon-512.png
└── templates/
    ├── base.html        ← PWA meta tags, navbar, footer
    ├── index.html
    ├── dashboard.html
    ├── login.html
    ├── register.html
    ├── leaderboard.html
    ├── badges.html
    ├── challenges.html
    ├── log_activity.html
    └── profile.html
```
