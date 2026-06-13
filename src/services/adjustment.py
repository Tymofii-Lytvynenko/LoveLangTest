from src.domain.needs import RelationalNeedsComponent
from src.domain.psychometrics import PsychometricsComponent
from src.services.neurodivergence import NeurodivergenceService


def _clamp(value: float) -> float:
    return min(max(value, 0.0), 1.0)


def _bounded_uplift(current_value: float, target_value: float, influence: float, max_uplift: float = 0.10) -> float:
    if target_value <= current_value:
        return _clamp(current_value)
    uplift = (target_value - current_value) * influence
    return _clamp(current_value + min(max_uplift, uplift))


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
            priority_safety=raw_needs.priority_safety,
            priority_resource=raw_needs.priority_resource,
            priority_resonance=raw_needs.priority_resonance,
            priority_expansion=raw_needs.priority_expansion,
        )
        context = NeurodivergenceService.analyze(psycho)

        adjusted.adjusted_safety = _bounded_uplift(
            adjusted.raw_safety,
            context.safety_target,
            influence=0.35,
        )

        adjusted.adjusted_resource = _bounded_uplift(
            adjusted.raw_resource,
            context.resource_target,
            influence=0.40,
        )

        cognitive_capacity = psycho.openness.ideas
        emotional_capacity = (psycho.openness.feelings + psycho.agreeableness.tender_mindedness) / 2
        resonance_floor = 0.65 if (cognitive_capacity > 0.8 or emotional_capacity > 0.8) else 0.0
        resonance_target = max(context.resonance_target, resonance_floor)
        adjusted.adjusted_resonance = _bounded_uplift(
            adjusted.raw_resonance,
            resonance_target,
            influence=0.25,
        )

        adjusted.adjusted_expansion = _bounded_uplift(
            adjusted.raw_expansion,
            context.expansion_signal,
            influence=0.25,
        )
        return adjusted
