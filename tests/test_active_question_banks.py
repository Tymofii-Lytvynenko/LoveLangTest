from src.question_bank import get_question_bank_registry
from src.services.question_bank_quality import QuestionBankQualityGate


def test_active_question_bank_sizes_are_intentional() -> None:
    registry = get_question_bank_registry()

    assert len(registry.get("needs").questions) == 24
    assert len(registry.get("shadow").questions) == 8
    assert len(registry.get("eros").questions) == 8


def test_active_question_banks_pass_local_quality_gates() -> None:
    registry = get_question_bank_registry()

    expected_counts = {
        "needs": 24,
        "shadow": 8,
        "eros": 8,
    }
    for module, expected_count in expected_counts.items():
        report = QuestionBankQualityGate.evaluate(
            registry.get(module),
            expected_question_count=expected_count,
            strict_content_checks=True,
        )

        assert report.passed, report.to_dict()
