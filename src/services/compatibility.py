from __future__ import annotations

from dataclasses import dataclass

from src.enums import AttachmentStyle
from src.profile import UserProfile
from src.services.provision import ProvisionService
from src.services.shadow_analysis import analyze_shadow


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
        first_priority = CompatibilityComparator._priority(first)
        second_priority = CompatibilityComparator._priority(second)

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

        first_priority_label = max(first_priority, key=first_priority.get)
        second_priority_label = max(second_priority, key=second_priority.get)
        if first_priority_label != second_priority_label:
            notes.append(
                CompatibilityItem(
                    title="Різні пріоритети в trade-off ситуаціях",
                    detail=(
                        f"Коли неможливо підтримати все одночасно, перший профіль частіше ставить на перше місце "
                        f"{CompatibilityComparator.NEED_LABELS[first_priority_label].lower()}, а другий — "
                        f"{CompatibilityComparator.NEED_LABELS[second_priority_label].lower()}."
                    ),
                    severity="note",
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

        first_shadow = analyze_shadow(first.shadow)
        second_shadow = analyze_shadow(second.shadow)
        first_style = first_shadow.style
        second_style = second_shadow.style

        if first_style is None or second_style is None:
            notes.append(
                CompatibilityItem(
                    title="Прив'язаність потребує обережної інтерпретації",
                    detail=(
                        "Один або обидва профілі мають змішаний або слабко виражений attachment-патерн, "
                        "тому висновки про anxious/avoidant петлі та secure-збіг тут менш надійні."
                    ),
                    severity="note",
                )
            )
        else:
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

        # Evaluate 5 Critical Discussion Flags
        # 1. Pursuit-Distance Loop
        pursuit_distance = False
        if {first_style, second_style} == {AttachmentStyle.ANXIOUS, AttachmentStyle.AVOIDANT}:
            pursuit_distance = True
        elif (first.shadow.anxious_score >= 0.45 and second.shadow.avoidant_score >= 0.45) or \
             (second.shadow.anxious_score >= 0.45 and first.shadow.avoidant_score >= 0.45):
            pursuit_distance = True

        if pursuit_distance:
            tensions.append(
                CompatibilityItem(
                    title="Цикл Переслідування-Дистанціювання",
                    detail="Один із партнерів може схилятися до пошуку активного контакту під час стресу, тоді як інший відступає для саморегуляції. Рекомендується встановити передбачуваний протокол відновлення контакту (repair).",
                    severity="high",
                )
            )

        # 2. Expansion-Safety Conflict
        expansion_safety = (
            (first_needs["expansion"] >= 0.70 and (second_needs["safety"] >= 0.70 or second.psychometrics.openness.average <= 0.40 or second.psychometrics.extraversion.excitement_seeking <= 0.35)) or
            (second_needs["expansion"] >= 0.70 and (first_needs["safety"] >= 0.70 or first.psychometrics.openness.average <= 0.40 or first.psychometrics.extraversion.excitement_seeking <= 0.35))
        )
        if expansion_safety:
            tensions.append(
                CompatibilityItem(
                    title="Конфлікт Експансії та Безпеки",
                    detail="Потреба одного з партнерів у новизні та розвитку може викликати тривогу в іншого, для кого пріоритетом є стабільність. Рекомендується спільно узгодити межі експеріментів та зону безпеки.",
                    severity="medium",
                )
            )

        # 3. Resource-Routine Friction
        resource_routine = (
            (first_needs["resource"] >= 0.70 and (second_provision["resource"] <= 0.40 or second.psychometrics.conscientiousness.average <= 0.40)) or
            (second_needs["resource"] >= 0.70 and (first_provision["resource"] <= 0.40 or first.psychometrics.conscientiousness.average <= 0.40))
        )
        if resource_routine:
            tensions.append(
                CompatibilityItem(
                    title="Побутове тертя (Ресурс vs Рутина)",
                    detail="Високий запит на практичну підтримку та організацію побуту стикається з обмеженим виконавчим ресурсом партнера. Це питання ємності та планування, а не дефіциту почуттів.",
                    severity="medium",
                )
            )

        # 4. Resonance-Style Mismatch
        resonance_style = (
            (first_needs["resonance"] >= 0.70 and second_provision["resonance"] <= 0.40) or
            (second_needs["resonance"] >= 0.70 and first_provision["resonance"] <= 0.40)
        )
        if resonance_style:
            tensions.append(
                CompatibilityItem(
                    title="Розбіжність стилів резонансу",
                    detail="Запит на глибоке емоційне або когнітивне спілкування стикається з більш практичним або низьковербальним стилем вираження турботи іншого партнера.",
                    severity="medium",
                )
            )

        # 5. Eros Brake/Pressure Loop
        eros_brake_pressure = (
            (first.eros.accelerator >= 0.65 and second.eros.brake >= 0.65) or
            (second.eros.accelerator >= 0.65 and first.eros.brake >= 0.65)
        )
        if eros_brake_pressure:
            tensions.append(
                CompatibilityItem(
                    title="Цикл тиску та сексуального гальмування",
                    detail="Прагнення до сексуальної близькості через ініціативу одного партнера стикається з високою чутливістю сексуального гальма іншого (через стрес, втому чи тривогу).",
                    severity="high",
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
        if user.provision is not None:
            return {
                "safety": user.provision.get("safety_provision", 0.0),
                "resource": user.provision.get("resource_provision", 0.0),
                "resonance": user.provision.get("resonance_provision", 0.0),
                "expansion": user.provision.get("expansion_provision", 0.0),
            }
        provision = ProvisionService.analyze(user.psychometrics, user.professional)
        return {
            "safety": provision.safety_score,
            "resource": provision.resource_score,
            "resonance": provision.resonance_score,
            "expansion": provision.expansion_score,
        }

    @staticmethod
    def _priority(user: UserProfile) -> dict[str, float]:
        return {
            "safety": user.needs.priority_safety,
            "resource": user.needs.priority_resource,
            "resonance": user.needs.priority_resonance,
            "expansion": user.needs.priority_expansion,
        }
