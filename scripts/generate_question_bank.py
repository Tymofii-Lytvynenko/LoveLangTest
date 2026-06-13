from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.services.question_bank_generation import (  # noqa: E402
    OpenRouterGenerationConfig,
    QuestionBankGenerationRequest,
    SmolagentsOpenRouterQuestionBankGenerator,
)
from src.services.question_bank_quality import QuestionBankQualityGate  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a CRNAS question bank with smolagents + OpenRouter and validate it."
    )
    parser.add_argument("--module", choices=["needs", "shadow", "eros"], required=True)
    parser.add_argument("--questions", type=int, required=True, help="Exact number of questions to generate.")
    parser.add_argument("--output", type=Path, required=True, help="Target JSON file.")
    parser.add_argument("--bank-id", help="metadata.bank_id value. Default: crnas-<module>-generated")
    parser.add_argument("--version", default="0.1.0", help="metadata.version value.")
    parser.add_argument("--max-attempts", type=int, default=3, help="How many repair attempts the generator may use.")
    parser.add_argument("--skip-pytest", action="store_true", help="Skip the generated-bank pytest contract.")
    parser.add_argument("--force", action="store_true", help="Overwrite the output file if it already exists.")
    parser.add_argument(
        "--quality-report",
        type=Path,
        help="Where to write the quality JSON report. Default: <output>.quality.json",
    )
    return parser


def log(message: str) -> None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)


def run_pytest_contract(output_path: Path, expected_question_count: int) -> None:
    command = [
        sys.executable,
        "-m",
        "pytest",
        "tests/test_generated_bank_contract.py",
        f"--generated-bank={output_path}",
        f"--expected-question-count={expected_question_count}",
    ]
    log("Running pytest contract for the generated bank.")
    result = subprocess.run(command, cwd=ROOT, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    log("Pytest contract passed.")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    output_path: Path = args.output.resolve()
    if output_path.exists() and not args.force:
        parser.error(f"Output file already exists: {output_path}. Use --force to overwrite it.")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    config = OpenRouterGenerationConfig.from_env()
    config = OpenRouterGenerationConfig(
        model_id=config.model_id,
        api_key=config.api_key,
        api_base=config.api_base,
        http_referer=config.http_referer,
        app_title=config.app_title,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        max_attempts=args.max_attempts,
    )

    log("Starting CRNAS question-bank generation.")
    log(f"Module: {args.module}")
    log(f"Questions: {args.questions}")
    log(f"Output: {output_path}")
    log(f"Model: {config.model_id}")
    log(f"API base: {config.api_base}")
    if args.bank_id:
        log(f"Bank ID: {args.bank_id}")

    request = QuestionBankGenerationRequest(
        module=args.module,
        question_count=args.questions,
        output_path=output_path,
        bank_id=args.bank_id or f"crnas-{args.module}-generated",
        version=args.version,
    )

    generator = SmolagentsOpenRouterQuestionBankGenerator(config, logger=log)
    log("Calling LLM generator.")
    result = generator.generate(request)
    log("Generation completed. Writing JSON payload to disk.")

    output_path.write_text(
        json.dumps(result.payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    quality_report_path = args.quality_report or output_path.with_suffix(".quality.json")
    QuestionBankQualityGate.write_report(quality_report_path, result.quality_report)
    log(f"Saved initial quality report: {quality_report_path}")

    # Re-run the gate from disk so the on-disk artifact is guaranteed to match the saved report.
    log("Re-running quality gate against the saved file.")
    saved_report = QuestionBankQualityGate.evaluate_path(
        output_path,
        expected_question_count=args.questions,
        strict_generated_bank=True,
    )
    saved_report.require_pass()
    QuestionBankQualityGate.write_report(quality_report_path, saved_report)
    log("Quality gate passed on saved file.")

    log(f"Generated {args.module} bank: {output_path}")
    log(f"Quality report: {quality_report_path}")
    log(f"Attempts used: {result.attempt_count}")

    if not args.skip_pytest:
        run_pytest_contract(output_path, args.questions)
    else:
        log("Skipping pytest contract by request.")

    log("Generation pipeline finished successfully.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
