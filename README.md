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

The active core questionnaire currently contains 40 domain items:
- `needs.json`: 24 questions, 6 for each SRME dimension
- `shadow.json`: 8 attachment-strategy questions
- `eros.json`: 8 Dual Control Model questions

This keeps content separate from scoring logic and makes the banks reviewable without changing code.

When authoring banks, prefer concrete wording over abstract social inference:
- literal scenarios instead of vibes
- sensory and executive-load examples where relevant
- direct communication and repair timing over hidden social rules
- no assumption that spontaneity, eye contact, multitasking, or clutter tolerance are universally positive

## Methodology

CRNAS is not a diagnostic instrument and is not presented as a validated clinical test. It is a structured compatibility and self-description prototype built from established psychological constructs, then adapted into relationship-specific scenario questions.

The main methodological bases are:
- Big Five / IPIP-style facets for broad personality tendencies and adjustment factors
- Attachment theory for closeness, distance, rupture, repair, and threat responses
- Dual Control Model for sexual excitation and inhibition
- Self-Determination Theory for autonomy, competence, and relatedness needs
- Self-Expansion Model for novelty, growth, and shared exploration
- Social exchange and household-load framing for resource, task, and logistics compatibility
- Neurodivergent-friendly questionnaire design: literal wording, low inference, sensory load, transition time, executive support, and optional ADHD/ASD/AuDHD context

The project uses custom tests and custom question banks because there is no ready-made validated instrument that measures this exact combination: partner compatibility across practical support, attachment strategy, erotic activation/inhibition, neurodivergent support needs, Big Five facets, and relationship-specific scenario tradeoffs. Existing validated instruments cover parts of the space, but not this integrated compatibility matrix. For that reason CRNAS borrows constructs from established research traditions while keeping the item bank custom, transparent, and locally testable.

Current quality controls are engineering and content guardrails, not final psychometric validation:
- every bank is schema-validated before use
- scores are normalized so the number of questions does not inflate results
- items use forced-choice tradeoffs instead of obvious good/bad answers
- vectors are balanced across target dimensions
- all public scores stay within `0..1`
- tests cover loading, scoring, transport, sanitization, reporting, and active bank quality

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
