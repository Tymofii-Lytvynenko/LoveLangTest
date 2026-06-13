import pytest

from src.question_bank import (
    get_question_bank_registry,
    load_question_bank_from_path,
    QuestionBankValidationError,
)
from conftest import write_json


def _build_bank_payload() -> dict:
    return {
        "metadata": {
            "bank_id": "test-custom",
            "version": "1.0.0",
            "module": "custom",
            "authoring_instructions": "Test instructions",
            "vector_labels": ["safety", "resource"],
        },
        "questions": [
            {
                "id": "q1",
                "question": "Question 1",
                "description": "Description 1",
                "options": [
                    {"id": "opt_1", "text": "Option 1", "vector": [1.0, 0.0]},
                    {"id": "opt_2", "text": "Option 2", "vector": [0.0, 1.0]},
                ],
            }
        ],
    }


def test_actual_banks_load_cleanly() -> None:
    registry = get_question_bank_registry()
    assert set(registry.banks) == {"needs", "shadow", "eros", "provision", "calibration"}
    assert registry.fingerprint


def test_loader_rejects_invalid_vector_length(tmp_path) -> None:
    payload = _build_bank_payload()
    payload["questions"][0]["options"][0]["vector"] = [1.0]
    path = write_json(tmp_path, "invalid.json", payload)

    with pytest.raises(QuestionBankValidationError):
        load_question_bank_from_path(path)


def test_loader_rejects_duplicate_question_ids(tmp_path) -> None:
    payload = _build_bank_payload()
    payload["questions"].append(payload["questions"][0].copy())
    path = write_json(tmp_path, "duplicate.json", payload)

    with pytest.raises(QuestionBankValidationError):
        load_question_bank_from_path(path)


def test_loader_requires_authoring_instructions(tmp_path) -> None:
    payload = _build_bank_payload()
    del payload["metadata"]["authoring_instructions"]
    path = write_json(tmp_path, "missing_instructions.json", payload)

    with pytest.raises(QuestionBankValidationError):
        load_question_bank_from_path(path)


def test_loader_rejects_wrong_vector_labels_for_known_module(tmp_path) -> None:
    payload = _build_bank_payload()
    payload["metadata"]["module"] = "shadow"
    payload["metadata"]["vector_labels"] = ["secure", "anxious", "avoidant"]
    path = write_json(tmp_path, "wrong_labels.json", payload)

    with pytest.raises(QuestionBankValidationError):
        load_question_bank_from_path(path)
