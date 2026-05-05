
from typing import List, Dict
from app.ai.preprocessor import preprocessor
from app.ai.embeddings import embedding_model
from app.ai.clustering import clusterer
from app.ai.ranking import ranker

class AIPipeline:
    """
    Orchestrates the AI processing flow for civic solutions.
    """
    
    def process_solutions(self, solutions: List[Dict]) -> List[Dict]:
        """
        Full pipeline:
        1. Preprocess text
        2. Generate embeddings
        3. Cluster similar solutions
        4. Rank solutions using weighted algorithm
        """
        if not solutions:
            return []
            
        # 1. Preprocess
        processed_texts = []
        for sol in solutions:
            # Combine title and description for better context
            full_text = f"{sol.get('title', '')} {sol.get('description', '')}"
            clean_text = preprocessor.preprocess(full_text)
            processed_texts.append(clean_text)
            
        # 2. Embeddings
        embeddings = embedding_model.encode(processed_texts)
        
        # 3. Clustering
        # Modifies solutions in-place by adding 'cluster_id'
        solutions = clusterer.cluster_solutions(solutions, embeddings)
        
        # 4. Ranking
        # Modifies solutions in-place by adding 'overall_score'
        ranked_solutions = ranker.rank_solutions(solutions)
        
        return ranked_solutions

    def analyze_single_solution(self, title: str, description: str) -> Dict:
        """
        Analyze a newly submitted solution to determine its initial AI scores.
        Note: Real feasibility/cost detection would need a trained classifier or LLM.
        For now, we return dummy/heuristic values or placeholder logic.
        """
        # Placeholder logic for "AI" analysis of feasibility/impact
        # In a real system, you'd pass this text to an LLM or specific classifier models
        
        text_len = len(description)
        
        # Heuristic: Longer, detailed descriptions might be more feasible?
        feasibility = min(0.5 + (text_len / 1000.0), 0.9)
        
        # Heuristic: "save", "money", "efficient" keywords -> potentially lower cost
        low_cost_keywords = ["cheap", "save", "efficient", "low cost", "budget"]
        cost_score = 0.7 # Default high cost
        if any(w in description.lower() for w in low_cost_keywords):
            cost_score = 0.3
            
        overall = round((feasibility + 0.6 + (1.0 - cost_score)) / 3.0, 2)
        
        return {
            "feasibility": round(feasibility, 2),
            "impact": 0.6,
            "cost": cost_score,
            "overall": overall
        }

ai_pipeline = AIPipeline()
