from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json
import math
import re

from src.question_bank import QuestionBank, load_question_bank_from_path
from src.question_bank_blueprints import QuestionBankBlueprint, get_question_bank_blueprint


_WORD_RE = re.compile(r"[A-Za-zА-Яа-яІіЇїЄєҐґ0-9']+")
_LATIN_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'/-]*")
_CYRILLIC_RE = re.compile(r"[А-Яа-яІіЇїЄєҐґ]")
_ALLOWED_LATIN_USER_FACING_TOKENS = {"adhd", "asd", "audhd", "crnas"}
_RUSSIAN_SPECIFIC_CHARS = set("ыэёъ")
_SUSPICIOUS_RUSSIAN_TOKENS = {
    "что",
    "это",
    "если",
    "или",
    "когда",
    "после",
    "между",
    "только",
    "нужно",
    "самый",
    "который",
    "сегодня",
    "тебя",
    "меня",
}
_UKRAINIAN_MARKER_TOKENS = {
    "і",
    "й",
    "та",
    "це",
    "що",
    "як",
    "для",
    "після",
    "коли",
    "щоб",
    "мені",
    "потрібно",
    "партнер",
    "підтримка",
    "розмова",
    "безпека",
}


@dataclass(frozen=True)
class QualityMetric:
    name: str
    value: Any


@dataclass
class QuestionBankQualityReport:
    module: str
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: list[QualityMetric] = field(default_factory=list)

    def add_metric(self, name: str, value: Any) -> None:
        self.metrics.append(QualityMetric(name=name, value=value))

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "passed": self.passed,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "metrics": {metric.name: metric.value for metric in self.metrics},
        }

    def require_pass(self) -> None:
        if self.passed:
            return
        raise ValueError("Question bank quality gate failed:\n- " + "\n- ".join(self.errors))


def _tokenize(text: str) -> list[str]:
    return [token.lower() for token in _WORD_RE.findall(text)]


def _matches_any_keyword(text: str, keywords: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in keywords)


