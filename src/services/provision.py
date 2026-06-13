from dataclasses import dataclass
from src.domain.psychometrics import PsychometricsComponent
from src.domain.professional import ProfessionalComponent
from src.enums import HollandCode
from src.services.neurodivergence import NeurodivergenceService

@dataclass
class ProvisionProfile:
    safety_score: float      
    resource_score: float    
    resonance_score: float   
    expansion_score: float   

class ProvisionService:
    @staticmethod
    def analyze(psycho: PsychometricsComponent, prof: ProfessionalComponent) -> ProvisionProfile:
        return ProvisionProfile(
            safety_score=ProvisionService._calc_safety(psycho, prof),
            resource_score=ProvisionService._calc_resource(psycho, prof),
            resonance_score=ProvisionService._calc_resonance(psycho, prof),
            expansion_score=ProvisionService._calc_expansion(psycho, prof)
        )

    @staticmethod
    def _calc_safety(p: PsychometricsComponent, prof: ProfessionalComponent) -> float:
        # Safety = Emotional Stability (Low Neuroticism avg) + Reliability (C: Dutifulness)
        base = (1.0 - p.neuroticism.average) * 0.6 + p.conscientiousness.dutifulness * 0.4
        
        bonus = 0.0
        if prof.primary_type in [HollandCode.CONVENTIONAL, HollandCode.REALISTIC]:
            bonus = 0.1
        return min(base + bonus, 1.0)

    @staticmethod
    def _calc_resource(p: PsychometricsComponent, prof: ProfessionalComponent) -> float:
        # Resource = C: Competence + C: Order
        base = (p.conscientiousness.competence + p.conscientiousness.order) / 2
        context = NeurodivergenceService.analyze(p)
        base -= context.resource_provision_penalty
        
        bonus = 0.0
        if prof.primary_type in [HollandCode.ENTERPRISING, HollandCode.REALISTIC, HollandCode.CONVENTIONAL]:
            bonus = 0.15
        elif prof.primary_type == HollandCode.ARTISTIC:
            bonus = -0.1
        return min(max(base + bonus, 0.0), 1.0)

    @staticmethod
    def _calc_resonance(p: PsychometricsComponent, prof: ProfessionalComponent) -> float:
        # Resonance = A: Tender-mindedness + O: Feelings
        base = (p.agreeableness.tender_mindedness + p.openness.feelings) / 2
        
        bonus = 0.0
        if prof.primary_type == HollandCode.SOCIAL: 
            bonus = 0.2
        elif prof.primary_type == HollandCode.INVESTIGATIVE: # Cognitive Resonance
            bonus = 0.1
        
        # Якщо низька A:Compliance (любить сперечатися), це знижує емоційну безпеку
        if p.agreeableness.compliance < 0.3:
            penalty = 0.15
            if p.has_asd and p.agreeableness.straightforwardness > 0.5:
                penalty = 0.08
            bonus -= penalty
            
        return min(max(base + bonus, 0.0), 1.0)

    @staticmethod
    def _calc_expansion(p: PsychometricsComponent, prof: ProfessionalComponent) -> float:
        # Expansion = E: Excitement Seeking + O: Actions
        base = (p.extraversion.excitement_seeking + p.openness.actions) / 2
        
        bonus = 0.0
        if prof.primary_type in [HollandCode.ARTISTIC, HollandCode.ENTERPRISING]:
            bonus = 0.15
        elif prof.primary_type == HollandCode.CONVENTIONAL:
            bonus = -0.1
            
        return min(max(base + bonus, 0.0), 1.0)
