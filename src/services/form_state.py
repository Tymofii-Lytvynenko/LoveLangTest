from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from src.question_bank import QuestionBank, QuestionResponse, question_state_key


@dataclass(frozen=True)
class BankResponseState:
    responses: dict[str, QuestionResponse]
    missing_questions: tuple[str, ...]

    @property
    def is_complete(self) -> bool:
        return not self.missing_questions


def collect_bank_responses(bank: QuestionBank, state: Mapping[str, object]) -> BankResponseState:
    responses: dict[str, QuestionResponse] = {}
    missing_questions: list[str] = []

    for question in bank.questions:
        if question.is_best_worst:
            best_key = question_state_key(bank.module, question.id, "best")
            worst_key = question_state_key(bank.module, question.id, "worst")
            best_value = state.get(best_key)
            worst_value = state.get(worst_key)
            if (
                isinstance(best_value, str)
                and isinstance(worst_value, str)
                and best_value in question.option_ids()
                and worst_value in question.option_ids()
                and best_value != worst_value
            ):
                responses[question.id] = QuestionResponse.best_worst(best_value, worst_value)
            else:
                missing_questions.append(
                    f"{question.question} (оберіть окремо найважливіше і найменш критичне)"
                )
        else:
            state_key = question_state_key(bank.module, question.id)
            raw_value = state.get(state_key)
            if isinstance(raw_value, str) and raw_value in question.option_ids():
                responses[question.id] = QuestionResponse.single_choice(raw_value)
            else:
                missing_questions.append(question.question)

    return BankResponseState(
        responses=responses,
        missing_questions=tuple(missing_questions),
    )
