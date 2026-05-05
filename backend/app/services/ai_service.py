from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.problem import Problem, ProblemStatus
from app.models.vote import Vote, VoteType
from app.models.user import User
from sqlalchemy.orm import selectinload

class AIAnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_priority_score(self, problem: Problem) -> float:
        """
        AI Formula:
        Score = (Upvotes * 10) - (Downvotes * 5) + (Comments * 3) + (ReporterLevel * 5)
        """
        upvotes = sum(1 for v in problem.votes if v.vote_type == VoteType.UPVOTE)
        downvotes = sum(1 for v in problem.votes if v.vote_type == VoteType.DOWNVOTE)
        comments_count = len(problem.comments)
        reporter_level = problem.author.level if problem.author else 1

        score = (upvotes * 10) - (downvotes * 5) + (comments_count * 3) + (reporter_level * 5)
        
        # Add boost for critical categories (AI Hotspots)
        critical_keywords = ["water", "electricity", "road", "safety", "hazard"]
        if any(kw in problem.title.lower() or kw in problem.description.lower() for kw in critical_keywords):
            score += 20
            
        return max(0, score)

    async def get_city_insights(self) -> Dict[str, Any]:
        """
        Aggregate data for the Government Dashboard 'Insights' tab.
        """
        # Fetch problems with necessary relations
        stmt = select(Problem).options(
            selectinload(Problem.votes),
            selectinload(Problem.author),
            selectinload(Problem.comments)
        )
        result = await self.db.execute(stmt)
        problems = result.scalars().all()

        scored_problems = []
        total_sentiment = 0
        
        for p in problems:
            score = await self.calculate_priority_score(p)
            upvotes = sum(1 for v in p.votes if v.vote_type == VoteType.UPVOTE)
            downvotes = sum(1 for v in p.votes if v.vote_type == VoteType.DOWNVOTE)
            
            sentiment = (upvotes / (upvotes + downvotes + 1)) * 100
            total_sentiment += sentiment
            
            scored_problems.append({
                "id": str(p.id),
                "title": p.title,
                "score": score,
                "sentiment": sentiment,
                "category": p.category,
                "status": p.status
            })

        # Sort by priority
        scored_problems.sort(key=lambda x: x["score"], reverse=True)

        avg_sentiment = total_sentiment / len(problems) if problems else 0
        
        return {
            "top_priorities": scored_problems[:5],
            "city_sentiment": round(avg_sentiment, 1),
            "hotspots": self._calculate_hotspots(scored_problems),
            "ai_summary": f"City sentiment is {self._get_sentiment_label(avg_sentiment)}. Highest priority detected in {scored_problems[0]['category'] if scored_problems else 'N/A'}."
        }

    def _calculate_hotspots(self, scored_problems: List[Dict]) -> List[Dict]:
        categories = {}
        for p in scored_problems:
            cat = p["category"]
            categories[cat] = categories.get(cat, 0) + p["score"]
        
        return [{"category": k, "intensity": v} for k, v in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]]

    def _get_sentiment_label(self, score: float) -> str:
        if score > 80: return "Highly Positive"
        if score > 60: return "Positive"
        if score > 40: return "Neutral"
        return "Concerned"
