from src.question_bank import load_question_bank
from src.services.scoring import QuestionnaireScorer
from src.enums import ContextDependency


def test_eros_normalization_preserves_distinct_high_scores() -> None:
    bank = load_question_bank("eros")

    medium_high = QuestionnaireScorer.build_eros_component(
        bank,
        {
            "eros_01": "opt_2",
            "eros_02": "opt_1",
            "eros_03": "opt_3",
        },
    )
    maximum = QuestionnaireScorer.build_eros_component(
        bank,
        {
            "eros_01": "opt_2",
            "eros_02": "opt_1",
            "eros_03": "opt_2",
        },
    )

    assert medium_high.accelerator < maximum.accelerator
    assert maximum.accelerator == 1.0


def test_eros_brake_maps_to_context_dependency() -> None:
    bank = load_question_bank("eros")
    component = QuestionnaireScorer.build_eros_component(
        bank,
        {
            "eros_01": "opt_1",
            "eros_02": "opt_3",
            "eros_03": "opt_1",
        },
    )

    assert 0.0 <= component.brake <= 1.0
    assert component.context_dependency == ContextDependency.HIGH
