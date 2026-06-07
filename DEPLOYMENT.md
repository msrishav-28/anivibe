# AniVibe Deployment Guide (Cloud-Only Edition)

> **Note:** This project is configured for **Zero-Terminal Deployment**. You do not need to run commands locally. All deployments happen via GitHub Actions.

## Architecture Overview

```
Vercel (Frontend) → Render (Backend) → Supabase (Database)
                         ↓
                    Modal (ML Models)
```

---

## 1. Supabase (Database) - DEPLOY FIRST

### Already Done
Your Supabase project should already be set up. Just note down:

```
Project URL: https://xxxxx.supabase.co
Anon Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Service Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Run Migrations
1. Go to Supabase Dashboard -> SQL Editor
2. Run migration files from `alembic/versions/` (Copy/Paste content)
*Note: Since you have no local terminal, you must run SQL manually or connect a cloud SQL client.*

---

## 2. Modal (ML Models) - AUTOMATED

We have set up a **GitHub Action** to deploy this for you.

### Step 1: Get Token
1. Go to [modal.com](https://modal.com) -> Settings -> API Tokens.
2. Create a new token.

### Step 2: Add Secrets to GitHub
1. Go to your GitHub Repo -> **Settings** -> **Secrets and variables** -> **Actions**.
2. Add `MODAL_TOKEN_ID`
3. Add `MODAL_TOKEN_SECRET`

### Step 3: Trigger Deployment
*   Just **push any change** to the `main` branch.
*   Go to "Actions" tab in GitHub to see the URL (e.g., `https://...modal.run`).

---

## 3. Render (Backend API)

### Step 1: Create Service
1. Go to [render.com](https://render.com)
2. **New** -> **Web Service**
3. Connect your Repo.

### Step 2: Configure Environment
Render will auto-detect `render.yaml`, but verify:
*   **Build Command**: `pip install -r requirements-lite.txt` (This is CRITICAL for free tier)
*   **Start Command**: `uvicorn app.main:app ...`

### Step 3: Set Environment Variables
Add these in the Dashboard:

```bash
# Database
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_KEY=...
SUPABASE_DB_PASSWORD=...

# ML Service (From Step 2)
ML_SERVICE_URL=https://your-workspace--anivibe-ml-semantic-search.modal.run
ENABLE_IMAGE_SEARCH=true
USE_GPU=false
```

---

## 4. Vercel (Frontend)

### Step 1: Import Project
1. Go to Vercel Dashboard.
2. Import `anivibe-dev` repo.
3. Select `frontend` folder as Root Directory.

### Step 2: Set Environment Variables
```bash
NEXT_PUBLIC_API_URL=https://your-render-backend.onrender.com/api/v1
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
NEXT_PUBLIC_ENABLE_IMAGE_SEARCH=true
```

### Step 3: Deploy
Click **Deploy**.

---

## Verify Deployment

### Checklist
- [ ] GitHub Action "Deploy Modal App" matches (Remote ML)
- [ ] Render Backend `/health` returns `healthy`
- [ ] Frontend loads and features work:
    - [ ] Visual Search (`/search/image`)
    - [ ] Personalized Feed (Home Page)
    - [ ] Reviews & Ratings (Anime Detail)
    - [ ] Profile Editing (Settings Tab)
- [ ] **Low-End Optimization**: Disabled (High Performance Mode Active)

---
