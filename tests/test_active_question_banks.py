from src.question_bank import get_question_bank_registry
from src.services.question_bank_quality import QuestionBankQualityGate


def test_active_question_bank_sizes_are_intentional() -> None:
    registry = get_question_bank_registry()

    assert len(registry.get("needs").for_mode("simple").questions) == 24
    assert len(registry.get("shadow").for_mode("simple").questions) == 8
    assert len(registry.get("eros").for_mode("simple").questions) == 8
    assert len(registry.get("needs").for_mode("extended").questions) == 40
    assert len(registry.get("shadow").for_mode("extended").questions) == 16
    assert len(registry.get("eros").for_mode("extended").questions) == 16


def test_active_question_banks_pass_local_quality_gates() -> None:
    registry = get_question_bank_registry()

    expected_counts = {
        "needs": 40,
        "shadow": 16,
        "eros": 16,
    }
    for module, expected_count in expected_counts.items():
        report = QuestionBankQualityGate.evaluate(
            registry.get(module),
            expected_question_count=expected_count,
            strict_content_checks=True,
        )

        assert report.passed, report.to_dict()
