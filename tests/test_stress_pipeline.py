from __future__ import annotations

from random import Random
from statistics import mean

from src.domain.professional import ProfessionalComponent
from src.domain.psychometrics import PsychometricsComponent
from src.enums import HollandCode
from src.profile import UserProfile
from src.question_bank import QuestionBank, get_question_bank_registry
from src.services.adjustment import NeedsAdjustmentService
from src.services.reporting import ReportGenerator
from src.services.scoring import QuestionnaireScorer


def _cycled_responses(bank: QuestionBank) -> dict[str, str]:
    return {
        question.id: question.options[index % len(question.options)].id
        for index, question in enumerate(bank.questions)
    }


def _random_responses(bank: QuestionBank, rng: Random) -> dict[str, str]:
    return {
        question.id: rng.choice(question.options).id
        for question in bank.questions
    }


def _build_user(needs_responses: dict[str, str], shadow_responses: dict[str, str], eros_responses: dict[str, str]) -> UserProfile:
    registry = get_question_bank_registry()
    psycho = PsychometricsComponent.from_high_level_scores(50, 50, 50, 50, 50)
    professional = ProfessionalComponent(
        primary_type=HollandCode.REALISTIC,
        secondary_type=HollandCode.INVESTIGATIVE,
        tertiary_type=HollandCode.ARTISTIC,
        career_centrality=0.5,
    )

    needs_bank = registry.get("needs").for_mode("extended")
    shadow_bank = registry.get("shadow").for_mode("extended")
    eros_bank = registry.get("eros").for_mode("extended")

    needs = NeedsAdjustmentService.adjust_needs(
        QuestionnaireScorer.build_needs_component(needs_bank, needs_responses),
        psycho,
    )
    shadow = QuestionnaireScorer.build_shadow_component(shadow_bank, shadow_responses)
    eros = QuestionnaireScorer.build_eros_component(eros_bank, eros_responses)
    return UserProfile(
        name="Stress user",
        psychometrics=psycho,
        shadow=shadow,
        eros=eros,
        needs=needs,
        professional=professional,
    )


def test_balanced_synthetic_profile_stays_midrange() -> None:
    registry = get_question_bank_registry()
    needs_bank = registry.get("needs").for_mode("extended")
    shadow_bank = registry.get("shadow").for_mode("extended")
    eros_bank = registry.get("eros").for_mode("extended")

    user = _build_user(
        _cycled_responses(needs_bank),
        _cycled_responses(shadow_bank),
        _cycled_responses(eros_bank),
    )

    report = ReportGenerator.generate_manual(user)

    assert all(0.25 <= value <= 0.75 for value in report["scores"].values())
    assert all(0.4 <= value <= 0.75 for value in report["provision_scores"].values())
    assert "зміш" in report["shadow_warning"].lower()


def test_random_stress_profiles_remain_bounded_and_centered() -> None:
    registry = get_question_bank_registry()
    needs_bank = registry.get("needs").for_mode("extended")
    shadow_bank = registry.get("shadow").for_mode("extended")
    eros_bank = registry.get("eros").for_mode("extended")
    rng = Random(20260613)

    score_samples: list[tuple[float, float, float, float]] = []
    provision_samples: list[tuple[float, float, float, float]] = []

    for _ in range(30):
        user = _build_user(
            _random_responses(needs_bank, rng),
            _random_responses(shadow_bank, rng),
            _random_responses(eros_bank, rng),
        )
        report = ReportGenerator.generate_manual(user)

        assert all(0.0 <= value <= 1.0 for value in report["scores"].values())
        assert all(0.0 <= value <= 1.0 for value in report["provision_scores"].values())

        score_samples.append(tuple(report["scores"].values()))
        provision_samples.append(tuple(report["provision_scores"].values()))

    score_means = [mean(sample[index] for sample in score_samples) for index in range(4)]
    provision_means = [mean(sample[index] for sample in provision_samples) for index in range(4)]

    assert all(0.35 <= value <= 0.65 for value in score_means)
    assert all(0.4 <= value <= 0.7 for value in provision_means)
