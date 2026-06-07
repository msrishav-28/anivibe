"""
Modal ML Service - GPU-powered inference for AniVibe

Deploy: modal deploy modal_app.py
Local test: modal run modal_app.py
"""
import modal
import os

# Create Modal app
app = modal.App("anivibe-ml")

# Docker image with ML dependencies
image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install(
        "torch",
        "torchvision", 
        "transformers",
        "sentence-transformers",
        "open-clip-torch",
        "faiss-cpu",
        "pillow",
        "numpy",
        "fastapi",
    )
)

# Secrets (add in Modal dashboard)
secrets = [
    modal.Secret.from_name("supabase-credentials"),  # SUPABASE_URL, SUPABASE_SERVICE_KEY
]


@app.function(
    image=image,
    secrets=secrets,
    gpu="T4",  # NVIDIA T4 GPU
    timeout=300,  # 5 minutes max
    container_idle_timeout=60,  # Keep warm for 1 minute
)
@modal.web_endpoint(method="POST")
def clip_image_search(request: dict):
    """
    CLIP-based image search endpoint.
    
    Request:
        {
            "image_base64": "...",  # Base64 encoded image
            "limit": 20
        }
    
    Response:
        {
            "results": [{"anime_id": 1, "title": "...", "similarity": 0.95}, ...]
        }
    """
    import torch
    from PIL import Image
    import base64
    from io import BytesIO
    from supabase import create_client, Client
    import os
    
    # Load model (cached after first run)
    import open_clip
    model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')
    model.eval()
    
    # Decode image
    try:
        if "base64," in request["image_base64"]:
             request["image_base64"] = request["image_base64"].split("base64,")[1]
             
        image_data = base64.b64decode(request["image_base64"])
        image = Image.open(BytesIO(image_data))
    except Exception as e:
        return {"error": f"Invalid image data: {str(e)}"}
    
    # Get image embedding
    with torch.no_grad():
        image_tensor = preprocess(image).unsqueeze(0)
        image_embedding = model.encode_image(image_tensor)
        image_embedding = image_embedding / image_embedding.norm(dim=-1, keepdim=True)
        embedding_list = image_embedding.cpu().numpy()[0].tolist()
    
    # Connect to Supabase
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_SERVICE_KEY")
    supabase: Client = create_client(url, key)
    
    # Query via RPC
    try:
        response = supabase.rpc(
            "match_anime_embeddings", 
            {
                "query_embedding": embedding_list,
                "match_threshold": 0.5,
                "match_count": request.get("limit", 20)
            }
        ).execute()
        
        return {"results": response.data}
        
    except Exception as e:
        print(f"Supabase RPC failed: {e}")
        # Fallback empty
        return {"results": []}


@app.function(
    image=image,
    secrets=secrets,
    gpu="T4",
    timeout=300,
)
@modal.web_endpoint(method="POST")
def gnn_recommendations(request: dict):
    """
    GNN-based recommendations.
    
    Request:
        {
            "user_id": "uuid",
            "limit": 20
        }
    
    Response:
        {
            "recommendations": [{"anime_id": 1, "score": 0.92, "reason": "...", ...]
        }
    """
    # TODO: Load trained GNN model
    # TODO: Generate embeddings for user's watched anime
    # TODO: Query graph for similar nodes
    
    return {
        "recommendations": [
            {"anime_id": 1, "score": 0.92, "reason": "Graph neighborhood match"},
        ]
    }


@app.function(
    image=image,
    secrets=secrets,
    cpu=2,  # No GPU needed for SBERT
    timeout=60,
)
@modal.web_endpoint(method="POST")
def semantic_search(request: dict):
    """
    Semantic search using Sentence-BERT.
    
    Request:
        {
            "query": "dark psychological thriller",
            "limit": 20
        }
    
    Response:
        {
            "results": [{"anime_id": 1, "similarity": 0.89, ...], ...]
        }
    """
    from sentence_transformers import SentenceTransformer
    import numpy as np
    
    # Load model (cached)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Get query embedding
    query_embedding = model.encode(request["query"])
    
    # TODO: Query Supabase pgvector for similar anime synopses
    
    return {
        "results": [
            {"anime_id": 46, "title": "Death Note", "similarity": 0.89},
            {"anime_id": 16498, "title": "Psycho-Pass", "similarity": 0.85},
        ]
    }


@app.function(image=image)
@modal.web_endpoint(method="GET")
def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "anivibe-ml"}


# Local testing
if __name__ == "__main__":
    # Test locally with: modal run modal_app.py
    with app.run():
        print("Testing semantic search...")
        result = semantic_search.remote({"query": "action anime", "limit": 5})
        print(result)
