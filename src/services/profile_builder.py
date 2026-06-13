from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from src.data import EROS_TAGS_EXPLANATIONS
from src.domain.eros import ErosComponent
from src.domain.professional import ProfessionalComponent
from src.domain.psychometrics import PsychometricsComponent
from src.domain.shadow import ShadowComponent
from src.enums import AttachmentStyle, ConflictResponse, ContextDependency, HollandCode, RegulationMethod
from src.profile import UserProfile
from src.question_bank import QuestionBankRegistry
from src.services.adjustment import NeedsAdjustmentService
from src.services.bigfive_pdf_parser import FACET_SPECS
from src.services.form_state import collect_bank_responses
from src.services.scoring import QuestionnaireScorer


QUESTIONNAIRE_MODE_KEY = "questionnaire_mode"
QUESTIONNAIRE_MODES = {"simple", "extended"}


@dataclass(frozen=True)
class BuiltProfile:
    user: UserProfile | None
    missing_inputs: tuple[str, ...]
    mode: str

    @property
    def is_complete(self) -> bool:
        return self.user is not None and not self.missing_inputs


def normalize_questionnaire_mode(raw_mode: object) -> str:
    return str(raw_mode) if raw_mode in QUESTIONNAIRE_MODES else "extended"


def _enum_from_state(state: Mapping[str, Any], key: str, enum_class, default):
    value = state.get(key)
    if isinstance(value, enum_class):
        return value
    if isinstance(value, str) and value in enum_class.__members__:
        return enum_class[value]
    return default


def _number_from_state(state: Mapping[str, Any], key: str, default: float) -> float:
    value = state.get(key)
    return float(value) if isinstance(value, (int, float)) else default


def _build_psychometrics(state: Mapping[str, Any]) -> PsychometricsComponent:
    psycho = PsychometricsComponent.from_high_level_scores(
        _number_from_state(state, "psycho_o", 50.0),
        _number_from_state(state, "psycho_c", 50.0),
        _number_from_state(state, "psycho_e", 50.0),
        _number_from_state(state, "psycho_a", 50.0),
        _number_from_state(state, "psycho_n", 50.0),
        adhd=state.get("psycho_adhd") is True,
        asd=state.get("psycho_asd") is True,
    )

    for spec in FACET_SPECS:
        value = state.get(spec.session_key)
        if isinstance(value, (int, float)):
            domain = getattr(psycho, spec.domain)
            setattr(domain, spec.attr_name, min(max(float(value) / 20.0, 0.0), 1.0))
    return psycho


def _build_shadow(state: Mapping[str, Any], registry: QuestionBankRegistry, mode: str) -> tuple[ShadowComponent | None, list[str]]:
    if state.get("shadow_input_mode", "quiz") == "manual":
        required_keys = ("shadow_manual_att", "shadow_manual_conf", "shadow_manual_reg")
        missing = [key for key in required_keys if key not in state]
        if missing:
            return None, missing
        return (
            ShadowComponent(
                attachment_style=_enum_from_state(state, "shadow_manual_att", AttachmentStyle, AttachmentStyle.SECURE),
                conflict_response=_enum_from_state(state, "shadow_manual_conf", ConflictResponse, ConflictResponse.FLIGHT),
                regulation_method=_enum_from_state(state, "shadow_manual_reg", RegulationMethod, RegulationMethod.AUTO_REGULATION),
            ),
            [],
        )

    bank = registry.get("shadow").for_mode(mode)
    response_state = collect_bank_responses(bank, state)
    if not response_state.is_complete:
        return None, list(response_state.missing_questions)
    return QuestionnaireScorer.build_shadow_component(bank, response_state.responses), []


def _build_eros(state: Mapping[str, Any], registry: QuestionBankRegistry, mode: str) -> tuple[ErosComponent | None, list[str]]:
    raw_tags = state.get("eros_tags", [])
    erotic_tags = [
        tag for tag in raw_tags
        if isinstance(raw_tags, list) and isinstance(tag, str) and tag in EROS_TAGS_EXPLANATIONS
    ]

    if state.get("eros_input_mode", "quiz") == "manual":
        if "eros_manual_ctx" not in state:
            return None, ["Контекст Eros"]
        return (
            ErosComponent(
                accelerator=_number_from_state(state, "eros_manual_acc", 0.5),
                brake=_number_from_state(state, "eros_manual_brk", 0.5),
                context_dependency=_enum_from_state(state, "eros_manual_ctx", ContextDependency, ContextDependency.LOW),
                erotic_tags=erotic_tags,
            ),
            [],
        )

    bank = registry.get("eros").for_mode(mode)
    response_state = collect_bank_responses(bank, state)
    if not response_state.is_complete:
        return None, list(response_state.missing_questions)
    return QuestionnaireScorer.build_eros_component(bank, response_state.responses, erotic_tags=erotic_tags), []


def _build_professional(state: Mapping[str, Any]) -> ProfessionalComponent:
    return ProfessionalComponent(
        primary_type=_enum_from_state(state, "prof_primary", HollandCode, HollandCode.REALISTIC),
        secondary_type=_enum_from_state(state, "prof_secondary", HollandCode, HollandCode.INVESTIGATIVE),
        tertiary_type=_enum_from_state(state, "prof_tertiary", HollandCode, HollandCode.ARTISTIC),
        career_centrality=_number_from_state(state, "prof_centrality", 0.5),
    )


def build_user_profile_from_state(
    state: Mapping[str, Any],
    registry: QuestionBankRegistry,
    *,
    name: str = "User",
) -> BuiltProfile:
    mode = normalize_questionnaire_mode(state.get(QUESTIONNAIRE_MODE_KEY))
    missing: list[str] = []
    psycho = _build_psychometrics(state)

    shadow, shadow_missing = _build_shadow(state, registry, mode)
    missing.extend(f"Shadow: {item}" for item in shadow_missing)

    eros, eros_missing = _build_eros(state, registry, mode)
    missing.extend(f"Eros: {item}" for item in eros_missing)

    needs_bank = registry.get("needs").for_mode(mode)
    needs_state = collect_bank_responses(needs_bank, state)
    if not needs_state.is_complete:
        missing.extend(f"Needs: {item}" for item in needs_state.missing_questions)
        needs = None
    else:
        needs = QuestionnaireScorer.build_needs_component(needs_bank, needs_state.responses)
        needs = NeedsAdjustmentService.adjust_needs(needs, psycho)

    if missing or shadow is None or eros is None or needs is None:
        return BuiltProfile(user=None, missing_inputs=tuple(missing), mode=mode)

    return BuiltProfile(
        user=UserProfile(
            name=name,
            psychometrics=psycho,
            shadow=shadow,
            eros=eros,
            needs=needs,
            professional=_build_professional(state),
        ),
        missing_inputs=(),
        mode=mode,
    )
