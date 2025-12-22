"""
ANALYSIS LAYER: PROVISION CAPABILITY
====================================

Scientific Rationale:
---------------------
This module calculates what the user is *capable of providing* (Provision Capacity)
based on their stable traits (Big Five) and professional inclination (RIASEC).

Mapping Logic:
1. Safety Provision (The Rock):
   - Driven by Low Neuroticism (Stability) and High Conscientiousness (Reliability).
   - Conventional/Realistic types reinforce this via predictability.

2. Resource Provision (The Manager):
   - Driven by High Conscientiousness (Executive Function).
   - Reinforced by Enterprising (Resource accumulation) or Realistic (Practical skills).

3. Resonance Provision (The Soul):
   - Emotional Resonance: Driven by Agreeableness (Empathy) + Social type.
   - Cognitive Resonance: Driven by Openness (Intellect) + Investigative type.

4. Expansion Provision (The Catalyst):
   - Driven by Extraversion (Social Expansion) and Openness (Novelty).
   - Artistic/Enterprising types act as multipliers for chaos/growth.
"""

from dataclasses import dataclass
from .components import PsychometricsComponent, ProfessionalComponent
from .enums import HollandCode

@dataclass
class ProvisionProfile:
    safety_score: float      # Capacity to provide stability
    resource_score: float    # Capacity to provide pragmatic support
    resonance_score: float   # Capacity to provide emotional/cognitive depth
    expansion_score: float   # Capacity to provide novelty and growth

class ProvisionAnalyzer:
    @staticmethod
    def analyze(psycho: PsychometricsComponent, prof: ProfessionalComponent) -> ProvisionProfile:
        return ProvisionProfile(
            safety_score=ProvisionAnalyzer._calc_safety(psycho, prof),
            resource_score=ProvisionAnalyzer._calc_resource(psycho, prof),
            resonance_score=ProvisionAnalyzer._calc_resonance(psycho, prof),
            expansion_score=ProvisionAnalyzer._calc_expansion(psycho, prof)
        )

    @staticmethod
    def _calc_safety(p: PsychometricsComponent, prof: ProfessionalComponent) -> float:
        # Safety = Emotional Stability (Low N) + Reliability (High C)
        # Neuroticism is the strongest inverse predictor of relationship stability (Karney & Bradbury).
        base = (1.0 - p.neuroticism) * 0.6 + p.conscientiousness * 0.4
        
        # Bonus: Conventional/Realistic types value structure, increasing predictability.
        bonus = 0.0
        if prof.primary_type in [HollandCode.CONVENTIONAL, HollandCode.REALISTIC]:
            bonus = 0.1
            
        return min(base + bonus, 1.0)

    @staticmethod
    def _calc_resource(p: PsychometricsComponent, prof: ProfessionalComponent) -> float:
        # Resource = Executive Function (High C) + Pragmatic Orientation
        base = p.conscientiousness
        
        # Penalties for Neurodivergence (Executive Dysfunction risk)
        if p.has_adhd: base -= 0.15
        
        # Bonus: Career types that focus on resources/systems
        # Enterprising = Money/Status; Realistic = Tools/Repairs; Conventional = Logistics
        bonus = 0.0
        if prof.primary_type in [HollandCode.ENTERPRISING, HollandCode.REALISTIC, HollandCode.CONVENTIONAL]:
            bonus = 0.15
        elif prof.primary_type == HollandCode.ARTISTIC:
            # Artists often prioritize expression over resource management
            bonus = -0.1
            
        return min(max(base + bonus, 0.0), 1.0)

    @staticmethod
    def _calc_resonance(p: PsychometricsComponent, prof: ProfessionalComponent) -> float:
        # Resonance is split: Emotional (Agreeableness) + Cognitive (Openness)
        # We take the average capacity for connection.
        base = (p.agreeableness + p.openness) / 2
        
        # Bonus: Types specialized in human connection or ideas
        bonus = 0.0
        if prof.primary_type == HollandCode.SOCIAL: # The "Helper"
            bonus = 0.2
        elif prof.primary_type == HollandCode.INVESTIGATIVE: # The "Thinker" (Cognitive Resonance)
            bonus = 0.1
        elif prof.primary_type == HollandCode.ARTISTIC: # The "Feeler"
            bonus = 0.15
            
        # Penalty: Low Agreeableness (Competitive/Blunt) reduces safety of connection
        if p.agreeableness < 0.3:
            bonus -= 0.2
            
        return min(max(base + bonus, 0.0), 1.0)

    @staticmethod
    def _calc_expansion(p: PsychometricsComponent, prof: ProfessionalComponent) -> float:
        # Expansion = Energy (Extraversion) + Novelty (Openness)
        base = (p.extraversion + p.openness) / 2
        
        # Bonus: Types that drive change
        bonus = 0.0
        if prof.primary_type in [HollandCode.ARTISTIC, HollandCode.ENTERPRISING]:
            bonus = 0.15
        elif prof.primary_type == HollandCode.CONVENTIONAL:
            # Resistance to change
            bonus = -0.1
            
        return min(max(base + bonus, 0.0), 1.0)