from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import hashlib
import json
from typing import Any, Mapping

from src.question_bank_blueprints import get_question_bank_blueprint

QUESTION_BANK_DIR = Path(__file__).resolve().parent.parent / "question_bank"
QUESTION_STATE_PREFIXES = {
    "needs": "scenario",
    "shadow": "shadow_q",
    "eros": "eros_q",
}


class QuestionBankValidationError(ValueError):
    """Raised when a question bank file has an invalid shape."""


@dataclass(frozen=True)
class QuestionOption:
    id: str
    text: str
    vector: tuple[float, ...]


@dataclass(frozen=True)
class QuestionItem:
    id: str
    question: str
    description: str
    options: tuple[QuestionOption, ...]

    def option_ids(self) -> tuple[str, ...]:
        return tuple(option.id for option in self.options)

    def get_option(self, option_id: str) -> QuestionOption:
        for option in self.options:
            if option.id == option_id:
                return option
        raise KeyError(f"Unknown option id '{option_id}' for question '{self.id}'.")


@dataclass(frozen=True)
class QuestionBankMetadata:
    bank_id: str
    version: str
    module: str
    authoring_instructions: str
    vector_labels: tuple[str, ...]


@dataclass(frozen=True)
class QuestionBank:
    metadata: QuestionBankMetadata
    questions: tuple[QuestionItem, ...]
    fingerprint: str

    @property
    def module(self) -> str:
        return self.metadata.module

    @property
    def vector_size(self) -> int:
        return len(self.metadata.vector_labels)

    def question_ids(self) -> tuple[str, ...]:
        return tuple(question.id for question in self.questions)

    def get_question(self, question_id: str) -> QuestionItem:
        for question in self.questions:
            if question.id == question_id:
                return question
        raise KeyError(f"Unknown question id '{question_id}' in module '{self.module}'.")

    def min_vector(self) -> tuple[float, ...]:
        mins = [0.0] * self.vector_size
        for question in self.questions:
            for index in range(self.vector_size):
                mins[index] += min(option.vector[index] for option in question.options)
        return tuple(mins)

    def max_vector(self) -> tuple[float, ...]:
        maxes = [0.0] * self.vector_size
        for question in self.questions:
            for index in range(self.vector_size):
                maxes[index] += max(option.vector[index] for option in question.options)
        return tuple(maxes)


@dataclass(frozen=True)
class QuestionBankRegistry:
    banks: dict[str, QuestionBank]
    fingerprint: str

    def get(self, module: str) -> QuestionBank:
        return self.banks[module]


def question_state_key(module: str, question_id: str) -> str:
    prefix = QUESTION_STATE_PREFIXES[module]
    return f"{prefix}_{question_id}"


