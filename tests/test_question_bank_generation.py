import pytest

from src.question_bank_blueprints import QUESTION_BANK_BLUEPRINTS
from src.services.question_bank_generation import (
    DEFAULT_OPENROUTER_MODEL,
    OpenRouterGenerationConfig,
    QuestionBankGenerationError,
    SmolagentsOpenRouterQuestionBankGenerator,
)


def test_openrouter_config_requires_key_and_defaults_model(monkeypatch) -> None:
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(QuestionBankGenerationError):
        OpenRouterGenerationConfig.from_env()

    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    config = OpenRouterGenerationConfig.from_env()

    assert config.api_key == "test-key"
    assert config.model_id == DEFAULT_OPENROUTER_MODEL


def test_parse_json_response_extracts_object_from_fenced_output() -> None:
    raw = """```json
    {"metadata": {"module": "needs"}}
    ```"""

    payload = SmolagentsOpenRouterQuestionBankGenerator._parse_json_response(raw)

    assert payload["metadata"]["module"] == "needs"


def test_parse_json_response_repairs_trailing_commas() -> None:
    raw = """
    {
      "metadata": {
        "module": "needs",
        "draft": true,
      },
      "questions": [],
    }
    """

    payload = SmolagentsOpenRouterQuestionBankGenerator._parse_json_response(raw)

    assert payload["metadata"]["module"] == "needs"
    assert payload["metadata"]["draft"] is True


def test_parse_json_response_surfaces_context_for_invalid_json() -> None:
    raw = '{"metadata": {"module": "needs"}, "questions": [1,,2]}'

    with pytest.raises(QuestionBankGenerationError) as exc_info:
        SmolagentsOpenRouterQuestionBankGenerator._parse_json_response(raw)

    message = str(exc_info.value)
    assert "Model returned invalid JSON." in message
    assert "Context:" in message
    assert "<<<HERE>>>" in message


def test_system_prompt_contains_scientific_and_confound_guardrails() -> None:
    prompt = SmolagentsOpenRouterQuestionBankGenerator._build_system_prompt(
        QUESTION_BANK_BLUEPRINTS["needs"]
    )

    assert "evidence-constrained" in prompt
    assert "Distinguish attachment threat from sensory overload" in prompt
    assert "Never frame neurodivergence as moral failure" in prompt
    assert "All user-facing content in the generated bank must be written in natural Ukrainian." in prompt
    assert "Never use raw English vector labels such as safety, resource, resonance, expansion" in prompt
    assert "Return one strict JSON object only." in prompt


def test_prompt_builders_include_balance_and_localized_label_guidance() -> None:
    balance_hint = SmolagentsOpenRouterQuestionBankGenerator._build_balance_hint(
        12,
        QUESTION_BANK_BLUEPRINTS["needs"].vector_labels,
        QUESTION_BANK_BLUEPRINTS["needs"].display_vector_labels,
    )
    repair_guidance = SmolagentsOpenRouterQuestionBankGenerator._build_repair_guidance(
        [
            "Generated bank contains non-Ukrainian Latin user-facing text.",
            "Module 'needs' is overly skewed across dimensions.",
        ],
        QUESTION_BANK_BLUEPRINTS["needs"].vector_labels,
        QUESTION_BANK_BLUEPRINTS["needs"].display_vector_labels,
    )

    assert "about 3 primary questions" in balance_hint
    assert "safety, resource, resonance, expansion" in repair_guidance
    assert "distributed as evenly as possible" in repair_guidance


def test_repair_guidance_includes_json_constraints() -> None:
    repair_guidance = SmolagentsOpenRouterQuestionBankGenerator._build_repair_guidance(
        ["Model returned invalid JSON. Expecting value at line 10 column 4 (char 120)."],
        QUESTION_BANK_BLUEPRINTS["needs"].vector_labels,
        QUESTION_BANK_BLUEPRINTS["needs"].display_vector_labels,
    )

    assert "strict JSON object only" in repair_guidance
    assert "trailing commas" in repair_guidance
