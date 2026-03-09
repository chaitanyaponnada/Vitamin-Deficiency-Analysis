import os
# Load environment variables from .env file (for local development)
try:
    from dotenv import load_dotenv  # type: ignore[import-not-found]
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, ok for production

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
import gc
import signal
import threading
from contextlib import contextmanager

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

# Import authentication modules
from firebase_auth import get_user_profile, store_analysis, get_analysis_history
from auth_ui_modern import show_authentication_gateway
from ui_components import (
    inject_global_styles, render_header, render_profile_dropdown,
    render_loading_animation, render_page_header, render_stat_card,
    get_current_date_display, show_error_modal
)


class TimeoutException(Exception):
    pass


@contextmanager
def time_limit(seconds):
    """Context manager to limit execution time when signal alarms are supported."""
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out")

    # signal.signal/signal.alarm only work in the main interpreter thread.
    supports_alarm = (
        hasattr(signal, 'SIGALRM')
        and threading.current_thread() is threading.main_thread()
    )

    if supports_alarm:
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
    else:
        # Streamlit often runs user code in a worker thread; avoid signal usage there.
        yield


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


def get_runtime_setting(name, default=""):
    """Read config from env first, then Streamlit secrets as fallback."""
    env_val = os.getenv(name)
    if env_val not in (None, ""):
        return str(env_val)

    try:
        secret_val = st.secrets.get(name, "")
        if secret_val not in (None, ""):
            return str(secret_val)
    except Exception:
        pass

    return str(default)


@keras.utils.register_keras_serializable(package='Custom', name='Dense')
class CompatDense(keras.layers.Dense):
    """Backwards-compatible Dense that tolerates legacy serialization fields."""

    @classmethod
    def from_config(cls, config):
        cfg = dict(config or {})
        # Keras 3 may reject legacy/no-op quantization metadata found in old H5 files.
        cfg.pop('quantization_config', None)
        return super().from_config(cfg)


@keras.utils.register_keras_serializable(package='Custom', name='Conv2D')
class CompatConv2D(keras.layers.Conv2D):
    @classmethod
    def from_config(cls, config):
        cfg = dict(config or {})
        cfg.pop('quantization_config', None)
        return super().from_config(cfg)


@keras.utils.register_keras_serializable(package='Custom', name='DepthwiseConv2D')
class CompatDepthwiseConv2D(keras.layers.DepthwiseConv2D):
    @classmethod
    def from_config(cls, config):
        cfg = dict(config or {})
        cfg.pop('quantization_config', None)
        return super().from_config(cfg)


@keras.utils.register_keras_serializable(package='Custom', name='SeparableConv2D')
class CompatSeparableConv2D(keras.layers.SeparableConv2D):
    @classmethod
    def from_config(cls, config):
        cfg = dict(config or {})
        cfg.pop('quantization_config', None)
        return super().from_config(cfg)


@keras.utils.register_keras_serializable(package='Custom', name='BatchNormalization')
class CompatBatchNormalization(keras.layers.BatchNormalization):
    @classmethod
    def from_config(cls, config):
        cfg = dict(config or {})
        cfg.pop('quantization_config', None)
        return super().from_config(cfg)


