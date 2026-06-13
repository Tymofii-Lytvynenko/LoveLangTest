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

The active core questionnaire has two modes:
- Simple: 40 domain items for faster first-pass screening
- Extended: 72 domain items for a more stable profile

Simple mode contains:
- `needs.json`: 24 questions, 6 for each SRME dimension
- `shadow.json`: 8 attachment-strategy questions
- `eros.json`: 8 Dual Control Model questions

Extended mode contains:
- `needs.json`: 40 questions, 10 for each SRME dimension
- `shadow.json`: 16 attachment-strategy questions
- `eros.json`: 16 Dual Control Model questions

This keeps content separate from scoring logic and makes the banks reviewable without changing code.

When authoring banks, prefer concrete wording over abstract social inference:
- literal scenarios instead of vibes
- sensory and executive-load examples where relevant
- direct communication and repair timing over hidden social rules
- no assumption that spontaneity, eye contact, multitasking, or clutter tolerance are universally positive

## Methodology

CRNAS is not a diagnostic instrument and is not presented as a validated clinical test. It is a structured compatibility and self-description prototype: the constructs come from established research traditions, while the relationship-specific item bank is custom, transparent, and testable.

The current model combines:
- Big Five / [IPIP](https://ipip.ori.org/) facets for broad personality tendencies, because the five-factor model is one of the most replicated personality taxonomies and IPIP provides open, reviewable public-domain item pools.
- Attachment theory and adult romantic attachment research, especially Hazan and Shaver's attachment framing of romantic love ([DOI](https://doi.org/10.1037/0022-3514.52.3.511)), because compatibility often depends on closeness, distance, rupture, repair, and threat responses.
- The Dual Control Model of sexual response ([Bancroft and Janssen, 2000](https://doi.org/10.1080/00224490009552075)), because erotic compatibility is better modeled as excitation plus inhibition/context rather than as a single libido score.
- Self-Determination Theory ([Deci and Ryan, 2000](https://doi.org/10.1037/0003-066X.55.1.68)), because autonomy, competence, and relatedness are well-established psychological needs relevant to support, pressure, and repair.
- Self-Expansion research on close relationships and shared novel activity ([Aron et al., 2000](https://doi.org/10.1037/0022-3514.78.2.273)), because long-term compatibility also includes growth, curiosity, novelty, and shared exploration.
- Social exchange / investment-model thinking ([Rusbult, 1980](https://doi.org/10.1037/0022-3514.38.1.172)) for practical reciprocity, effort, task load, and resource compatibility.
- Interest and lifestyle structure inspired by RIASEC-style interest models, using [O*NET Interest Profiler](https://www.onetcenter.org/IP.html) as an authoritative applied reference.
- Neurodivergent-friendly questionnaire design informed by clinical guidance on ADHD and autism support needs, including [NICE ADHD guideline NG87](https://www.nice.org.uk/guidance/ng87) and [NICE autism guideline CG142](https://www.nice.org.uk/guidance/cg142): literal wording, low hidden inference, sensory-load examples, transition time, executive support, and optional ADHD/ASD/AuDHD context.

Custom tests are used because no ready-made validated instrument currently measures this exact integrated matrix: partner compatibility across practical support, attachment strategy, erotic activation/inhibition, neurodivergent support needs, Big Five facets, interests, and relationship-specific scenario tradeoffs. Existing validated tools cover parts of the space, but not the full product goal. Therefore CRNAS borrows reliable constructs from established literature, keeps scoring explicit, and treats the current output as structured conversation guidance rather than a final psychometric diagnosis.

Current quality controls are engineering and content guardrails, not final psychometric validation:
- question banks are schema-validated before use
- public scores are normalized to `0..1`, so adding more questions does not inflate results
- items use concrete forced-choice tradeoffs instead of obvious good/bad answers
- vectors are balanced across target dimensions and checked by tests
- profile transport uses checksums and bank fingerprints
- tests cover loading, scoring, transport, sanitization, reporting, comparison, and active bank quality

Future scientific validation should follow modern scale-development and measurement-quality standards such as [Boateng et al. on scale development](https://doi.org/10.3389/fpubh.2018.00149) and the [COSMIN](https://www.cosmin.nl/) framework: expert review, cognitive interviews, pilot data, reliability analysis, construct validity, measurement invariance, and outcome validation.

## Compatibility comparison

The app can compare two local profile strings. A profile is still client-side only: it is exported as a compact `base64url(zlib(json_payload))` string and pasted into the comparison field by the other person.

The comparison highlights:
- potentially positive matches, such as one person's strong provision matching the other person's high need
- potentially difficult gaps, such as high Safety needs paired with low Safety provision
- large differences in SRME needs
- attachment loops such as anxious/avoidant pursuit-distance dynamics
- Eros differences in activation or inhibition context

The comparison output is intentionally framed as conversation guidance. It should highlight topics to discuss, not decide whether a relationship is good or bad.

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
