# How to Upload Large CSV File to Render

Since your CSV file is 1.26 GB (too large for Git), upload it directly to Render:

## Method 1: Upload via Render Shell (Quick Fix)

1. **Go to Render Dashboard**
   - Open your service: `nyc-crashes-backend`
   - Click "Shell" tab
   - Click "Connect" or "Open Shell"

2. **Navigate to backend directory**
   ```bash
   cd backend
   ```

3. **Upload the file**
   - If Render has file upload: Use the upload button
   - Or use Python to receive the file:
   ```bash
   python3 -m http.server 8000
   # Then download from your local machine to Render
   ```

## Method 2: Use External Storage (Recommended - Permanent)

Store the CSV file externally and download it at startup:

1. **Upload CSV to cloud storage**:
   - Google Drive (make it publicly accessible)
   - GitHub Releases (max 2GB per file)
   - AWS S3 or similar
   - Dropbox (with public link)

2. **Update app.py to download at startup**:
   ```python
   import urllib.request
   import os
   
   CSV_URL = os.environ.get('CSV_URL', 'https://your-drive-url/file.csv')
   CSV_FILE = 'crashes_cleaned.csv'
   
   if not os.path.exists(CSV_FILE):
       print(f"Downloading CSV from {CSV_URL}...")
       urllib.request.urlretrieve(CSV_URL, CSV_FILE)
       print("Download complete!")
   
   df = pd.read_csv(CSV_FILE)
   ```

3. **Set environment variable in Render**:
   - Name: `CSV_URL`
   - Value: Your file URL

## Method 3: Use Git LFS (For Future)

For very large files in Git:
```bash
git lfs install
git lfs track "*.csv"
git add .gitattributes
git add backend/crashes_cleaned.csv
git commit -m "Add CSV with Git LFS"
git push origin main
```

---

## Immediate Solution: Upload via Shell

The fastest way is to upload directly via Render Shell. Once uploaded, your backend will work!

