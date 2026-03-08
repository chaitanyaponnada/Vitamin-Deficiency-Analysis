# GitHub Release Setup for Model Files

## Step 1: Create GitHub Release

1. Go to your repository: https://github.com/chaitanyaponnada/Vitamin-Deficiency-Analysis
2. Click on `Releases` (right sidebar)
3. Click `Create a new release` or `Draft a new release`
4. Fill in the following:
   - **Tag version**: `v1.0-models` (IMPORTANT: must match exactly)
   - **Release title**: `Model Files v1.0`
   - **Description**: `Pre-trained model files for vitamin deficiency detection`

## Step 2: Upload Model Files

Upload ALL these files from `model_saved_files/` folder:

Required files:
- [ ] Cnn.h5
- [ ] EfficientNetV2L.h5
- [ ] InceptionResNetV2.h5
- [ ] InceptionV3.h5
- [ ] Mobilenet.h5
- [ ] ResNet.h5
- [ ] VGG16.h5
- [ ] Xception.h5
- [ ] ensemble_metadata.json

**How to upload:**
- Drag and drop all 9 files into the "Attach binaries" area at the bottom of the release form
- Wait for all uploads to complete (this may take several minutes due to large file sizes)

## Step 3: Publish Release

1. Once all files are uploaded, click `Publish release`
2. Verify all 9 files appear as release assets

## Step 4: Push Updated Code

After creating the release, run:

```powershell
git add .
git commit -m "Switch from Git LFS to GitHub Releases for model files"
git push origin main
```

## Step 5: Deploy to Render

1. Go to Render Dashboard
2. Your service will auto-deploy (or click Manual Deploy)
3. Watch build logs for: "Downloading model files from GitHub Release..."
4. Verify all models download successfully

## Why This Works

- GitHub Releases have much higher bandwidth limits than LFS
- Models are downloaded fresh during each Docker build
- No LFS quota issues
- Deployment is now reliable and free
