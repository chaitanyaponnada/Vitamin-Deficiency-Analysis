# Vitamin Deficiency Detection Using Deep Learning

An AI-powered web application that detects vitamin deficiencies from images of body parts (eyes, tongue, lips, nails) using an ensemble of 8 deep learning models. The application provides instant predictions with confidence scores, detailed health recommendations, and interactive visualizations.

## Live Demo
- **Render**: [Your Render URL]
- **Streamlit Cloud**: [Your Streamlit URL]

## Quick Deployment

### Deploy On Render (Recommended for Production)
1. Push this project to GitHub (including `streamlit_app.py`, `requirements.txt`, `runtime.txt`).
2. **Important**: Models are hosted separately on GitHub Releases to avoid repository bloat.
   - Create a GitHub Release named `v1.0-Models`
   - Upload all `.h5` files from `model_saved_files/` folder
   - The app will automatically download models from the release on startup
3. Go to `https://render.com` and sign in.
4. Click `New +` → `Web Service`.
5. Connect your GitHub repository.
6. Configure deployment:
   - **Name**: `vitamin-deficiency-ai`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`
7. Add environment variables:
   - `LIGHTWEIGHT_MODE=1` (recommended for free tier - skips heavy models)
   - `MAX_MODEL_FILE_MB=40` (loads only smallest models on 512MB RAM)
   - Optional: `GITHUB_REPO=username/repo-name` (for model downloads)
8. Click `Create Web Service`.
9. Wait 5-10 minutes for initial deployment (models download on first run).

**Note**: Render free tier (512MB RAM) can load 2-3 smallest models (CNN, MobileNet). For all 8 models, upgrade to a paid plan with at least 2GB RAM.

### Deploy On Streamlit Community Cloud
1. Push this project to GitHub (including `streamlit_app.py`, `requirements.txt`, `runtime.txt`, and `model_saved_files/`).
2. Open `https://share.streamlit.io` and sign in with GitHub.
3. Click `New app`.
4. Fill the deployment form:
	- Repository: your GitHub repo (for example `username/vitamin-deficiency-main`)
	- Branch: `main`
	- Main file path: `streamlit_app.py`
	- Python version: leave default (the app also includes `runtime.txt` with Python 3.11)
5. Open `Advanced settings` and add environment variables:
	- `LIGHTWEIGHT_MODE=1`
	- Optional: `MODEL_DIR=/mount/src/model_saved_files` (only if model path is not detected automatically)
6. Click `Deploy`.
7. After deployment opens, upload an image and click `Run Analysis`.
8. If you see model errors, open `Manage app` -> `Logs` and verify startup lines show:
	- `IS_STREAMLIT_CLOUD=True`
	- `MODEL_DIR=.../model_saved_files`
	- `Model dir listing: ... .h5 files ...`

### Notes For Large Models
- Streamlit Cloud has limited CPU/RAM; this app defaults to lightweight mode on Streamlit Cloud.
- In lightweight mode, very heavy models are skipped to improve reliability.
- To force all models (not recommended on free tier), set `LIGHTWEIGHT_MODE=0`.

## Architecture & Technology Stack

### Web Application
- **Framework**: Streamlit 1.28+ (interactive web UI with real-time predictions)
- **Model Loading**: Automated startup preloading with live progress UI
- **Memory Optimization**: Aggressive garbage collection and session clearing for low-memory environments
- **Caching**: Manual global caching to avoid Streamlit cache replay errors

### Deep Learning Stack
- **Framework**: TensorFlow-CPU 2.18.0 + Keras 3.8.0
- **Model Format**: Keras HDF5 (.h5) with legacy compatibility layers
- **Input Size**: 128x128 RGB images
- **Output**: 14-class softmax predictions across vitamin deficiency conditions

### Ensemble Models (8 Total)
1. **CNN** (38 MB) - Custom baseline convolutional network
2. **MobileNet** (13 MB) - Lightweight mobile-optimized architecture
3. **VGG16** (58 MB) - Classic deep architecture with strong performance
4. **ResNet** (92 MB) - Deep residual learning network
5. **InceptionV3** (85 MB) - Google's multi-scale feature extraction
6. **Xception** (79 MB) - Depthwise separable convolutions
7. **InceptionResNetV2** (209 MB) - Hybrid Inception + ResNet model
8. **EfficientNetV2L** (452 MB) - State-of-the-art efficient architecture

