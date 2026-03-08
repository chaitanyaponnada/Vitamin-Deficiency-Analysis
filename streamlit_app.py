import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
# Force CPU runtime on platforms like Render to avoid CUDA init overhead/noise.
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import warnings
warnings.filterwarnings('ignore')

import logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)
import time
import traceback
from pathlib import Path

import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import keras
from keras.models import load_model
from keras import ops
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime


APP_LOGGER = logging.getLogger("vitamin_app")
if not APP_LOGGER.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(message)s"))
    APP_LOGGER.addHandler(_handler)
APP_LOGGER.setLevel(logging.INFO)


def log_event(message, level="info"):
    """Log to Render CLI and keep flush behavior predictable."""
    msg = f"[vitamin-app] {message}"
    if level == "error":
        APP_LOGGER.error(msg)
    elif level == "warning":
        APP_LOGGER.warning(msg)
    else:
        APP_LOGGER.info(msg)
    print(msg, flush=True)

# Page configuration
st.set_page_config(
    page_title="Vitamin Deficiency AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

THEME_BASE = (st.get_option("theme.base") or "light").lower()
IS_DARK_THEME = THEME_BASE == "dark"

# Custom CSS for professional styling
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background: transparent !important;
    }

    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stSidebar"] {
        background: transparent !important;
    }

    [data-testid="stAppViewContainer"] > .main,
    [data-testid="stAppViewContainer"] .block-container {
        position: relative;
        z-index: 2;
    }

    .video-bg-wrap {
        position: fixed;
        inset: 0;
        overflow: hidden;
        z-index: 0;
        pointer-events: none;
    }

    .video-bg-wrap video {
        width: 100%;
        height: 100%;
        object-fit: cover;
        filter: none;
    }

    .video-bg-overlay {
        position: fixed;
        inset: 0;
        z-index: 1;
        pointer-events: none;
        background: rgba(245, 247, 250, 0.16);
    }

    .block-container {
        max-width: 1120px;
        margin: 0 auto;
        padding-top: 0.4rem;
        padding-bottom: 0.6rem;
    }

    .main-shell {
        background: transparent;
        border: none;
        border-radius: 0;
        box-shadow: none;
        padding: 8px 4px 2px 4px;
        margin-top: 0;
        animation: fadeInUp 700ms ease-out;
        text-align: center;
    }

    .top-title {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0;
        letter-spacing: 0.2px;
        text-shadow: 0 1px 1px rgba(255,255,255,0.35);
    }

    .top-subtitle {
        margin-top: 6px;
        color: #1f2937;
        font-size: 1.02rem;
        font-weight: 500;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .center-wrap {
        background: rgba(255, 255, 255, 0.18);
        border: 1px solid rgba(15, 23, 42, 0.10);
        border-radius: 14px;
        padding: 14px;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        animation: fadeInUp 550ms ease-out;
    }

    .section-title {
        color: #0f172a;
        font-size: 1.12rem;
        font-weight: 700;
        margin: 0 0 6px 0;
    }

    .result-note {
        color: #1f2937;
        font-size: 0.92rem;
        line-height: 1.45;
        margin-bottom: 8px;
    }

    .prediction-card {
        background: rgba(255,255,255,0.50);
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-radius: 14px;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.10);
        padding: 14px;
        margin: 8px 0;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        animation: fadeInUp 500ms ease-out;
    }

    .soft-info {
        background: rgba(255,255,255,0.44);
        border: 1px solid rgba(15, 23, 42, 0.12);
        border-radius: 12px;
        padding: 10px 12px;
        color: #0f172a;
        font-size: 0.95rem;
        line-height: 1.5;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }

    .stButton>button {
        background: #111827;
        color: #ffffff;
        border: 1px solid #111827;
        border-radius: 12px;
        padding: 10px 18px;
        font-weight: 500;
        font-size: 0.95rem;
        transition: transform 260ms ease, box-shadow 260ms ease, background 260ms ease;
    }

    .stButton>button:hover {
        transform: translateY(-1px);
        background: #1f2937;
        box-shadow: 0 10px 28px rgba(17, 24, 39, 0.20);
    }

    .center-loader-wrap {
        position: fixed;
        inset: 0;
        z-index: 9999;
        display: flex;
        justify-content: center;
        align-items: center;
        background: rgba(255, 255, 255, 0.32);
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
    }

    .center-loader-card {
        display: inline-flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-width: 220px;
        padding: 20px 22px;
        border-radius: 14px;
        background: rgba(255,255,255,0.66);
        border: 1px solid rgba(15, 23, 42, 0.16);
        box-shadow: 0 18px 36px rgba(15, 23, 42, 0.18);
    }

    .center-loader {
        width: 52px;
        height: 52px;
        border: 4px solid rgba(15, 23, 42, 0.14);
        border-top-color: #0f172a;
        border-radius: 50%;
        animation: spinLoader 0.9s linear infinite;
    }

    .center-loader-text {
        margin-top: 10px;
        text-align: center;
        color: #0f172a;
        font-weight: 600;
        letter-spacing: 0.2px;
    }

    @keyframes spinLoader {
        to { transform: rotate(360deg); }
    }

    @keyframes fadeInUp {
        0% {
            opacity: 0;
            transform: translateY(10px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @media (max-width: 900px) {
        .block-container {
            padding-left: 0.7rem;
            padding-right: 0.7rem;
        }

        .top-title {
            font-size: 1.72rem;
        }

        .top-subtitle {
            font-size: 0.92rem;
        }

        .center-wrap {
            padding: 10px;
        }

        .stButton > button {
            width: 100%;
        }
    }
</style>
""", unsafe_allow_html=True)

# Configuration
BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / 'model_saved_files'
DATA_DIR = BASE_DIR / 'dataset' / 'train'
IMG_HEIGHT, IMG_WIDTH = 128, 128
ENSEMBLE_METHOD = 'soft_voting'
MODEL_MAPPING = {
    'CNN': 'Cnn.h5',
    'EfficientNetV2L': 'EfficientNetV2L.h5',
    'InceptionResNetV2': 'InceptionResNetV2.h5',
    'InceptionV3': 'InceptionV3.h5',
    'MobileNet': 'Mobilenet.h5',
    'ResNet': 'ResNet.h5',
    'VGG16': 'VGG16.h5',
    'Xception': 'Xception.h5'
}

HEAVY_MODELS = {'EfficientNetV2L', 'InceptionResNetV2'}
IS_RENDER = any([
    os.getenv('RENDER', '').lower() == 'true',
    bool(os.getenv('RENDER_SERVICE_ID')),
    bool(os.getenv('RENDER_INSTANCE_ID')),
])
LIGHTWEIGHT_MODE = os.getenv('LIGHTWEIGHT_MODE', '1' if IS_RENDER else '0') == '1'
ACTIVE_MODEL_NAMES = [
    name for name in MODEL_MAPPING.keys()
    if (not LIGHTWEIGHT_MODE) or (name not in HEAVY_MODELS)
]


@keras.utils.register_keras_serializable(package='Custom')
class CustomScaleLayer(keras.layers.Layer):
    """Compatibility layer for legacy InceptionResNetV2 H5 models."""

    def __init__(self, scale=1.0, axis=-1, beta_init='zeros', gamma_init='ones', use_affine=False, **kwargs):
        super().__init__(**kwargs)
        self.scale = float(scale)
        self.axis = axis
        self.use_affine = bool(use_affine)
        self.beta_init = keras.initializers.get(beta_init)
        self.gamma_init = keras.initializers.get(gamma_init)

    def build(self, input_shape):
        if not self.use_affine:
            super().build(input_shape)
            return

        axis = self.axis if self.axis >= 0 else len(input_shape) + self.axis
        channel_dim = input_shape[axis]
        if channel_dim is None:
            raise ValueError('Channel dimension must be defined for CustomScaleLayer.')

        self.gamma = self.add_weight(
            name='gamma',
            shape=(int(channel_dim),),
            initializer=self.gamma_init,
            trainable=True,
        )
        self.beta = self.add_weight(
            name='beta',
            shape=(int(channel_dim),),
            initializer=self.beta_init,
            trainable=True,
        )
        super().build(input_shape)

    def call(self, inputs):
        if isinstance(inputs, (list, tuple)):
            if len(inputs) != 2:
                raise ValueError('CustomScaleLayer expects 2 tensors in list form.')
            outputs = inputs[0] + (inputs[1] * self.scale)
        else:
            outputs = inputs * self.scale

        if not self.use_affine:
            return outputs

        ndim = len(outputs.shape)
        axis = self.axis if self.axis >= 0 else ndim + self.axis
        broadcast_shape = [1] * ndim
        broadcast_shape[axis] = outputs.shape[axis]
        gamma = ops.reshape(self.gamma, broadcast_shape)
        beta = ops.reshape(self.beta, broadcast_shape)
        return outputs * gamma + beta

    def compute_output_shape(self, input_shape):
        if isinstance(input_shape, (list, tuple)) and len(input_shape) == 2 and isinstance(input_shape[0], (list, tuple)):
            return tuple(input_shape[0])
        return tuple(input_shape)

    def get_config(self):
        config = super().get_config()
        config.update({
            'scale': self.scale,
            'axis': self.axis,
            'use_affine': self.use_affine,
            'beta_init': keras.initializers.serialize(self.beta_init),
            'gamma_init': keras.initializers.serialize(self.gamma_init),
        })
        return config


def load_model_compat(model_path):
    """Load models with fallback custom objects for legacy serialized layers."""
    try:
        return load_model(str(model_path), compile=False)
    except Exception as e:
        if 'Unknown layer' in str(e):
            custom_objects = {
                'CustomScaleLayer': CustomScaleLayer,
                'Scale': CustomScaleLayer,
            }
            return load_model(str(model_path), compile=False, custom_objects=custom_objects)
        raise

# Vitamin deficiency information
DEFICIENCY_INFO = {
    "aloperia areata": {
        "vitamin": "Vitamin D",
        "description": "Alopecia areata is an autoimmune condition causing hair loss in patches. Vitamin D deficiency is linked to autoimmune diseases.",
        "recommendations": "Consider the Mediterranean diet high in fruits, vegetables, nuts, whole grains, fish, and healthy oils. Supplement with vitamin D if deficient. Consult a dermatologist for proper diagnosis and treatment.",
        "icon": "🦱"
    },
    "beaus lines": {
        "vitamin": "Vitamin C & Magnesium",
        "description": "Beau's lines are horizontal indentations on nails indicating temporary growth arrest. Often linked to vitamin C deficiency.",
        "recommendations": "Eat dark green leafy vegetables like spinach and kale, quinoa, almonds, cashews, peanuts, edamame, and black beans. Adequate magnesium is crucial for nail health and protein synthesis.",
        "icon": "💅"
    },
    "bluish nail": {
        "vitamin": "Vitamin B12",
        "description": "Bluish discoloration of nails may indicate poor circulation or vitamin B12 deficiency.",
        "recommendations": "Include plenty of nutrients like fruits, lean meats, salmon, leafy greens, beans, eggs, nuts, and whole grains in your diet to strengthen nails.",
        "icon": "💙"
    },
    "bulging eyes": {
        "vitamin": "Vitamin A",
        "description": "Bulging eyes (proptosis) can be associated with thyroid issues or vitamin A deficiency.",
        "recommendations": "Eat foods high in potassium to balance electrolytes: bananas, yogurt, potatoes, dried apricots. Also, include vitamin A-rich foods like carrots, sweet potatoes, and leafy greens.",
        "icon": "👁️"
    },
    "cataracts eyes": {
        "vitamin": "Vitamin D & E",
        "description": "Cataracts cause clouding of the eye lens, often age-related but vitamin D deficiency may contribute.",
        "recommendations": "Eat foods high in antioxidants like vitamins C and E: citrus fruits, berries, nuts, seeds. Maintain a healthy diet with fresh vegetables and fruits to support eye health.",
        "icon": "👓"
    },
    "clubbing": {
        "vitamin": "Vitamin D",
        "description": "Clubbing of fingers/toes indicates underlying conditions like lung disease or vitamin D deficiency.",
        "recommendations": "Include meat, fish, eggs, beans, and nuts in your diet. Aim for two portions daily, with fish twice weekly (including oily fish like salmon).",
        "icon": "🖐️"
    },
    "crossed eyes": {
        "vitamin": "Vitamin B6 & C",
        "description": "Strabismus (crossed eyes) in adults may relate to neurological issues or vitamin B6 deficiency.",
        "recommendations": "Consume omega-3 fatty acids from cold-water fish like salmon, tuna, sardines, halibut. Also, eat vitamin C-rich foods: oranges, grapefruits, tomatoes, lemons for eye health.",
        "icon": "👀"
    },
    "Dariers disease": {
        "vitamin": "Vitamin A",
        "description": "Darier's disease is a rare genetic skin disorder, not directly caused by diet but vitamin A deficiency may worsen symptoms.",
        "recommendations": "There is no specific diet cure. Treatment includes aciclovir for herpes simplex, oral retinoids like acitretin or isotretinoin for severe cases, or ciclosporin. Consult a dermatologist.",
        "icon": ""
    },
    "eczema": {
        "vitamin": "Vitamin D",
        "description": "Eczema (atopic dermatitis) causes itchy, inflamed skin. Vitamin D deficiency is linked to increased risk.",
        "recommendations": "Eat anti-inflammatory foods: apples, broccoli, cherries, blueberries, spinach, kale. Flavonoids help reduce skin inflammation.",
        "icon": "🌿"
    },
    "glucoma eyes": {
        "vitamin": "Vitamin B Complex",
        "description": "Glaucoma damages the optic nerve, often due to high eye pressure. Vitamin B deficiencies may contribute.",
        "recommendations": "Drink hot tea daily (associated with lower risk). Include chocolate, bananas, avocados, pumpkin seeds, black beans for vitamin B sources.",
        "icon": "🫐"
    },
    "Lindsays nails": {
        "vitamin": "Vitamin B12",
        "description": "Lindsay's nails show half white, half red/pink nails, associated with chronic kidney disease or vitamin B12 deficiency.",
        "recommendations": "Maintain a healthy diet to prevent hangnails: include protein-rich foods, folic acid, vitamins B, C, keratin sources like kiwi, broccoli, bell peppers, tomatoes.",
        "icon": "💅"
    },
    "lip": {
        "vitamin": "Vitamin B2 (Riboflavin)",
        "description": "Angular cheilitis (cracked lip corners) often due to vitamin B2 (riboflavin) deficiency.",
        "recommendations": "Eat eggs, milk, carrots, spinach, apricots. Vitamin C-rich foods like orange juice, strawberries, green peppers, citrus fruits, tomatoes, sweet potatoes help heal lips and boost immunity.",
        "icon": "👄"
    },
    "tounge": {
        "vitamin": "Vitamin B3 (Niacin)",
        "description": "Burning tongue syndrome may be caused by vitamin B3 (niacin) deficiency or other factors.",
        "recommendations": "Eat cool, soothing foods like yogurt or applesauce. Drink water to remove food debris. Include niacin-rich foods: meat, fish, eggs, dairy, nuts, legumes.",
        "icon": "👅"
    },
    "uvieties eyes": {
        "vitamin": "Vitamin D",
        "description": "Uveitis is inflammation of the eye's middle layer. Vitamin D may help reduce inflammation.",
        "recommendations": "Get sunlight exposure and eat vitamin D-rich foods like fatty fish, fortified dairy, and egg yolks. Consult an ophthalmologist for proper diagnosis.",
        "icon": "🌞"
    }
}

# Model information
MODEL_INFO = {
    'CNN': {'description': 'Basic Convolutional Neural Network', 'color': '#667eea'},
    'EfficientNetV2L': {'description': 'Highly efficient modern architecture', 'color': '#764ba2'},
    'InceptionResNetV2': {'description': 'Hybrid Inception + ResNet model', 'color': '#f093fb'},
    'InceptionV3': {'description': 'Google\'s deep learning model', 'color': '#4facfe'},
    'MobileNet': {'description': 'Lightweight mobile-optimized model', 'color': '#43e97b'},
    'ResNet': {'description': 'Deep residual learning network', 'color': '#fa709a'},
    'VGG16': {'description': 'Classic deep architecture', 'color': '#fee140'},
    'Xception': {'description': 'Extreme Inception architecture', 'color': '#30cfd0'}
}

@st.cache_resource(show_spinner=False)
def load_all_models(num_classes):
    """Load all trained models and keep only class-compatible ones."""
    models = {}
    available_models = []
    load_status = []

    selected_mapping = {k: MODEL_MAPPING[k] for k in ACTIVE_MODEL_NAMES if k in MODEL_MAPPING}
    log_event(f"Model load started. total_selected={len(selected_mapping)} num_classes={num_classes} lightweight={LIGHTWEIGHT_MODE}")

    for model_name, model_file in selected_mapping.items():
        model_start = time.perf_counter()
        model_path = MODEL_DIR / model_file
        log_event(f"Loading model={model_name} file={model_file}")
        if not model_path.exists():
            log_event(f"Missing model file for {model_name}: {model_path}", level="warning")
            load_status.append({
                'model': model_name,
                'status': 'missing',
                'details': f'Model file not found: {model_file}'
            })
            continue

        try:
            mdl = load_model_compat(model_path)

            output_shape = mdl.output_shape
            if isinstance(output_shape, list):
                output_shape = output_shape[0]
            output_dim = output_shape[-1] if isinstance(output_shape, tuple) else None

            if output_dim is not None and num_classes > 0 and int(output_dim) != int(num_classes):
                elapsed = time.perf_counter() - model_start
                log_event(
                    f"Skipped model={model_name} due to class mismatch output_dim={output_dim} expected={num_classes} elapsed={elapsed:.2f}s",
                    level="warning",
                )
                load_status.append({
                    'model': model_name,
                    'status': 'skipped',
                    'details': f'Output classes mismatch ({output_dim} != {num_classes})'
                })
            else:
                elapsed = time.perf_counter() - model_start
                log_event(f"Loaded model={model_name} elapsed={elapsed:.2f}s")
                models[model_name] = mdl
                available_models.append(model_name)
                load_status.append({
                    'model': model_name,
                    'status': 'loaded',
                    'details': f'Loaded from {model_file}'
                })
        except Exception as e:
            elapsed = time.perf_counter() - model_start
            tb = traceback.format_exc(limit=6)
            log_event(f"Failed model={model_name} elapsed={elapsed:.2f}s error={e}", level="error")
            log_event(tb, level="error")
            load_status.append({
                'model': model_name,
                'status': 'failed',
                'details': f"{e}\n{tb}"
            })

    log_event(f"Model load completed. loaded={len(available_models)} issues={len(load_status) - len(available_models)}")

    return models, available_models, load_status

@st.cache_data
def get_class_names():
    """Get class names from dataset"""
    classes = []
    if not DATA_DIR.exists():
        return classes
    for file in sorted(os.listdir(DATA_DIR)):
        if file != "clear" and (DATA_DIR / file).is_dir():
            classes.append(file)
    return classes


@st.cache_data(show_spinner=False)
def load_ensemble_metadata():
    """Load optional ensemble metadata (best method, class names, weights)."""
    metadata_path = MODEL_DIR / 'ensemble_metadata.json'
    if not metadata_path.exists():
        return {}

    try:
        import json
        with open(metadata_path, 'r') as f:
            return json.load(f)
    except Exception:
        return {}


def normalize_probabilities(pred_vector):
    """Ensure each model output is a proper probability distribution."""
    v = np.asarray(pred_vector, dtype=np.float64).flatten()
    if v.size == 0:
        return v

    # If model output is not a valid probability distribution, convert via softmax.
    if np.any(v < 0) or not np.isfinite(v).all() or (v.sum() <= 0):
        shifted = v - np.max(v)
        exps = np.exp(shifted)
        denom = np.sum(exps)
        return exps / denom if denom > 0 else np.ones_like(v) / len(v)

    s = v.sum()
    if not np.isclose(s, 1.0, atol=1e-3):
        return v / s if s > 0 else np.ones_like(v) / len(v)
    return v

def preprocess_for_model(img, model):
    """Preprocess uploaded image based on each model expected input shape."""
    input_shape = model.input_shape
    if isinstance(input_shape, list):
        input_shape = input_shape[0]

    target_h = input_shape[1] if isinstance(input_shape, tuple) and len(input_shape) > 2 else IMG_HEIGHT
    target_w = input_shape[2] if isinstance(input_shape, tuple) and len(input_shape) > 2 else IMG_WIDTH
    channels = input_shape[3] if isinstance(input_shape, tuple) and len(input_shape) > 3 else 3

    target_h = target_h if target_h else IMG_HEIGHT
    target_w = target_w if target_w else IMG_WIDTH

    if channels == 1:
        pre_img = img.convert('L')
    else:
        pre_img = img.convert('RGB')

    pre_img = pre_img.resize((int(target_w), int(target_h)))
    img_array = np.array(pre_img, dtype=np.float32)

    if channels == 1:
        img_array = np.expand_dims(img_array, axis=-1)

    if np.max(img_array) > 1.0:
        img_array = img_array / 255.0

    img_expanded = np.expand_dims(img_array, axis=0)
    return img_expanded

def predict_ensemble(img, models, available_models, num_classes, method='soft_voting', model_weights=None):
    """Make ensemble prediction and keep running even if some models fail."""
    predictions = []
    individual_predictions = {}
    runtime_errors = {}

    log_event(f"Inference started. models={len(available_models)} method={method}")

    for model_name in available_models:
        try:
            infer_start = time.perf_counter()
            log_event(f"Infer model={model_name} started")
            img_expanded = preprocess_for_model(img, models[model_name])
            pred = models[model_name].predict(img_expanded, verbose=0)
            pred_vector = normalize_probabilities(pred[0])

            if len(pred_vector) != num_classes:
                runtime_errors[model_name] = (
                    f'Prediction size mismatch ({len(pred_vector)} != {num_classes})'
                )
                log_event(runtime_errors[model_name], level="warning")
                continue

            predictions.append(pred_vector)
            individual_predictions[model_name] = pred_vector
            infer_elapsed = time.perf_counter() - infer_start
            log_event(f"Infer model={model_name} completed elapsed={infer_elapsed:.2f}s")
        except Exception as e:
            tb = traceback.format_exc(limit=6)
            runtime_errors[model_name] = f"{e}\n{tb}"
            log_event(f"Infer model={model_name} failed error={e}", level="error")
            log_event(tb, level="error")

    if not predictions:
        log_event("Inference failed: no valid model predictions were produced.", level="error")
        raise ValueError('No model produced a valid prediction. Check model diagnostics.')

    pred_matrix = np.array(predictions, dtype=np.float64)

    if method == 'hard_voting':
        votes = [int(np.argmax(p)) for p in pred_matrix]
        class_idx = int(np.bincount(votes, minlength=num_classes).argmax())
        confidence = float(votes.count(class_idx) / len(votes))
        # For charts, still provide a probability-like average view.
        ensemble_vector = np.mean(pred_matrix, axis=0)
    elif method == 'weighted_voting' and model_weights:
        weights = []
        used_models = list(individual_predictions.keys())
        for name in used_models:
            weights.append(float(model_weights.get(name, 1.0)))
        weights = np.asarray(weights, dtype=np.float64)
        if weights.sum() <= 0:
            weights = np.ones_like(weights)
        weights = weights / weights.sum()
        ensemble_vector = np.sum(pred_matrix * weights[:, None], axis=0)
        class_idx = int(np.argmax(ensemble_vector))
        confidence = float(ensemble_vector[class_idx])
    else:
        ensemble_vector = np.mean(pred_matrix, axis=0)
        class_idx = int(np.argmax(ensemble_vector))
        confidence = float(ensemble_vector[class_idx])

    log_event(f"Inference completed. class_idx={class_idx} confidence={confidence:.4f} runtime_errors={len(runtime_errors)}")
    return class_idx, confidence, individual_predictions, ensemble_vector, runtime_errors

def create_prediction_chart(individual_predictions, classes, predicted_class):
    """Create interactive prediction chart"""
    fig = go.Figure()
    
    for model_name, pred in individual_predictions.items():
        fig.add_trace(go.Bar(
            name=model_name,
            x=[classes[i] for i in range(len(pred))],
            y=pred,
            marker_color=MODEL_INFO.get(model_name, {'color': '#667eea'})['color']
        ))
    
    fig.update_layout(
        title="Individual Model Predictions",
        xaxis_title="Condition",
        yaxis_title="Confidence",
        barmode='group',
        height=500,
        template="plotly_white",
        hovermode='x unified'
    )
    
    fig.update_xaxes(tickangle=-45)
    
    return fig

def create_ensemble_gauge(confidence):
    """Create confidence gauge chart"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=confidence * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Ensemble Confidence", 'font': {'size': 24}},
        delta={'reference': 75},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#667eea"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#fee140'},
                {'range': [50, 75], 'color': '#43e97b'},
                {'range': [75, 100], 'color': '#667eea'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    return fig

def create_top_predictions_chart(ensemble_pred, classes):
    """Create top predictions bar chart"""
    top_5_idx = np.argsort(ensemble_pred)[-5:][::-1]
    top_5_classes = [classes[i] for i in top_5_idx]
    top_5_probs = [ensemble_pred[i] * 100 for i in top_5_idx]
    
    fig = go.Figure(go.Bar(
        x=top_5_probs,
        y=top_5_classes,
        orientation='h',
        marker=dict(
            color=top_5_probs,
            colorscale='Viridis',
            showscale=True
        ),
        text=[f'{p:.2f}%' for p in top_5_probs],
        textposition='auto',
    ))
    
    fig.update_layout(
        title="Top 5 Predictions",
        xaxis_title="Confidence (%)",
        yaxis_title="Condition",
        height=400,
        template="plotly_white"
    )
    
    return fig


def show_center_loader(message):
    """Render a centered animated loader and return placeholder for cleanup."""
    placeholder = st.empty()
    placeholder.markdown(
        f"""
        <div class="center-loader-wrap">
            <div class="center-loader-card">
                <div class="center-loader"></div>
                <div class="center-loader-text">{message}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return placeholder

# ==================== MAIN APP ====================

def main():
    if 'uploader_nonce' not in st.session_state:
        st.session_state.uploader_nonce = 0

    if IS_DARK_THEME:
        st.markdown(
            """
            <style>
                .video-bg-overlay {
                    background: rgba(2, 6, 23, 0.30);
                }

                .top-title,
                .section-title,
                .center-loader-text {
                    color: #f8fafc;
                    text-shadow: none;
                }

                .top-subtitle,
                .result-note,
                .soft-info {
                    color: #e2e8f0;
                }

                .center-wrap,
                .prediction-card,
                .soft-info {
                    border-color: rgba(255,255,255,0.25);
                    box-shadow: 0 14px 32px rgba(2, 6, 23, 0.35);
                }

                .center-loader {
                    border-color: rgba(248, 250, 252, 0.24);
                    border-top-color: #ffffff;
                }

                .center-loader-wrap {
                    background: rgba(2, 6, 23, 0.38);
                }

                .center-loader-card {
                    background: rgba(2, 6, 23, 0.66);
                    border-color: rgba(255,255,255,0.30);
                    box-shadow: 0 18px 36px rgba(2, 6, 23, 0.55);
                }

                .stButton > button {
                    background: rgba(248, 250, 252, 0.88);
                    color: #0f172a;
                    border-color: rgba(248, 250, 252, 0.92);
                }

                .stButton > button:hover {
                    background: #ffffff;
                    color: #0f172a;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

    video_url = (
        "https://res.cloudinary.com/doiceztkc/video/upload/v1772946158/3d_abstract_waves_black_background_1_ov3p5e.mp4"
        if IS_DARK_THEME else
        "https://res.cloudinary.com/doiceztkc/video/upload/v1769665529/2_hff2at.mp4"
    )

    st.markdown(
        f"""
        <div class="video-bg-wrap">
            <video autoplay muted loop playsinline webkit-playsinline preload="auto">
                <source src="{video_url}" type="video/mp4">
            </video>
        </div>
        <div class="video-bg-overlay"></div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div class="main-shell">
        <p class="top-title">Vitamin Deficiency Analysis</p>
        <p class="top-subtitle">Clinical-style ensemble inference powered by eight deep learning models.</p>
    </div>
    """, unsafe_allow_html=True)

    dataset_classes = get_class_names()
    metadata = load_ensemble_metadata()
    classes = metadata.get('class_names', dataset_classes)

    # Do not load models on page open; load on demand to prevent Render gateway timeouts.
    models = {}
    available_models = []
    load_status = st.session_state.get('load_status', [])

    active_method = metadata.get('best_method', ENSEMBLE_METHOD)
    active_weights = metadata.get('model_weights', {})

    status_df = pd.DataFrame(load_status) if load_status else pd.DataFrame(columns=['model', 'status', 'details'])
    loaded_count = int((status_df['status'] == 'loaded').sum()) if not status_df.empty else 0
    issue_count = int((status_df['status'] != 'loaded').sum()) if not status_df.empty else 0

    nav_analysis, nav_performance, nav_about = st.tabs(["Analysis", "Model Performance", "About"])

    with nav_analysis:
        st.markdown('<div class="center-wrap">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Upload and Infer</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="result-note">Upload an image and run inference. The result panel will show image and diagnosis side-by-side for faster review.</p>',
            unsafe_allow_html=True,
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Loaded Models", f"{loaded_count}")
        c2.metric("Detected Classes", f"{len(classes)}")
        c3.metric("Model Issues", f"{issue_count}")
        st.caption("Models load when you click Run Analysis to keep startup fast on Render.")

        uploaded_file = st.file_uploader(
            "Select image",
            type=['png', 'jpg', 'jpeg'],
            help="Use a clear, well-lit, and focused image.",
            key=f"image_uploader_{st.session_state.uploader_nonce}"
        )

        inference_result = None
        image_for_result = None

        if uploaded_file is not None:
            img = Image.open(uploaded_file)
            image_for_result = img.copy()

            run_col, reset_col = st.columns([1, 1])
            with run_col:
                run_analysis = st.button("Run Analysis", type="primary")
            with reset_col:
                reset_upload = st.button("Upload Another Image")

            if reset_upload:
                st.session_state.uploader_nonce += 1
                st.rerun()

            if run_analysis:
                if not classes:
                    st.error("No class folders found. Verify the dataset/train directory.")
                    st.markdown('</div>', unsafe_allow_html=True)
                    return

                try:
                    startup_ui = show_center_loader("Initializing model runtime")
                    try:
                        models, available_models, load_status = load_all_models(len(classes))
                        st.session_state['load_status'] = load_status
                    finally:
                        startup_ui.empty()

                    if not available_models:
                        st.error("No models are available for inference. Check diagnostics and logs.")
                        if load_status:
                            st.dataframe(pd.DataFrame(load_status), width='stretch', hide_index=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        return

                    infer_ui = show_center_loader("Analyzing image")
                    try:
                        class_idx, confidence, individual_preds, ensemble_pred, runtime_errors = predict_ensemble(
                            img,
                            models,
                            available_models,
                            len(classes),
                            method=active_method,
                            model_weights=active_weights,
                        )
                    finally:
                        infer_ui.empty()
                    predicted_class = classes[class_idx]
                    deficiency_data = DEFICIENCY_INFO.get(
                        predicted_class,
                        {
                            "vitamin": "Unknown",
                            "description": "Condition detected.",
                            "recommendations": "Consult a healthcare professional.",
                            "icon": ""
                        }
                    )
                    inference_result = {
                        'predicted_class': predicted_class,
                        'confidence': confidence,
                        'individual_preds': individual_preds,
                        'ensemble_pred': ensemble_pred,
                        'runtime_errors': runtime_errors,
                        'deficiency_data': deficiency_data,
                    }
                except Exception as e:
                    log_event(f"Run Analysis failed: {e}", level="error")
                    log_event(traceback.format_exc(limit=8), level="error")
                    st.error("Inference failed. Review model diagnostics and try another image.")
                    st.exception(e)
                    st.markdown('</div>', unsafe_allow_html=True)
                    return

        if inference_result is not None and image_for_result is not None:
            st.markdown("---")
            left_col, right_col = st.columns([1.05, 1], gap='large')

            with left_col:
                st.markdown('<p class="section-title">Image</p>', unsafe_allow_html=True)
                st.image(image_for_result, width='stretch')

            with right_col:
                predicted_class = inference_result['predicted_class']
                confidence = inference_result['confidence']
                individual_preds = inference_result['individual_preds']
                ensemble_pred = inference_result['ensemble_pred']
                runtime_errors = inference_result['runtime_errors']
                deficiency_data = inference_result['deficiency_data']

                st.markdown('<p class="section-title">Prediction</p>', unsafe_allow_html=True)
                st.markdown('<div class="prediction-card">', unsafe_allow_html=True)
                st.markdown(f"**Condition:** {predicted_class.title()}")
                st.markdown(f"**Potential Deficiency:** {deficiency_data['vitamin']}")
                st.markdown(f"**Clinical Notes:** {deficiency_data['description']}")
                st.markdown(f"**Recommendations:** {deficiency_data['recommendations']}")
                st.markdown('</div>', unsafe_allow_html=True)

                metric_a, metric_b = st.columns(2)
                metric_a.metric("Confidence", f"{confidence*100:.1f}%")
                metric_b.metric("Method", active_method.replace('_', ' ').title())

                votes = [int(np.argmax(pred)) for pred in individual_preds.values()]
                top_vote_count = int(np.bincount(votes, minlength=len(classes)).max()) if votes else 0
                vote_ratio = (top_vote_count / len(votes)) if votes else 0.0

                if vote_ratio < 0.50:
                    st.warning("Low model consensus. Try a clearer image and compare top predictions.")
                elif vote_ratio < 0.70:
                    st.info("Moderate model consensus. Review the top predictions before interpretation.")

            st.markdown("---")
            st.plotly_chart(create_top_predictions_chart(inference_result['ensemble_pred'], classes), width='stretch')

            with st.expander("Advanced model breakdown", expanded=False):
                for model_name, pred in individual_preds.items():
                    model_class_idx = np.argmax(pred)
                    model_confidence = pred[model_class_idx]
                    model_class = classes[model_class_idx]

                    col_a, col_b, col_c = st.columns([2, 2, 1])
                    with col_a:
                        st.markdown(f"**{model_name}**")
                        st.caption(MODEL_INFO.get(model_name, {'description': 'Deep learning model'})['description'])
                    with col_b:
                        st.markdown(f"Predicted: **{model_class}**")
                    with col_c:
                        progress_value = float(np.clip(model_confidence, 0.0, 1.0))
                        st.progress(progress_value)
                        st.caption(f"{model_confidence*100:.1f}%")

                st.plotly_chart(create_prediction_chart(individual_preds, classes, predicted_class), width='stretch')

            if runtime_errors:
                st.warning("Some models were skipped during prediction.")
                runtime_df = pd.DataFrame([
                    {'model': m, 'error': err} for m, err in runtime_errors.items()
                ])
                st.dataframe(runtime_df, width='stretch', hide_index=True)

            report_data = f"""
VITAMIN DEFICIENCY DETECTION REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PREDICTION SUMMARY
==================
Detected Condition: {predicted_class.title()}
Confidence Score: {confidence*100:.2f}%
Deficiency Type: {deficiency_data['vitamin']}
Models Used: {len(available_models)}

DESCRIPTION
===========
{deficiency_data['description']}

RECOMMENDATIONS
===============
{inference_result['deficiency_data']['recommendations']}
"""
            for model_name, pred in inference_result['individual_preds'].items():
                model_class_idx = np.argmax(pred)
                report_data += f"\n{model_name}: {classes[model_class_idx]} ({pred[model_class_idx]*100:.2f}%)"

            st.download_button(
                label="Download Report",
                data=report_data,
                file_name=f"deficiency_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

        st.markdown('</div>', unsafe_allow_html=True)

    with nav_performance:
        st.markdown("### Performance and Diagnostics")
        st.markdown('<div class="soft-info">This section presents model metrics and load diagnostics from the current runtime.</div>', unsafe_allow_html=True)

        if not status_df.empty:
            st.dataframe(status_df, width='stretch', hide_index=True)
        else:
            st.info("No model load logs yet. Click Run Analysis once to initialize models and populate diagnostics.")

        metadata_path = MODEL_DIR / 'ensemble_metadata.json'
        if metadata_path.exists():
            import json
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

            r1, r2, r3 = st.columns(3)
            r1.metric("Best Ensemble Accuracy", f"{metadata.get('best_ensemble_accuracy', 0)*100:.2f}%")
            r2.metric("Best Individual Accuracy", f"{metadata.get('best_individual_accuracy', 0)*100:.2f}%")
            r3.metric("Best Method", metadata.get('best_method', 'soft_voting').replace('_', ' ').title())

            if 'model_accuracies' in metadata:
                model_acc_df = pd.DataFrame({
                    'Model': list(metadata['model_accuracies'].keys()),
                    'Accuracy (%)': [v * 100 for v in metadata['model_accuracies'].values()]
                }).sort_values('Accuracy (%)', ascending=False)

                fig = px.bar(
                    model_acc_df,
                    x='Model',
                    y='Accuracy (%)',
                    color='Accuracy (%)',
                    color_continuous_scale='Blues',
                    title='Model Accuracy Comparison'
                )
                fig.update_layout(height=460, template='plotly_white')
                st.plotly_chart(fig, width='stretch')
                st.dataframe(model_acc_df, width='stretch', hide_index=True)
        else:
            st.info("No performance metadata file found. Run ensemble evaluation to populate this section.")

    with nav_about:
        st.markdown("### About")
        st.markdown("""
This application performs vitamin deficiency inference from images using an ensemble of deep learning models.

- Inference engine: TensorFlow/Keras
- App framework: Streamlit
- Model family: CNN, EfficientNetV2L, InceptionResNetV2, InceptionV3, MobileNet, ResNet, VGG16, Xception

Medical disclaimer: This tool is for informational purposes only and is not a substitute for professional diagnosis.
        """)

    st.markdown("---")
    st.caption("Vitamin Deficiency AI | Ensemble Inference Interface")

if __name__ == "__main__":
    try:
        log_event("Streamlit script execution started.")
        log_event(
            f"Environment snapshot: RENDER={os.getenv('RENDER', '')} "
            f"RENDER_SERVICE_ID={'set' if os.getenv('RENDER_SERVICE_ID') else 'unset'} "
            f"LIGHTWEIGHT_MODE_ENV={os.getenv('LIGHTWEIGHT_MODE', '<not-set>')} "
            f"LIGHTWEIGHT_MODE_RESOLVED={LIGHTWEIGHT_MODE}"
        )
        main()
    except Exception as exc:
        log_event(f"Fatal app error: {exc}", level="error")
        log_event(traceback.format_exc(limit=12), level="error")
        raise
