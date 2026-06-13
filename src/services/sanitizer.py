from __future__ import annotations

from enum import Enum
from typing import Any, Mapping

from src.data import EROS_TAGS_EXPLANATIONS
from src.enums import (
    AttachmentStyle,
    ConflictResponse,
    ContextDependency,
    HollandCode,
    RegulationMethod,
)
from src.question_bank import get_question_bank_registry, question_state_key

FACET_KEYS = {
    "facet_neur_anxiety",
    "facet_neur_hostility",
    "facet_neur_depression",
    "facet_neur_self_consciousness",
    "facet_neur_impulsiveness",
    "facet_neur_vulnerability",
    "facet_extr_warmth",
    "facet_extr_gregariousness",
    "facet_extr_assertiveness",
    "facet_extr_activity",
    "facet_extr_excitement_seeking",
    "facet_extr_positive_emotions",
    "facet_open_fantasy",
    "facet_open_aesthetics",
    "facet_open_feelings",
    "facet_open_actions",
    "facet_open_ideas",
    "facet_open_values",
    "facet_agre_trust",
    "facet_agre_straightforwardness",
    "facet_agre_altruism",
    "facet_agre_compliance",
    "facet_agre_modesty",
    "facet_agre_tender_mindedness",
    "facet_cons_competence",
    "facet_cons_order",
    "facet_cons_dutifulness",
    "facet_cons_achievement",
    "facet_cons_self_discipline",
    "facet_cons_deliberation",
}


class StateSanitizer:
    @staticmethod
    def get_current_bank_fingerprint() -> str:
        return get_question_bank_registry().fingerprint

    @staticmethod
    def extract_persistable_state(source_state: Mapping[str, Any]) -> dict[str, Any]:
        clean_state, _ = StateSanitizer.sanitize(
            incoming_state={
                key: value
                for key, value in source_state.items()
                if not key.startswith("FormSubmitter")
            },
            incoming_bank_fingerprint=StateSanitizer.get_current_bank_fingerprint(),
        )
        return clean_state

    @staticmethod
    def sanitize(
        incoming_state: Mapping[str, Any],
        incoming_bank_fingerprint: str | None = None,
    ) -> tuple[dict[str, Any], list[str]]:
        clean_state: dict[str, Any] = {}
        removal_log: list[str] = []
        registry = get_question_bank_registry()

        if incoming_bank_fingerprint and incoming_bank_fingerprint != registry.fingerprint:
            removal_log.append("Профіль створений на іншій версії банку питань. Дані перевірені повторно.")

        valid_question_values: dict[str, set[str]] = {}
        for bank in registry.banks.values():
            for question in bank.questions:
                valid_question_values[question_state_key(bank.module, question.id)] = set(question.option_ids())

        for key, value in incoming_state.items():
            if key in valid_question_values:
                if isinstance(value, str) and value in valid_question_values[key]:
                    clean_state[key] = value
                else:
                    removal_log.append(f"Видалено невалідну відповідь для '{key}'.")
                continue

            if key in {"shadow_input_mode", "eros_input_mode", "psycho_input_mode"}:
                valid_modes = {"pdf", "manual"} if key == "psycho_input_mode" else {"quiz", "manual"}
                if value in valid_modes:
                    clean_state[key] = value
                else:
                    removal_log.append(f"Видалено невалідний режим '{key}'.")
                continue

            if key in {"psycho_o", "psycho_c", "psycho_e", "psycho_a", "psycho_n"}:
                sanitized = StateSanitizer._sanitize_number(value, 0.0, 100.0)
                if sanitized is not None:
                    clean_state[key] = sanitized
                else:
                    removal_log.append(f"Видалено невалідне числове поле '{key}'.")
                continue

            if key in {"psycho_adhd", "psycho_asd"}:
                if isinstance(value, bool):
                    clean_state[key] = value
                else:
                    removal_log.append(f"Видалено невалідний прапорець '{key}'.")
                continue

            if key in FACET_KEYS:
                sanitized = StateSanitizer._sanitize_number(value, 0.0, 20.0)
                if sanitized is not None:
                    clean_state[key] = sanitized
                else:
                    removal_log.append(f"Видалено невалідний facet '{key}'.")
                continue

            if key == "shadow_manual_att":
                sanitized = StateSanitizer._sanitize_enum_token(value, AttachmentStyle)
                if sanitized is not None:
                    clean_state[key] = sanitized
                else:
                    removal_log.append(f"Видалено невалідний enum '{key}'.")
                continue

            if key == "shadow_manual_conf":
                sanitized = StateSanitizer._sanitize_enum_token(value, ConflictResponse)
                if sanitized is not None:
                    clean_state[key] = sanitized
                else:
                    removal_log.append(f"Видалено невалідний enum '{key}'.")
                continue

            if key == "shadow_manual_reg":
                sanitized = StateSanitizer._sanitize_enum_token(value, RegulationMethod)
                if sanitized is not None:
                    clean_state[key] = sanitized
                else:
                    removal_log.append(f"Видалено невалідний enum '{key}'.")
                continue

            if key == "eros_manual_ctx":
                sanitized = StateSanitizer._sanitize_enum_token(value, ContextDependency)
                if sanitized is not None:
                    clean_state[key] = sanitized
                else:
                    removal_log.append(f"Видалено невалідний enum '{key}'.")
                continue

            if key in {"eros_manual_acc", "eros_manual_brk", "prof_centrality"}:
                sanitized = StateSanitizer._sanitize_number(value, 0.0, 1.0)
                if sanitized is not None:
                    clean_state[key] = sanitized
                else:
                    removal_log.append(f"Видалено невалідне числове поле '{key}'.")
                continue

            if key == "eros_tags":
                sanitized_tags = StateSanitizer._sanitize_tag_list(value)
                if sanitized_tags is not None:
                    clean_state[key] = sanitized_tags
                else:
                    removal_log.append("Видалено невалідні erotic tags.")
                continue

            if key in {"prof_primary", "prof_secondary", "prof_tertiary"}:
                sanitized = StateSanitizer._sanitize_enum_token(value, HollandCode)
                if sanitized is not None:
                    clean_state[key] = sanitized
                else:
                    removal_log.append(f"Видалено невалідний enum '{key}'.")
                continue

            removal_log.append(f"Видалено невідоме поле '{key}'.")

        return clean_state, removal_log

    @staticmethod
    def _sanitize_number(value: Any, min_value: float, max_value: float) -> float | None:
        if not isinstance(value, (int, float)):
            return None
        numeric = float(value)
        if numeric < min_value or numeric > max_value:
            return None
        return numeric

    @staticmethod
    def _sanitize_enum_token(value: Any, enum_class: type[Enum]) -> str | None:
        if isinstance(value, enum_class):
            return value.name
        if not isinstance(value, str):
            return None
        if value in enum_class.__members__:
            return value
        for member in enum_class:
            if member.value == value:
                return member.name
        return None

    @staticmethod
    def _sanitize_tag_list(value: Any) -> list[str] | None:
        if not isinstance(value, list):
            return None

        valid_tags = []
        seen_tags: set[str] = set()
        for tag in value:
            if not isinstance(tag, str):
                return None
            if tag not in EROS_TAGS_EXPLANATIONS:
                return None
            if tag not in seen_tags:
                seen_tags.add(tag)
                valid_tags.append(tag)
        return valid_tags