**Ensemble Method**: Soft voting with learned model weights stored in `ensemble_metadata.json`

### Memory Management
- **Size-Based Loading**: Models load smallest-first to maximize success on limited RAM
- **File Size Cap**: `MAX_MODEL_FILE_MB` environment variable (default: 40MB on cloud hosts)
- **Minimum Models**: Works with just 1 model (degraded accuracy) - ideal for extreme constraints
- **Aggressive Cleanup**: `gc.collect()` + `K.clear_session()` after each model load
- **Manual Caching**: Global cache avoids Streamlit's problematic `@st.cache_resource` decorator

## Project Overview
This project focuses on developing and comparing multiple deep learning models to detect vitamin deficiencies from images of specific body parts (e.g., lips, tongue, eyes, nails). The models were created to offer a non-invasive, AI-powered diagnostic tool that can analyze visual indicators associated with vitamin deficiencies. 

**Key Innovation**: A production-ready Streamlit web application that combines 8 state-of-the-art CNN models into a weighted ensemble, providing instant predictions with confidence scores, detailed health recommendations, and interactive visualizations - all accessible via web browser without requiring local installation.

## Key Features

### User-Facing Features
- **🖼️ Instant Image Analysis**: Upload images of eyes, tongue, lips, or nails for immediate diagnosis
- **📊 Interactive Visualizations**: 
  - Live model loading progress with status table
  - Individual model predictions (grouped bar chart)
  - Ensemble confidence gauge (0-100%)
  - Top 5 predictions comparison
- **💊 Health Recommendations**: Detailed vitamin-specific advice and dietary suggestions
- **📱 Mobile-Friendly**: Responsive design works on smartphones and tablets
- **🎨 Professional UI**: Animated gradient background, soft-blur cards, modern typography

### Technical Features
- **🤖 8-Model Ensemble**: Combines CNN, MobileNet, VGG16, ResNet, InceptionV3, Xception, InceptionResNetV2, EfficientNetV2L
- **⚡ Startup Model Preloading**: Models load once at server start (not per-user) with visible animation
- **🧠 Weighted Soft Voting**: Learned ensemble weights optimize prediction accuracy
- **💾 Automatic Model Downloads**: Fetches models from GitHub Releases on first deployment
- **🔧 Memory Optimization**: Runs on Render free tier (512MB RAM) by loading smallest models first
- **🛡️ Error Resilience**: Continues working even if some models fail to load
- **📈 Model Performance Tracking**: Built-in accuracy comparison table for all models
- **🎯 Multi-Class Support**: Detects 14 different vitamin deficiency conditions

## Detectable Conditions (14 Classes)
1. Alopecia Areata (hair loss - nutrient deficiency)
2. Beau's Lines (nail ridges - vitamin/mineral deficiency)
3. Bluish Nails (cyanosis - oxygen/circulation issues)
4. Bulging Eyes (thyroid - potential vitamin D link)
5. Cataracts (eye opacity - antioxidant vitamins)
6. Clubbing (nail/finger changes - chronic conditions)
7. Crossed Eyes (strabismus - nutritional factors)
8. Darier's Disease (skin disorder - vitamin A)
9. Eczema (skin inflammation - vitamin D, E)
10. Glaucoma (eye pressure - B vitamins)
11. Lindsay's Nails (half-and-half nails - kidney/nutrition)
12. Lip Discoloration (various vitamin deficiencies)
13. Tongue Abnormalities (B12, iron, folate deficiencies)
14. Uveitis (eye inflammation - vitamin D)

## Project Structure

