# vitamin-deficiency

## Deploy On Streamlit Community Cloud
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

## Project Overview
This project focuses on developing and comparing multiple deep learning models to detect vitamin deficiencies from images of specific body parts (e.g., lips, tongue, eyes, nails). The models were created to offer a non-invasive, AI-powered diagnostic tool that can analyze visual indicators associated with vitamin deficiencies. The aim is to provide an accessible solution to detect deficiencies using a smartphone app, without requiring costly lab tests.

## Key Features
- **Multiple CNN Models**: Trained several Convolutional Neural Networks (CNNs), including EfficientNetV2, InceptionResNetV2, MobileNet, VGG16, ResNet, and InceptionV3, to compare efficiency and accuracy in detecting deficiency indicators.
- **Ensemble Learning**: Integrated multiple models to enhance prediction accuracy through ensemble techniques.
- **Image Analysis with Deep Learning**: Detects visual symptoms, like discoloration or structural abnormalities, associated with various vitamin deficiencies.
- **Non-Invasive Testing**: Utilizes image-based analysis, allowing users to get insights without blood samples.

## Files and Models
- **EfficientNetV2L.ipynb**: Notebook for EfficientNetV2 model training and efficiency calculation.
- **InceptionResNetV2.ipynb**: Implements the InceptionResNetV2 model, comparing performance on deficiency detection.
- **Mobilenet.ipynb**: Trains the MobileNet model, known for its lightweight structure, ideal for mobile deployment.
- **cnn.ipynb**: A base CNN architecture used as a benchmark.
- **ensemble.ipynb**: Combines multiple models to create an ensemble that aggregates predictions for better accuracy.
- **inceptionV3.ipynb**: Uses the InceptionV3 model to analyze deficiencies and assess performance.
- **resnet.ipynb**: Trains the ResNet model with updated parameters for optimized prediction accuracy.
- **test.ipynb**: Contains test cases and evaluation metrics for all models after removing fuzzy inference.
- **vgg16.ipynb**: Trains and evaluates the VGG16 model, known for its strong performance in image classification.
- **xception.ipynb**: Implements the Xception model, which uses depthwise separable convolutions for efficient feature extraction.

## Requirements
- **Python** and **Jupyter Notebook**
- **TensorFlow** and **Keras**: For building and training the deep learning models.
- **Android Studio** (optional): For testing and deploying the model on mobile applications.

## Usage Instructions
1. **Run Models**: Open each notebook and run cells to train individual models on the dataset.
2. **Evaluate Models**: After training, each notebook calculates efficiency and accuracy metrics.
3. **Ensemble Approach**: Use the `ensemble.ipynb` to aggregate predictions from individual models, enhancing overall accuracy.
4. **Deployment**: Export the trained model as a TensorFlow Lite format for deployment on mobile devices.

## Future Work
- **Extended Dataset**: Improve model robustness by training with a more diverse image dataset.
- **App Integration**: Incorporate into a smartphone app to allow real-time deficiency detection.
- **Enhance Model Efficiency**: Optimize model parameters for faster, low-latency inference suitable for mobile deployment.

