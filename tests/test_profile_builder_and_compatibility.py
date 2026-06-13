from src.enums import HollandCode
from src.question_bank import get_question_bank_registry, question_state_key
from src.services.compatibility import CompatibilityComparator
from src.services.profile_builder import build_user_profile_from_state


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


def test_compatibility_comparator_reports_strengths_and_tensions() -> None:
    registry = get_question_bank_registry()
    first = build_user_profile_from_state(_complete_state("simple", option_index=0), registry, name="A")
    second = build_user_profile_from_state(_complete_state("simple", option_index=2), registry, name="B")

    report = CompatibilityComparator.compare(first.user, second.user)

    assert 0.0 <= report.score <= 1.0
    assert report.strengths or report.tensions
    assert report.tensions
