from src.question_bank import load_question_bank_from_path
from src.services.question_bank_quality import QuestionBankQualityGate


def test_generated_bank_contract(generated_bank_path, expected_question_count) -> None:
    bank = load_question_bank_from_path(generated_bank_path)

    report = QuestionBankQualityGate.evaluate(
        bank,
        expected_question_count=expected_question_count,
        strict_generated_bank=True,
    )

    assert report.passed, "\n".join(report.errors)
