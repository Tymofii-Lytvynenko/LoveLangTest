from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CoverageCluster:
    name: str
    keywords: tuple[str, ...]


@dataclass(frozen=True)
class QuestionBankBlueprint:
    module: str
    vector_labels: tuple[str, ...]
    display_vector_labels: tuple[str, ...]
    scientific_basis: tuple[str, ...]
    audience_notes: tuple[str, ...]
    coverage_clusters: tuple[CoverageCluster, ...]
    banned_terms: tuple[str, ...]
    min_question_count: int
    min_options_per_question: int
    max_options_per_question: int
    required_description_ratio: float
    max_vector_magnitude: float = 1.0
    require_negative_weights: bool = False
    require_mixed_direction_vectors: bool = False


_COMMON_BANNED_TERMS = (
    "астролог",
    "астрологі",
    "зодіак",
    "гороскоп",
    "соулмейт",
    "soulmate",
    "twin flame",
    "близнюкове полум'я",
    "альфа-самець",
    "бета-самець",
    "жіноча енергія",
    "чоловіча енергія",
    "доля",
    "карма",
    "карміч",
    "приречен",
    "ідеальн",
    "єдино правильн",
)


QUESTION_BANK_BLUEPRINTS: dict[str, QuestionBankBlueprint] = {
    "needs": QuestionBankBlueprint(
        module="needs",
        vector_labels=("safety", "resource", "resonance", "expansion"),
        display_vector_labels=("Безпека", "Ресурс", "Резонанс", "Експансія"),
        scientific_basis=(
            "Attachment Theory",
            "Polyvagal Theory",
            "Self-Determination Theory",
            "Self-Expansion Model",
            "Social Exchange Theory",
        ),
        audience_notes=(
            "Treat ADHD/ASD/AuDHD as optional context, not diagnosis.",
            "Use literal scenarios and low-inference wording.",
            "Separate attachment threat from sensory overload or executive friction.",
        ),
        coverage_clusters=(
            CoverageCluster("safety", ("безпек", "передбач", "тиша", "крик", "перевантаж", "сенсор")),
            CoverageCluster("resource", ("план", "побут", "бюджет", "задач", "нагад", "логіст")),
            CoverageCluster("resonance", ("валідац", "слух", "обговор", "емоці", "сенс", "repair")),
            CoverageCluster("expansion", ("новизн", "спонтан", "експер", "подорож", "інтерес", "драйв")),
        ),
        banned_terms=_COMMON_BANNED_TERMS,
        min_question_count=8,
        min_options_per_question=4,
        max_options_per_question=4,
        required_description_ratio=1.0,
        require_negative_weights=False,
        require_mixed_direction_vectors=False,
    ),
    "shadow": QuestionBankBlueprint(
        module="shadow",
        vector_labels=("secure", "anxious", "avoidant", "disorganized"),
        display_vector_labels=("Надійний", "Тривожний", "Уникаючий", "Дезорганізований"),
        scientific_basis=(
            "Attachment Theory",
            "Gottman Conflict Research",
        ),
        audience_notes=(
            "Separate shutdown, burnout, sensory overload, and delayed processing from attachment by wording the scenario carefully.",
            "Keep options behavioral and non-clinical.",
        ),
        coverage_clusters=(
            CoverageCluster("rupture", ("свар", "конфлікт", "repair", "віднов", "після")),
            CoverageCluster("distance", ("віддал", "простір", "самот", "зник", "контакт")),
            CoverageCluster("dependence", ("потріб", "опора", "довір", "близьк", "покин")),
        ),
        banned_terms=_COMMON_BANNED_TERMS + ("токсич", "маніпулят", "red flag"),
        min_question_count=4,
        min_options_per_question=4,
        max_options_per_question=4,
        required_description_ratio=1.0,
    ),
    "eros": QuestionBankBlueprint(
        module="eros",
        vector_labels=("accelerator", "brake"),
        display_vector_labels=("Акселератор", "Гальмо"),
        scientific_basis=(
            "Dual Control Model",
        ),
        audience_notes=(
            "Do not moralize libido or desire.",
            "Include context, inhibition, sensory load, stress, and recovery.",
            "Do not assume spontaneity is universally healthier than responsive desire.",
        ),
        coverage_clusters=(
            CoverageCluster("accelerator", ("збуджен", "потяг", "флірт", "тригер", "бажан")),
            CoverageCluster("brake", ("стрес", "гальм", "контекст", "відволік", "сенсор", "втом")),
            CoverageCluster("recovery", ("віднов", "перепоч", "після", "тиша", "час")),
        ),
        banned_terms=_COMMON_BANNED_TERMS + ("нормальн", "правильн"),
        min_question_count=4,
        min_options_per_question=3,
        max_options_per_question=4,
        required_description_ratio=1.0,
        require_mixed_direction_vectors=True,
    ),
}


def get_question_bank_blueprint(module: str) -> QuestionBankBlueprint | None:
    return QUESTION_BANK_BLUEPRINTS.get(module)
