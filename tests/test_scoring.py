from src.domain.psychometrics import PsychometricsComponent
from src.question_bank import load_question_bank_from_path
from src.services.adjustment import NeedsAdjustmentService
from src.services.scoring import QuestionnaireScorer
from conftest import write_json


def _build_needs_bank(question_count: int) -> dict:
    questions = []
    for index in range(question_count):
        questions.append(
            {
                "id": f"q{index + 1}",
                "question": f"Question {index + 1}",
                "description": "",
                "options": [
                    {"id": "opt_1", "text": "Low safety", "vector": [-1.0, 0.0, 0.0, 0.0]},
                    {"id": "opt_2", "text": "High safety", "vector": [1.0, 0.0, 0.0, 0.0]},
                ],
            }
        )
    return {
        "metadata": {
            "bank_id": "test-needs",
            "version": "1.0.0",
            "module": "needs",
            "authoring_instructions": "Test instructions",
            "vector_labels": ["safety", "resource", "resonance", "expansion"],
        },
        "questions": questions,
    }


def test_normalized_scores_do_not_depend_on_question_count(tmp_path) -> None:
    short_bank = load_question_bank_from_path(write_json(tmp_path, "short.json", _build_needs_bank(2)))
    long_bank = load_question_bank_from_path(write_json(tmp_path, "long.json", _build_needs_bank(4)))

    short_score = QuestionnaireScorer.score(short_bank, {"q1": "opt_2", "q2": "opt_1"})
    long_score = QuestionnaireScorer.score(
        long_bank,
        {"q1": "opt_2", "q2": "opt_2", "q3": "opt_1", "q4": "opt_1"},
    )

    assert short_score.normalized[0] == 0.5
    assert long_score.normalized[0] == 0.5


def test_negative_weights_lower_position_within_bounds(tmp_path) -> None:
    bank = load_question_bank_from_path(write_json(tmp_path, "needs.json", _build_needs_bank(2)))

    low_score = QuestionnaireScorer.score(bank, {"q1": "opt_1", "q2": "opt_1"})
    mixed_score = QuestionnaireScorer.score(bank, {"q1": "opt_1", "q2": "opt_2"})

    assert low_score.normalized[0] == 0.0
    assert 0.0 < mixed_score.normalized[0] < 1.0


def test_adjustment_does_not_saturate_from_bank_size(tmp_path) -> None:
    bank = load_question_bank_from_path(write_json(tmp_path, "needs.json", _build_needs_bank(4)))
    raw_needs = QuestionnaireScorer.build_needs_component(
        bank,
        {"q1": "opt_2", "q2": "opt_1", "q3": "opt_2", "q4": "opt_1"},
    )
    psycho = PsychometricsComponent.from_high_level_scores(50, 50, 50, 50, 50)

    adjusted = NeedsAdjustmentService.adjust_needs(raw_needs, psycho)

    assert adjusted.adjusted_safety < 1.0
    assert 0.0 <= adjusted.adjusted_safety <= 1.0