class QuestionBankQualityGate:
    @staticmethod
    def evaluate(
        bank: QuestionBank,
        *,
        expected_question_count: int | None = None,
        strict_content_checks: bool = False,
    ) -> QuestionBankQualityReport:
        blueprint = get_question_bank_blueprint(bank.module)
        report = QuestionBankQualityReport(module=bank.module, passed=True)

        if blueprint is None:
            report.errors.append(f"No blueprint registered for module '{bank.module}'.")
            report.passed = False
            return report

        QuestionBankQualityGate._check_count(bank, blueprint, report, expected_question_count)
        QuestionBankQualityGate._check_descriptions(bank, blueprint, report, strict_content_checks)
        QuestionBankQualityGate._check_question_shapes(bank, blueprint, report)
        QuestionBankQualityGate._check_user_facing_language(bank, report, strict_content_checks)
        QuestionBankQualityGate._check_banned_terms(bank, blueprint, report)
        QuestionBankQualityGate._check_vector_ranges(bank, blueprint, report)
        QuestionBankQualityGate._check_tradeoffs(bank, blueprint, report)
        QuestionBankQualityGate._check_balance(bank, blueprint, report)
        QuestionBankQualityGate._check_coverage(bank, blueprint, report)
        QuestionBankQualityGate._check_module_specific(bank, blueprint, report)

        report.passed = not report.errors
        return report

    @staticmethod
    def evaluate_path(
        path: Path,
        *,
        expected_question_count: int | None = None,
        strict_content_checks: bool = False,
    ) -> QuestionBankQualityReport:
        bank = load_question_bank_from_path(path)
        return QuestionBankQualityGate.evaluate(
            bank,
            expected_question_count=expected_question_count,
            strict_content_checks=strict_content_checks,
        )

    @staticmethod
    def write_report(path: Path, report: QuestionBankQualityReport) -> None:
        path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    @staticmethod
    def _check_count(
        bank: QuestionBank,
        blueprint: QuestionBankBlueprint,
        report: QuestionBankQualityReport,
        expected_question_count: int | None,
    ) -> None:
        question_count = len(bank.questions)
        report.add_metric("question_count", question_count)
        if question_count < blueprint.min_question_count:
            report.errors.append(
                f"Module '{bank.module}' needs at least {blueprint.min_question_count} questions; got {question_count}."
            )
        if expected_question_count is not None and question_count != expected_question_count:
            report.errors.append(
                f"Expected exactly {expected_question_count} questions for module '{bank.module}', got {question_count}."
            )

    @staticmethod
    def _check_descriptions(
        bank: QuestionBank,
        blueprint: QuestionBankBlueprint,
        report: QuestionBankQualityReport,
        strict_content_checks: bool,
    ) -> None:
        described = sum(1 for question in bank.questions if question.description.strip())
        ratio = described / len(bank.questions)
        report.add_metric("description_ratio", ratio)
        if strict_content_checks and ratio < blueprint.required_description_ratio:
            report.errors.append(
                f"Descriptions are required for strict '{bank.module}' banks. Ratio {ratio:.2f} is below "
                f"{blueprint.required_description_ratio:.2f}."
            )

    @staticmethod
    def _check_question_shapes(
        bank: QuestionBank,
        blueprint: QuestionBankBlueprint,
        report: QuestionBankQualityReport,
    ) -> None:
        for question in bank.questions:
            option_count = len(question.options)
            if option_count < blueprint.min_options_per_question or option_count > blueprint.max_options_per_question:
                report.errors.append(
                    f"Question '{question.id}' must have between {blueprint.min_options_per_question} and "
                    f"{blueprint.max_options_per_question} options."
                )

            if len(_tokenize(question.question)) < 3:
                report.errors.append(f"Question '{question.id}' is too short to be behaviorally clear.")

            option_texts = [option.text.strip().lower() for option in question.options]
            if len(option_texts) != len(set(option_texts)):
                report.errors.append(f"Question '{question.id}' has duplicate option texts.")

            vectors = {option.vector for option in question.options}
            if len(vectors) == 1:
                report.errors.append(f"Question '{question.id}' has identical vectors for every option.")

    @staticmethod
    def _check_user_facing_language(
        bank: QuestionBank,
        report: QuestionBankQualityReport,
        strict_content_checks: bool,
    ) -> None:
        if not strict_content_checks:
            return

        all_text_parts: list[str] = []
        suspicious_russian_hits: list[str] = []
        latin_token_hits: list[str] = []
        missing_cyrillic_fields: list[str] = []

        for question in bank.questions:
            fields = {
                f"{question.id}.question": question.question,
                f"{question.id}.description": question.description,
            }
            fields.update(
                {
                    f"{question.id}.{option.id}": option.text
                    for option in question.options
                }
            )

            for field_name, text in fields.items():
                stripped = text.strip()
                all_text_parts.append(stripped)

                if not _CYRILLIC_RE.search(stripped):
                    missing_cyrillic_fields.append(field_name)

                latin_tokens = [
                    token
                    for token in _LATIN_WORD_RE.findall(stripped)
                    if token.lower() not in _ALLOWED_LATIN_USER_FACING_TOKENS
                ]
                if latin_tokens:
                    latin_token_hits.append(f"{field_name}: {', '.join(sorted(set(latin_tokens))[:4])}")

                lowered = stripped.lower()
                if any(char in lowered for char in _RUSSIAN_SPECIFIC_CHARS):
                    suspicious_russian_hits.append(f"{field_name}: russian-specific characters")
                    continue

                russian_tokens = sorted(set(_tokenize(lowered)).intersection(_SUSPICIOUS_RUSSIAN_TOKENS))
                if russian_tokens:
                    suspicious_russian_hits.append(f"{field_name}: {', '.join(russian_tokens[:4])}")

        combined_text = " ".join(all_text_parts).lower()
        ukrainian_marker_count = sum(combined_text.count(char) for char in "іїєґ")
        ukrainian_marker_count += len(set(_tokenize(combined_text)).intersection(_UKRAINIAN_MARKER_TOKENS))

        report.add_metric("ukrainian_marker_count", ukrainian_marker_count)
        report.add_metric("latin_user_facing_hits", latin_token_hits)
        report.add_metric("suspicious_russian_hits", suspicious_russian_hits)

        if missing_cyrillic_fields:
            report.errors.append(
                "Strict bank must keep all user-facing fields in Ukrainian; missing Cyrillic in: "
                + ", ".join(missing_cyrillic_fields[:8])
                + ("..." if len(missing_cyrillic_fields) > 8 else "")
            )

        if latin_token_hits:
            report.errors.append(
                "Strict bank contains non-Ukrainian Latin user-facing text: "
                + "; ".join(latin_token_hits[:6])
                + ("..." if len(latin_token_hits) > 6 else "")
            )

        if suspicious_russian_hits:
            report.errors.append(
                "Strict bank contains suspicious non-Ukrainian / Russian user-facing text: "
                + "; ".join(suspicious_russian_hits[:6])
                + ("..." if len(suspicious_russian_hits) > 6 else "")
            )

        if ukrainian_marker_count < max(3, len(bank.questions)):
            report.errors.append(
                "Strict bank does not look sufficiently Ukrainian in aggregate; rewrite all user-facing content in natural Ukrainian."
            )

    @staticmethod
    def _check_banned_terms(
        bank: QuestionBank,
        blueprint: QuestionBankBlueprint,
        report: QuestionBankQualityReport,
    ) -> None:
        hits: list[str] = []
        for question in bank.questions:
            segments = [question.question, question.description, *(option.text for option in question.options)]
            combined = " ".join(segment for segment in segments if segment).lower()
            for term in blueprint.banned_terms:
                if term in combined:
                    hits.append(f"{question.id}:{term}")
        report.add_metric("banned_term_hits", hits)
        if hits:
            report.errors.append(
                f"Bank '{bank.module}' contains banned pseudo-scientific or moralizing terms: {', '.join(hits[:8])}."
            )

    @staticmethod
    def _check_vector_ranges(
        bank: QuestionBank,
        blueprint: QuestionBankBlueprint,
        report: QuestionBankQualityReport,
    ) -> None:
        negative_count = 0
        max_magnitude_seen = 0.0
        for question in bank.questions:
            for option in question.options:
                for value in option.vector:
                    max_magnitude_seen = max(max_magnitude_seen, abs(value))
                    if abs(value) > blueprint.max_vector_magnitude:
                        report.errors.append(
                            f"Question '{question.id}' has vector value {value} outside +/-{blueprint.max_vector_magnitude}."
                        )
                    if value < 0:
                        negative_count += 1
        report.add_metric("negative_weight_count", negative_count)
        report.add_metric("max_vector_magnitude", max_magnitude_seen)
        if blueprint.require_negative_weights and negative_count == 0:
            report.errors.append(f"Module '{bank.module}' should include some negative weights to encode tradeoffs.")

    @staticmethod
    def _check_tradeoffs(
        bank: QuestionBank,
        blueprint: QuestionBankBlueprint,
        report: QuestionBankQualityReport,
    ) -> None:
        mixed_direction_questions = 0
        tradeoff_questions = 0
        for question in bank.questions:
            non_zero_dimensions: set[int] = set()
            has_negative = False
            has_positive = False
            for option in question.options:
                for index, value in enumerate(option.vector):
                    if value != 0:
                        non_zero_dimensions.add(index)
                    if value < 0:
                        has_negative = True
                    if value > 0:
                        has_positive = True
            if len(non_zero_dimensions) >= 2:
                tradeoff_questions += 1
            if has_negative and has_positive:
                mixed_direction_questions += 1

        report.add_metric("tradeoff_question_count", tradeoff_questions)
        report.add_metric("mixed_direction_question_count", mixed_direction_questions)

        required_tradeoffs = max(1, math.ceil(len(bank.questions) * 0.6))
        if tradeoff_questions < required_tradeoffs:
            report.errors.append(
                f"Bank '{bank.module}' does not contain enough real tradeoffs; got {tradeoff_questions}, "
                f"need at least {required_tradeoffs}."
            )
        if blueprint.require_mixed_direction_vectors and mixed_direction_questions == 0:
            report.errors.append(f"Module '{bank.module}' should include both positive and inhibiting/negative cues.")

    @staticmethod
    def _check_balance(
        bank: QuestionBank,
        blueprint: QuestionBankBlueprint,
        report: QuestionBankQualityReport,
    ) -> None:
        dominant_counts = {label: 0 for label in blueprint.vector_labels}
        positive_counts = {label: 0 for label in blueprint.vector_labels}
        question_primary_counts = {label: 0 for label in blueprint.vector_labels}
        for question in bank.questions:
            positive_totals = [0.0] * len(blueprint.vector_labels)
            for option in question.options:
                dominant_index = max(range(len(option.vector)), key=lambda index: option.vector[index])
                dominant_counts[blueprint.vector_labels[dominant_index]] += 1
                for index, value in enumerate(option.vector):
                    if value > 0:
                        positive_counts[blueprint.vector_labels[index]] += 1
                        positive_totals[index] += value

            if bank.module == "needs":
                primary_index = max(range(len(positive_totals)), key=lambda index: positive_totals[index])
                question_primary_counts[blueprint.vector_labels[primary_index]] += 1

        report.add_metric("dominant_counts", dominant_counts)
        report.add_metric("positive_counts", positive_counts)
        if bank.module == "needs":
            report.add_metric("question_primary_counts", question_primary_counts)

        if any(count == 0 for count in positive_counts.values()):
            missing = [label for label, count in positive_counts.items() if count == 0]
            report.errors.append(
                f"Module '{bank.module}' is unbalanced; no positive coverage for dimensions: {', '.join(missing)}."
            )

        skew_source = question_primary_counts if bank.module == "needs" else dominant_counts
        min_dominant = min(skew_source.values())
        max_dominant = max(skew_source.values())
        if max_dominant > max(1, min_dominant * 3):
            report.errors.append(
                f"Module '{bank.module}' is overly skewed across dimensions: {skew_source}."
            )

    @staticmethod
    def _check_coverage(
        bank: QuestionBank,
        blueprint: QuestionBankBlueprint,
        report: QuestionBankQualityReport,
    ) -> None:
        matched_clusters: dict[str, int] = {cluster.name: 0 for cluster in blueprint.coverage_clusters}
        for question in bank.questions:
            combined = " ".join([question.question, question.description, *(option.text for option in question.options)])
            for cluster in blueprint.coverage_clusters:
                if _matches_any_keyword(combined, cluster.keywords):
                    matched_clusters[cluster.name] += 1

        report.add_metric("coverage_clusters", matched_clusters)
        missing_clusters = [name for name, count in matched_clusters.items() if count == 0]
        if missing_clusters:
            report.errors.append(
                f"Module '{bank.module}' is missing coverage for core constructs: {', '.join(missing_clusters)}."
            )

    @staticmethod
    def _check_module_specific(
        bank: QuestionBank,
        blueprint: QuestionBankBlueprint,
        report: QuestionBankQualityReport,
    ) -> None:
        if bank.module == "shadow":
            QuestionBankQualityGate._check_shadow_specific(bank, report)
        elif bank.module == "eros":
            QuestionBankQualityGate._check_eros_specific(bank, report)

    @staticmethod
    def _check_shadow_specific(bank: QuestionBank, report: QuestionBankQualityReport) -> None:
        one_hot_errors = 0
        label_count = len(bank.metadata.vector_labels)
        style_positive_counts = {label: 0 for label in bank.metadata.vector_labels}
        for question in bank.questions:
            if len(question.options) != label_count:
                report.errors.append(
                    f"Shadow question '{question.id}' must expose exactly one option per attachment style."
                )
            for option in question.options:
                positives = [value for value in option.vector if value > 0]
                if len(positives) != 1 or any(value not in {0.0, 1.0} for value in option.vector):
                    one_hot_errors += 1
                for index, value in enumerate(option.vector):
                    if value > 0:
                        style_positive_counts[bank.metadata.vector_labels[index]] += 1

        report.add_metric("shadow_style_positive_counts", style_positive_counts)
        if one_hot_errors:
            report.errors.append("Shadow bank must use one-hot vectors so each option maps to one attachment style.")
        if len(set(style_positive_counts.values())) > 1:
            report.errors.append(
                f"Shadow bank should represent each attachment style equally across options: {style_positive_counts}."
            )

    @staticmethod
    def _check_eros_specific(bank: QuestionBank, report: QuestionBankQualityReport) -> None:
        mixed_option_count = 0
        zero_brake_options = 0
        zero_accel_options = 0
        for question in bank.questions:
            for option in question.options:
                accel, brake = option.vector
                if accel > 0 and brake > 0:
                    mixed_option_count += 1
                if brake == 0:
                    zero_brake_options += 1
                if accel == 0:
                    zero_accel_options += 1

        report.add_metric("eros_mixed_option_count", mixed_option_count)
        if mixed_option_count == 0:
            report.errors.append("Eros bank should include at least one context-sensitive option with both accelerator and brake.")
        if zero_brake_options == 0 or zero_accel_options == 0:
            report.errors.append("Eros bank should include both activating and inhibiting options.")
