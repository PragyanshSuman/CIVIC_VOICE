import pytest
from app.ai.pipeline import AIPipeline

def test_preprocessing():
    pipeline = AIPipeline()
    text = "This is a <br> TEST! http://example.com"
    processed = pipeline.preprocessor.preprocess(text)
    assert "test" in processed
    assert "http" not in processed
    assert "<br>" not in processed

def test_ranking_logic():
    pipeline = AIPipeline()
    # High votes, moderate feasibility
    score, breakdown = pipeline.ranker.calculate_score(votes=100, feasibility=0.8, impact=0.8, cost=0.2)
    assert score > 0.5
    assert "votes_score" in breakdown
