from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from src.domain.eros import ErosComponent
from src.domain.needs import RelationalNeedsComponent
from src.domain.shadow import ShadowComponent
from src.question_bank import QuestionBank, QuestionItem, QuestionResponse


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


def _coerce_single_choice_response(question: QuestionItem, response: str | QuestionResponse) -> str:
    if isinstance(response, str):
        return response
    if response.option_id is None:
        raise ValueError(f"Question '{question.id}' requires a single-choice response.")
    return response.option_id


def _coerce_best_worst_response(question: QuestionItem, response: str | QuestionResponse) -> tuple[str, str]:
    if isinstance(response, str):
        raise ValueError(f"Question '{question.id}' requires a best/worst response object.")
    if response.best_option_id is None or response.worst_option_id is None:
        raise ValueError(f"Question '{question.id}' requires both best and worst selections.")
    if response.best_option_id == response.worst_option_id:
        raise ValueError(f"Question '{question.id}' must have different best and worst selections.")
    return response.best_option_id, response.worst_option_id


def _dominant_dimension(question: QuestionItem, option_id: str) -> int:
    option = question.get_option(option_id)
    return max(range(len(option.vector)), key=lambda index: option.vector[index])


class QuestionnaireScorer:
    @staticmethod
    def score(bank: QuestionBank, responses: Mapping[str, str | QuestionResponse]) -> VectorScore:
        missing = [question.id for question in bank.questions if question.id not in responses]
        if missing:
            raise ValueError(
                f"Incomplete responses for module '{bank.module}'. Missing question ids: {', '.join(missing)}"
            )

        totals = [0.0] * bank.vector_size
        for question in bank.questions:
            selected_option = question.get_option(
                _coerce_single_choice_response(question, responses[question.id])
            )
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
    def build_needs_component(
        bank: QuestionBank,
        responses: Mapping[str, str | QuestionResponse],
    ) -> RelationalNeedsComponent:
        if all(question.family is None for question in bank.questions):
            score = QuestionnaireScorer.score(bank, responses)
            return RelationalNeedsComponent(
                raw_safety=score.normalized[0],
                raw_resource=score.normalized[1],
                raw_resonance=score.normalized[2],
                raw_expansion=score.normalized[3],
            )

        label_to_index = {label: index for index, label in enumerate(bank.metadata.vector_labels)}
        absolute_totals = [0.0] * bank.vector_size
        absolute_counts = [0] * bank.vector_size
        priority_points = [0.0] * bank.vector_size

        for question in bank.questions:
            response = responses[question.id]
            if question.family == "absolute":
                option_id = _coerce_single_choice_response(question, response)
                dimension_index = label_to_index[question.dimension or ""]
                absolute_totals[dimension_index] += question.get_option(option_id).vector[dimension_index]
                absolute_counts[dimension_index] += 1
                continue

            if question.family == "priority":
                best_option_id, worst_option_id = _coerce_best_worst_response(question, response)
                priority_points[_dominant_dimension(question, best_option_id)] += 1.0
                priority_points[_dominant_dimension(question, worst_option_id)] -= 1.0
                continue

            raise ValueError(f"Unsupported needs question family for '{question.id}'.")

        normalized_absolute = [
            absolute_totals[index] / absolute_counts[index] if absolute_counts[index] else 0.5
            for index in range(bank.vector_size)
        ]
        return RelationalNeedsComponent(
            raw_safety=normalized_absolute[0],
            raw_resource=normalized_absolute[1],
            raw_resonance=normalized_absolute[2],
            raw_expansion=normalized_absolute[3],
            priority_safety=priority_points[0],
            priority_resource=priority_points[1],
            priority_resonance=priority_points[2],
            priority_expansion=priority_points[3],
        )

    @staticmethod
    def build_eros_component(
        bank: QuestionBank,
        responses: Mapping[str, str | QuestionResponse],
        erotic_tags: list[str] | None = None,
    ) -> ErosComponent:
        score = QuestionnaireScorer.score(bank, responses)
        component = ErosComponent(erotic_tags=erotic_tags or [])
        component.calculate_from_quiz(score.normalized[0], score.normalized[1])
        return component

    @staticmethod
    def build_shadow_component(
        bank: QuestionBank,
        responses: Mapping[str, str | QuestionResponse],
    ) -> ShadowComponent:
        score = QuestionnaireScorer.score(bank, responses)
        component = ShadowComponent()
        component.calculate_from_quiz(score.normalized)
        return component
