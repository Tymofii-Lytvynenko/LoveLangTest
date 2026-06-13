from typing import Any

from src.enums import AttachmentStyle, RegulationMethod
from src.profile import UserProfile
from src.services.neurodivergence import NeurodivergenceService
from src.services.provision import ProvisionService


class ReportGenerator:
    @staticmethod
    def generate_manual(user: UserProfile) -> dict[str, Any]:
        context = NeurodivergenceService.analyze(user.psychometrics)
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

        shadow_warning = "Стабільний патерн прив'язаності."
        if user.shadow.attachment_style == AttachmentStyle.AVOIDANT:
            shadow_warning = "Схильність до дистанціювання при стресі."
        elif user.shadow.attachment_style == AttachmentStyle.ANXIOUS:
            shadow_warning = "Висока потреба в контакті та чутливість до віддалення."
        elif user.shadow.attachment_style == AttachmentStyle.DISORGANIZED:
            shadow_warning = "Хаотична реакція на близькість: одночасний потяг і страх."

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
        }