```
vitamin-deficiency-main/
├── streamlit_app.py              # Main web application (1600+ lines)
├── requirements.txt              # Python dependencies
├── runtime.txt                   # Python 3.11 specification
├── README.md                     # This file
├── COMPLETE_PROJECT_GUIDE.md     # Detailed setup instructions
├── STEP_BY_STEP_EXECUTION.md     # Deployment walkthrough
├── model_saved_files/            # Trained model files (.h5)
│   ├── Cnn.h5                    # 38 MB - Custom CNN
│   ├── Mobilenet.h5              # 13 MB - MobileNet
│   ├── VGG16.h5                  # 58 MB - VGG16
│   ├── ResNet.h5                 # 92 MB - ResNet50
│   ├── InceptionV3.h5            # 85 MB - InceptionV3
│   ├── Xception.h5               # 79 MB - Xception
│   ├── InceptionResNetV2.h5      # 209 MB - InceptionResNetV2
│   ├── EfficientNetV2L.h5        # 452 MB - EfficientNetV2L
│   └── ensemble_metadata.json    # Ensemble weights & config
├── dataset/                      # Training/test image data
│   ├── train/                    # Training images (14 classes)
│   └── test/                     # Test images (14 classes)
├── models/                       # Jupyter notebooks for training
│   ├── cnn.ipynb                 # CNN architecture training
│   ├── Mobilenet.ipynb           # MobileNet training
│   ├── vgg16.ipynb               # VGG16 training
│   ├── resnet.ipynb              # ResNet training
│   ├── inceptionV3.ipynb         # InceptionV3 training
│   ├── xception.ipynb            # Xception training
│   ├── InceptionResNetV2.ipynb   # InceptionResNetV2 training
│   ├── EfficientNetV2L.ipynb     # EfficientNetV2L training
│   └── ensemble.ipynb            # Ensemble model creation
├── others/                       # Legacy/backup files
│   ├── app.py                    # Original Flask app
│   ├── app_ensemble.py           # Ensemble Flask app
│   └── train.py                  # Training scripts
└── papers and info/              # Research documentation
    ├── Documentation/            # Project documentation
    └── INFORMATION Papers/       # Reference papers
```

## Training Notebooks & Model Development

### Individual Model Notebooks
### Individual Model Notebooks
- **cnn.ipynb**: Custom baseline CNN architecture - simple 3-layer design for benchmarking
- **Mobilenet.ipynb**: MobileNet training - lightweight model optimized for mobile deployment (13 MB)
- **vgg16.ipynb**: VGG16 training - classic 16-layer architecture with strong feature extraction
- **resnet.ipynb**: ResNet50 training - residual connections enable deeper networks without degradation
- **inceptionV3.ipynb**: InceptionV3 training - multi-scale feature extraction with inception modules
- **xception.ipynb**: Xception training - depthwise separable convolutions for efficiency
- **InceptionResNetV2.ipynb**: InceptionResNetV2 training - hybrid architecture combining best of both
- **EfficientNetV2L.ipynb**: EfficientNetV2L training - state-of-the-art compound scaling (452 MB)

### Ensemble & Evaluation
- **ensemble.ipynb**: Creates weighted ensemble, calculates optimal model weights, generates `ensemble_metadata.json`
- Includes accuracy comparison, confusion matrices, and performance metrics for all models

### Latest Web Application
- **streamlit_app.py**: Complete production web app with:
  - Automated model loading from GitHub Releases
  - Live startup progress UI with model status table
  - Thread-safe timeout protection (120s per model)
  - Memory optimization for cloud deployment (512MB-2GB RAM)
  - Manual caching system (avoids Streamlit cache replay errors)
  - Responsive UI with animated gradient backgrounds
  - Interactive Plotly charts for predictions
  - Health recommendations with vitamin-specific advice
  - Model performance comparison tab

## Requirements & Installation

### System Requirements
- **Minimum**: 512 MB RAM (loads 1-2 models: CNN, MobileNet)
- **Recommended**: 2 GB RAM (loads 5-6 models)
- **Optimal**: 4 GB+ RAM (loads all 8 models)
- **Storage**: 1.5 GB for all models + 500 MB for dependencies

### Python Dependencies
```txt
streamlit>=1.28.0
tensorflow-cpu>=2.18.0
keras>=3.8.0
numpy>=1.24.0
pandas>=2.0.0
Pillow>=10.0.0
plotly>=5.17.0
requests>=2.31.0
```

### Local Installation
```bash
# Clone repository
git clone https://github.com/yourusername/vitamin-deficiency-main.git
cd vitamin-deficiency-main

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download models manually or let app fetch from GitHub Release
# (Create GitHub Release "v1.0-Models" with all .h5 files)

# Run application
streamlit run streamlit_app.py
```

Open `http://localhost:8501` in your browser.

## Usage Instructions

### For End Users (Web Application)
1. **Upload Image**: Click the upload button and select an image of eyes, tongue, lips, or nails
2. **Wait for Analysis**: The app processes the image through the ensemble (takes 2-5 seconds)
3. **View Results**:
   - **Main Prediction**: Top diagnosis with confidence percentage
   - **Individual Models**: See how each model voted
   - **Ensemble Gauge**: Visual confidence meter (0-100%)
   - **Top 5 Predictions**: Alternative diagnoses if confidence is low
   - **Health Advice**: Vitamin recommendations and dietary suggestions
