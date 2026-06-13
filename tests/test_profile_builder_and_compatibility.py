from src.domain.eros import ErosComponent
from src.domain.needs import RelationalNeedsComponent
from src.domain.professional import ProfessionalComponent
from src.domain.psychometrics import PsychometricsComponent
from src.domain.shadow import ShadowComponent
from src.enums import HollandCode
from src.profile import UserProfile
from src.question_bank import get_question_bank_registry, question_state_key
from src.services.compatibility import CompatibilityComparator
from src.services.profile_builder import build_user_profile_from_state, normalize_questionnaire_mode


def _complete_state(mode: str, option_index: int = 0) -> dict[str, object]:
    registry = get_question_bank_registry()
    state: dict[str, object] = {
        "questionnaire_mode": mode,
        "psycho_o": 70,
        "psycho_c": 70,
        "psycho_e": 55,
        "psycho_a": 65,
        "psycho_n": 35,
        "psycho_adhd": False,
        "psycho_asd": False,
        "prof_primary": HollandCode.SOCIAL.name,
        "prof_secondary": HollandCode.INVESTIGATIVE.name,
        "prof_tertiary": HollandCode.ARTISTIC.name,
        "prof_centrality": 0.45,
    }
    for module in ("needs", "shadow", "eros"):
        bank = registry.get(module).for_mode(mode)
        for question in bank.questions:
            if question.is_best_worst:
                best_idx = option_index % len(question.options)
                worst_idx = (option_index + 1) % len(question.options)
                state[question_state_key(module, question.id, "best")] = question.options[best_idx].id
                state[question_state_key(module, question.id, "worst")] = question.options[worst_idx].id
            else:
                option = question.options[min(option_index, len(question.options) - 1)]
                state[question_state_key(module, question.id)] = option.id
    return state


def test_profile_builder_uses_questionnaire_mode_to_require_active_subset() -> None:
    registry = get_question_bank_registry()

    simple_profile = build_user_profile_from_state(_complete_state("simple"), registry)
    extended_profile = build_user_profile_from_state(_complete_state("extended"), registry)

    assert simple_profile.is_complete
    assert simple_profile.mode == "simple"
    assert extended_profile.is_complete
    assert extended_profile.mode == "extended"


def test_normalize_questionnaire_mode_defaults_to_full() -> None:
    assert normalize_questionnaire_mode(None) == "full"
    assert normalize_questionnaire_mode("unsupported") == "full"


def test_compatibility_comparator_reports_strengths_and_tensions() -> None:
    registry = get_question_bank_registry()
    first = build_user_profile_from_state(_complete_state("simple", option_index=0), registry, name="A")
    second = build_user_profile_from_state(_complete_state("simple", option_index=2), registry, name="B")

    report = CompatibilityComparator.compare(first.user, second.user)

    assert 0.0 <= report.score <= 1.0
    assert report.strengths or report.tensions
    assert report.tensions


def _neutral_profile(shadow: ShadowComponent) -> UserProfile:
    return UserProfile(
        name="Neutral",
        psychometrics=PsychometricsComponent.from_high_level_scores(50, 50, 50, 50, 50),
        shadow=shadow,
        eros=ErosComponent(),
        needs=RelationalNeedsComponent(
            raw_safety=0.5,
            raw_resource=0.5,
            raw_resonance=0.5,
            raw_expansion=0.5,
            adjusted_safety=0.5,
            adjusted_resource=0.5,
            adjusted_resonance=0.5,
            adjusted_expansion=0.5,
        ),
        professional=ProfessionalComponent(),
    )


def test_compatibility_comparator_treats_mixed_attachment_as_low_confidence() -> None:
    first_shadow = ShadowComponent()
    first_shadow.calculate_from_quiz((0.34, 0.30, 0.32, 0.04))
    second_shadow = ShadowComponent()
    second_shadow.calculate_from_quiz((0.0, 1.0, 0.0, 0.0))

    report = CompatibilityComparator.compare(_neutral_profile(first_shadow), _neutral_profile(second_shadow))

    assert all(item.title != "Тривожно-уникаюча петля" for item in report.tensions)
    assert all(item.title != "Схожий стабільний стиль прив'язаності" for item in report.strengths)
    assert any("обережної інтерпретації" in item.title.lower() for item in report.notes)


def test_compatibility_comparator_still_detects_clear_anxious_avoidant_loop() -> None:
    first_shadow = ShadowComponent()
    first_shadow.calculate_from_quiz((0.0, 1.0, 0.0, 0.0))
    second_shadow = ShadowComponent()
    second_shadow.calculate_from_quiz((0.0, 0.0, 1.0, 0.0))

    report = CompatibilityComparator.compare(_neutral_profile(first_shadow), _neutral_profile(second_shadow))

    assert any(item.title == "Тривожно-уникаюча петля" for item in report.tensions)
