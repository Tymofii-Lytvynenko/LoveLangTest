from dataclasses import dataclass, field
from typing import List
from .enums import AttachmentStyle, ConflictResponse, RegulationMethod, ContextDependency, HollandCode

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
    # --- ВИПРАВЛЕНО: Додані значення за замовчуванням ---
    attachment_style: AttachmentStyle = AttachmentStyle.SECURE
    conflict_response: ConflictResponse = ConflictResponse.FLIGHT
    regulation_method: RegulationMethod = RegulationMethod.AUTO_REGULATION
    
    # Поля для результатів тесту
    secure_score: float = 0.0
    anxious_score: float = 0.0
    avoidant_score: float = 0.0

    def calculate_from_quiz(self, scores: tuple):
        """
        scores: (sum_secure, sum_anxious, sum_avoidant)
        """
        self.secure_score, self.anxious_score, self.avoidant_score = scores
        
        mx = max(scores)
        # Проста логіка визначення типу за максимумом балів
        if mx == self.anxious_score:
            self.attachment_style = AttachmentStyle.ANXIOUS
            self.conflict_response = ConflictResponse.FIGHT
            self.regulation_method = RegulationMethod.CO_REGULATION
        elif mx == self.avoidant_score:
            self.attachment_style = AttachmentStyle.AVOIDANT
            self.conflict_response = ConflictResponse.FLIGHT
            self.regulation_method = RegulationMethod.AUTO_REGULATION
        else:
            self.attachment_style = AttachmentStyle.SECURE
            self.conflict_response = ConflictResponse.FAWN
            self.regulation_method = RegulationMethod.CO_REGULATION

@dataclass
class ErosComponent:
    # --- ВИПРАВЛЕНО: Додані значення за замовчуванням ---
    accelerator: float = 0.5
    brake: float = 0.5
    context_dependency: ContextDependency = ContextDependency.LOW
    erotic_tags: List[str] = field(default_factory=list)

    def calculate_from_quiz(self, accel_score: float, brake_score: float):
        self.accelerator = min(max(accel_score, 0.0), 1.0)
        self.brake = min(max(brake_score, 0.0), 1.0)
        
        if self.brake > 0.6:
            self.context_dependency = ContextDependency.HIGH
        else:
            self.context_dependency = ContextDependency.LOW

@dataclass
class RelationalNeedsComponent:
    raw_safety: float = 0.0
    raw_resource: float = 0.0
    raw_resonance: float = 0.0
    raw_expansion: float = 0.0
    
    adjusted_safety: float = field(init=False)
    adjusted_resource: float = field(init=False)
    adjusted_resonance: float = field(init=False)
    adjusted_expansion: float = field(init=False)

    def calculate_adjustments(self, psycho: PsychometricsComponent):
        # 1. SAFETY
        n_weight = 0.65
        base_safety = self.raw_safety * (1.0 - n_weight)
        implicit_safety = psycho.neuroticism * n_weight
        if psycho.has_asd: implicit_safety += 0.2
        self.adjusted_safety = min(base_safety + implicit_safety, 1.0)

        # 2. RESOURCE
        dysfunction_penalty = (1.0 - psycho.conscientiousness)
        if psycho.has_adhd: dysfunction_penalty += 0.25
        self.adjusted_resource = max(self.raw_resource, min(dysfunction_penalty, 1.0))

        # 3. RESONANCE
        cognitive_floor = 0.0
        if psycho.openness > 0.75: cognitive_floor = 0.8
        self.adjusted_resonance = max(self.raw_resonance, cognitive_floor)

        # 4. EXPANSION
        expansion_driver = (psycho.extraversion + psycho.openness) / 2
        if psycho.has_adhd: expansion_driver += 0.15
        self.adjusted_expansion = (self.raw_expansion + expansion_driver) / 2

@dataclass
class ProfessionalComponent:
    primary_type: HollandCode = HollandCode.INVESTIGATIVE
    secondary_type: HollandCode = HollandCode.ARTISTIC
    tertiary_type: HollandCode = HollandCode.REALISTIC # <--- Додаємо третій тип
    career_centrality: float = 0.5
    
    def get_interaction_style(self) -> str:
        style_map = {
            HollandCode.REALISTIC: "Дія замість слів. 'Я полагодив кран' = 'Я тебе люблю'.",
            HollandCode.INVESTIGATIVE: "Аналіз замість емоцій. Потреба в інтелектуальному спарингу.",
            HollandCode.ARTISTIC: "Емоційні гойдалки та спонтанність. Рутина вбиває.",
            HollandCode.SOCIAL: "Гіпер-комунікація. Потреба постійного обговорення почуттів.",
            HollandCode.ENTERPRISING: "Стосунки як проєкт. Стратегічне планування.",
            HollandCode.CONVENTIONAL: "Ритуали та стабільність. Домовленості — це святе."
        }
        # Можна повертати комбінований опис, але поки залишимо за домінантою
        return style_map.get(self.primary_type, "")