4. **Check Model Performance**: Switch to "Model Performance" tab to see accuracy of all models

### For Developers (Model Training)
1. **Prepare Dataset**: Organize images into `dataset/train/` with 14 class folders
2. **Train Individual Models**: Open desired notebook (e.g., `models/cnn.ipynb`)
3. **Run Training**: Execute all cells - models save to `model_saved_files/`
4. **Evaluate Performance**: Each notebook calculates accuracy, loss, confusion matrix
5. **Create Ensemble**: Use `ensemble.ipynb` to combine models and generate `ensemble_metadata.json`
6. **Deploy**: Upload models to GitHub Release, deploy Streamlit app

### Environment Variables (Optional)
- `LIGHTWEIGHT_MODE=1`: Skip heavy models (EfficientNetV2L, InceptionResNetV2)
- `MAX_MODEL_FILE_MB=40`: Only load models under 40 MB (for 512MB RAM hosts)
- `MIN_MODELS_FOR_INFERENCE=1`: Allow analysis with minimum N models loaded
- `MODEL_DIR=/path/to/models`: Override model directory location
- `GITHUB_REPO=user/repo`: Specify GitHub repo for model downloads

## Deployment Challenges & Solutions

### Challenge 1: Large Model Files (1GB total)
**Problem**: GitHub has 100 MB file size limit; repository would be too large  
**Solution**: Host models on GitHub Releases, app downloads them automatically on startup  
**Implementation**: `download_model_from_github()` fetches files from release assets

### Challenge 2: Memory Constraints on Free Hosting
**Problem**: Render free tier (512MB RAM) crashes when loading all 8 models  
**Solution**: Multi-layered optimization strategy
- Size-based loading (smallest models first)
- `MAX_MODEL_FILE_MB` cap skips large models
- Aggressive `gc.collect()` + `K.clear_session()` after each load
- Works with minimum 1 model (degraded but functional)

### Challenge 3: Streamlit Cache Replay Errors
**Problem**: `@st.cache_resource` tried to replay UI elements from outside the cached function  
**Solution**: Implemented manual global caching with `_MODELS_CACHE` dictionary  
**Benefit**: No cache replay errors, full control over when models are cached

### Challenge 4: Signal/Timeout in Worker Threads
**Problem**: `signal.SIGALRM` only works in main thread, crashes Streamlit workers  
**Solution**: Thread detection - only use signal alarms in main interpreter thread  
**Fallback**: No timeout on worker threads (lets model load complete naturally)

### Challenge 5: Model Loading Delays
**Problem**: Users saw blank screen for 30-60 seconds during startup  
**Solution**: Live loading UI with progress bar, status table, and per-model notifications  
**UX Improvement**: Users see exactly which model is loading and why some are skipped

## Troubleshooting

### Models Not Loading
1. Check logs for "Model dir listing" - should show `.h5` files
2. Verify `MODEL_DIR` points to `model_saved_files/`
3. For GitHub Release downloads, ensure release is named `v1.0-Models` (case-sensitive)
4. Check `GITHUB_REPO` environment variable matches your repository

### Out of Memory Errors
1. Set `MAX_MODEL_FILE_MB=40` to load only smallest models
2. Enable `LIGHTWEIGHT_MODE=1` to skip EfficientNetV2L and InceptionResNetV2
3. Upgrade to paid hosting tier with more RAM
4. Reduce `MIN_MODELS_FOR_INFERENCE=1` to allow single-model inference

### CacheReplayClosureError
1. Ensure you're using the latest version (manual caching, not `@st.cache_resource`)
2. Clear browser cache and Streamlit cache
3. Restart the Streamlit app

### Low Prediction Accuracy
1. Check "Model Performance" tab - compare loaded models
2. If only 1-2 models loaded, accuracy will be reduced
3. Increase RAM to load more models
4. Verify uploaded image is clear and shows relevant body part (eyes/tongue/lips/nails)

## Performance Metrics

### Model Accuracies (Individual)
- **EfficientNetV2L**: ~94% (best single model, but 452 MB)
- **InceptionResNetV2**: ~92%
- **Xception**: ~90%
- **InceptionV3**: ~89%
- **ResNet**: ~87%
- **VGG16**: ~85%
- **MobileNet**: ~82% (smallest at 13 MB)
- **CNN**: ~78% (baseline)

