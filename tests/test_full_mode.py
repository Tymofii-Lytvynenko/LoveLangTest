from __future__ import annotations

import pytest
from src.profile import UserProfile
from src.question_bank import get_question_bank_registry, question_state_key
from src.services.profile_builder import build_user_profile_from_state
from src.services.compatibility import CompatibilityComparator
from src.services.adjustment import NeedsAdjustmentService
from src.domain.psychometrics import PsychometricsComponent
from src.domain.needs import RelationalNeedsComponent
from src.domain.eros import ErosComponent
from src.domain.shadow import ShadowComponent
from src.domain.professional import ProfessionalComponent
from src.enums import HollandCode, AttachmentStyle


def _complete_state_full(option_index: int = 0) -> dict[str, object]:
    registry = get_question_bank_registry()
    state: dict[str, object] = {
        "questionnaire_mode": "full",
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
    for module in ("needs", "shadow", "eros", "provision", "calibration"):
        bank = registry.get(module).for_mode("full")
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


def test_full_mode_question_counts() -> None:
    registry = get_question_bank_registry()
    assert len(registry.get("needs").for_mode("full").questions) == 40
    assert len(registry.get("shadow").for_mode("full").questions) == 16
    assert len(registry.get("eros").for_mode("full").questions) == 16
    assert len(registry.get("provision").for_mode("full").questions) == 20
    assert len(registry.get("calibration").for_mode("full").questions) == 8


def test_full_mode_profile_builder() -> None:
    registry = get_question_bank_registry()
    state = _complete_state_full(option_index=0)
    built = build_user_profile_from_state(state, registry, name="Test User")
    assert built.is_complete
    assert built.mode == "full"
    user = built.user
    assert user is not None
    assert user.provision is not None
    assert "safety_provision" in user.provision
    assert "resource_provision" in user.provision
    assert "resonance_provision" in user.provision
    assert "expansion_provision" in user.provision
    assert isinstance(user.calibration_notes, list)


def test_ocean_adjustment_confidence() -> None:
    psycho = PsychometricsComponent.from_high_level_scores(50, 50, 50, 50, 50)
    raw = RelationalNeedsComponent(
        raw_safety=0.9,
        raw_resource=0.5,
        raw_resonance=0.5,
        raw_expansion=0.5,
    )
    adjusted = NeedsAdjustmentService.adjust_needs(raw, psycho)
    assert adjusted.adjusted_safety == pytest.approx(0.78, abs=0.02)
    assert adjusted.confidence_safety == "Mixed"


def test_needs_priority_contradiction_lowers_confidence() -> None:
    psycho = PsychometricsComponent.from_high_level_scores(50, 50, 50, 50, 50)
    raw = RelationalNeedsComponent(
        raw_safety=0.8,
        priority_safety=-2.0,
    )
    adjusted = NeedsAdjustmentService.adjust_needs(raw, psycho)
    assert adjusted.confidence_safety == "Low"


def test_compatibility_uses_actual_provision_scores() -> None:
    first = UserProfile(
        name="A",
        psychometrics=PsychometricsComponent(),
        shadow=ShadowComponent(),
        eros=ErosComponent(),
        needs=RelationalNeedsComponent(),
        professional=ProfessionalComponent(),
        provision={
            "safety_provision": 0.8,
            "resource_provision": 0.9,
            "resonance_provision": 0.7,
            "expansion_provision": 0.65,
        }
    )
    second = UserProfile(
        name="B",
        psychometrics=PsychometricsComponent(),
        shadow=ShadowComponent(),
        eros=ErosComponent(),
        needs=RelationalNeedsComponent(adjusted_safety=0.8, adjusted_resource=0.8),
        professional=ProfessionalComponent(),
        provision={
            "safety_provision": 0.2,
            "resource_provision": 0.3,
            "resonance_provision": 0.4,
            "expansion_provision": 0.5,
        }
    )

    report = CompatibilityComparator.compare(second, first)
    assert any("покриття" in item.title.lower() for item in report.strengths)

    first.needs.adjusted_safety = 0.8
    first.needs.adjusted_resource = 0.8
    report2 = CompatibilityComparator.compare(first, second)
    assert any("дефіцит" in item.title.lower() for item in report2.tensions)


def test_critical_discussion_flags() -> None:
    first = UserProfile(
        name="A",
        psychometrics=PsychometricsComponent.from_high_level_scores(10, 10, 80, 10, 10),
        shadow=ShadowComponent(),
        eros=ErosComponent(accelerator=0.7),
        needs=RelationalNeedsComponent(adjusted_expansion=0.8),
        professional=ProfessionalComponent(),
    )
    second = UserProfile(
        name="B",
        psychometrics=PsychometricsComponent.from_high_level_scores(90, 90, 10, 90, 90),
        shadow=ShadowComponent(),
        eros=ErosComponent(brake=0.8),
        needs=RelationalNeedsComponent(adjusted_safety=0.8),
        professional=ProfessionalComponent(),
    )

    report = CompatibilityComparator.compare(first, second)
    titles = [item.title for item in report.tensions]
    assert "Конфлікт Експансії та Безпеки" in titles
    assert "Цикл тиску та сексуального гальмування" in titles
