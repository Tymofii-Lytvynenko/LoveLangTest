from dataclasses import dataclass, field

@dataclass
class RelationalNeedsComponent:
    raw_safety: float = 0.0
    raw_resource: float = 0.0
    raw_resonance: float = 0.0
    raw_expansion: float = 0.0
    
    # Ці поля заповнюються сервісом AdjustmentService
    adjusted_safety: float = 0.0
    adjusted_resource: float = 0.0
    adjusted_resonance: float = 0.0
    adjusted_expansion: float = 0.0
    priority_safety: float = 0.0
    priority_resource: float = 0.0
    priority_resonance: float = 0.0
    priority_expansion: float = 0.0

    confidence_safety: str = "Medium"
    confidence_resource: str = "Medium"
    confidence_resonance: str = "Medium"
    confidence_expansion: str = "Medium"
