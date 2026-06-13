from src.question_bank import load_question_bank
from src.services.scoring import QuestionnaireScorer
from src.enums import ContextDependency


def _responses_for_vector_extreme(bank, vector_index: int, *, highest: bool) -> dict[str, str]:
    responses = {}
    for question in bank.questions:
        selector = max if highest else min
        option = selector(question.options, key=lambda item: item.vector[vector_index])
        responses[question.id] = option.id
    return responses


def test_eros_normalization_preserves_distinct_high_scores() -> None:
    bank = load_question_bank("eros")

    medium_high = QuestionnaireScorer.build_eros_component(
        bank,
        {question.id: "opt_2" for question in bank.questions},
    )
    maximum = QuestionnaireScorer.build_eros_component(
        bank,
        _responses_for_vector_extreme(bank, 0, highest=True),
    )

    assert medium_high.accelerator < maximum.accelerator
    assert maximum.accelerator == 1.0


def test_eros_brake_maps_to_context_dependency() -> None:
    bank = load_question_bank("eros")
    component = QuestionnaireScorer.build_eros_component(
        bank,
        _responses_for_vector_extreme(bank, 1, highest=True),
    )

    assert 0.0 <= component.brake <= 1.0
    assert component.context_dependency == ContextDependency.HIGH
