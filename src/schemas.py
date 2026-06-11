from dataclasses import dataclass
from typing import List, Literal, Optional, Dict

@dataclass
class BehavioralLog:
    timestamp: str  # Note: Unvalidated string; assumed valid ISO8601 for MVP
    action: str
    magnitude: float

@dataclass
class DomainData:
    self_talk: List[str]
    behavioral_logs: List[BehavioralLog]

@dataclass
class UserProfile:
    user_id: str
    domains: Dict[str, DomainData]

DivergenceType = Literal[
    "OVERSTATEMENT", 
    "UNDERSTATEMENT", 
    "BLIND_SPOT", 
    "ASPIRATION_GAP", 
    "INSUFFICIENT_EVIDENCE",
    "ALIGNED"  # Handles non-divergent states safely
]

@dataclass
class DomainDivergenceOutput:
    domain: str
    classification: DivergenceType
    uncertainty_score: float
    alignment_score: Optional[float] = None
    behavioral_volume: Optional[float] = None