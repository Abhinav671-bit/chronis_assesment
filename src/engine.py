from typing import List
from src.schemas import DomainData, DomainDivergenceOutput

# Hardcoded baselines for volume normalization
DOMAIN_MAXIMUMS = {
    "fitness": 120.0,
    "work": 8.0,
    "social": 5.0
}

def calculate_uncertainty(n_talk: int, n_logs: int, n_optimal: int = 15) -> float:
    """Calculates explicit uncertainty based on evidence sparsity."""
    return max(0.0, 1.0 - min(1.0, (n_talk + n_logs) / n_optimal))

def get_alignment_score(self_talk: List[str], behavioral_actions: List[str]) -> float:
    """Calculates Jaccard Similarity (Token Overlap) for semantic alignment."""
    talk_tokens = set(" ".join(self_talk).lower().split())
    action_tokens = set(" ".join(behavioral_actions).lower().split())
    
    if not talk_tokens or not action_tokens:
        return 0.0
        
    intersection = talk_tokens.intersection(action_tokens)
    union = talk_tokens.union(action_tokens)
    return len(intersection) / len(union)

def evaluate_domain(domain_name: str, data: DomainData, evaluation_days: int) -> DomainDivergenceOutput:
    if evaluation_days <= 0:
        raise ValueError(f"evaluation_days must be >= 1. Received: {evaluation_days}")

    n_talk = len(data.self_talk)
    n_logs = len(data.behavioral_logs)
    
    uncertainty = round(calculate_uncertainty(n_talk, n_logs), 3)
    
    # 1. Pure Evidence Abstention Gate
    if n_talk < 2 and n_logs < 3:
        return DomainDivergenceOutput(domain_name, "INSUFFICIENT_EVIDENCE", uncertainty)
        
    # 2. Blind Spot Detection (Behaviorally active, narratively absent)
    if n_talk < 2 and n_logs >= 3:
        return DomainDivergenceOutput(domain_name, "BLIND_SPOT", uncertainty)
        
    # --- Standard Execution Logic ---
    total_magnitude = sum(log.magnitude for log in data.behavioral_logs)
    
    # Fallback to 10.0 if domain is unknown (documented limitation)
    m_expected = DOMAIN_MAXIMUMS.get(domain_name, 10.0) 
    b_vol = min(1.0, total_magnitude / (evaluation_days * m_expected))
    
    actions = [log.action for log in data.behavioral_logs]
    s_sim = get_alignment_score(data.self_talk, actions)
    
    # 3. Aspiration Gap
    if n_talk >= 2 and b_vol <= 0.05:
         return DomainDivergenceOutput(
             domain=domain_name, 
             classification="ASPIRATION_GAP", 
             uncertainty_score=uncertainty,
             alignment_score=None,           # <- Cleaned up!
             behavioral_volume=round(b_vol, 3)
        )
    
    # 4. Overstatement (Some narrative overlap, but volume is highly lacking)
    # Note: s_sim threshold is 0.1 to account for naturally sparse Jaccard scores
    if s_sim >= 0.1 and b_vol < 0.4:
        classification = "OVERSTATEMENT"
        
    # 5. Understatement (Actions occur heavily, but semantic overlap in narrative is near zero)
    elif s_sim < 0.1 and b_vol > 0.6:
        classification = "UNDERSTATEMENT"
        
    # 6. Aligned (Data is sufficient, but no pronounced divergence pattern exists)
    else:
        classification = "ALIGNED"
        
    return DomainDivergenceOutput(
        domain=domain_name,
        classification=classification,
        uncertainty_score=uncertainty,
        alignment_score=round(s_sim, 3),
        behavioral_volume=round(b_vol, 3)
    )