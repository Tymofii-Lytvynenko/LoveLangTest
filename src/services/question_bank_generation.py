from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
import json
import os
import re

from src.question_bank import QuestionBank, load_question_bank_from_payload
from src.question_bank_blueprints import get_question_bank_blueprint
from src.services.question_bank_quality import QuestionBankQualityGate, QuestionBankQualityReport


DEFAULT_OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
DEFAULT_OPENROUTER_MODEL = "deepseek/deepseek-v4-flash"


class QuestionBankGenerationError(RuntimeError):
    """Raised when generation cannot produce a valid question bank."""


@dataclass(frozen=True)
class OpenRouterGenerationConfig:
    model_id: str
    api_key: str
    api_base: str = DEFAULT_OPENROUTER_API_BASE
    http_referer: str | None = None
    app_title: str | None = None
    temperature: float = 0.4
    max_tokens: int = 6000
    max_attempts: int = 3

    @classmethod
    def from_env(cls) -> "OpenRouterGenerationConfig":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise QuestionBankGenerationError("OPENROUTER_API_KEY is required.")
        return cls(
            model_id=os.getenv("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL),
            api_key=api_key,
            api_base=os.getenv("OPENROUTER_API_BASE", DEFAULT_OPENROUTER_API_BASE),
            http_referer=os.getenv("OPENROUTER_HTTP_REFERER"),
            app_title=os.getenv("OPENROUTER_APP_TITLE"),
        )


@dataclass(frozen=True)
class QuestionBankGenerationRequest:
    module: str
    question_count: int
    output_path: Path
    bank_id: str
    version: str
    audience: str = "ADHD/ASD/AuDHD-friendly, literal, low-inference"
    content_language: str = "Ukrainian (uk)"


@dataclass(frozen=True)
class QuestionBankGenerationResult:
    bank: QuestionBank
    payload: dict[str, Any]
    quality_report: QuestionBankQualityReport
    attempt_count: int
    raw_response: str


ProgressLogger = Callable[[str], None]


class SmolagentsOpenRouterQuestionBankGenerator:
    def __init__(
        self,
        config: OpenRouterGenerationConfig,
        logger: ProgressLogger | None = None,
    ) -> None:
        self.config = config
        self._logger = logger
        self._model = self._build_model()

    def _log(self, message: str) -> None:
        if self._logger is not None:
            self._logger(message)

    def generate(self, request: QuestionBankGenerationRequest) -> QuestionBankGenerationResult:
        blueprint = get_question_bank_blueprint(request.module)
        if blueprint is None:
            raise QuestionBankGenerationError(f"Unsupported module '{request.module}'.")

        self._log(
            f"Starting generation for module='{request.module}' "
            f"with {request.question_count} questions and max_attempts={self.config.max_attempts}."
        )
        self._log(f"Using model='{self.config.model_id}' and api_base='{self.config.api_base}'.")

        repair_feedback: list[str] = []
        last_exception: Exception | None = None
        for attempt in range(1, self.config.max_attempts + 1):
            self._log(f"Attempt {attempt}/{self.config.max_attempts}: calling model.")
            raw_response = self._generate_raw_json(request, blueprint, repair_feedback)
            self._log(f"Attempt {attempt}: received {len(raw_response)} characters of response text.")
            try:
                payload = self._parse_json_response(raw_response)
                self._log(f"Attempt {attempt}: JSON parsed successfully.")
                bank = load_question_bank_from_payload(payload)
                self._log(
                    f"Attempt {attempt}: loaded bank with {len(bank.questions)} questions "
                    f"and fingerprint {bank.fingerprint}."
                )
                report = QuestionBankQualityGate.evaluate(
                    bank,
                    expected_question_count=request.question_count,
                    strict_generated_bank=True,
                )
                if report.passed:
                    self._log(f"Attempt {attempt}: quality gate passed.")
                    return QuestionBankGenerationResult(
                        bank=bank,
                        payload=payload,
                        quality_report=report,
                        attempt_count=attempt,
                        raw_response=raw_response,
                    )
                repair_feedback = report.errors
                self._log(f"Attempt {attempt}: quality gate failed with {len(report.errors)} error(s).")
                for error in report.errors[:5]:
                    self._log(f"  - {error}")
                last_exception = QuestionBankGenerationError(
                    "Quality gate failed:\n- " + "\n- ".join(report.errors)
                )
            except Exception as exc:  # noqa: BLE001 - bubble up last failure with context
                repair_feedback = [str(exc)]
                last_exception = exc
                self._log(f"Attempt {attempt}: generation failed with error: {exc}")

        self._log(f"Generation failed after {self.config.max_attempts} attempt(s).")
        raise QuestionBankGenerationError(
            f"Unable to generate a valid '{request.module}' bank after {self.config.max_attempts} attempts: "
            f"{last_exception}"
        ) from last_exception

    def _build_model(self):
        try:
            from smolagents import OpenAIModel
        except ImportError as exc:  # pragma: no cover - depends on optional runtime dependency
            raise QuestionBankGenerationError(
                "smolagents OpenAI integration is not installed. Run `pip install \"smolagents[openai]\"`."
            ) from exc

        client_kwargs: dict[str, Any] = {}
        default_headers: dict[str, str] = {}
        if self.config.http_referer:
            default_headers["HTTP-Referer"] = self.config.http_referer
        if self.config.app_title:
            default_headers["X-OpenRouter-Title"] = self.config.app_title
        if default_headers:
            client_kwargs["default_headers"] = default_headers

        return OpenAIModel(
            model_id=self.config.model_id,
            api_base=self.config.api_base,
            api_key=self.config.api_key,
            client_kwargs=client_kwargs or None,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

    def _generate_raw_json(
        self,
        request: QuestionBankGenerationRequest,
        blueprint,
        repair_feedback: list[str],
    ) -> str:
        prompt = self._build_prompt(request, blueprint, repair_feedback)
        message = self._model.generate(
            [
                {
                    "role": "system",
                    "content": self._build_system_prompt(blueprint),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format={"type": "json_object"},
        )
        return self._coerce_message_text(message)

    @staticmethod
    def _build_system_prompt(blueprint) -> str:
        scientific_basis = "\n".join(f"- {item}" for item in blueprint.scientific_basis)
        audience_notes = "\n".join(f"- {item}" for item in blueprint.audience_notes)
        localized_labels = ", ".join(blueprint.display_vector_labels)
        return f"""
You are the CRNAS scientific item writer and structured question-bank generator.

Your job is to generate questionnaire items that are as scientifically grounded, psychometrically cautious,
and behaviorally interpretable as possible inside the limits of an LLM workflow.

Epistemic rules:
- Stay evidence-constrained. Use only constructs explicitly requested by the CRNAS module and its declared scientific basis.
- Do not invent theories, diagnostic claims, prevalence claims, treatment advice, or unsupported causal explanations.
- Do not present speculation as scientific fact.
- If a construct could be confounded, resolve it through clearer wording rather than through explanation after the item.

Scientific basis for this module:
{scientific_basis}

Audience and interpretation rules:
{audience_notes}
- All user-facing content in the generated bank must be written in natural Ukrainian.
- The fields `question`, `description`, and every `options[*].text` must be Ukrainian.
- Avoid English or Russian wording in user-facing text, except short acronyms such as ADHD, ASD, or AuDHD when strictly needed.
- If user-facing text mentions the bank dimensions, use only these Ukrainian labels: {localized_labels}.
- Never use raw English vector labels such as {", ".join(blueprint.vector_labels)} inside user-facing text.
- JSON keys, stable ids, and `metadata.authoring_instructions` may remain in English if that better preserves schema clarity and future LLM reuse.
- Treat ADHD, ASD, and AuDHD as optional context for support needs, sensory load, predictability, recovery,
  communication style, and executive scaffolding.
- Never frame neurodivergence as moral failure, low worth, low empathy by default, or relationship incapacity.
- Distinguish attachment threat from sensory overload, shutdown, burnout, delayed processing, masking fatigue,
  novelty-seeking, and executive dysfunction whenever those could be mistaken for one another.

Item-writing standards:
- Every item must probe one concrete relational tension, tradeoff, rupture, repair pattern, support pattern, or desire-regulation pattern.
- Use literal, observable, low-inference scenarios. Prefer behavior and context over identity labels or abstract vibes.
- Avoid double-barreled items, hidden assumptions, metaphors, vague symbolism, and culture-war framing.
- Avoid yes/no preference questions when a forced-choice tradeoff can be written instead.
- Avoid leading language that makes one answer sound healthier, more evolved, more mature, or more scientific.
- Avoid moralizing, spiritualized, essentialist, gender-essentialist, and pseudo-scientific language.
- Options must be mutually exclusive enough that a respondent can recognize a best fit.
- Options must all sound plausible to a real person; do not create one absurd distractor and one obviously correct answer.
- Descriptions must explain what construct or tension the item probes, not repeat the question text.

Scoring and bank-construction standards:
- Follow the exact vector label order supplied by the user prompt.
- Keep every vector numeric and within the supplied magnitude limits.
- Use negative values only when an option actively moves away from a dimension rather than merely failing to maximize it.
- Preserve meaningful tradeoffs across the bank; do not make every strong option increase every dimension.
- Maintain balanced coverage across the target dimensions and core scenario clusters.
- Do not duplicate item semantics under slightly different wording.

Module-specific discipline:
- If the module is attachment/shadow, keep the focus on rupture, distance, dependence, repair, and threat response.
- If the module is needs, keep the focus on Safety / Resource / Resonance / Expansion tradeoffs in real life.
- If the module is eros, follow the Dual Control Model and distinguish activation from inhibition without moral ranking.

Output protocol:
- Return one strict JSON object only.
- Never wrap the output in markdown.
- Never add commentary before or after the JSON.
- Keep every JSON string value on a single line. Do not emit multiline string literals.
- Before finalizing internally self-check for: schema compliance, construct clarity, confound control, balance, tradeoff quality,
  neurodivergent-friendliness, and absence of pseudo-scientific language.
""".strip()

    @staticmethod
    def _coerce_message_text(message: Any) -> str:
        if isinstance(message, str):
            return message
        content = getattr(message, "content", None)
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict) and isinstance(item.get("text"), str):
                    parts.append(item["text"])
            if parts:
                return "".join(parts)
        if hasattr(message, "model_dump"):
            dumped = message.model_dump()
            if isinstance(dumped, dict):
                dumped_content = dumped.get("content")
                if isinstance(dumped_content, str):
                    return dumped_content
        raise QuestionBankGenerationError(f"Unable to extract text from model response of type {type(message)!r}.")

    @staticmethod
    def _parse_json_response(raw_response: str) -> dict[str, Any]:
        candidate = SmolagentsOpenRouterQuestionBankGenerator._extract_json_object_text(raw_response)
        json_error: json.JSONDecodeError | None = None

        for variant in SmolagentsOpenRouterQuestionBankGenerator._iter_json_candidates(candidate):
            try:
                payload = json.loads(variant)
                break
            except json.JSONDecodeError as exc:
                json_error = exc
        else:
            python_like_candidate = (
                SmolagentsOpenRouterQuestionBankGenerator._convert_outside_strings_json_literals_to_python(
                    SmolagentsOpenRouterQuestionBankGenerator._strip_trailing_commas(candidate)
                )
            )
            try:
                payload = ast.literal_eval(python_like_candidate)
            except (SyntaxError, ValueError) as exc:
                raise QuestionBankGenerationError(
                    SmolagentsOpenRouterQuestionBankGenerator._format_json_parse_error(
                        candidate,
                        json_error or exc,
                    )
                ) from exc
        if not isinstance(payload, dict):
            raise QuestionBankGenerationError("The generated payload must be a JSON object.")
        return payload

    @staticmethod
    def _extract_json_object_text(raw_response: str) -> str:
        candidate = raw_response.strip()
        if candidate.startswith("```"):
            lines = candidate.splitlines()
            if lines and lines[0].strip().startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            candidate = "\n".join(lines).strip()
            if candidate.lower().startswith("json"):
                candidate = candidate[4:].strip()

        start = candidate.find("{")
        end = candidate.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = candidate[start : end + 1]
        return candidate.strip()

    @staticmethod
    def _iter_json_candidates(candidate: str) -> tuple[str, ...]:
        repaired_candidate = SmolagentsOpenRouterQuestionBankGenerator._strip_trailing_commas(candidate)
        variants: list[str] = [candidate]
        if repaired_candidate != candidate:
            variants.append(repaired_candidate)
        return tuple(variants)

    @staticmethod
    def _strip_trailing_commas(candidate: str) -> str:
        return re.sub(r",(?=\s*[}\]])", "", candidate)

    @staticmethod
    def _convert_outside_strings_json_literals_to_python(candidate: str) -> str:
        replacements = {
            "true": "True",
            "false": "False",
            "null": "None",
        }
        result: list[str] = []
        token_buffer: list[str] = []
        in_string = False
        escape = False

        def flush_token() -> None:
            if not token_buffer:
                return
            token = "".join(token_buffer)
            result.append(replacements.get(token, token))
            token_buffer.clear()

        for char in candidate:
            if in_string:
                result.append(char)
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
                continue

            if char == '"':
                flush_token()
                in_string = True
                result.append(char)
                continue

            if char.isalpha():
                token_buffer.append(char)
                continue

            flush_token()
            result.append(char)

        flush_token()
        return "".join(result)

    @staticmethod
    def _format_json_parse_error(candidate: str, error: Exception) -> str:
        if isinstance(error, json.JSONDecodeError):
            position = error.pos
            prefix = f"{error.msg} at line {error.lineno} column {error.colno} (char {error.pos})"
        elif isinstance(error, SyntaxError):
            position = max((error.offset or 1) - 1, 0)
            prefix = f"{error.msg} at line {error.lineno or 1} column {error.offset or 1}"
        else:
            position = 0
            prefix = str(error)

        start = max(position - 100, 0)
        end = min(position + 100, len(candidate))
        snippet = candidate[start:position] + "<<<HERE>>>" + candidate[position:end]
        compact_snippet = snippet.replace("\r", "\\r").replace("\n", "\\n")
        return (
            "Model returned invalid JSON. "
            f"{prefix}. Context: {compact_snippet}. "
            "Return one strict JSON object only, with no trailing commas, comments, or multiline string values."
        )

    @staticmethod
    def _build_prompt(request: QuestionBankGenerationRequest, blueprint, repair_feedback: list[str]) -> str:
        existing_instructions = SmolagentsOpenRouterQuestionBankGenerator._load_existing_authoring_instructions(
            request.module
        )
        scientific_basis = "\n".join(f"- {item}" for item in blueprint.scientific_basis)
        audience_notes = "\n".join(f"- {item}" for item in blueprint.audience_notes)
        localized_labels = ", ".join(
            f"{raw} -> {localized}"
            for raw, localized in zip(blueprint.vector_labels, blueprint.display_vector_labels)
        )
        coverage_clusters = "\n".join(
            f"- {cluster.name}: {', '.join(cluster.keywords)}" for cluster in blueprint.coverage_clusters
        )
        balance_hint = SmolagentsOpenRouterQuestionBankGenerator._build_balance_hint(
            request.question_count,
            blueprint.vector_labels,
            blueprint.display_vector_labels,
        )
        banned_terms = ", ".join(blueprint.banned_terms)
        repair_block = ""
        if repair_feedback:
            repair_block = (
                "\nThe previous draft failed these validation checks. Fix every issue in the next draft:\n- "
                + "\n- ".join(repair_feedback)
                + "\n"
            )
            repair_block += SmolagentsOpenRouterQuestionBankGenerator._build_repair_guidance(
                repair_feedback,
                blueprint.vector_labels,
                blueprint.display_vector_labels,
            )

        return f"""
Generate a CRNAS question bank for module "{request.module}".

Output requirements:
- Return one JSON object only.
- Use this exact root shape:
  {{
    "metadata": {{
      "bank_id": "{request.bank_id}",
      "version": "{request.version}",
      "module": "{request.module}",
      "authoring_instructions": "...",
      "vector_labels": {json.dumps(list(blueprint.vector_labels), ensure_ascii=False)}
    }},
    "questions": [
      {{
        "id": "stable_snake_case_id",
        "question": "clear literal question",
        "description": "one-line explanation of what tension or tradeoff this item probes",
        "options": [
          {{
            "id": "opt_1",
            "text": "behaviorally concrete answer option",
            "vector": [numbers matching vector_labels]
          }}
        ]
      }}
    ]
  }}

Hard constraints:
- Create exactly {request.question_count} questions.
- Every question must be a forced-choice scenario with a real tradeoff.
- Keep wording literal, concrete, and understandable for {request.audience}.
- All user-facing content must be in {request.content_language}.
- If descriptions mention dimensions, use Ukrainian labels only: {localized_labels}.
- Include descriptions for every question.
- Option count per question must stay between {blueprint.min_options_per_question} and {blueprint.max_options_per_question}.
- Every vector value must stay within +/-{blueprint.max_vector_magnitude}.
- Avoid any pseudo-scientific, mystical, or moralizing framing.
- Do not mention diagnoses as defects. Treat ADHD/ASD/AuDHD as context for support needs, sensory load, predictability, recovery, or executive scaffolding.
- `metadata.authoring_instructions` may stay in English, but the questionnaire content shown to users must stay Ukrainian.
- Keep every JSON string value on one line. Do not place literal line breaks inside quoted strings.
- Primary question coverage should stay balanced across the dimensions.
- {balance_hint}

Scientific basis to respect:
{scientific_basis}

Audience notes:
{audience_notes}

Core coverage clusters to distribute across the bank:
{coverage_clusters}

Banned terms and framings:
{banned_terms}

Reference authoring instructions from the current CRNAS bank:
{existing_instructions}
{repair_block}
Return the final JSON object only.
""".strip()

    @staticmethod
    def _build_balance_hint(
        question_count: int,
        vector_labels: tuple[str, ...],
        display_vector_labels: tuple[str, ...],
    ) -> str:
        base = question_count // len(vector_labels)
        remainder = question_count % len(vector_labels)
        parts: list[str] = []
        for index, label in enumerate(display_vector_labels):
            target = base + (1 if index < remainder else 0)
            parts.append(f"{label}: about {target} primary questions")
        return "Aim for this approximate primary-dimension split: " + "; ".join(parts) + "."

    @staticmethod
    def _build_repair_guidance(
        repair_feedback: list[str],
        vector_labels: tuple[str, ...],
        display_vector_labels: tuple[str, ...],
    ) -> str:
        notes: list[str] = []
        joined_feedback = "\n".join(repair_feedback).lower()
        if "non-ukrainian latin user-facing text" in joined_feedback:
            notes.append(
                "Rewrite every user-facing field fully in Ukrainian. "
                "If you mention dimensions, replace raw labels "
                f"{', '.join(vector_labels)} with {', '.join(display_vector_labels)}."
            )
        if "overly skewed across dimensions" in joined_feedback:
            notes.append(
                "Rebalance the bank so the primary focus of questions is distributed as evenly as possible across all dimensions."
            )
        if "invalid json" in joined_feedback or "expecting value at line" in joined_feedback:
            notes.append(
                "Return one strict JSON object only. Do not include trailing commas, comments, markdown fences, or multiline string values."
            )
        if not notes:
            return ""
        return "\nAdditional repair guidance:\n- " + "\n- ".join(notes) + "\n"

    @staticmethod
    def _load_existing_authoring_instructions(module: str) -> str:
        path = Path(__file__).resolve().parent.parent.parent / "question_bank" / f"{module}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        return str(payload["metadata"]["authoring_instructions"])
