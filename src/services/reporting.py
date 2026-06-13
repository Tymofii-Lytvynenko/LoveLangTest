from typing import Any

from src.domain.shadow import ShadowComponent
from src.enums import AttachmentStyle, RegulationMethod
from src.profile import UserProfile
from src.services.neurodivergence import NeurodivergenceService
from src.services.provision import ProvisionService
from src.services.shadow_analysis import analyze_shadow


class ReportGenerator:
    NEED_DESCRIPTIONS = {
        "Безпека (Safety)": "Передбачуваність, емоційна безпека, паузи, межі й відновлення після перевантаження.",
        "Ресурс (Resource)": "Практична опора, побутова координація, видимий розподіл навантаження й зниження тертя.",
        "Резонанс (Resonance)": "Точне розуміння, уважне слухання, спільне осмислення і якісний repair після напруги.",
        "Експансія (Expansion)": "Новизна, інтерес, рух, спільні відкриття й відчуття розвитку у стосунках.",
    }

    @staticmethod
    def _shadow_warning(shadow: ShadowComponent) -> str:
        signal = analyze_shadow(shadow)

        if not signal.is_confident:
            return (
                "Змішаний або слабко виражений патерн прив'язаності: "
                "окремий стиль поки не домінує."
            )
        if signal.style == AttachmentStyle.AVOIDANT:
            return "Схильність до дистанціювання при стресі."
        if signal.style == AttachmentStyle.ANXIOUS:
            return "Висока потреба в контакті та чутливість до віддалення."
        if signal.style == AttachmentStyle.DISORGANIZED:
            return "Хаотична реакція на близькість: одночасний потяг і страх."
        return "Стабільний патерн прив'язаності."

    @staticmethod
    def generate_manual(user: UserProfile) -> dict[str, Any]:
        context = NeurodivergenceService.analyze(user.psychometrics)
        if user.provision is not None:
            provision_map = {
                "Safety Provider (Надійність)": user.provision.get("safety_provision", 0.0),
                "Resource Provider (Підтримка)": user.provision.get("resource_provision", 0.0),
                "Resonance Provider (Емпатія/Розуміння)": user.provision.get("resonance_provision", 0.0),
                "Expansion Provider (Драйв/Натхнення)": user.provision.get("expansion_provision", 0.0),
            }
        else:
            provision = ProvisionService.analyze(user.psychometrics, user.professional)
            provision_map = {
                "Safety Provider (Надійність)": provision.safety_score,
                "Resource Provider (Підтримка)": provision.resource_score,
                "Resonance Provider (Емпатія/Розуміння)": provision.resonance_score,
                "Expansion Provider (Драйв/Натхнення)": provision.expansion_score,
            }
        best_provision = max(provision_map.items(), key=lambda item: item[1])

        needs_map = {
            "Безпека (Safety)": user.needs.adjusted_safety,
            "Ресурс (Resource)": user.needs.adjusted_resource,
            "Резонанс (Resonance)": user.needs.adjusted_resonance,
            "Експансія (Expansion)": user.needs.adjusted_expansion,
        }
        sorted_needs = sorted(needs_map.items(), key=lambda item: item[1], reverse=True)

        priority_map = {
            "Безпека (Safety)": user.needs.priority_safety,
            "Ресурс (Resource)": user.needs.priority_resource,
            "Резонанс (Resonance)": user.needs.priority_resonance,
            "Експансія (Expansion)": user.needs.priority_expansion,
        }
        sorted_priority = sorted(
            priority_map.items(),
            key=lambda item: (item[1], needs_map[item[0]]),
            reverse=True,
        )

        shadow_warning = ReportGenerator._shadow_warning(user.shadow)
        if user.shadow.regulation_method == RegulationMethod.AUTO_REGULATION:
            shadow_warning += " Потребує часу на самоті для відновлення."

        resource_warning = ""
        if user.professional.career_centrality > 0.75:
            resource_warning = (
                "Висока кар'єроцентричність. Можливий дефіцит побутового або емоційного ресурсу в стосунках."
            )

        professional_key = " / ".join(
            (
                user.professional.primary_type.name,
                user.professional.secondary_type.name,
                user.professional.tertiary_type.name,
            )
        )

        return {
            "primary_driver": sorted_needs[0],
            "secondary_driver": sorted_needs[1],
            "scores": needs_map,
            "priority_scores": priority_map,
            "priority_top": sorted_priority[0],
            "priority_secondary": sorted_priority[1],
            "priority_order": [label for label, _ in sorted_priority],
            "need_descriptions": ReportGenerator.NEED_DESCRIPTIONS,
            "shadow_warning": shadow_warning,
            "erotic_key": (
                f"Accelerator: {int(user.eros.accelerator * 100)}% | "
                f"Brake: {int(user.eros.brake * 100)}% | "
                f"Context: {user.eros.context_dependency.value}"
            ),
            "professional_key": professional_key,
            "interaction_style": user.professional.get_interaction_style(),
            "resource_warning": resource_warning,
            "provision_scores": provision_map,
            "superpower": best_provision,
            "neurodivergence_context": context.label,
            "support_notes": list(context.support_notes),
            "context_disclaimer": (
                "ADHD/ASD/AuDHD flags are optional self-identified context. "
                "They calibrate interpretation and do not diagnose anything."
            ),
            "calibration_notes": user.calibration_notes,
            "confidence_ratings": {
                "Safety": user.needs.confidence_safety,
                "Resource": user.needs.confidence_resource,
                "Resonance": user.needs.confidence_resonance,
                "Expansion": user.needs.confidence_expansion,
            },
        }
