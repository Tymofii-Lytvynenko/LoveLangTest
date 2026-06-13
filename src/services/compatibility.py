from __future__ import annotations

from dataclasses import dataclass

from src.enums import AttachmentStyle
from src.profile import UserProfile
from src.services.provision import ProvisionService


@dataclass(frozen=True)
class CompatibilityItem:
    title: str
    detail: str
    severity: str


@dataclass(frozen=True)
class CompatibilityReport:
    score: float
    strengths: tuple[CompatibilityItem, ...]
    tensions: tuple[CompatibilityItem, ...]
    notes: tuple[CompatibilityItem, ...]


class CompatibilityComparator:
    NEED_LABELS = {
        "safety": "Безпека",
        "resource": "Ресурс",
        "resonance": "Резонанс",
        "expansion": "Експансія",
    }

    @staticmethod
    def compare(first: UserProfile, second: UserProfile) -> CompatibilityReport:
        strengths: list[CompatibilityItem] = []
        tensions: list[CompatibilityItem] = []
        notes: list[CompatibilityItem] = []

        first_needs = CompatibilityComparator._needs(first)
        second_needs = CompatibilityComparator._needs(second)
        first_provision = CompatibilityComparator._provision(first)
        second_provision = CompatibilityComparator._provision(second)

        total_gap = 0.0
        for key, label in CompatibilityComparator.NEED_LABELS.items():
            need_gap = abs(first_needs[key] - second_needs[key])
            total_gap += need_gap
            if need_gap >= 0.35:
                tensions.append(
                    CompatibilityItem(
                        title=f"Різний рівень потреби: {label}",
                        detail=(
                            f"Профілі відрізняються приблизно на {need_gap * 100:.0f} пунктів. "
                            "Це варто проговорити як очікування, а не як чиюсь помилку."
                        ),
                        severity="high" if need_gap >= 0.5 else "medium",
                    )
                )
            elif need_gap <= 0.15:
                strengths.append(
                    CompatibilityItem(
                        title=f"Схожий запит: {label}",
                        detail="Ваші потреби в цьому вимірі близькі, тому домовленості можуть даватися легше.",
                        severity="positive",
                    )
                )

            for demander_name, demand, provider_name, provision in (
                ("Перший профіль", first_needs[key], "другий профіль", second_provision[key]),
                ("Другий профіль", second_needs[key], "перший профіль", first_provision[key]),
            ):
                if demand >= 0.68 and provision <= 0.38:
                    tensions.append(
                        CompatibilityItem(
                            title=f"Можливий дефіцит підтримки: {label}",
                            detail=(
                                f"{demander_name} має високий запит, а {provider_name} може давати мало цього ресурсу. "
                                "Потрібні явні правила підтримки."
                            ),
                            severity="high",
                        )
                    )
                elif demand >= 0.65 and provision >= 0.65:
                    strengths.append(
                        CompatibilityItem(
                            title=f"Добре покриття потреби: {label}",
                            detail=f"{provider_name.capitalize()} природно дає те, що важливо для {demander_name.lower()}.",
                            severity="positive",
                        )
                    )

        eros_gap = abs(first.eros.accelerator - second.eros.accelerator) + abs(first.eros.brake - second.eros.brake)
        if abs(first.eros.accelerator - second.eros.accelerator) >= 0.35:
            tensions.append(
                CompatibilityItem(
                    title="Різний темп сексуальної активації",
                    detail="Одному профілю бажання може вмикатись значно легше. Це потребує обережності з ініціюванням.",
                    severity="medium",
                )
            )
        if abs(first.eros.brake - second.eros.brake) >= 0.35:
            tensions.append(
                CompatibilityItem(
                    title="Різна чутливість сексуального гальма",
                    detail="Контекст, стрес або сенсорне середовище можуть мати різну вагу для вас двох.",
                    severity="medium",
                )
            )
        if eros_gap <= 0.25:
            strengths.append(
                CompatibilityItem(
                    title="Схожий еротичний контекст",
                    detail="Акселератор і гальмо близькі, тому легше узгоджувати темп і умови близькості.",
                    severity="positive",
                )
            )

        first_style = first.shadow.attachment_style
        second_style = second.shadow.attachment_style
        if {first_style, second_style} == {AttachmentStyle.ANXIOUS, AttachmentStyle.AVOIDANT}:
            tensions.append(
                CompatibilityItem(
                    title="Тривожно-уникаюча петля",
                    detail="Один профіль може шукати більше контакту саме тоді, коли інший відступає для регуляції.",
                    severity="high",
                )
            )
        if AttachmentStyle.DISORGANIZED in {first_style, second_style}:
            notes.append(
                CompatibilityItem(
                    title="Потрібний дуже явний repair",
                    detail="Дезорганізований патерн не є вироком, але потребує передбачуваного відновлення контакту після напруги.",
                    severity="note",
                )
            )
        if first_style == second_style == AttachmentStyle.SECURE:
            strengths.append(
                CompatibilityItem(
                    title="Схожий стабільний стиль прив'язаності",
                    detail="Обидва профілі мають більше шансів повертатися до контакту без драматизації дистанції.",
                    severity="positive",
                )
            )

        score = 1.0 - min(1.0, (total_gap / 4 * 0.55) + (eros_gap / 2 * 0.25) + (len(tensions) * 0.04))
        return CompatibilityReport(
            score=max(0.0, min(1.0, score)),
            strengths=tuple(strengths[:8]),
            tensions=tuple(tensions[:8]),
            notes=tuple(notes[:6]),
        )

    @staticmethod
    def _needs(user: UserProfile) -> dict[str, float]:
        return {
            "safety": user.needs.adjusted_safety,
            "resource": user.needs.adjusted_resource,
            "resonance": user.needs.adjusted_resonance,
            "expansion": user.needs.adjusted_expansion,
        }

    @staticmethod
    def _provision(user: UserProfile) -> dict[str, float]:
        provision = ProvisionService.analyze(user.psychometrics, user.professional)
        return {
            "safety": provision.safety_score,
            "resource": provision.resource_score,
            "resonance": provision.resonance_score,
            "expansion": provision.expansion_score,
        }
