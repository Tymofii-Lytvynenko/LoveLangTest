import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def write_json(tmp_path: Path, filename: str, payload: dict) -> Path:
    path = tmp_path / filename
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def pytest_addoption(parser) -> None:
    parser.addoption(
        "--generated-bank",
        action="store",
        default=None,
        help="Path to a freshly generated question bank JSON file to validate.",
    )
    parser.addoption(
        "--expected-question-count",
        action="store",
        default=None,
        help="Exact number of questions expected in the generated bank.",
    )


@pytest.fixture
def generated_bank_path(request) -> Path:
    raw_value = request.config.getoption("--generated-bank")
    if not raw_value:
        pytest.skip("No generated bank path was provided.")
    path = Path(raw_value)
    if not path.exists():
        pytest.fail(f"Generated bank file does not exist: {path}")
    return path


@pytest.fixture
def expected_question_count(request) -> int | None:
    raw_value = request.config.getoption("--expected-question-count")
    return int(raw_value) if raw_value is not None else None