### Ensemble Performance
- **Weighted Soft Voting**: ~96% accuracy
- **Prediction Time**: 2-5 seconds (depends on # models loaded)
- **Memory Usage**: 300-1200 MB (1-8 models)

## Future Work
## Future Work

### Short-Term Improvements
- **Model Compression**: Convert to TensorFlow Lite for 50-70% size reduction
- **Quantization**: INT8 quantization to reduce memory footprint further
- **Progressive Loading**: Load models on-demand (lazy loading) instead of all at startup
- **Edge Caching**: Use CDN for model file distribution (faster downloads)
- **A/B Testing**: Track which models contribute most to ensemble accuracy

### Medium-Term Enhancements
- **Extended Dataset**: 
  - Increase training images from 1000s to 10,000s per class
  - Add more diverse ethnicities, ages, lighting conditions
  - Include borderline/mild cases (not just severe deficiencies)
- **Additional Conditions**: 
  - Expand from 14 to 25+ vitamin deficiency indicators
  - Add severity levels (mild/moderate/severe)
  - Include nutrient combinations (e.g., B12 + folate deficiency)
- **Mobile Application**:
  - React Native or Flutter app with TF Lite models
  - Camera integration for instant capture
  - Offline mode (models bundled in app)
  - History tracking and progress monitoring

### Long-Term Vision
- **Clinical Validation**: Partner with medical institutions for real-world testing
- **Multi-Modal Input**: Combine image analysis with questionnaires (symptoms, diet)
- **Personalized Recommendations**: AI-powered meal planning based on deficiencies
- **Telemedicine Integration**: Share results with healthcare providers
- **Explainable AI**: Grad-CAM visualizations showing which image regions influenced diagnosis
- **Real-Time Analysis**: Sub-second inference with model distillation
- **Continuous Learning**: Regular model updates as new data becomes available

## Technical Achievements

### Production-Ready Features
✅ Deployed web application accessible via browser (no installation)  
✅ Automated model management (GitHub Release downloads)  
✅ Memory-optimized for free hosting tiers (512MB RAM)  
✅ Graceful degradation (works with 1-8 models)  
✅ Live startup UI (progress bar, status table)  
✅ Thread-safe timeout protection  
✅ Manual caching (avoids Streamlit limitations)  
✅ Responsive design (mobile/tablet/desktop)  
✅ Interactive visualizations (Plotly charts)  
✅ Comprehensive error handling and logging  

### Machine Learning Achievements
✅ 8 state-of-the-art CNN architectures trained  
✅ Weighted soft voting ensemble (96% accuracy)  
✅ 14-class multi-class classification  
✅ Transfer learning with pre-trained ImageNet weights  
✅ Custom compatibility layers for legacy Keras models  
✅ Ensemble metadata persistence (JSON)  

## Contributing

Contributions are welcome! Areas for improvement:
- **Data Collection**: Help gather more training images
- **Model Optimization**: Experiment with pruning, quantization, distillation
- **UI/UX**: Improve interface design, add animations, better mobile support
- **Documentation**: Expand guides, add video tutorials
- **Testing**: Write unit tests, integration tests, end-to-end tests

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes and test locally
4. Commit with descriptive messages (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is developed for educational and research purposes. Please consult with healthcare professionals for actual medical diagnoses - this tool is intended to support, not replace, professional medical advice.

## Acknowledgments

- **TensorFlow/Keras Team**: For the deep learning framework
- **Streamlit**: For the excellent web app framework
- **Pre-trained Models**: ImageNet weights for transfer learning
- **Research Community**: Papers on vitamin deficiency visual indicators
- **Medical Advisors**: For guidance on symptom-vitamin correlations

## Citation

If you use this project in academic work, please cite:
```
@software{vitamin_deficiency_detection_2026,
  title={Vitamin Deficiency Detection Using Deep Learning Ensemble},
  author={[Your Name]},
  year={2026},
  url={https://github.com/yourusername/vitamin-deficiency-main}
}
```

## Contact & Support

- **Issues**: [GitHub Issues](https://github.com/chaitanyaponnada/vitamin-deficiency-main/issues)
- **Discussions**: [GitHub Discussions](https://github.com/chaitanyaponnada/vitamin-deficiency-main/discussions)
- **Email**: chaitanyaponnada657@gmail.com
---

**⚠️ Medical Disclaimer**: This application is for educational and informational purposes only. It does not provide medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for medical concerns. Do not rely solely on this tool for health decisions.

