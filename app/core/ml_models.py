"""
ML Models initialization and management
"""
import logging
from pathlib import Path
from typing import Any, Tuple, Optional

from config import settings

logger = logging.getLogger(__name__)

# Global model instances
clip_model = None
clip_preprocess = None
clip_tokenizer = None

sbert_model = None
sentiment_model = None
sentiment_tokenizer = None

device = None

# Lazy load flags
_torch_available = False
_ml_libs_available = False


def check_ml_availability():
    """Check if ML libraries are installed"""
    global _torch_available, _ml_libs_available
    try:
        import torch
        _torch_available = True
        import open_clip
        import sentence_transformers
        import transformers
        _ml_libs_available = True
        return True
    except ImportError:
        _torch_available = False
        _ml_libs_available = False
        return False


async def init_ml_models():
    """Initialize all ML models"""
    global clip_model, clip_preprocess, clip_tokenizer
    global sbert_model, sentiment_model, sentiment_tokenizer, device
    
    # If we are strictly using remote ML, skip initialization
    if not settings.use_gpu and settings.ml_service_url:
        logger.info("Skipping local ML model initialization (Forwarding Mode)")
        return

    try:
        if not check_ml_availability():
             logger.warning("ML libraries not found. Running in 'Lite' mode.")
             return

        import torch
        import open_clip
        from sentence_transformers import SentenceTransformer
        from transformers import AutoTokenizer, AutoModelForSequenceClassification

        # Set device
        device = torch.device(settings.gpu_device if settings.use_gpu and torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {device}")
        
        # Create cache directory
        Path(settings.model_cache_dir).mkdir(parents=True, exist_ok=True)
        
        # Load CLIP model
        logger.info(f"Loading CLIP model: {settings.clip_model_name}")
        clip_model, clip_preprocess, clip_tokenizer = open_clip.create_model_and_transforms(
            settings.clip_model_name,
            pretrained=settings.clip_pretrained,
            cache_dir=settings.model_cache_dir
        )
        clip_model = clip_model.to(device)
        clip_model.eval()
        logger.info("CLIP model loaded successfully")
        
        # Load Sentence-BERT model
        logger.info(f"Loading Sentence-BERT model: {settings.sbert_model_name}")
        sbert_model = SentenceTransformer(
            settings.sbert_model_name,
            cache_folder=settings.model_cache_dir,
            device=str(device)
        )
        logger.info("Sentence-BERT model loaded successfully")
        
        # Load sentiment analysis model
        logger.info(f"Loading sentiment model: {settings.sentiment_model_name}")
        sentiment_tokenizer = AutoTokenizer.from_pretrained(
            settings.sentiment_model_name,
            cache_dir=settings.model_cache_dir
        )
        sentiment_model = AutoModelForSequenceClassification.from_pretrained(
            settings.sentiment_model_name,
            cache_dir=settings.model_cache_dir,
            num_labels=3  # positive, neutral, negative
        )
        sentiment_model = sentiment_model.to(device)
        sentiment_model.eval()
        logger.info("Sentiment model loaded successfully")
        
        logger.info("All ML models initialized successfully")
        
    except Exception as e:
        logger.error(f"ML models initialization failed: {e}")
        # Be resilient - don't crash app if models fail to load
        logger.warning("Continuing without local ML models")


def get_clip_model():
    """Get CLIP model instance"""
    return clip_model, clip_preprocess, clip_tokenizer, device


def get_sbert_model():
    """Get Sentence-BERT model instance"""
    return sbert_model


def get_sentiment_model():
    """Get sentiment analysis model instance"""
    return sentiment_model, sentiment_tokenizer, device


def encode_image_clip(image, model=None, preprocess=None, device=None):
    """
    Encode image using CLIP (Local Fallback)
    """
    if not _ml_libs_available:
        return None

    if model is None:
        model, preprocess, _, device = get_clip_model()
    
    if model is None: 
        return None

    import torch
    
    with torch.no_grad():
        image_input = preprocess(image).unsqueeze(0).to(device)
        image_features = model.encode_image(image_input)
        image_features /= image_features.norm(dim=-1, keepdim=True)
        return image_features.cpu().numpy()[0]


def encode_text_clip(text, model=None, tokenizer=None, device=None):
    """
    Encode text using CLIP (Local Fallback)
    """
    if not _ml_libs_available:
        return None

    if model is None:
        model, _, tokenizer, device = get_clip_model()
    
    if model is None:
        return None

    import torch

    if isinstance(text, str):
        text = [text]
    
    with torch.no_grad():
        text_input = tokenizer(text).to(device)
        text_features = model.encode_text(text_input)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        return text_features.cpu().numpy()


def encode_text_sbert(text, model=None):
    """
    Encode text using Sentence-BERT (Local Fallback)
    """
    if not _ml_libs_available:
        # Fallback to None if libs missing (Service should handle this)
        return None

    if model is None:
        model = get_sbert_model()
    
    if model is None:
        return None

    embeddings = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )
    
    return embeddings


def analyze_sentiment(text, model=None, tokenizer=None, device=None):
    """
    Analyze sentiment of text
    """
    if not _ml_libs_available:
        return {"sentiment": "neutral", "scores": {"neutral": 1.0}, "confidence": 1.0}

    if model is None:
        model, tokenizer, device = get_sentiment_model()
        
    if model is None:
        return {"sentiment": "neutral", "scores": {"neutral": 1.0}, "confidence": 1.0}

    import torch

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True
    ).to(device)
    
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)
        
        sentiment_labels = ["negative", "neutral", "positive"]
        scores = {
            label: float(prob)
            for label, prob in zip(sentiment_labels, probs[0])
        }
        
        predicted_label = sentiment_labels[torch.argmax(probs[0]).item()]
        
        return {
            "sentiment": predicted_label,
            "scores": scores,
            "confidence": max(scores.values())
        }
