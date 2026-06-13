from __future__ import annotations

from src.services.bigfive_pdf_parser import FACET_SPECS, HIGH_LEVEL_SESSION_KEYS, ParsedBigFiveFacets
from src.services.bigfive_state import (
    BIGFIVE_IMPORT_FILENAME_KEY,
    BIGFIVE_IMPORT_SOURCE_KEY,
    BIGFIVE_PDF_SOURCE,
    BIGFIVE_UPLOAD_REVISION_KEY,
    apply_bigfive_pdf_scores,
    clear_bigfive_state,
    get_bigfive_import_status,
)


def _raw_facet_scores() -> dict[str, int]:
    return {
        spec.session_key: (index % 21)
        for index, spec in enumerate(FACET_SPECS, start=1)
    }


def test_apply_bigfive_pdf_scores_sets_scores_and_import_metadata(monkeypatch) -> None:
    raw_scores = _raw_facet_scores()
    parsed = ParsedBigFiveFacets(raw_scores=raw_scores)

    monkeypatch.setattr(
        "src.services.bigfive_state.BigFivePdfParser.parse_pdf_bytes",
        lambda _: parsed,
    )

    state: dict[str, object] = {}
    imported_count = apply_bigfive_pdf_scores(state, b"fake-pdf", file_name="results.pdf")

    assert imported_count == len(FACET_SPECS)
    assert state[BIGFIVE_IMPORT_SOURCE_KEY] == BIGFIVE_PDF_SOURCE
    assert state[BIGFIVE_IMPORT_FILENAME_KEY] == "results.pdf"
    for key, value in raw_scores.items():
        assert state[key] == value
    for domain_key in HIGH_LEVEL_SESSION_KEYS.values():
        assert domain_key in state


def test_get_bigfive_import_status_does_not_treat_manual_facets_as_pdf_import() -> None:
    state = {spec.session_key: 10 for spec in FACET_SPECS}

    status = get_bigfive_import_status(state)

    assert status.facet_count == len(FACET_SPECS)
    assert not status.has_pdf_import
    assert status.import_source is None
    assert status.import_filename is None


def test_clear_bigfive_state_removes_scores_and_bumps_upload_revision() -> None:
    state: dict[str, object] = {
        **{spec.session_key: 12 for spec in FACET_SPECS},
        **{key: 55 for key in HIGH_LEVEL_SESSION_KEYS.values()},
        BIGFIVE_IMPORT_SOURCE_KEY: BIGFIVE_PDF_SOURCE,
        BIGFIVE_IMPORT_FILENAME_KEY: "results.pdf",
        BIGFIVE_UPLOAD_REVISION_KEY: 2,
    }

    clear_bigfive_state(state)

    for spec in FACET_SPECS:
        assert spec.session_key not in state
    for key in HIGH_LEVEL_SESSION_KEYS.values():
        assert key not in state
    assert BIGFIVE_IMPORT_SOURCE_KEY not in state
    assert BIGFIVE_IMPORT_FILENAME_KEY not in state
    assert state[BIGFIVE_UPLOAD_REVISION_KEY] == 3
