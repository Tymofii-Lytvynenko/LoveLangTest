import pytest

from src.services.profile_codec import ProfileCodec, ProfileCodecError


def test_profile_payload_roundtrip() -> None:
    state = {"scenario_conf_01": "opt_1", "psycho_o": 75}
    encoded = ProfileCodec.encode_state(state, bank_fingerprint="bank-fp-1")
    payload = ProfileCodec.decode_string(encoded)

    assert payload.bank_fingerprint == "bank-fp-1"
    assert payload.state == state


def test_profile_payload_checksum_is_verified() -> None:
    payload = ProfileCodec.build_payload({"scenario_conf_01": "opt_1"}, "bank-fp-1")
    raw_payload = ProfileCodec.to_json_dict(payload)
    raw_payload["checksum"] = "broken"

    with pytest.raises(ProfileCodecError):
        ProfileCodec.from_json_dict(raw_payload)
