from __future__ import annotations

from dataclasses import dataclass

from src.domain.eros import ErosComponent
from src.domain.needs import RelationalNeedsComponent
from src.domain.shadow import ShadowComponent
from src.question_bank import QuestionBank


@dataclass(frozen=True)
class VectorScore:
    raw_totals: tuple[float, ...]
    min_totals: tuple[float, ...]
    max_totals: tuple[float, ...]
    normalized: tuple[float, ...]


def _normalize_score(raw_value: float, min_value: float, max_value: float) -> float:
    if max_value == min_value:
        return 0.5
    normalized = (raw_value - min_value) / (max_value - min_value)
    return min(max(normalized, 0.0), 1.0)


class QuestionnaireScorer:
    @staticmethod
    def score(bank: QuestionBank, responses: dict[str, str]) -> VectorScore:
        missing = [question.id for question in bank.questions if question.id not in responses]
        if missing:
            raise ValueError(
                f"Incomplete responses for module '{bank.module}'. Missing question ids: {', '.join(missing)}"
            )

        totals = [0.0] * bank.vector_size
        for question in bank.questions:
            selected_option = question.get_option(responses[question.id])
            for index, value in enumerate(selected_option.vector):
                totals[index] += value

        minimums = bank.min_vector()
        maximums = bank.max_vector()
        normalized = tuple(
            _normalize_score(raw_value, min_value, max_value)
            for raw_value, min_value, max_value in zip(totals, minimums, maximums)
        )
        return VectorScore(
            raw_totals=tuple(totals),
            min_totals=minimums,
            max_totals=maximums,
            normalized=normalized,
        )

    @staticmethod
    def build_needs_component(bank: QuestionBank, responses: dict[str, str]) -> RelationalNeedsComponent:
        score = QuestionnaireScorer.score(bank, responses)
        return RelationalNeedsComponent(
            raw_safety=score.normalized[0],
            raw_resource=score.normalized[1],
            raw_resonance=score.normalized[2],
            raw_expansion=score.normalized[3],
        )

    @staticmethod
    def build_eros_component(
        bank: QuestionBank,
        responses: dict[str, str],
        erotic_tags: list[str] | None = None,
    ) -> ErosComponent:
        score = QuestionnaireScorer.score(bank, responses)
        component = ErosComponent(erotic_tags=erotic_tags or [])
        component.calculate_from_quiz(score.normalized[0], score.normalized[1])
        return component

    @staticmethod
    def build_shadow_component(bank: QuestionBank, responses: dict[str, str]) -> ShadowComponent:
        score = QuestionnaireScorer.score(bank, responses)
        component = ShadowComponent()
        component.calculate_from_quiz(score.normalized)
        return component
