from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
import subprocess
import sys


SUPPORTED_GENERATION_MODULES = ("needs", "shadow", "eros")

DEFAULT_BATCH_QUESTION_COUNTS = MappingProxyType(
    {
        "needs": 12,
        "shadow": 8,
        "eros": 8,
    }
)


@dataclass(frozen=True)
class GenerationBatchModulePlan:
    module: str
    question_count: int
    output_path: Path
    quality_report_path: Path
    bank_id: str


def build_generation_batch_plan(
    output_dir: Path,
    question_counts: dict[str, int] | None = None,
    bank_id_prefix: str = "crnas",
) -> tuple[GenerationBatchModulePlan, ...]:
    counts = dict(DEFAULT_BATCH_QUESTION_COUNTS)
    if question_counts:
        counts.update(question_counts)

    plans: list[GenerationBatchModulePlan] = []
    for module in SUPPORTED_GENERATION_MODULES:
        question_count = counts[module]
        if question_count <= 0:
            raise ValueError(f"Question count for module '{module}' must be positive.")

        output_path = output_dir / f"generated_{module}.json"
        plans.append(
            GenerationBatchModulePlan(
                module=module,
                question_count=question_count,
                output_path=output_path,
                quality_report_path=output_path.with_suffix(".quality.json"),
                bank_id=f"{bank_id_prefix}-{module}-generated",
            )
        )

    return tuple(plans)


def build_generation_command(
    plan: GenerationBatchModulePlan,
    *,
    version: str,
    max_attempts: int,
    force: bool,
    skip_pytest: bool,
    python_executable: str | None = None,
) -> list[str]:
    command = [
        python_executable or sys.executable,
        "scripts/generate_question_bank.py",
        "--module",
        plan.module,
        "--questions",
        str(plan.question_count),
        "--output",
        str(plan.output_path),
        "--bank-id",
        plan.bank_id,
        "--version",
        version,
        "--max-attempts",
        str(max_attempts),
        "--quality-report",
        str(plan.quality_report_path),
    ]
    if force:
        command.append("--force")
    if skip_pytest:
        command.append("--skip-pytest")
    return command


def build_full_pytest_command(python_executable: str | None = None) -> list[str]:
    return [
        python_executable or sys.executable,
        "-m",
        "pytest",
    ]


def render_command(command: list[str]) -> str:
    return subprocess.list2cmdline(command)