def _compute_fingerprint(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _require_non_empty_string(raw_value: Any, field_name: str) -> str:
    if not isinstance(raw_value, str) or not raw_value.strip():
        raise QuestionBankValidationError(f"Field '{field_name}' must be a non-empty string.")
    return raw_value.strip()


def load_question_bank_from_payload(raw_bank: Mapping[str, Any]) -> QuestionBank:
    if not isinstance(raw_bank, dict):
        raise QuestionBankValidationError("Question bank root must be a JSON object.")

    metadata_raw = raw_bank.get("metadata")
    questions_raw = raw_bank.get("questions")
    if not isinstance(metadata_raw, dict):
        raise QuestionBankValidationError("Question bank must contain a 'metadata' object.")
    if not isinstance(questions_raw, list) or not questions_raw:
        raise QuestionBankValidationError("Question bank must contain a non-empty 'questions' list.")

    vector_labels_raw = metadata_raw.get("vector_labels")
    if not isinstance(vector_labels_raw, list) or not vector_labels_raw:
        raise QuestionBankValidationError("metadata.vector_labels must be a non-empty list.")

    vector_labels = tuple(
        _require_non_empty_string(label, "metadata.vector_labels")
        for label in vector_labels_raw
    )
    metadata = QuestionBankMetadata(
        bank_id=_require_non_empty_string(metadata_raw.get("bank_id"), "metadata.bank_id"),
        version=_require_non_empty_string(metadata_raw.get("version"), "metadata.version"),
        module=_require_non_empty_string(metadata_raw.get("module"), "metadata.module"),
        authoring_instructions=_require_non_empty_string(
            metadata_raw.get("authoring_instructions"),
            "metadata.authoring_instructions",
        ),
        vector_labels=vector_labels,
    )
    blueprint = get_question_bank_blueprint(metadata.module)
    if blueprint is not None and metadata.vector_labels != blueprint.vector_labels:
        raise QuestionBankValidationError(
            f"metadata.vector_labels for module '{metadata.module}' must be {list(blueprint.vector_labels)}."
        )

    question_ids: set[str] = set()
    questions: list[QuestionItem] = []
    for question_index, raw_question in enumerate(questions_raw, start=1):
        if not isinstance(raw_question, dict):
            raise QuestionBankValidationError(f"Question #{question_index} must be a JSON object.")

        question_id = _require_non_empty_string(raw_question.get("id"), f"questions[{question_index}].id")
        if question_id in question_ids:
            raise QuestionBankValidationError(f"Duplicate question id '{question_id}'.")
        question_ids.add(question_id)

        options_raw = raw_question.get("options")
        if not isinstance(options_raw, list) or not options_raw:
            raise QuestionBankValidationError(f"Question '{question_id}' must have a non-empty options list.")

        option_ids: set[str] = set()
        options: list[QuestionOption] = []
        for option_index, raw_option in enumerate(options_raw, start=1):
            if not isinstance(raw_option, dict):
                raise QuestionBankValidationError(
                    f"Question '{question_id}' option #{option_index} must be a JSON object."
                )

            option_id = _require_non_empty_string(
                raw_option.get("id"),
                f"questions[{question_id}].options[{option_index}].id",
            )
            if option_id in option_ids:
                raise QuestionBankValidationError(
                    f"Duplicate option id '{option_id}' in question '{question_id}'."
                )
            option_ids.add(option_id)

            vector_raw = raw_option.get("vector")
            if not isinstance(vector_raw, list) or len(vector_raw) != len(vector_labels):
                raise QuestionBankValidationError(
                    f"Question '{question_id}' option '{option_id}' has invalid vector length."
                )

            vector: list[float] = []
            for score_index, raw_score in enumerate(vector_raw, start=1):
                if not isinstance(raw_score, (int, float)):
                    raise QuestionBankValidationError(
                        f"Question '{question_id}' option '{option_id}' score #{score_index} must be numeric."
                    )
                vector.append(float(raw_score))

            options.append(
                QuestionOption(
                    id=option_id,
                    text=_require_non_empty_string(
                        raw_option.get("text"),
                        f"questions[{question_id}].options[{option_index}].text",
                    ),
                    vector=tuple(vector),
                )
            )

        questions.append(
            QuestionItem(
                id=question_id,
                question=_require_non_empty_string(raw_question.get("question"), f"questions[{question_id}].question"),
                description=(
                    str(raw_question.get("description", ""))
                    if raw_question.get("description") is not None
                    else ""
                ),
                options=tuple(options),
            )
        )

    fingerprint = _compute_fingerprint(raw_bank)
    return QuestionBank(metadata=metadata, questions=tuple(questions), fingerprint=fingerprint)


def load_question_bank_from_path(path: Path) -> QuestionBank:
    raw_bank = json.loads(path.read_text(encoding="utf-8"))
    return load_question_bank_from_payload(raw_bank)


@lru_cache(maxsize=None)
def load_question_bank(module: str) -> QuestionBank:
    path = QUESTION_BANK_DIR / f"{module}.json"
    if not path.exists():
        raise FileNotFoundError(f"Question bank file not found: {path}")
    bank = load_question_bank_from_path(path)
    if bank.module != module:
        raise QuestionBankValidationError(
            f"Bank file '{path.name}' declares module '{bank.module}' instead of '{module}'."
        )
    return bank


@lru_cache(maxsize=1)
def get_question_bank_registry() -> QuestionBankRegistry:
    banks = {
        module: load_question_bank(module)
        for module in ("needs", "shadow", "eros")
    }
    payload = {
        module: {
            "bank_id": bank.metadata.bank_id,
            "version": bank.metadata.version,
            "fingerprint": bank.fingerprint,
        }
        for module, bank in banks.items()
    }
    return QuestionBankRegistry(banks=banks, fingerprint=_compute_fingerprint(payload))
