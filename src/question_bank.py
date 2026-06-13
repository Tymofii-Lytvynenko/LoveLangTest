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
    "provision": "provision_q",
    "calibration": "calibration_q",
}
QUESTION_RESPONSE_TYPES = {"single_choice", "best_worst"}
NEEDS_QUESTION_FAMILIES = {"absolute", "priority"}


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
    mode: str = "simple"
    response_type: str = "single_choice"
    family: str | None = None
    dimension: str | None = None

    def option_ids(self) -> tuple[str, ...]:
        return tuple(option.id for option in self.options)

    def get_option(self, option_id: str) -> QuestionOption:
        for option in self.options:
            if option.id == option_id:
                return option
        raise KeyError(f"Unknown option id '{option_id}' for question '{self.id}'.")

    @property
    def is_best_worst(self) -> bool:
        return self.response_type == "best_worst"


@dataclass(frozen=True)
class QuestionResponse:
    option_id: str | None = None
    best_option_id: str | None = None
    worst_option_id: str | None = None

    @classmethod
    def single_choice(cls, option_id: str) -> "QuestionResponse":
        return cls(option_id=option_id)

    @classmethod
    def best_worst(cls, best_option_id: str, worst_option_id: str) -> "QuestionResponse":
        return cls(best_option_id=best_option_id, worst_option_id=worst_option_id)


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

    def for_mode(self, mode: str) -> "QuestionBank":
        if mode not in {"simple", "extended", "full"}:
            raise QuestionBankValidationError(f"Unsupported questionnaire mode '{mode}'.")
        if mode in {"extended", "full"}:
            return self
        return QuestionBank(
            metadata=self.metadata,
            questions=tuple(question for question in self.questions if question.mode == "simple"),
            fingerprint=self.fingerprint,
        )


@dataclass(frozen=True)
class QuestionBankRegistry:
    banks: dict[str, QuestionBank]
    fingerprint: str

    def get(self, module: str) -> QuestionBank:
        return self.banks[module]


def question_state_key(module: str, question_id: str, slot: str | None = None) -> str:
    prefix = QUESTION_STATE_PREFIXES[module]
    base_key = f"{prefix}_{question_id}"
    if slot is None:
        return base_key
    if slot not in {"best", "worst"}:
        raise QuestionBankValidationError(f"Unsupported response slot '{slot}'.")
    return f"{base_key}__{slot}"


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
        mode = str(raw_question.get("mode", "simple")).strip() or "simple"
        if mode not in {"simple", "extended", "full"}:
            raise QuestionBankValidationError(f"Question '{question_id}' has unsupported mode '{mode}'.")
        response_type = str(raw_question.get("response_type", "single_choice")).strip() or "single_choice"
        if response_type not in QUESTION_RESPONSE_TYPES:
            raise QuestionBankValidationError(
                f"Question '{question_id}' has unsupported response_type '{response_type}'."
            )
        raw_family = raw_question.get("family")
        family = str(raw_family).strip() if raw_family is not None else None
        if family == "":
            family = None
        raw_dimension = raw_question.get("dimension")
        dimension = str(raw_dimension).strip() if raw_dimension is not None else None
        if dimension == "":
            dimension = None

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

        if metadata.module == "needs":
            if family not in NEEDS_QUESTION_FAMILIES:
                raise QuestionBankValidationError(
                    f"Needs question '{question_id}' must declare family in {sorted(NEEDS_QUESTION_FAMILIES)}."
                )
            if family == "absolute":
                if response_type != "single_choice":
                    raise QuestionBankValidationError(
                        f"Needs question '{question_id}' in family 'absolute' must use response_type 'single_choice'."
                    )
                if dimension not in vector_labels:
                    raise QuestionBankValidationError(
                        f"Needs question '{question_id}' in family 'absolute' must declare a valid dimension."
                    )
            if family == "priority":
                if response_type != "best_worst":
                    raise QuestionBankValidationError(
                        f"Needs question '{question_id}' in family 'priority' must use response_type 'best_worst'."
                    )
                if dimension is not None:
                    raise QuestionBankValidationError(
                        f"Needs question '{question_id}' in family 'priority' must not declare a fixed dimension."
                    )
        elif family is not None or dimension is not None:
            raise QuestionBankValidationError(
                f"Only needs questions may declare family/dimension metadata; found on '{question_id}'."
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
                mode=mode,
                response_type=response_type,
                family=family,
                dimension=dimension,
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
        for module in ("needs", "shadow", "eros", "provision", "calibration")
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
