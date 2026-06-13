# CRNAS

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://lovelangtest.streamlit.app/)

CRNAS is a Streamlit prototype for a structured relationship-needs profile based on:
- Big Five facet adjustments
- SRME needs scoring
- attachment / shadow patterns
- Dual Control Model for eros
- RIASEC professional style

The current calibration especially tries to stay usable for neurodivergent users:
- ADHD
- autism / ASD
- AuDHD

These flags are optional self-identified context. They do not diagnose anything and are only used to interpret support load, predictability, directness, and household coordination a bit more carefully.

## Run locally

1. Install runtime dependencies:

```bash
pip install -r requirements.txt
```

2. Run the app:

```bash
streamlit run streamlit_app.py
```

## Dev setup

Install test dependencies:

```bash
pip install -r requirements-dev.txt
```

Run tests:

```bash
pytest
```

## LLM question-bank generation

Install the optional generation stack:

```bash
pip install -r requirements-llm.txt
```

Set environment variables:

```bash
OPENROUTER_API_KEY=...
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
OPENROUTER_HTTP_REFERER=https://your-app.example
OPENROUTER_APP_TITLE=CRNAS Bank Generator
```

`OPENROUTER_MODEL` is optional. If you do not set it, the generator defaults to `deepseek/deepseek-v4-flash`.

Generate a bank and automatically validate it:

```bash
python scripts/generate_question_bank.py --module needs --questions 12 --output question_bank/generated_needs.json
```

Generate all three banks in one pass:

```bash
python scripts/generate_all_question_banks.py --force --run-full-pytest
```

The generator will:
- call OpenRouter through `smolagents`
- validate the JSON shape against the CRNAS bank schema
- run balance and evidence-alignment checks
- require all user-facing questionnaire content to be in Ukrainian
- run `pytest tests/test_generated_bank_contract.py` against the saved file

Important: these checks are scientific guardrails, not a substitute for expert psychometric review or external validation studies.

## Question banks

External question banks live in `question_bank/`:
- `needs.json`
- `shadow.json`
- `eros.json`

Each bank includes:
- `metadata.bank_id`
- `metadata.version`
- `metadata.module`
- `metadata.authoring_instructions`
- `metadata.vector_labels`
- `questions`

This keeps content separate from scoring logic and makes the banks easy to regenerate with LLMs.

When authoring or regenerating banks, prefer concrete wording over abstract social inference:
- literal scenarios instead of vibes
- sensory and executive-load examples where relevant
- direct communication and repair timing over hidden social rules
- no assumption that spontaneity, eye contact, multitasking, or clutter tolerance are universally positive

## Profile transport

Profiles are portable without server-side storage:
- main format: compact `base64url(zlib(json_payload))` string
- dev/debug format: the same payload exported as JSON

The payload contains:
- `format_version`
- `bank_fingerprint`
- `state`
- `created_at`
- `checksum`
