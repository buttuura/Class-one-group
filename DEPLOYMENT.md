# Simple Deployment Guide

Follow these 3 easy steps to deploy your app.

---

## STEP 1: Create Google Sheets Setup (5 minutes)

### A. Create Service Account

1. Go to: https://console.cloud.google.com/
2. Click **"Create Project"** (if you don't have one)
3. Name it: "Savings App" → Click **Create**
4. Wait for project to be created
5. Click **"Go to project dashboard"**

6. **Enable Google Sheets API:**
   - Search for "Google Sheets API" in search bar
   - Click on it
   - Click **ENABLE**

7. **Create Service Account:**
   - Go to: **Menu** (☰) → **IAM & Admin** → **Service Accounts**
   - Click **+ CREATE SERVICE ACCOUNT**
   - Name: `savings-service`
   - Click **CREATE AND CONTINUE**
   - Click **DONE** (skip optional steps)

8. **Download Credentials:**
   - Click on the service account you just created
   - Go to **KEYS** tab
   - Click **ADD KEY** → **Create new key**
   - Choose **JSON**
   - Click **CREATE**
   - File downloads automatically ✅

### B. Create Google Sheet

1. Go to: https://sheets.google.com/
2. Click **+ Blank** to create new sheet
3. Name it: "Savings Data"
4. **Copy the ID from URL:**
   ```
   https://docs.google.com/spreadsheets/d/THIS-IS-THE-ID/edit
   ```
   Save this ID somewhere!

5. **Share with Service Account:**
   - Click **Share** button (top right)
   - Open the JSON file you downloaded
   - Find `"client_email"` (looks like: name@project.iam.gserviceaccount.com)
   - Copy that email
   - Paste into Share dialog
   - Choose **Editor**
   - **UNCHECK** "Notify people"
   - Click **Share**

✅ Google Sheets Setup Complete!

---

## STEP 2: Push Code to GitHub (2 minutes)

1. Go to: https://github.com/new
2. Repository name: `savings-app`
3. Choose **Public** or **Private**
4. **DO NOT** check "Initialize with README"
5. Click **Create repository**

6. **Upload your files:**
   - Click **uploading an existing file**
   - Drag all your files and folders
   - Click **Commit changes**

✅ Code on GitHub!

---

## STEP 3: Deploy on Render (5 minutes)

### A. Create Web Service

1. Go to: https://dashboard.render.com/
2. Click **New +** → **Web Service**
3. Click **Connect GitHub** (if not connected)
4. Find and select your `savings-app` repository
5. Click **Connect**

### B. Configure Service

Fill in these fields:

**Name:** `savings-app` (or anything you like)

**Runtime:** `Python 3`

**Build Command:** 
```
cd backend && pip install -r requirements.txt
```

**Start Command:**
```
cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT
```

**Instance Type:** `Free`

### C. Add Environment Variables

Scroll down to **Environment Variables** section.

Click **Add Environment Variable** 3 times and add these:

**Variable 1:**
- Key: `JWT_SECRET`
- Value: `my-super-secret-key-change-this-later`

**Variable 2:**
- Key: `SPREADSHEET_ID`
- Value: [Paste the ID you copied from Google Sheets URL]

**Variable 3:**
- Key: `GOOGLE_CREDENTIALS_JSON`
- Value: [Open the JSON file you downloaded, copy EVERYTHING, paste here]

**Important:** For GOOGLE_CREDENTIALS_JSON:
- Open the downloaded JSON file in Notepad
- Select ALL (Ctrl+A)
- Copy (Ctrl+C)
- Paste into Render

### D. Deploy!

1. Click **Create Web Service** (bottom of page)
2. Wait 2-3 minutes for deployment
3. You'll see: ✅ **Live** (green)
4. Your app URL: `https://your-app-name.onrender.com`

✅ App is Live!

---

## STEP 4: First Login

1. Visit your app URL
2. Click **Login**
3. Enter:
   - Username: `admin`
   - Password: `123456`
4. You're in! 🎉

**⚠️ Change password immediately:**
- Go to your Google Sheet
- Find the Users tab
- Change admin password in the sheet

---

## That's It!

Your app is now live and working!

**What you can do:**
- ✅ Register new users
- ✅ Make deposits
- ✅ Request withdrawals
- ✅ Admin approves requests
- ✅ Premium members get loans

**Your App URL:** Check Render dashboard for your link

---

## If Something Goes Wrong

**App shows error page:**
1. Go to Render Dashboard
2. Click on your service
3. Click **Logs** tab
4. Look for error messages
5. Most common issue: Environment variables not set correctly

**"Failed to load data":**
- Make sure you shared Google Sheet with service account email
- Check SPREADSHEET_ID is correct

**Need help?**
- Check Render logs first
- Verify all 3 environment variables are set
- Make sure Google Sheet is shared
