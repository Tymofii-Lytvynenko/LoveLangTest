from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.services.question_bank_generation_batch import (  # noqa: E402
    DEFAULT_BATCH_QUESTION_COUNTS,
    build_full_pytest_command,
    build_generation_batch_plan,
    build_generation_command,
    render_command,
)
from src.services.question_bank_generation import (  # noqa: E402
    OpenRouterGenerationConfig,
    QuestionBankGenerationError,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate all CRNAS question banks with shared settings and validations."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "question_bank",
        help="Directory where generated_<module>.json files will be written.",
    )
    parser.add_argument(
        "--needs-questions",
        type=int,
        default=DEFAULT_BATCH_QUESTION_COUNTS["needs"],
        help="Exact number of generated questions for the needs bank.",
    )
    parser.add_argument(
        "--shadow-questions",
        type=int,
        default=DEFAULT_BATCH_QUESTION_COUNTS["shadow"],
        help="Exact number of generated questions for the shadow bank.",
    )
    parser.add_argument(
        "--eros-questions",
        type=int,
        default=DEFAULT_BATCH_QUESTION_COUNTS["eros"],
        help="Exact number of generated questions for the eros bank.",
    )
    parser.add_argument("--version", default="0.1.0", help="metadata.version value.")
    parser.add_argument(
        "--bank-id-prefix",
        default="crnas",
        help="Prefix for metadata.bank_id values, producing <prefix>-<module>-generated.",
    )
    parser.add_argument("--max-attempts", type=int, default=3, help="Repair attempts per module.")
    parser.add_argument("--skip-pytest", action="store_true", help="Skip per-bank pytest contracts.")
    parser.add_argument(
        "--run-full-pytest",
        action="store_true",
        help="Run the full pytest suite after all banks are generated successfully.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated files.")
    return parser


def log(message: str) -> None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        config = OpenRouterGenerationConfig.from_env()
    except QuestionBankGenerationError as error:
        log(f"Configuration error: {error}")
        log("Set OPENROUTER_API_KEY in the current shell session before running batch generation.")
        return 2

    plans = build_generation_batch_plan(
        output_dir=args.output_dir.resolve(),
        question_counts={
            "needs": args.needs_questions,
            "shadow": args.shadow_questions,
            "eros": args.eros_questions,
        },
        bank_id_prefix=args.bank_id_prefix,
    )

    log("Starting CRNAS batch question-bank generation.")
    log(f"Output directory: {args.output_dir.resolve()}")
    log(f"Model: {config.model_id}")
    log(f"API base: {config.api_base}")
    log(
        "Counts: "
        f"needs={args.needs_questions}, "
        f"shadow={args.shadow_questions}, "
        f"eros={args.eros_questions}"
    )
    log(f"Max attempts per module: {args.max_attempts}")
    log(f"Per-bank pytest contracts: {'disabled' if args.skip_pytest else 'enabled'}")
    log(f"Full pytest after generation: {'enabled' if args.run_full_pytest else 'disabled'}")

    for plan in plans:
        command = build_generation_command(
            plan,
            version=args.version,
            max_attempts=args.max_attempts,
            force=args.force,
            skip_pytest=args.skip_pytest,
        )
        log(f"Launching module '{plan.module}' with {plan.question_count} questions.")
        log(f"Command: {render_command(command)}")
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode != 0:
            log(f"Module '{plan.module}' failed with exit code {result.returncode}.")
            return result.returncode
        log(f"Module '{plan.module}' finished successfully.")

    if args.run_full_pytest:
        pytest_command = build_full_pytest_command()
        log("Running full pytest suite after successful generation.")
        log(f"Command: {render_command(pytest_command)}")
        result = subprocess.run(pytest_command, cwd=ROOT, check=False)
        if result.returncode != 0:
            log(f"Full pytest failed with exit code {result.returncode}.")
            return result.returncode
        log("Full pytest suite passed.")

    log("Batch generation pipeline finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
