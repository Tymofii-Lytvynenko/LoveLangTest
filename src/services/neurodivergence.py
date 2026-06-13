from __future__ import annotations

from dataclasses import dataclass

from src.domain.psychometrics import PsychometricsComponent


def _clamp(value: float) -> float:
    return min(max(value, 0.0), 1.0)


def _mean(*values: float) -> float:
    return sum(values) / len(values)


@dataclass(frozen=True)
class NeurodivergenceContext:
    label: str | None
    safety_target: float
    resource_target: float
    resonance_target: float
    expansion_signal: float
    resource_provision_penalty: float
    support_notes: tuple[str, ...]

    @property
    def is_enabled(self) -> bool:
        return self.label is not None


class NeurodivergenceService:
    """
    Treat ADHD / ASD flags as optional self-identified context, not diagnosis.

    The outputs are bounded heuristics used to slightly calibrate interpretation
    around sensory load, executive scaffolding, directness, and novelty needs.
    """

    @staticmethod
    def analyze(psycho: PsychometricsComponent) -> NeurodivergenceContext:
        label = psycho.neurodivergence_label
        safety_target = _mean(
            psycho.neuroticism.anxiety,
            psycho.neuroticism.vulnerability,
        )
        resource_target = 1.0 - _mean(
            psycho.conscientiousness.order,
            psycho.conscientiousness.self_discipline,
            psycho.conscientiousness.competence,
        )
        resonance_target = _mean(
            psycho.openness.feelings,
            psycho.agreeableness.tender_mindedness,
            psycho.agreeableness.straightforwardness,
        )
        expansion_signal = _mean(
            psycho.extraversion.excitement_seeking,
            psycho.openness.actions,
        )
        resource_provision_penalty = 0.0
        support_notes: list[str] = []

        if psycho.has_asd:
            safety_target = _clamp(safety_target + 0.15)
            resonance_target = _clamp(resonance_target + 0.08)
            support_notes.append(
                "Пряма мова, сенсорна передбачуваність і час на відновлення можуть бути важливіші за читання між рядків."
            )

        if psycho.has_adhd:
            resource_target = _clamp(resource_target + 0.15)
            expansion_signal = _clamp(expansion_signal + 0.12)
            executive_friction = 1.0 - _mean(
                psycho.conscientiousness.order,
                psycho.conscientiousness.self_discipline,
            )
            resource_provision_penalty = 0.12 * executive_friction
            support_notes.append(
                "Зовнішні опори, явний розподіл задач і низький побутовий friction можуть впливати на сумісність сильніше за добрі наміри."
            )

        if psycho.has_adhd and psycho.has_asd:
            safety_target = _clamp(safety_target + 0.05)
            resource_target = _clamp(resource_target + 0.05)
            support_notes.append(
                "AuDHD-профіль часто потребує одночасно новизни й передбачуваності; це краще трактувати як вимогу до середовища, а не як суперечливість."
            )

        return NeurodivergenceContext(
            label=label,
            safety_target=safety_target,
            resource_target=resource_target,
            resonance_target=resonance_target,
            expansion_signal=expansion_signal,
            resource_provision_penalty=resource_provision_penalty,
            support_notes=tuple(support_notes),
        )
