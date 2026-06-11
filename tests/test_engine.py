import pytest
from src.schemas import BehavioralLog, DomainData
from src.engine import evaluate_domain

def create_mock_log(magnitude: float, action: str = "mock_action", day_offset: int = 1) -> BehavioralLog:
    """
    Helper to generate logs. 
    Note: default 'mock_action' ensures near-zero Jaccard overlap unless overridden.
    day_offset dynamically shifts dates to prevent future issues if temporal logic is added.
    """
    timestamp = f"2026-06-{day_offset:02d}"
    return BehavioralLog(timestamp=timestamp, action=action, magnitude=magnitude)

def test_insufficient_evidence_abstention():
    """Test pure abstention gate (<2 talk AND <3 logs)."""
    data = DomainData(self_talk=["One snippet"], behavioral_logs=[create_mock_log(1.0)])
    result = evaluate_domain("work", data, evaluation_days=3)
    assert result.classification == "INSUFFICIENT_EVIDENCE"

def test_blind_spot_detection():
    """Test behaviorally active but narratively absent."""
    logs = [create_mock_log(2.0, day_offset=i+1) for i in range(5)]
    data = DomainData(self_talk=["Only one snippet"], behavioral_logs=logs)
    result = evaluate_domain("social", data, evaluation_days=3)
    assert result.classification == "BLIND_SPOT"

def test_aspiration_gap():
    """Test stated goals but zero behavioral volume."""
    logs = [create_mock_log(0.0, day_offset=i+1) for i in range(3)]
    data = DomainData(
        self_talk=["I will work out.", "Getting fit!"], 
        behavioral_logs=logs
    )
    result = evaluate_domain("fitness", data, evaluation_days=3)
    assert result.classification == "ASPIRATION_GAP"
    assert result.behavioral_volume == 0.0

def test_overstatement():
    """
    Test high talk semantic overlap but low action volume.
    Note: Strings are intentionally identical to guarantee s_sim = 1.0 (overlap > 0.1).
    b_vol = 75 / 360 (fitness max over 3 days) = ~0.20 (which is < 0.4 but > 0.05).
    """
    logs = [create_mock_log(25.0, "running on treadmill", day_offset=i+1) for i in range(3)]
    data = DomainData(
        self_talk=["running on treadmill", "running on treadmill"], 
        behavioral_logs=logs
    )
    result = evaluate_domain("fitness", data, evaluation_days=3)
    assert result.classification == "OVERSTATEMENT"

def test_understatement():
    """
    Test high action volume but low/no semantic overlap in narrative.
    Total magnitude = 300. Expected fitness max over 3 days = 360. 
    b_vol = 300 / 360 = 0.833 (which is > 0.6).
    s_sim = 0.0 (no lexical overlap).
    """
    logs = [create_mock_log(100.0, "heavy lifting", day_offset=i+1) for i in range(3)] 
    data = DomainData(
        self_talk=["I ate a sandwich", "Thinking about sleep"], 
        behavioral_logs=logs
    )
    result = evaluate_domain("fitness", data, evaluation_days=3)
    assert result.classification == "UNDERSTATEMENT"

def test_aligned_case():
    """
    Test the fallback else branch where divergence is not extreme.
    b_vol = 180 / 360 = 0.5 (normal volume, not triggering over/under limits).
    s_sim = 1.0 (perfect semantic match).
    """
    logs = [create_mock_log(60.0, "running", day_offset=i+1) for i in range(3)]
    data = DomainData(
        self_talk=["running", "running is good"],
        behavioral_logs=logs
    )
    result = evaluate_domain("fitness", data, evaluation_days=3)
    assert result.classification == "ALIGNED"
    
def test_value_error_on_zero_days():
    """Test parameter guard logic correctly raises ValueError."""
    data = DomainData(self_talk=["a", "b"], behavioral_logs=[create_mock_log(1.0)]*3)
    with pytest.raises(ValueError):
        evaluate_domain("work", data, evaluation_days=0)