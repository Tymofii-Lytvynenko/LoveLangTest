from __future__ import annotations

from dataclasses import dataclass
from typing import Any, MutableMapping

from src.services.bigfive_pdf_parser import BigFivePdfParser, FACET_SPECS, HIGH_LEVEL_SESSION_KEYS


BIGFIVE_IMPORT_SOURCE_KEY = "_bigfive_facets_source"
BIGFIVE_IMPORT_FILENAME_KEY = "_bigfive_facets_filename"
BIGFIVE_UPLOAD_REVISION_KEY = "_bigfive_pdf_upload_revision"
BIGFIVE_PDF_SOURCE = "pdf"


@dataclass(frozen=True)
class BigFiveImportStatus:
    facet_count: int
    import_source: str | None
    import_filename: str | None

    @property
    def has_pdf_import(self) -> bool:
        return self.import_source == BIGFIVE_PDF_SOURCE


def apply_bigfive_pdf_scores(
    state: MutableMapping[str, Any],
    pdf_bytes: bytes,
    *,
    file_name: str | None = None,
) -> int:
    parsed = BigFivePdfParser.parse_pdf_bytes(pdf_bytes)
    for key, value in parsed.raw_scores.items():
        state[key] = value
    for key, value in parsed.high_level_scores.items():
        state[key] = value
    state[BIGFIVE_IMPORT_SOURCE_KEY] = BIGFIVE_PDF_SOURCE
    state[BIGFIVE_IMPORT_FILENAME_KEY] = file_name or ""
    return len(parsed.raw_scores)


def clear_bigfive_state(state: MutableMapping[str, Any]) -> None:
    for spec in FACET_SPECS:
        state.pop(spec.session_key, None)
    for key in HIGH_LEVEL_SESSION_KEYS.values():
        state.pop(key, None)

    state.pop(BIGFIVE_IMPORT_SOURCE_KEY, None)
    state.pop(BIGFIVE_IMPORT_FILENAME_KEY, None)
    state[BIGFIVE_UPLOAD_REVISION_KEY] = get_bigfive_upload_revision(state) + 1


def get_bigfive_import_status(state: MutableMapping[str, Any]) -> BigFiveImportStatus:
    facet_count = sum(1 for spec in FACET_SPECS if isinstance(state.get(spec.session_key), (int, float)))
    import_source = state.get(BIGFIVE_IMPORT_SOURCE_KEY)
    import_filename = state.get(BIGFIVE_IMPORT_FILENAME_KEY)
    return BigFiveImportStatus(
        facet_count=facet_count,
        import_source=str(import_source) if isinstance(import_source, str) and import_source else None,
        import_filename=str(import_filename) if isinstance(import_filename, str) and import_filename else None,
    )


def get_bigfive_upload_revision(state: MutableMapping[str, Any]) -> int:
    revision = state.get(BIGFIVE_UPLOAD_REVISION_KEY, 0)
    return int(revision) if isinstance(revision, int) else 0
