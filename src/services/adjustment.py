from src.domain.needs import RelationalNeedsComponent
from src.domain.psychometrics import PsychometricsComponent
from src.services.neurodivergence import NeurodivergenceService


def _clamp(value: float) -> float:
    return min(max(value, 0.0), 1.0)


def _raise_floor(current_value: float, target_value: float, influence: float) -> float:
    if target_value <= current_value:
        return _clamp(current_value)
    return _clamp(current_value + (target_value - current_value) * influence)


class NeedsAdjustmentService:
    @staticmethod
    def adjust_needs(
        raw_needs: RelationalNeedsComponent,
        psycho: PsychometricsComponent,
    ) -> RelationalNeedsComponent:
        """
        Adjusts already-normalized SRME scores using detailed Big Five facets.
        """
        adjusted = RelationalNeedsComponent(
            raw_safety=_clamp(raw_needs.raw_safety),
            raw_resource=_clamp(raw_needs.raw_resource),
            raw_resonance=_clamp(raw_needs.raw_resonance),
            raw_expansion=_clamp(raw_needs.raw_expansion),
        )
        context = NeurodivergenceService.analyze(psycho)

        adjusted.adjusted_safety = _raise_floor(
            adjusted.raw_safety,
            context.safety_target,
            influence=0.45,
        )

        adjusted.adjusted_resource = _raise_floor(
            adjusted.raw_resource,
            context.resource_target,
            influence=0.55,
        )

        cognitive_capacity = psycho.openness.ideas
        emotional_capacity = (psycho.openness.feelings + psycho.agreeableness.tender_mindedness) / 2
        resonance_floor = 0.65 if (cognitive_capacity > 0.8 or emotional_capacity > 0.8) else 0.0
        resonance_target = max(context.resonance_target, resonance_floor)
        adjusted.adjusted_resonance = _raise_floor(
            adjusted.raw_resonance,
            resonance_target,
            influence=0.30,
        )

        adjusted.adjusted_expansion = _raise_floor(
            adjusted.raw_expansion,
            context.expansion_signal,
            influence=0.35,
        )
        return adjusted
