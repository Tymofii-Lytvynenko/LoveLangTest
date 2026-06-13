from pathlib import Path

from src.services.question_bank_generation_batch import (
    DEFAULT_BATCH_QUESTION_COUNTS,
    build_full_pytest_command,
    build_generation_batch_plan,
    build_generation_command,
)


def test_build_generation_batch_plan_uses_defaults_and_generated_paths(tmp_path: Path) -> None:
    plans = build_generation_batch_plan(tmp_path)

    assert [plan.module for plan in plans] == ["needs", "shadow", "eros"]
    assert [plan.question_count for plan in plans] == [
        DEFAULT_BATCH_QUESTION_COUNTS["needs"],
        DEFAULT_BATCH_QUESTION_COUNTS["shadow"],
        DEFAULT_BATCH_QUESTION_COUNTS["eros"],
    ]
    assert plans[0].output_path == tmp_path / "generated_needs.json"
    assert plans[1].quality_report_path == tmp_path / "generated_shadow.quality.json"
    assert plans[2].bank_id == "crnas-eros-generated"


def test_build_generation_batch_plan_accepts_overrides(tmp_path: Path) -> None:
    plans = build_generation_batch_plan(
        tmp_path,
        question_counts={"needs": 16, "shadow": 6, "eros": 10},
        bank_id_prefix="custom",
    )

    assert [plan.question_count for plan in plans] == [16, 6, 10]
    assert [plan.bank_id for plan in plans] == [
        "custom-needs-generated",
        "custom-shadow-generated",
        "custom-eros-generated",
    ]


def test_build_generation_command_includes_shared_flags(tmp_path: Path) -> None:
    plan = build_generation_batch_plan(tmp_path)[0]

    command = build_generation_command(
        plan,
        version="0.2.0",
        max_attempts=5,
        force=True,
        skip_pytest=True,
        python_executable="python",
    )

    assert command[:2] == ["python", "scripts/generate_question_bank.py"]
    assert "--module" in command
    assert "needs" in command
    assert "--quality-report" in command
    assert str(plan.quality_report_path) in command
    assert "--force" in command
    assert "--skip-pytest" in command


def test_build_full_pytest_command_defaults_to_module_invocation() -> None:
    command = build_full_pytest_command("python")

    assert command == ["python", "-m", "pytest"]
