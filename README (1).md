# YTGrab – Deployment Guide

## File Structure
```
your-project/
├── app.py            ← Flask backend
├── requirements.txt  ← Python dependencies
├── Procfile          ← Railway start command
└── index.html        ← Frontend (deploy to Netlify)
```

---

## Step 1: Backend → Railway (Free Python Hosting)

Railway ek free Python hosting hai jo automatically port set karta hai.

1. **railway.app** pe jaao → GitHub se sign up karo (free)
2. "New Project" → "Deploy from GitHub repo" click karo
3. GitHub pe ek **new repository** banao (e.g. `ytgrab-backend`)
4. In files upload karo: `app.py`, `requirements.txt`, `Procfile`
5. Railway automatically detect karega Python app
6. Deploy hone ke baad, Settings → Networking → "Generate Domain" click karo
7. Tumhara backend URL milega, kuch aisa:
   `https://ytgrab-backend-production.up.railway.app`

---

## Step 2: Frontend URL Update karo

`index.html` mein line 190 ke paas yeh line hai:

```javascript
const BACKEND_URL = 'http://127.0.0.1:5000';
```

Isko apne Railway URL se replace karo:

```javascript
const BACKEND_URL = 'https://ytgrab-backend-production.up.railway.app';
```

---

## Step 3: Frontend → Netlify (Free Static Hosting)

1. **netlify.com** pe jaao → GitHub se sign up karo
2. "Add new site" → "Deploy manually" click karo
3. `index.html` file drag & drop karo
4. Done! Tumhara site live ho jaayega kuch aisa:
   `https://amazing-name-123456.netlify.app`

> **Custom domain** ke liye: Netlify Dashboard → Domain settings → Add custom domain

---

## 1080p ke baare mein

YouTube 1080p ko do alag streams mein serve karta hai (video + audio alag).
Inhe merge karne ke liye **ffmpeg** server pe install hona chahiye.

Railway pe ffmpeg install karne ke liye `nixpacks.toml` banao:

```toml
[phases.setup]
nixPkgs = ["ffmpeg"]
```

Aur `app.py` mein format ko update karo - but is setup mein hum
best available single-stream dete hain jo directly browser mein play hota hai.

---

## Local Testing

```bash
pip install flask flask-cors yt-dlp
python app.py
```

Phir `index.html` browser mein open karo.
