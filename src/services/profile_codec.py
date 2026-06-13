from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, UTC
import base64
import hashlib
import json
import zlib
from typing import Any


class ProfileCodecError(ValueError):
    """Raised when encoded profile data is malformed or invalid."""


@dataclass(frozen=True)
class ProfilePayload:
    format_version: str
    bank_fingerprint: str
    state: dict[str, Any]
    created_at: str
    checksum: str


class ProfileCodec:
    FORMAT_VERSION = "4.0"

    @staticmethod
    def _canonical_payload_data(payload_data: Mapping[str, Any]) -> str:
        return json.dumps(
            payload_data,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    @staticmethod
    def _calculate_checksum(payload_data: Mapping[str, Any]) -> str:
        canonical = ProfileCodec._canonical_payload_data(payload_data)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def build_payload(
        state: Mapping[str, Any],
        bank_fingerprint: str,
        created_at: str | None = None,
    ) -> ProfilePayload:
        created_at = created_at or datetime.now(UTC).isoformat()
        payload_data = {
            "format_version": ProfileCodec.FORMAT_VERSION,
            "bank_fingerprint": bank_fingerprint,
            "state": dict(state),
            "created_at": created_at,
        }
        checksum = ProfileCodec._calculate_checksum(payload_data)
        return ProfilePayload(checksum=checksum, **payload_data)

    @staticmethod
    def to_json_dict(payload: ProfilePayload) -> dict[str, Any]:
        return {
            "format_version": payload.format_version,
            "bank_fingerprint": payload.bank_fingerprint,
            "state": payload.state,
            "created_at": payload.created_at,
            "checksum": payload.checksum,
        }

    @staticmethod
    def from_json_dict(raw_payload: Mapping[str, Any]) -> ProfilePayload:
        required_fields = {
            "format_version",
            "bank_fingerprint",
            "state",
            "created_at",
            "checksum",
        }
        missing_fields = sorted(field for field in required_fields if field not in raw_payload)
        if missing_fields:
            raise ProfileCodecError(f"Missing profile payload fields: {', '.join(missing_fields)}")
        if not isinstance(raw_payload["state"], Mapping):
            raise ProfileCodecError("Profile payload field 'state' must be an object.")

        payload = ProfilePayload(
            format_version=str(raw_payload["format_version"]),
            bank_fingerprint=str(raw_payload["bank_fingerprint"]),
            state=dict(raw_payload["state"]),
            created_at=str(raw_payload["created_at"]),
            checksum=str(raw_payload["checksum"]),
        )
        ProfileCodec.validate_payload(payload)
        return payload

    @staticmethod
    def validate_payload(payload: ProfilePayload) -> None:
        payload_data = {
            "format_version": payload.format_version,
            "bank_fingerprint": payload.bank_fingerprint,
            "state": payload.state,
            "created_at": payload.created_at,
        }
        expected_checksum = ProfileCodec._calculate_checksum(payload_data)
        if expected_checksum != payload.checksum:
            raise ProfileCodecError("Profile payload checksum mismatch.")

    @staticmethod
    def encode_payload(payload: ProfilePayload) -> str:
        raw_json = json.dumps(
            ProfileCodec.to_json_dict(payload),
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        compressed = zlib.compress(raw_json)
        encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
        return encoded.rstrip("=")

    @staticmethod
    def encode_state(state: Mapping[str, Any], bank_fingerprint: str) -> str:
        payload = ProfileCodec.build_payload(state=state, bank_fingerprint=bank_fingerprint)
        return ProfileCodec.encode_payload(payload)

    @staticmethod
    def decode_string(encoded_payload: str) -> ProfilePayload:
        encoded_payload = encoded_payload.strip()
        if not encoded_payload:
            raise ProfileCodecError("Encoded profile string is empty.")

        padding = "=" * (-len(encoded_payload) % 4)
        try:
            compressed = base64.urlsafe_b64decode(encoded_payload + padding)
            raw_json = zlib.decompress(compressed).decode("utf-8")
            raw_payload = json.loads(raw_json)
        except Exception as exc:  # noqa: BLE001
            raise ProfileCodecError("Unable to decode profile string.") from exc

        return ProfileCodec.from_json_dict(raw_payload)
