from __future__ import annotations

from src.domain.needs import RelationalNeedsComponent
from src.domain.psychometrics import PsychometricsComponent
from src.services.neurodivergence import NeurodivergenceService


def _clamp(value: float) -> float:
    return min(max(value, 0.0), 1.0)


def _weighted_mean(parts: list[tuple[float, float]]) -> float:
    total_weight = sum(weight for _, weight in parts)
    if total_weight <= 0:
        return 0.0
    return sum(value * weight for value, weight in parts) / total_weight


def calculate_adjusted_score(
    direct_score: float,
    ocean_prediction: float,
    context_modifier: float,
    direct_weight: float = 0.70,
    ocean_weight: float = 0.20,
    context_weight: float = 0.10,
) -> float:
    """
    OCEAN adjusts interpretation but does not erase direct answers.
    The context modifier should be bounded and should not act as a hidden diagnosis.
    """
    return _clamp(
        direct_score * direct_weight
        + ocean_prediction * ocean_weight
        + context_modifier * context_weight
    )


def predict_safety_from_ocean(psycho: PsychometricsComponent) -> float:
    return _weighted_mean([
        (psycho.neuroticism.anxiety, 0.30),
        (psycho.neuroticism.vulnerability, 0.25),
        (psycho.neuroticism.self_consciousness, 0.15),
        (1.0 - psycho.agreeableness.trust, 0.20),
        (psycho.conscientiousness.deliberation, 0.10),
    ])


def predict_resource_from_ocean(psycho: PsychometricsComponent) -> float:
    return _weighted_mean([
        (psycho.conscientiousness.order, 0.35),
        (psycho.conscientiousness.dutifulness, 0.25),
        (1.0 - psycho.conscientiousness.self_discipline, 0.20),
        (psycho.neuroticism.vulnerability, 0.20),
    ])


def predict_resonance_from_ocean(psycho: PsychometricsComponent) -> float:
    return _weighted_mean([
        (psycho.openness.feelings, 0.25),
        (psycho.openness.ideas, 0.20),
        (psycho.agreeableness.tender_mindedness, 0.25),
        (psycho.extraversion.warmth, 0.20),
        (psycho.agreeableness.trust, 0.10),
    ])


def predict_expansion_from_ocean(psycho: PsychometricsComponent) -> float:
    return _weighted_mean([
        (psycho.openness.actions, 0.35),
        (psycho.extraversion.excitement_seeking, 0.30),
        (1.0 - psycho.conscientiousness.deliberation, 0.15),
        (psycho.openness.fantasy, 0.10),
        (psycho.extraversion.gregariousness, 0.10),
    ])


def confidence_from_alignment(
    direct_score: float,
    ocean_prediction: float,
    calibration_flags: dict[str, bool],
) -> str:
    disagreement = abs(direct_score - ocean_prediction)
    if calibration_flags.get("critical_contradiction"):
        return "Low"
    if disagreement >= 0.40:
        return "Mixed"
    if disagreement >= 0.25:
        return "Medium"
    return "High"


class NeedsAdjustmentService:
    @staticmethod
    def adjust_needs(
        raw_needs: RelationalNeedsComponent,
        psycho: PsychometricsComponent,
        calibration_scores: dict[str, float] | None = None,
        calibration_notes: list[str] | None = None,
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

        # 1. Compute predictions
        pred_safety = predict_safety_from_ocean(psycho)
        pred_resource = predict_resource_from_ocean(psycho)
        pred_resonance = predict_resonance_from_ocean(psycho)
        pred_expansion = predict_expansion_from_ocean(psycho)

        # 2. Adjust scores using the 0.70 / 0.20 / 0.10 formula
        adjusted.adjusted_safety = calculate_adjusted_score(
            adjusted.raw_safety, pred_safety, context.safety_target
        )
        adjusted.adjusted_resource = calculate_adjusted_score(
            adjusted.raw_resource, pred_resource, context.resource_target
        )
        adjusted.adjusted_resonance = calculate_adjusted_score(
            adjusted.raw_resonance, pred_resonance, context.resonance_target
        )
        adjusted.adjusted_expansion = calculate_adjusted_score(
            adjusted.raw_expansion, pred_expansion, context.expansion_signal
        )

        # 3. Analyze calibration flags and notes
        calibration_flags = {}
        if calibration_scores is not None:
            if calibration_scores.get("need_vs_priority", 0.0) >= 0.6:
                calibration_flags["critical_contradiction"] = True

            if calibration_notes is not None:
                if calibration_scores.get("stress_stability", 0.0) >= 0.6:
                    calibration_notes.append("Пріоритети та потреби можуть суттєво зміщуватися в умовах високого стресу.")
                if calibration_scores.get("ideal_vs_real", 0.0) >= 0.6:
                    calibration_notes.append("Показники забезпечення можуть відображати ідеалізоване уявлення, а не повсякденну практику.")
                if calibration_scores.get("context_dependency", 0.0) >= 0.6:
                    calibration_notes.append("Потреби та бажання мають значну чутливість до зовнішнього контексту та професійного навантаження.")
                if calibration_scores.get("need_vs_priority", 0.0) >= 0.6:
                    calibration_notes.append("Можливий внутрішній конфлікт між висловленими потребами та реальними виборами (пріоритетами).")

        # Check for need-priority trade-off contradictions
        has_contra = False
        for label, raw_val, priority_val in [
            ("безпеки", adjusted.raw_safety, adjusted.priority_safety),
            ("ресурсу", adjusted.raw_resource, adjusted.priority_resource),
            ("резонансу", adjusted.raw_resonance, adjusted.priority_resonance),
            ("експансії", adjusted.raw_expansion, adjusted.priority_expansion),
        ]:
            if (raw_val >= 0.7 and priority_val <= -1.5) or (raw_val <= 0.3 and priority_val >= 1.5):
                has_contra = True
                calibration_flags["critical_contradiction"] = True

        if has_contra and calibration_notes is not None:
            calibration_notes.append("Виявлено розбіжність між декларованою силою потреби та вибором її при компромісах (trade-offs).")

        # 4. Compute confidence ratings
        adjusted.confidence_safety = confidence_from_alignment(
            adjusted.raw_safety, pred_safety, calibration_flags
        )
        adjusted.confidence_resource = confidence_from_alignment(
            adjusted.raw_resource, pred_resource, calibration_flags
        )
        adjusted.confidence_resonance = confidence_from_alignment(
            adjusted.raw_resonance, pred_resonance, calibration_flags
        )
        adjusted.confidence_expansion = confidence_from_alignment(
            adjusted.raw_expansion, pred_expansion, calibration_flags
        )

        return adjusted