# Page configuration
st.set_page_config(
    page_title="Vitamin Deficiency AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

THEME_BASE = (st.get_option("theme.base") or "light").lower()
IS_DARK_THEME = THEME_BASE == "dark"
# Legacy style block removed. Global styles are defined in ui_components.inject_global_styles().

# Configuration
BASE_DIR = Path(__file__).resolve().parent


def resolve_model_dir():
    """Resolve model folder across local, Render native, and Docker runtimes."""
    env_model_dir = get_runtime_setting('MODEL_DIR', '').strip()
    candidates = []

    if env_model_dir:
        candidates.append(Path(env_model_dir))

    # Project-local path should be first because it is valid for local runs and many deploys.
    candidates.extend([
        BASE_DIR / 'model_saved_files',
        Path('/opt/render/project/src/model_saved_files'),
        Path('/app/model_saved_files'),
    ])

    for candidate in candidates:
        try:
            if candidate.exists() and candidate.is_dir():
                return candidate
        except Exception:
            # Continue scanning fallback paths if any candidate cannot be inspected.
            continue

    # Fall back to project-local expected location for better error messaging.
    return BASE_DIR / 'model_saved_files'


MODEL_DIR = resolve_model_dir()
DATA_DIR = BASE_DIR / 'dataset' / 'train'
IMG_HEIGHT, IMG_WIDTH = 128, 128
ENSEMBLE_METHOD = 'soft_voting'


def resolve_model_file(model_file):
    """Resolve model file from the model_saved_files folder only."""
    primary = MODEL_DIR / model_file
    if primary.exists() and primary.is_file():
        return primary

    # Handle case differences safely while still restricting search to model_saved_files.
    model_file_lower = model_file.lower()
    if MODEL_DIR.exists() and MODEL_DIR.is_dir():
        for candidate in MODEL_DIR.iterdir():
            if candidate.is_file() and candidate.name.lower() == model_file_lower:
                return candidate

    return primary


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
IS_STREAMLIT_CLOUD = any([
    os.getenv('STREAMLIT_SHARING_MODE', '').lower() == 'streamlit',
    bool(os.getenv('STREAMLIT_RUNTIME')),
    bool(os.getenv('STREAMLIT_SERVER_PORT')),
])
LIGHTWEIGHT_MODE = get_runtime_setting(
    'LIGHTWEIGHT_MODE',
    '1' if (IS_RENDER or IS_STREAMLIT_CLOUD) else '0'
) == '1'
ACTIVE_MODEL_NAMES = [
    name for name in MODEL_MAPPING.keys()
    if (not LIGHTWEIGHT_MODE) or (name not in HEAVY_MODELS)
]

try:
    _default_max_model_mb = '40' if (IS_RENDER or IS_STREAMLIT_CLOUD) else '0'
    MAX_MODEL_FILE_MB = float(get_runtime_setting('MAX_MODEL_FILE_MB', _default_max_model_mb))
except Exception:
    MAX_MODEL_FILE_MB = 0.0

# Minimum models needed for inference (1 = allow any single model)
MIN_MODELS_FOR_INFERENCE = 1

# Global cache for models (manual caching to avoid Streamlit cache replay issues)
_MODELS_CACHE = None
_MODELS_CACHE_KEY = None


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


COMPAT_CUSTOM_OBJECTS = {
    'CustomScaleLayer': CustomScaleLayer,
    'Scale': CustomScaleLayer,
    'Dense': CompatDense,
    'Conv2D': CompatConv2D,
    'DepthwiseConv2D': CompatDepthwiseConv2D,
    'SeparableConv2D': CompatSeparableConv2D,
    'BatchNormalization': CompatBatchNormalization,
}


def load_model_compat(model_path):
    """Load models with fallback custom objects for legacy serialized layers."""
    try:
        return load_model(str(model_path), compile=False)
    except Exception as e:
        err_text = str(e)
        if 'Unknown layer' in err_text:
            return load_model(str(model_path), compile=False, custom_objects=COMPAT_CUSTOM_OBJECTS)
        if 'quantization_config' in err_text or "deserializing class 'Dense'" in err_text:
            return load_model(str(model_path), compile=False, custom_objects=COMPAT_CUSTOM_OBJECTS)
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
        "icon": ""
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
        "icon": ""
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

def load_all_models(num_classes, _progress_callback=None):
    """Load all trained models and keep only class-compatible ones.
    
    Uses manual caching to avoid Streamlit cache replay errors with UI callbacks.
    """
    global _MODELS_CACHE, _MODELS_CACHE_KEY
    
    # Create cache key based on num_classes and active models
    cache_key = (num_classes, tuple(sorted(ACTIVE_MODEL_NAMES)))
    
    # Return cached models if available (only when called without progress callback)
    if _progress_callback is None and _MODELS_CACHE is not None and _MODELS_CACHE_KEY == cache_key:
        log_event("Returning cached models")
        return _MODELS_CACHE
    
    models = {}
    available_models = []
    load_status = []

    selected_mapping = {k: MODEL_MAPPING[k] for k in ACTIVE_MODEL_NAMES if k in MODEL_MAPPING}
    model_dir_exists = MODEL_DIR.exists()
    model_dir_listing = []
    if model_dir_exists:
        try:
            model_dir_listing = sorted([p.name for p in MODEL_DIR.iterdir()])
        except Exception:
            model_dir_listing = []

    log_event(
        f"Model load started. total_selected={len(selected_mapping)} num_classes={num_classes} "
        f"lightweight={LIGHTWEIGHT_MODE} model_dir={MODEL_DIR} exists={model_dir_exists}"
    )
    if _progress_callback:
        _progress_callback({
            'phase': 'init',
            'index': 0,
            'total': len(selected_mapping),
            'message': 'Model loading started.'
        })

    if model_dir_listing:
        log_event(f"Model dir listing: {', '.join(model_dir_listing)}")
    else:
        log_event("Model dir listing: <empty or unreadable>", level="warning")

    # Sort models by file size (smallest first) to maximize successful loads on low-memory hosts
    def get_model_size(item):
        model_name, model_file = item
        try:
            model_path = resolve_model_file(model_file)
            return model_path.stat().st_size if model_path.exists() else float('inf')
        except Exception:
            return float('inf')
    
    sorted_mapping = sorted(selected_mapping.items(), key=get_model_size)
    total_models = len(sorted_mapping)
    for idx, (model_name, model_file) in enumerate(sorted_mapping, start=1):
        model_start = time.perf_counter()
        model_path = resolve_model_file(model_file)
        log_event(f"Loading model={model_name} file={model_file} resolved_path={model_path}")
        if _progress_callback:
            _progress_callback({
                'phase': 'start',
                'index': idx,
                'total': total_models,
                'model': model_name,
                'file': model_file,
                'path': str(model_path),
                'message': f'Starting {model_name}'
            })

        if not model_path.exists():
            log_event(f"Missing model file for {model_name}: {model_path}", level="warning")
            status_row = {
                'model': model_name,
                'status': 'missing',
                'details': f'Model file not found: {model_file} (resolved: {model_path}). Required folder: {MODEL_DIR}'
            }
            load_status.append(status_row)
            if _progress_callback:
                _progress_callback({
                    'phase': 'missing',
                    'index': idx,
                    'total': total_models,
                    'model': model_name,
                    'details': status_row['details']
                })
            continue

        if MAX_MODEL_FILE_MB > 0:
            try:
                model_size_mb = model_path.stat().st_size / (1024 * 1024)
            except Exception:
                model_size_mb = 0.0
            if model_size_mb > MAX_MODEL_FILE_MB:
                details = (
                    f"Skipped due to size limit ({model_size_mb:.1f}MB > {MAX_MODEL_FILE_MB:.1f}MB). "
                    "Increase MAX_MODEL_FILE_MB to include this model."
                )
                log_event(f"Skipped model={model_name} {details}", level="warning")
                status_row = {
                    'model': model_name,
                    'status': 'skipped',
                    'details': details,
                }
                load_status.append(status_row)
                if _progress_callback:
                    _progress_callback({
                        'phase': 'skipped',
                        'index': idx,
                        'total': total_models,
                        'model': model_name,
                        'details': details,
                    })
                continue

        try:
            # Add timeout for model loading (120 seconds max per model)
            # This prevents hanging on memory-constrained environments
            load_timeout = 120
            try:
                with time_limit(load_timeout):
                    mdl = load_model_compat(model_path)
            except TimeoutException:
                elapsed = time.perf_counter() - model_start
                error_msg = f"Model loading timeout after {load_timeout}s"
                log_event(f"Timeout for {model_name}: {error_msg}", level="error")
                status_row = {
                    'model': model_name,
                    'status': 'failed',
                    'details': error_msg
                }
                load_status.append(status_row)
                if _progress_callback:
                    _progress_callback({
                        'phase': 'failed',
                        'index': idx,
                        'total': total_models,
                        'model': model_name,
                        'details': error_msg
                    })
                continue
            except Exception as load_error:
                elapsed = time.perf_counter() - model_start
                tb = traceback.format_exc(limit=6)
                log_event(f"Failed model={model_name} elapsed={elapsed:.2f}s error={load_error}", level="error")
                log_event(tb, level="error")
                status_row = {
                    'model': model_name,
                    'status': 'failed',
                    'details': f"{load_error}\n{tb}"
                }
                load_status.append(status_row)
                if _progress_callback:
                    _progress_callback({
                        'phase': 'failed',
                        'index': idx,
                        'total': total_models,
                        'model': model_name,
                        'details': str(load_error)
                    })
                continue
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
                status_row = {
                    'model': model_name,
                    'status': 'skipped',
                    'details': f'Output classes mismatch ({output_dim} != {num_classes})'
                }
                load_status.append(status_row)
                if _progress_callback:
                    _progress_callback({
                        'phase': 'skipped',
                        'index': idx,
                        'total': total_models,
                        'model': model_name,
                        'details': status_row['details']
                    })
            else:
                elapsed = time.perf_counter() - model_start
                log_event(f"Loaded model={model_name} elapsed={elapsed:.2f}s")
                models[model_name] = mdl
                available_models.append(model_name)
                status_row = {
                    'model': model_name,
                    'status': 'loaded',
                    'details': f'Loaded from {model_file}'
                }
                load_status.append(status_row)
                if _progress_callback:
                    _progress_callback({
                        'phase': 'loaded',
                        'index': idx,
                        'total': total_models,
                        'model': model_name,
                        'details': status_row['details']
                    })
                
                # Force garbage collection after each successful model load
                gc.collect()
                # On memory-constrained environments, clear TF session state
                if IS_RENDER or IS_STREAMLIT_CLOUD:
                    try:
                        import keras.backend as K
                        K.clear_session()
                    except Exception:
                        pass
                    gc.collect()
        except Exception as e:
            elapsed = time.perf_counter() - model_start
            tb = traceback.format_exc(limit=6)
            log_event(f"Failed model={model_name} elapsed={elapsed:.2f}s error={e}", level="error")
            log_event(tb, level="error")
            status_row = {
                'model': model_name,
                'status': 'failed',
                'details': f"{e}\n{tb}"
            }
            load_status.append(status_row)
            if _progress_callback:
                _progress_callback({
                    'phase': 'failed',
                    'index': idx,
                    'total': total_models,
                    'model': model_name,
                    'details': str(e)
                })

    log_event(f"Model load completed. loaded={len(available_models)} issues={len(load_status) - len(available_models)}")
    if _progress_callback:
        _progress_callback({
            'phase': 'complete',
            'index': total_models,
            'total': total_models,
            'loaded': len(available_models),
            'issues': len(load_status) - len(available_models),
            'message': f'Model loading completed. {len(available_models)} model(s) ready.'
        })
    
    # Final garbage collection
    gc.collect()
    if IS_RENDER or IS_STREAMLIT_CLOUD:
        try:
            import keras.backend as K
            K.clear_session()
        except Exception:
            pass

    result = (models, available_models, load_status)
    
    # Cache the result (only when called without progress callback)
    if _progress_callback is None:
        _MODELS_CACHE = result
        _MODELS_CACHE_KEY = cache_key
        log_event("Models cached successfully")
    
    return result

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


def load_models_with_live_ui(num_classes):
    """Load models once with simple centered loading message during startup."""
    loader_overlay = show_center_loader("Initializing AI models… Please wait.")

    try:
        # Load all models in background without progress callbacks
        models, available_models, load_status = load_all_models(
            num_classes,
            _progress_callback=None,
        )
    finally:
        loader_overlay.empty()

    return models, available_models, load_status

# ==================== MAIN APP ====================

def main():
    inject_global_styles()

    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False
    if "uploader_nonce" not in st.session_state:
        st.session_state.uploader_nonce = 0
    if "active_nav" not in st.session_state:
        st.session_state.active_nav = "Dashboard"

    if not st.session_state.is_authenticated:
        show_authentication_gateway()
        return

    dataset_classes = get_class_names()
    metadata = load_ensemble_metadata()
    classes = metadata.get("class_names", dataset_classes)
    active_method = metadata.get("best_method", ENSEMBLE_METHOD)
    active_weights = metadata.get("model_weights", {})

    models = None
    available_models = []
    load_status = st.session_state.get("load_status", [])
    status_df = pd.DataFrame(load_status) if load_status else pd.DataFrame(columns=["model", "status", "details"])
    loaded_count = int((status_df["status"] == "loaded").sum()) if not status_df.empty else 0
    issue_count = int((status_df["status"] != "loaded").sum()) if not status_df.empty else 0

    if st.session_state.get("models_loaded", False):
        models, available_models, load_status = load_all_models(len(classes))
        st.session_state["load_status"] = load_status
        status_df = pd.DataFrame(load_status) if load_status else pd.DataFrame(columns=["model", "status", "details"])
        loaded_count = int((status_df["status"] == "loaded").sum()) if not status_df.empty else 0
        issue_count = int((status_df["status"] != "loaded").sum()) if not status_df.empty else 0

    user_data = st.session_state.get("user_data", {})
    render_header(user_data)
    render_profile_dropdown(user_data)

    if st.session_state.get("active_tab") == "profile":
        render_page_header("Profile", "Manage your account settings")
        user_profile = get_user_profile(user_data.get("user_id", ""))
        if user_profile:
            col1, col2 = st.columns([1, 3])
            with col1:
                initial = user_profile.get("username", "U")[0].upper()
                st.markdown(
                    f"""
                    <div style="
                        width:96px;height:96px;border-radius:999px;background:#18181F;
                        border:1px solid #242430;color:#FFFFFF;display:flex;align-items:center;
                        justify-content:center;font-size:2.2rem;font-weight:700;">{initial}</div>
                    """,
                    unsafe_allow_html=True,
                )
            with col2:
                st.write(f"**Full Name:** {user_profile.get('full_name', 'N/A')}")
                st.write(f"**Username:** @{user_profile.get('username', 'N/A')}")
                st.write(f"**Email:** {user_profile.get('email', 'N/A')}")
                st.write(f"**Member Since:** {user_profile.get('created_at', 'N/A')[:10]}")
                st.write(f"**Total Analyses:** {len(get_analysis_history(user_data.get('user_id', '')))}")
        if st.button("Back to Dashboard", key="profile_back"):
            st.session_state.active_tab = None
            st.session_state.active_nav = "Dashboard"
            st.rerun()
        return

    if st.session_state.get("switch_to_analysis", False):
        st.session_state.active_nav = "Analysis"
        st.session_state.switch_to_analysis = False

    nav_options = ["Dashboard", "Analysis", "History", "Model Performance", "Model Status", "About"]
    if st.session_state.active_nav not in nav_options:
        st.session_state.active_nav = "Dashboard"

    st.markdown('<div class="nav-wrap">', unsafe_allow_html=True)
    st.radio("Navigation", nav_options, horizontal=True, key="active_nav", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    current_nav = st.session_state.active_nav

    if current_nav == "Dashboard":
        user_id = user_data.get("user_id", "")
        user_profile = get_user_profile(user_id)
        analysis_history = get_analysis_history(user_id)
        if user_profile:
            current_date, current_day = get_current_date_display()
            render_page_header(f"Welcome back, {user_profile.get('full_name', 'User')}", f"{current_day}, {current_date}")

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(render_stat_card(len(analysis_history), "Total Analyses"), unsafe_allow_html=True)
            with c2:
                last_analysis_date = analysis_history[0]["timestamp"][:10] if analysis_history else "Never"
                st.markdown(render_stat_card(last_analysis_date, "Last Analysis"), unsafe_allow_html=True)
            with c3:
                if analysis_history:
                    conditions = [a["predicted_condition"] for a in analysis_history]
                    most_common = max(set(conditions), key=conditions.count)
                    display_condition = most_common[:15] + "..." if len(most_common) > 15 else most_common
                else:
                    display_condition = "None"
                st.markdown(render_stat_card(display_condition, "Most Detected"), unsafe_allow_html=True)
            with c4:
                health_score = min(100, max(0, 100 - (len(analysis_history) * 5)))
                st.markdown(render_stat_card(f"{health_score}%", "Health Score"), unsafe_allow_html=True)

            mid_left, mid_center, mid_right = st.columns([2, 2, 2])
            with mid_center:
                if st.button("Start Analysis", type="primary", use_container_width=True):
                    st.session_state.active_nav = "Analysis"
                    st.rerun()

    elif current_nav == "History":
        render_page_header("Analysis History", "Review your past medical image analyses")
        user_id = user_data.get("user_id", "")
        analysis_history = get_analysis_history(user_id)
        if analysis_history:
            history_df = pd.DataFrame(
                [
                    {
                        "Date": h["timestamp"][:10],
                        "Time": h["timestamp"][11:19],
                        "Condition": h["predicted_condition"],
                        "Confidence": f"{h['confidence_score'] * 100:.1f}%",
                        "Image": h["image_name"][:30],
                    }
                    for h in analysis_history
                ]
            )
            st.dataframe(history_df, use_container_width=True, hide_index=True)
            if st.button("Clear All History", key="clear_history"):
                show_error_modal("Action Unavailable", "History clearing feature is not enabled yet.", key_prefix="history_clear")
        else:
            st.info("No analysis history yet. Visit Analysis to get started.")

    elif current_nav == "Analysis":
        render_page_header("AI Analysis", "Upload an image and run analysis when ready")

        m1, m2, m3 = st.columns(3)
        m1.metric("Loaded Models", str(loaded_count))
        m2.metric("Detectable Conditions", str(len(classes)))
        m3.metric("Model Issues", str(issue_count))
        st.caption("Models load only when you click Run Analysis.")

        uploaded_file = st.file_uploader(
            "Upload image",
            type=["png", "jpg", "jpeg"],
            key=f"image_uploader_{st.session_state.uploader_nonce}",
        )

        inference_result = None
        image_for_result = None

        if uploaded_file is not None:
            try:
                img = Image.open(uploaded_file)
                image_for_result = img.copy()
            except Exception as exc:
                show_error_modal("Upload Error", f"Unable to read image: {exc}", key_prefix="upload_err")
                return

            run_col, reset_col = st.columns([1, 1])
            with run_col:
                run_analysis = st.button("Run Analysis", type="primary", use_container_width=True)
            with reset_col:
                reset_upload = st.button("Upload Another Image", use_container_width=True)

            if reset_upload:
                st.session_state.uploader_nonce += 1
                st.rerun()

            if run_analysis:
                if not classes:
                    show_error_modal("Analysis Error", "No class folders found. Verify dataset/train.", key_prefix="class_missing")
                    return

                if not st.session_state.get("models_loaded", False):
                    render_loading_animation("Loading AI Models", "This runs once per session.")
                    try:
                        models, available_models, load_status = load_models_with_live_ui(len(classes))
                        st.session_state["models_loaded"] = True
                        st.session_state["load_status"] = load_status
                        status_df = pd.DataFrame(load_status) if load_status else pd.DataFrame(columns=["model", "status", "details"])
                        loaded_count = int((status_df["status"] == "loaded").sum()) if not status_df.empty else 0
                        issue_count = int((status_df["status"] != "loaded").sum()) if not status_df.empty else 0
                    except Exception as exc:
                        log_event(f"Model loading error: {exc}", level="error")
                        show_error_modal("Model Loading Error", str(exc), key_prefix="model_load_fail")
                        return

                if models is None or not available_models:
                    models, available_models, load_status = load_all_models(len(classes))

                if len(available_models) < MIN_MODELS_FOR_INFERENCE:
                    show_error_modal(
                        "Analysis Error",
                        f"Insufficient models loaded ({len(available_models)}/{MIN_MODELS_FOR_INFERENCE} required).",
                        key_prefix="model_insufficient",
                    )
                    if load_status:
                        st.dataframe(pd.DataFrame(load_status), use_container_width=True, hide_index=True)
                    return

                try:
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
                            "icon": "",
                        },
                    )
                    inference_result = {
                        "predicted_class": predicted_class,
                        "confidence": confidence,
                        "individual_preds": individual_preds,
                        "ensemble_pred": ensemble_pred,
                        "runtime_errors": runtime_errors,
                        "deficiency_data": deficiency_data,
                    }

                    if user_data.get("user_id"):
                        store_analysis(
                            user_id=user_data["user_id"],
                            image_name=f"analysis_{datetime.now().isoformat()}",
                            predicted_condition=predicted_class,
                            vitamin_deficiency=deficiency_data.get("vitamin", "Unknown"),
                            confidence_score=float(confidence),
                        )
                except Exception as exc:
                    log_event(f"Run Analysis failed: {exc}", level="error")
                    log_event(traceback.format_exc(limit=8), level="error")
                    show_error_modal("Analysis Failure", str(exc), key_prefix="analysis_fail")
                    return

        if inference_result is not None and image_for_result is not None:
            st.markdown("---")
            left_col, right_col = st.columns([1.05, 1], gap="large")
            with left_col:
                st.image(image_for_result, use_container_width=True)
            with right_col:
                predicted_class = inference_result["predicted_class"]
                confidence = inference_result["confidence"]
                individual_preds = inference_result["individual_preds"]
                deficiency_data = inference_result["deficiency_data"]

                st.markdown(f"**Condition:** {predicted_class.title()}")
                st.markdown(f"**Potential Deficiency:** {deficiency_data['vitamin']}")
                st.markdown(f"**Clinical Notes:** {deficiency_data['description']}")
                st.markdown(f"**Recommendations:** {deficiency_data['recommendations']}")

                metric_a, metric_b = st.columns(2)
                metric_a.metric("Confidence", f"{confidence * 100:.1f}%")
                metric_b.metric("Method", active_method.replace("_", " ").title())

                votes = [int(np.argmax(pred)) for pred in individual_preds.values()]
                top_vote_count = int(np.bincount(votes, minlength=len(classes)).max()) if votes else 0
                vote_ratio = (top_vote_count / len(votes)) if votes else 0.0
                if vote_ratio < 0.50:
                    st.warning("Low model consensus. Try a clearer image.")
                elif vote_ratio < 0.70:
                    st.info("Moderate model consensus. Review top predictions.")

            st.plotly_chart(create_top_predictions_chart(inference_result["ensemble_pred"], classes), use_container_width=True)
            with st.expander("Advanced model breakdown", expanded=False):
                for model_name, pred in individual_preds.items():
                    model_class_idx = np.argmax(pred)
                    model_confidence = pred[model_class_idx]
                    model_class = classes[model_class_idx]
                    col_a, col_b, col_c = st.columns([2, 2, 1])
                    with col_a:
                        st.markdown(f"**{model_name}**")
                        st.caption(MODEL_INFO.get(model_name, {"description": "Deep learning model"})["description"])
                    with col_b:
                        st.markdown(f"Predicted: **{model_class}**")
                    with col_c:
                        st.progress(float(np.clip(model_confidence, 0.0, 1.0)))
                        st.caption(f"{model_confidence * 100:.1f}%")
                st.plotly_chart(create_prediction_chart(individual_preds, classes, predicted_class), use_container_width=True)

            if inference_result["runtime_errors"]:
                runtime_df = pd.DataFrame(
                    [{"model": m, "error": err} for m, err in inference_result["runtime_errors"].items()]
                )
                st.dataframe(runtime_df, use_container_width=True, hide_index=True)

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
            for model_name, pred in individual_preds.items():
                model_class_idx = np.argmax(pred)
                report_data += f"\n{model_name}: {classes[model_class_idx]} ({pred[model_class_idx] * 100:.2f}%)"

            st.download_button(
                label="Download Report",
                data=report_data,
                file_name=f"deficiency_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
            )

    elif current_nav == "Model Performance":
        render_page_header("Performance and Diagnostics", "Model metrics and runtime diagnostics")
        if not status_df.empty:
            st.dataframe(status_df, use_container_width=True, hide_index=True)
        else:
            st.info("No model load logs yet. They appear after first Run Analysis.")

        metadata_path = MODEL_DIR / "ensemble_metadata.json"
        if metadata_path.exists():
            import json

            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            r1, r2, r3 = st.columns(3)
            r1.metric("Best Ensemble Accuracy", f"{metadata.get('best_ensemble_accuracy', 0) * 100:.2f}%")
            r2.metric("Best Individual Accuracy", f"{metadata.get('best_individual_accuracy', 0) * 100:.2f}%")
            r3.metric("Best Method", metadata.get("best_method", "soft_voting").replace("_", " ").title())

            if "model_accuracies" in metadata:
                model_acc_df = pd.DataFrame(
                    {
                        "Model": list(metadata["model_accuracies"].keys()),
                        "Accuracy (%)": [v * 100 for v in metadata["model_accuracies"].values()],
                    }
                ).sort_values("Accuracy (%)", ascending=False)
                fig = px.bar(
                    model_acc_df,
                    x="Model",
                    y="Accuracy (%)",
                    color="Accuracy (%)",
                    color_continuous_scale=[[0.0, "#4F46E5"], [1.0, "#9CA3AF"]],
                    title="Model Accuracy Comparison",
                )
                fig.update_layout(height=460, template="plotly_dark", paper_bgcolor="#121218", plot_bgcolor="#121218")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(model_acc_df, use_container_width=True, hide_index=True)
        else:
            st.info("No performance metadata file found.")

    elif current_nav == "Model Status":
        render_page_header("Model Loading Status", "Models load only during Run Analysis")
        if load_status:
            status_rows = []
            for i, row in enumerate(load_status, start=1):
                details_lines = str(row.get("details", "")).splitlines()
                status_rows.append(
                    {
                        "Step": i,
                        "Model": row.get("model", ""),
                        "Status": row.get("status", ""),
                        "Details": details_lines[0] if details_lines else "",
                    }
                )
            status_table_df = pd.DataFrame(status_rows)
            st.dataframe(status_table_df, use_container_width=True, hide_index=True)
            st.markdown(f"**Summary**: {loaded_count} loaded, {issue_count} issue(s).")
            if loaded_count < len(ACTIVE_MODEL_NAMES):
                st.warning(
                    f"Running in low-memory mode with {loaded_count} model(s). "
                    "For full ensemble performance, use higher-memory hosting."
                )
        else:
            st.info("No model loading status yet. Click Run Analysis to initialize models.")

    else:
        render_page_header("About", "Application overview")
        st.markdown(
            """
This application performs vitamin deficiency inference from images using an ensemble of deep learning models.

- Inference engine: TensorFlow/Keras
- App framework: Streamlit
- Model family: CNN, EfficientNetV2L, InceptionResNetV2, InceptionV3, MobileNet, ResNet, VGG16, Xception

Medical disclaimer: This tool is for informational purposes only and is not a substitute for professional diagnosis.
            """
        )

    st.markdown("---")
    st.caption("Vitamin Deficiency AI | Premium Inference Dashboard")

