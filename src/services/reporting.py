from typing import Dict
from src.profile import UserProfile
from src.services.provision import ProvisionService
from src.enums import AttachmentStyle, RegulationMethod

class ReportGenerator:
    @staticmethod
    def generate_manual(user: UserProfile) -> Dict:
        """
        Генерує фінальний звіт ("User Manual") на основі взаємодії всіх компонентів.
        """
        
        # 1. Розрахунок Provision
        provision = ProvisionService.analyze(user.psychometrics, user.professional)
        
        provision_map = {
            "Safety Provider (Надійність)": provision.safety_score,
            "Resource Provider (Підтримка)": provision.resource_score,
            "Resonance Provider (Емпатія/Розуміння)": provision.resonance_score,
            "Expansion Provider (Драйв/Натхнення)": provision.expansion_score
        }
        best_provision = max(provision_map.items(), key=lambda x: x[1])
        
        # 2. Сортування потреб (Needs)
        needs_map = {
            "Безпека (Safety)": user.needs.adjusted_safety,
            "Ресурс (Resource)": user.needs.adjusted_resource,
            "Резонанс (Resonance)": user.needs.adjusted_resonance,
            "Експансія (Expansion)": user.needs.adjusted_expansion
        }
        sorted_needs = sorted(needs_map.items(), key=lambda x: x[1], reverse=True)
        
        # 3. Логіка попереджень Shadow
        shadow_warn = "Стабільний"
        if user.shadow.attachment_style == AttachmentStyle.AVOIDANT:
            shadow_warn = "⚠️ Схильність до дистанціювання при стресі."
        elif user.shadow.attachment_style == AttachmentStyle.ANXIOUS:
            shadow_warn = "⚠️ Вимога постійного контакту. Паніка при віддаленні."
        elif user.shadow.attachment_style == AttachmentStyle.DISORGANIZED:
            shadow_warn = "⚠️ Хаотична реакція на близькість (страх + бажання)."
        
        if user.shadow.regulation_method == RegulationMethod.AUTO_REGULATION:
            shadow_warn += " (Потребує часу на самоті)."

        # 4. Логіка Professional
        prof_style = user.professional.get_interaction_style()
        resource_warning = ""
        if user.professional.career_centrality > 0.75:
            resource_warning = "⚠️ Висока кар'єроцентричність. Ризик дефіциту побутового ресурсу."

        prof_key = (
            f"{user.professional.primary_type.name} / "
            f"{user.professional.secondary_type.name} / "
            f"{user.professional.tertiary_type.name}"
        )

        return {
            "primary_driver": sorted_needs[0],
            "secondary_driver": sorted_needs[1],
            "scores": needs_map,
            "shadow_warning": shadow_warn,
            "erotic_key": f"Гальма: {int(user.eros.brake*100)}% | Контекст: {user.eros.context_dependency.name}",
            "professional_key": prof_key,
            "interaction_style": prof_style,
            "resource_warning": resource_warning,
            "provision_scores": provision_map,
            "superpower": best_provision
        }