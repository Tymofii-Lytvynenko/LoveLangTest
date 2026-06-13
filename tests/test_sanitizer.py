from src.enums import HollandCode
from src.question_bank import load_question_bank, question_state_key
from src.services.sanitizer import StateSanitizer


def test_sanitizer_revalidates_state_against_current_bank() -> None:
    bank = load_question_bank("needs")
    question = bank.questions[0]
    answer_key = question_state_key("needs", question.id)
    answer_value = question.options[0].id
    clean_state, removal_log = StateSanitizer.sanitize(
        incoming_state={
            answer_key: answer_value,
            "unknown_field": "bad",
        },
        incoming_bank_fingerprint="old-bank-fingerprint",
    )

    assert clean_state[answer_key] == answer_value
    assert any("іншій версії банку" in item for item in removal_log)
    assert any("невідоме поле" in item for item in removal_log)


def test_sanitizer_normalizes_enum_values_to_names() -> None:
    clean_state, removal_log = StateSanitizer.sanitize(
        incoming_state={"prof_primary": HollandCode.REALISTIC.value},
        incoming_bank_fingerprint=StateSanitizer.get_current_bank_fingerprint(),
    )

    assert not removal_log
    assert clean_state["prof_primary"] == HollandCode.REALISTIC.name


def test_sanitizer_keeps_bigfive_pdf_input_mode() -> None:
    clean_state, removal_log = StateSanitizer.sanitize(
        incoming_state={"psycho_input_mode": "pdf"},
        incoming_bank_fingerprint=StateSanitizer.get_current_bank_fingerprint(),
    )

    assert not removal_log
    assert clean_state["psycho_input_mode"] == "pdf"


def test_sanitizer_validates_best_worst_pairs() -> None:
    bank = load_question_bank("needs")
    priority_q = next(q for q in bank.questions if q.is_best_worst)
    best_key = question_state_key("needs", priority_q.id, "best")
    worst_key = question_state_key("needs", priority_q.id, "worst")

    # 1. Valid distinct choices
    incoming = {
        best_key: "opt_safety",
        worst_key: "opt_resource",
    }
    clean_state, removal_log = StateSanitizer.sanitize(incoming)
    assert not removal_log
    assert clean_state[best_key] == "opt_safety"
    assert clean_state[worst_key] == "opt_resource"

    # 2. Invalid duplicate choices (same option for best and worst)
    incoming_duplicate = {
        best_key: "opt_safety",
        worst_key: "opt_safety",
    }
    clean_state_dup, removal_log_dup = StateSanitizer.sanitize(incoming_duplicate)
    assert any("не можна обрати той самий варіант двічі" in item for item in removal_log_dup)
    assert best_key not in clean_state_dup
    assert worst_key not in clean_state_dup
