from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from src.question_bank import QuestionBank, question_state_key


@dataclass(frozen=True)
class BankResponseState:
    responses: dict[str, str]
    missing_questions: tuple[str, ...]

    @property
    def is_complete(self) -> bool:
        return not self.missing_questions


def collect_bank_responses(bank: QuestionBank, state: Mapping[str, object]) -> BankResponseState:
    responses: dict[str, str] = {}
    missing_questions: list[str] = []

    for question in bank.questions:
        state_key = question_state_key(bank.module, question.id)
        raw_value = state.get(state_key)
        if isinstance(raw_value, str) and raw_value in question.option_ids():
            responses[question.id] = raw_value
        else:
            missing_questions.append(question.question)

    return BankResponseState(
        responses=responses,
        missing_questions=tuple(missing_questions),
    )
