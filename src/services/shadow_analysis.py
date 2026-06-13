from __future__ import annotations

from dataclasses import dataclass

from src.domain.shadow import ShadowComponent
from src.enums import AttachmentStyle


@dataclass(frozen=True)
class ShadowSignal:
    style: AttachmentStyle | None
    top_score: float
    second_score: float
    gap: float

    @property
    def is_confident(self) -> bool:
        return self.style is not None


def analyze_shadow(shadow: ShadowComponent) -> ShadowSignal:
    scores = (
        (AttachmentStyle.SECURE, shadow.secure_score),
        (AttachmentStyle.ANXIOUS, shadow.anxious_score),
        (AttachmentStyle.AVOIDANT, shadow.avoidant_score),
        (AttachmentStyle.DISORGANIZED, shadow.disorganized_score),
    )
    ranked_scores = sorted(scores, key=lambda item: item[1], reverse=True)
    top_style, top_score = ranked_scores[0]
    second_score = ranked_scores[1][1]
    gap = top_score - second_score

    # We only treat a style as dominant when it is both high enough and clearly separated.
    is_confident = top_score >= 0.4 and gap >= 0.12
    return ShadowSignal(
        style=top_style if is_confident else None,
        top_score=top_score,
        second_score=second_score,
        gap=gap,
    )
