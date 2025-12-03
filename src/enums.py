from enum import Enum

class AttachmentStyle(Enum):
    SECURE = "Надійний (Secure)"
    ANXIOUS = "Тривожний (Anxious-Preoccupied)"
    AVOIDANT = "Уникаючий (Dismissive-Avoidant)"
    DISORGANIZED = "Дезорганізований (Fearful-Avoidant)"

class ConflictResponse(Enum):
    FIGHT = "Напад (Fight) — Критика, агресія"
    FLIGHT = "Втеча (Flight) — Дистанціювання"
    FREEZE = "Завмирання (Freeze) — Shutdown, мовчання"
    FAWN = "Пристосування (Fawn) — Поступливість заради миру"

class RegulationMethod(Enum):
    CO_REGULATION = "Ко-регуляція (Заспокоєння через контакт з іншим)"
    AUTO_REGULATION = "Авто-регуляція (Заспокоєння на самоті)"

class ContextDependency(Enum):
    HIGH = "Висока (Потрібні специфічні умови, безпека, відсутність стресу)"
    LOW = "Низька (Збудження спонтанне, стрес не заважає)"

class HollandCode(Enum):
    REALISTIC = "R - Практик (Речі, інструменти, техніка)"
    INVESTIGATIVE = "I - Дослідник (Ідеї, аналіз, наука)"
    ARTISTIC = "A - Митець (Креатив, хаос, емоції)"
    SOCIAL = "S - Соціальний (Люди, допомога, навчання)"
    ENTERPRISING = "E - Підприємець (Лідерство, вплив, ризик)"
    CONVENTIONAL = "C - Системний (Дані, порядок, алгоритми)"