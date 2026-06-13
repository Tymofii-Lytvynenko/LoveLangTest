from __future__ import annotations

from streamlit.testing.v1 import AppTest

from src.services.bigfive_pdf_parser import FACET_SPECS
from src.services.bigfive_state import (
    BIGFIVE_IMPORT_FILENAME_KEY,
    BIGFIVE_IMPORT_SOURCE_KEY,
    BIGFIVE_PDF_SOURCE,
)


def _build_app() -> AppTest:
    return AppTest.from_file("streamlit_app.py")


def _info_values(app: AppTest) -> list[str]:
    return [element.value for element in app.info]


def _uploader_labels(app: AppTest) -> list[str]:
    return [element.proto.label for element in app.get("file_uploader")]


def test_ui_defaults_to_extended_mode_and_shows_pdf_import_controls() -> None:
    app = _build_app()
    app.run()

    questionnaire_mode = next(radio for radio in app.radio if radio.key == "questionnaire_mode")
    buttons = {button.label: button for button in app.button}

    assert questionnaire_mode.value == "extended"
    assert "PDF результатів BigFive" in _uploader_labels(app)
    assert buttons["Імпортувати PDF"].disabled is True
    assert "Завантажте PDF, щоб не вводити 30 facets вручну." in _info_values(app)


def test_ui_does_not_claim_pdf_import_when_only_manual_facet_state_exists() -> None:
    app = _build_app()
    for spec in FACET_SPECS:
        app.session_state[spec.session_key] = 10

    app.run()

    info_values = _info_values(app)
    assert "Завантажте PDF, щоб не вводити 30 facets вручну." in info_values
    assert not any("PDF-імпорт" in message for message in info_values)


def test_ui_shows_pdf_import_status_only_when_metadata_exists() -> None:
    app = _build_app()
    for spec in FACET_SPECS:
        app.session_state[spec.session_key] = 11
    app.session_state[BIGFIVE_IMPORT_SOURCE_KEY] = BIGFIVE_PDF_SOURCE
    app.session_state[BIGFIVE_IMPORT_FILENAME_KEY] = "results.pdf"

    app.run()

    assert any(
        message == "Активний PDF-імпорт: 30 з 30 facets із `results.pdf`."
        for message in _info_values(app)
    )
