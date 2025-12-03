from dataclasses import dataclass, field
from typing import List
from .enums import AttachmentStyle, ConflictResponse, RegulationMethod, ContextDependency

@dataclass
class PsychometricsComponent:
    """
    Substrate Layer. Inputs 0-100 are normalized to 0.0-1.0 logic.
    """
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float
    has_adhd: bool = False
    has_asd: bool = False

    def __post_init__(self):
        # Normalize inputs immediately
        self.openness = self._norm(self.openness)
        self.conscientiousness = self._norm(self.conscientiousness)
        self.extraversion = self._norm(self.extraversion)
        self.agreeableness = self._norm(self.agreeableness)
        self.neuroticism = self._norm(self.neuroticism)

    def _norm(self, val):
        if val > 1.0: return val / 100.0
        return val

@dataclass
class ShadowComponent:
    attachment_style: AttachmentStyle
    conflict_response: ConflictResponse
    regulation_method: RegulationMethod

@dataclass
class ErosComponent:
    accelerator: float
    brake: float
    context_dependency: ContextDependency
    erotic_tags: List[str]

@dataclass
class RelationalNeedsComponent:
    """
    SRME Model Logic.
    """
    raw_safety: float = 0.0
    raw_resource: float = 0.0
    raw_resonance: float = 0.0
    raw_expansion: float = 0.0
    
    adjusted_safety: float = field(init=False)
    adjusted_resource: float = field(init=False)
    adjusted_resonance: float = field(init=False)
    adjusted_expansion: float = field(init=False)

    def calculate_adjustments(self, psycho: PsychometricsComponent):
        """
        Основний алгоритм корекції.
        Він бере "що користувач хоче" (Raw) і коригує на "що йому біологічно треба" (Adjusted).
        """
        
        # --- 1. SAFETY (Безпека) ---
        n_weight = 0.65
        base_safety = self.raw_safety * (1.0 - n_weight)
        implicit_safety = psycho.neuroticism * n_weight
        
        if psycho.has_asd: 
            implicit_safety += 0.2
            
        self.adjusted_safety = min(base_safety + implicit_safety, 1.0)

        # --- 2. RESOURCE (Ресурс/Опора) ---
        dysfunction_penalty = (1.0 - psycho.conscientiousness)
        if psycho.has_adhd: 
            dysfunction_penalty += 0.25
            
        self.adjusted_resource = max(self.raw_resource, min(dysfunction_penalty, 1.0))

        # --- 3. RESONANCE (Резонанс) ---
        cognitive_floor = 0.0
        if psycho.openness > 0.75: 
            cognitive_floor = 0.8
            
        self.adjusted_resonance = max(self.raw_resonance, cognitive_floor)

        # --- 4. EXPANSION (Експансія/Новизна) ---
        expansion_driver = (psycho.extraversion + psycho.openness) / 2
        
        if psycho.has_adhd:
            expansion_driver += 0.15
            
        self.adjusted_expansion = (self.raw_expansion + expansion_driver) / 2