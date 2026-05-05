
try:
    from sklearn.cluster import DBSCAN
    import numpy as np
except ImportError:
    DBSCAN = None
    np = None

class SolutionClusterer:
    """
    Groups similar solutions using density-based clustering (DBSCAN) on embeddings.
    """
    
    def __init__(self, eps: float = 0.5, min_samples: int = 2):
        self.eps = eps
        self.min_samples = min_samples

    def cluster_solutions(self, solutions_data: list[dict], embeddings: list) -> list[dict]:
        """
        Takes a list of solution dicts and their corresponding embeddings.
        Returns the solutions with an added 'cluster_id' field.
        """
        if not DBSCAN or not embeddings or len(embeddings) == 0:
            # Fallback: Assign unique cluster to everyone if ML libs missing
            for sol in solutions_data:
                sol['cluster_id'] = -1
            return solutions_data
            
        # Convert list of lists to numpy array
        X = np.array(embeddings)
        
        # Run DBSCAN
        # eps=0.5 is a standard starting point for cosine distance (if normalized) or euclidean
        # metric='cosine' is often better for embeddings, but DBSCAN defaults to euclidean
        clustering = DBSCAN(eps=self.eps, min_samples=self.min_samples, metric='euclidean').fit(X)
        
        labels = clustering.labels_
        
        for i, sol in enumerate(solutions_data):
            # map the label back to the solution
            sol['cluster_id'] = int(labels[i])
            
        return solutions_data

clusterer = SolutionClusterer()