if __name__ == "__main__":
    try:
        log_event("Streamlit script execution started.")
        candidate_dirs = [
            get_runtime_setting('MODEL_DIR', '').strip() or '<not-set>',
            str(BASE_DIR / 'model_saved_files'),
            '/opt/render/project/src/model_saved_files',
            '/app/model_saved_files',
        ]
        log_event(
            f"Environment snapshot: RENDER={os.getenv('RENDER', '')} "
            f"RENDER_SERVICE_ID={'set' if os.getenv('RENDER_SERVICE_ID') else 'unset'} "
            f"STREAMLIT_SHARING_MODE={os.getenv('STREAMLIT_SHARING_MODE', '')} "
            f"IS_STREAMLIT_CLOUD={IS_STREAMLIT_CLOUD} "
            f"LIGHTWEIGHT_MODE_RUNTIME={get_runtime_setting('LIGHTWEIGHT_MODE', '<not-set>')} "
            f"LIGHTWEIGHT_MODE_RESOLVED={LIGHTWEIGHT_MODE} "
            f"BASE_DIR={BASE_DIR} MODEL_DIR={MODEL_DIR} "
            f"MODEL_DIR_CANDIDATES={candidate_dirs}"
        )
        main()
    except Exception as exc:
        log_event(f"Fatal app error: {exc}", level="error")
        log_event(traceback.format_exc(limit=12), level="error")
        raise
