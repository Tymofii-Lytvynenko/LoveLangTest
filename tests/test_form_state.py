from src.question_bank import load_question_bank, question_state_key
from src.services.form_state import collect_bank_responses


def test_empty_state_keeps_questions_unanswered() -> None:
    bank = load_question_bank("needs")
    response_state = collect_bank_responses(bank, {})

    assert not response_state.is_complete
    assert len(response_state.missing_questions) == len(bank.questions)


def test_complete_state_collects_all_answers() -> None:
    bank = load_question_bank("shadow")
    state = {
        question_state_key("shadow", question.id): question.options[0].id
        for question in bank.questions
    }

    response_state = collect_bank_responses(bank, state)
    assert response_state.is_complete
    assert len(response_state.responses) == len(bank.questions)
