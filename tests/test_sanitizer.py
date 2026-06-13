from src.enums import HollandCode
from src.services.sanitizer import StateSanitizer


def test_sanitizer_revalidates_state_against_current_bank() -> None:
    clean_state, removal_log = StateSanitizer.sanitize(
        incoming_state={
            "scenario_conf_01": "opt_1",
            "unknown_field": "bad",
        },
        incoming_bank_fingerprint="old-bank-fingerprint",
    )

    assert clean_state["scenario_conf_01"] == "opt_1"
    assert any("іншій версії банку" in item for item in removal_log)
    assert any("невідоме поле" in item for item in removal_log)


def test_sanitizer_normalizes_enum_values_to_names() -> None:
    clean_state, removal_log = StateSanitizer.sanitize(
        incoming_state={"prof_primary": HollandCode.REALISTIC.value},
        incoming_bank_fingerprint=StateSanitizer.get_current_bank_fingerprint(),
    )

    assert not removal_log
    assert clean_state["prof_primary"] == HollandCode.REALISTIC.name


def test_sanitizer_keeps_bigfive_pdf_input_mode() -> None:
    clean_state, removal_log = StateSanitizer.sanitize(
        incoming_state={"psycho_input_mode": "pdf"},
        incoming_bank_fingerprint=StateSanitizer.get_current_bank_fingerprint(),
    )

    assert not removal_log
    assert clean_state["psycho_input_mode"] == "pdf"
