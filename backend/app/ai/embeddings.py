
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
except ImportError:
    # Fallback for environments without heavy AI deps installed
    SentenceTransformer = None
    np = None

class EmbeddingModel:
    """
    Wrapper for Sentence Transformer model to generate embeddings.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model_name = model_name
        self.model = None
        
        if SentenceTransformer:
            try:
                # This might download the model on first run
                self.model = SentenceTransformer(model_name)
            except Exception as e:
                print(f"Failed to load sentence-transformer model: {e}")
        else:
            print("SentenceTransformer library not found. AI features will be limited.")

    def encode(self, texts: list[str]) -> list:
        """
        Generates embeddings for a list of texts.
        """
        if not self.model or not texts:
            # Return dummy zero vectors if model is not available
            return [[0.0] * 384] * len(texts) if texts else []
            
        embeddings = self.model.encode(texts)
        return embeddings

    def cosine_similarity(self, vec_a, vec_b) -> float:
        """
        Calculates cosine similarity between two vectors.
        """
        if np is None:
            return 0.0
            
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        return np.dot(vec_a, vec_b) / (norm_a * norm_b)

embedding_model = EmbeddingModel()
