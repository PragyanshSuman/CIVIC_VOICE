
import math

class SolutionRanker:
    """
    Scores and ranks solutions based on weighted criteria.
    """
    
    # Weights for the scoring algorithm
    WEIGHT_VOTES = 0.4
    WEIGHT_FEASIBILITY = 0.3
    WEIGHT_IMPACT = 0.2
    WEIGHT_COST_EFFICIENCY = 0.1 # Lower cost is better

    def calculate_score(self, solution: dict) -> float:
        """
        Calculates the overall score for a single solution.
        Input dict is expected to have:
        - upvotes_count: int
        - downvotes_count: int
        - ai_score_feasibility: float (0-1)
        - ai_score_impact: float (0-1)
        - ai_score_cost: float (0-1, where 1 is high cost, 0 is low cost)
        """
        
        # 1. Vote Score (Normalized using Wilson Score Interval or simple net score)
        # Simple net score for now, with log scaling to dampen huge numbers
        upvotes = solution.get('upvotes_count', 0)
        downvotes = solution.get('downvotes_count', 0)
        net_votes = max(0, upvotes - downvotes)
    WEIGHTS = {
        "votes": 0.4,
        "feasibility": 0.3,
        "impact": 0.2,
        "cost": 0.1 # Lower cost is better
    }

    def calculate_score(self, votes: int, feasibility: float, impact: float, cost: float) -> tuple[float, dict]:
        """
        Calculate weighted score with breakdown.
        
        Formula:
        Score = (w_v * norm_votes) + (w_f * feasibility) + (w_i * impact) + (w_c * (1 - cost))
        """
        # Normalize votes (using log scale to dampen popularity bias)
        # log(1) = 0, so we add 1 to handle 0 votes. 
        # We assume max realistic votes for normalization context is ~1000 for this scale
        normalized_votes = min(np.log1p(votes) / np.log1p(1000), 1.0)
        
        # Invert cost (lower cost is better)
        # Cost is 0.0 to 1.0, so 1 - cost gives us an efficiency score
        cost_efficiency = 1.0 - cost
        
        score = (
            (self.WEIGHTS["votes"] * normalized_votes) +
            (self.WEIGHTS["feasibility"] * feasibility) +
            (self.WEIGHTS["impact"] * impact) +
            (self.WEIGHTS["cost"] * cost_efficiency)
        )
        
        breakdown = {
            "votes_score": round(self.WEIGHTS["votes"] * normalized_votes, 3),
            "feasibility_score": round(self.WEIGHTS["feasibility"] * feasibility, 3),
            "impact_score": round(self.WEIGHTS["impact"] * impact, 3),
            "cost_efficiency_score": round(self.WEIGHTS["cost"] * cost_efficiency, 3),
            "raw_metrics": {
                "votes": votes,
                "feasibility": feasibility,
                "impact": impact,
                "cost": cost
            }
        }

        return min(max(score, 0.0), 1.0), breakdown

    def rank_solutions(self, solutions: list[dict]) -> list[dict]:
        """
        Calculates scores for all solutions and sorts them.
        """
        for sol in solutions:
            sol['overall_score'] = self.calculate_score(sol)
            
        # Sort descending
        return sorted(solutions, key=lambda x: x['overall_score'], reverse=True)

ranker = SolutionRanker()
