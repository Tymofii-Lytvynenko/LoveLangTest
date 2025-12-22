from dataclasses import dataclass, field

@dataclass
class NeuroticismDomain:
    """Загроза та Емоційна стабільність"""
    anxiety: float = 0.5          # N1: Тривожність
    hostility: float = 0.5        # N2: Ворожість/Гнів
    depression: float = 0.5       # N3: Депресивність
    self_consciousness: float = 0.5 # N4: Сором'язливість
    impulsiveness: float = 0.5    # N5: Імпульсивність
    vulnerability: float = 0.5    # N6: Вразливість до стресу

    @property
    def average(self) -> float:
        return (self.anxiety + self.hostility + self.depression + 
                self.self_consciousness + self.impulsiveness + self.vulnerability) / 6

@dataclass
class ExtraversionDomain:
    """Енергія та Соціальна взаємодія"""
    warmth: float = 0.5           # E1: Теплота
    gregariousness: float = 0.5   # E2: Стадність
    assertiveness: float = 0.5    # E3: Асертивність
    activity: float = 0.5         # E4: Активність
    excitement_seeking: float = 0.5 # E5: Пошук вражень
    positive_emotions: float = 0.5  # E6: Позитивні емоції

    @property
    def average(self) -> float:
        return (self.warmth + self.gregariousness + self.assertiveness + 
                self.activity + self.excitement_seeking + self.positive_emotions) / 6

@dataclass
class OpennessDomain:
    """Когнітивний стиль"""
    fantasy: float = 0.5          # O1: Уява
    aesthetics: float = 0.5       # O2: Естетика
    feelings: float = 0.5         # O3: Почуття
    actions: float = 0.5          # O4: Дії (готовність до нового)
    ideas: float = 0.5            # O5: Ідеї (інтелектуальна допитливість)
    values: float = 0.5           # O6: Цінності (лібералізм)

    @property
    def average(self) -> float:
        return sum([self.fantasy, self.aesthetics, self.feelings, 
                    self.actions, self.ideas, self.values]) / 6

@dataclass
class AgreeablenessDomain:
    """Соціальний інтерфейс"""
    trust: float = 0.5            # A1: Довіра
    straightforwardness: float = 0.5 # A2: Прямолінійність
    altruism: float = 0.5         # A3: Альтруїзм
    compliance: float = 0.5       # A4: Поступливість
    modesty: float = 0.5          # A5: Скромність
    tender_mindedness: float = 0.5 # A6: Чуйність

    @property
    def average(self) -> float:
        return sum([self.trust, self.straightforwardness, self.altruism,
                    self.compliance, self.modesty, self.tender_mindedness]) / 6

@dataclass
class ConscientiousnessDomain:
    """Виконавча система"""
    competence: float = 0.5       # C1: Компетентність
    order: float = 0.5            # C2: Порядок
    dutifulness: float = 0.5      # C3: Почуття обов'язку
    achievement: float = 0.5      # C4: Прагнення досягнень
    self_discipline: float = 0.5  # C5: Самодисципліна
    deliberation: float = 0.5     # C6: Обережність

    @property
    def average(self) -> float:
        return sum([self.competence, self.order, self.dutifulness,
                    self.achievement, self.self_discipline, self.deliberation]) / 6

@dataclass
class PsychometricsComponent:
    """Hardware Layer: Composite Root"""
    neuroticism: NeuroticismDomain = field(default_factory=NeuroticismDomain)
    extraversion: ExtraversionDomain = field(default_factory=ExtraversionDomain)
    openness: OpennessDomain = field(default_factory=OpennessDomain)
    agreeableness: AgreeablenessDomain = field(default_factory=AgreeablenessDomain)
    conscientiousness: ConscientiousnessDomain = field(default_factory=ConscientiousnessDomain)
    
    # Global modifiers
    has_adhd: bool = False
    has_asd: bool = False

    @classmethod
    def from_high_level_scores(cls, o: float, c: float, e: float, a: float, n: float, adhd=False, asd=False):
        """Фабрика для створення з 5 загальних цифр (для сумісності зі старим UI)."""
        # Нормалізація (якщо 0-100 -> 0-1)
        o, c, e, a, n = [x/100.0 if x > 1.0 else x for x in [o,c,e,a,n]]
        
        return cls(
            neuroticism=NeuroticismDomain(*[n]*6),
            extraversion=ExtraversionDomain(*[e]*6),
            openness=OpennessDomain(*[o]*6),
            agreeableness=AgreeablenessDomain(*[a]*6),
            conscientiousness=ConscientiousnessDomain(*[c]*6),
            has_adhd=adhd,
            has_asd=asd
        )