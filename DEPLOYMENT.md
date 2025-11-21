# Deployment Guide

This guide will help you deploy both the frontend and backend of the NYC Car Crashes Analysis Dashboard.

## Prerequisites

- GitHub account with your repository: `https://github.com/NABILAAHMEDD/NYC-car-crashes-Analysis`
- Vercel account (for frontend)
- Render or Railway account (for backend)

---

## 🎨 Frontend Deployment (Vercel)

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**
   - Visit: https://vercel.com/nabilaahmedds-projects
   - Click "Add New..." → "Project"

2. **Import Your GitHub Repository**
   - Click "Import Git Repository"
   - Select `NABILAAHMEDD/NYC-car-crashes-Analysis`
   - Authorize Vercel if needed

3. **Configure Project Settings**
   - **Framework Preset**: React
   - **Root Directory**: `frontend` ⚠️ **IMPORTANT: Set this to `frontend`**
   - **Build Command**: `npm install && npm run build` (or just `npm run build` if dependencies are auto-installed)
   - **Output Directory**: `build`
   - **Install Command**: `npm install`

4. **Add Environment Variable**
   - Click "Environment Variables"
   - Add:
     - **Name**: `REACT_APP_API_URL`
     - **Value**: `https://your-backend-url.onrender.com/api` (or your Railway URL)
     - **Environment**: Production, Preview, Development (select all)

5. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Copy your frontend URL (e.g., `https://your-app.vercel.app`)

### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI globally
npm install -g vercel

# Navigate to frontend directory
cd frontend

# Login to Vercel
vercel login

# Deploy (first time will ask for configuration)
vercel

# Set environment variable
vercel env add REACT_APP_API_URL production

# Deploy to production
vercel --prod
```

---

## 🔧 Backend Deployment (Render)

### Step 1: Prepare Backend

✅ Already done:
- `requirements.txt` includes `gunicorn`
- `Procfile` created for production server
- CORS configured to allow all origins

### Step 2: Deploy on Render

1. **Create Account**
   - Go to: https://render.com
   - Sign up (use GitHub for easy integration)

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Click "Connect GitHub"
   - Authorize Render
   - Select repository: `NABILAAHMEDD/NYC-car-crashes-Analysis`

3. **Configure Service**
   - **Name**: `nyc-crashes-backend` (or any name you prefer)
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: `backend` ⚠️ **IMPORTANT: Set this to `backend`**
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

4. **Upload Data File**
   - **IMPORTANT**: You need to upload `crashes_cleaned.csv`
   - Option A: Use Render Shell
     - After deployment, go to your service
     - Click "Shell" tab
     - Upload `crashes_cleaned.csv` to the backend directory
   - Option B: Use GitHub (add to repository)
     - Add `crashes_cleaned.csv` to your repository
     - It will be automatically available during deployment

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (takes 5-10 minutes)
   - Copy your backend URL (e.g., `https://nyc-crashes-backend.onrender.com`)

6. **Update Frontend Environment Variable**
   - Go back to Vercel dashboard
   - Update `REACT_APP_API_URL` to: `https://your-backend-url.onrender.com/api`
   - Redeploy frontend

---

## 🚂 Backend Deployment (Railway) - Alternative

Railway is another great option for backend deployment:

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize Project**
   ```bash
   cd backend
   railway init
   ```

4. **Deploy**
   ```bash
   railway up
   ```

5. **Add Environment Variables** (if needed)
   ```bash
   railway variables set PORT=5000
   ```

6. **Get Your Backend URL**
   - Railway will provide a URL like: `https://your-app.up.railway.app`
   - Update Vercel environment variable with this URL

---

## 📝 Post-Deployment Checklist

### Backend ✅
- [ ] Backend is accessible at your backend URL
- [ ] Health check works: `https://your-backend-url.com/api/health`
- [ ] CORS allows requests from your Vercel domain
- [ ] `crashes_cleaned.csv` is accessible in the backend directory

### Frontend ✅
- [ ] Frontend is accessible at your Vercel URL
- [ ] `REACT_APP_API_URL` is set correctly in Vercel
- [ ] Frontend can communicate with backend (check browser console)
- [ ] All charts and visualizations load correctly

---

## 🔄 Updating Your Deployment

### To Update Frontend:
1. Make changes to your code
2. Commit and push to GitHub: `git push origin main`
3. Vercel will automatically redeploy

### To Update Backend:
1. Make changes to your code
2. Commit and push to GitHub: `git push origin main`
3. Render/Railway will automatically redeploy

---

## 🐛 Troubleshooting

### Frontend Issues

**Problem**: Frontend can't connect to backend
- **Solution**: Check `REACT_APP_API_URL` in Vercel environment variables
- Make sure it ends with `/api` (e.g., `https://backend.onrender.com/api`)

**Problem**: Build fails on Vercel
- **Solution**: Check Root Directory is set to `frontend`
- Verify `package.json` exists in frontend directory

### Backend Issues

**Problem**: Backend can't find `crashes_cleaned.csv`
- **Solution**: Upload the file to the backend directory on your hosting platform
- Or add it to GitHub (if not too large)

**Problem**: CORS errors
- **Solution**: Backend CORS is already configured to allow all origins
- If using specific domain, update `app.py` CORS settings

**Problem**: Backend crashes on Render
- **Solution**: Check Render logs
- Verify `Procfile` uses correct command: `gunicorn app:app --bind 0.0.0.0:$PORT`
- Ensure all dependencies are in `requirements.txt`

---

## 📊 Final URLs

After deployment, you should have:

- **Frontend URL**: `https://your-app.vercel.app`
- **Backend URL**: `https://your-backend.onrender.com` (or Railway URL)
- **Backend API Base**: `https://your-backend.onrender.com/api`

---

## 🎉 You're Done!

Your dashboard should now be live and accessible from anywhere!

