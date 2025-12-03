from dataclasses import dataclass
from typing import Dict

from .components import (
    PsychometricsComponent, 
    ShadowComponent, 
    ErosComponent, 
    RelationalNeedsComponent,
    ProfessionalComponent
)
from .enums import AttachmentStyle, RegulationMethod, HollandCode

@dataclass
class UserProfile:
    name: str
    psychometrics: PsychometricsComponent
    shadow: ShadowComponent
    eros: ErosComponent
    needs: RelationalNeedsComponent
    professional: ProfessionalComponent
    
    def generate_manual(self) -> Dict:
        """
        Генерує фінальний звіт ("User Manual") на основі взаємодії всіх компонентів.
        """
        
        # 1. Сортування потреб (Needs)
        needs_map = {
            "Безпека (Safety)": self.needs.adjusted_safety,
            "Ресурс (Resource)": self.needs.adjusted_resource,
            "Резонанс (Resonance)": self.needs.adjusted_resonance,
            "Експансія (Expansion)": self.needs.adjusted_expansion
        }
        sorted_needs = sorted(needs_map.items(), key=lambda x: x[1], reverse=True)
        
        # 2. Логіка попереджень Shadow (Attachment + Regulation)
        shadow_warn = "Стабільний"
        if self.shadow.attachment_style == AttachmentStyle.AVOIDANT:
            shadow_warn = "⚠️ Схильність до дистанціювання при стресі. Партнер може відчувати себе покинутим."
        elif self.shadow.attachment_style == AttachmentStyle.ANXIOUS:
            shadow_warn = "⚠️ Вимога постійного контакту. Загроза розриву викликає паніку."
        elif self.shadow.attachment_style == AttachmentStyle.DISORGANIZED:
            shadow_warn = "⚠️ Хаотична реакція на близькість (страх + бажання). Потребує терпіння."
        
        if self.shadow.regulation_method == RegulationMethod.AUTO_REGULATION:
            shadow_warn += " (Потребує часу на самоті для заспокоєння)."

        # 3. Логіка Professional (Interaction Style + Resource Availability)
        prof_style = self.professional.get_interaction_style()
        
        resource_warning = ""
        # Якщо кар'єра є центром життя (>75%), людина має менше ресурсу на побут/стосунки
        if self.professional.career_centrality > 0.75:
            resource_warning = "⚠️ Увага: Висока кар'єроцентричність. Ризик дефіциту побутового ресурсу (Low Resource Availability)."

        # Формування коду типу (наприклад: "REALISTIC / INVESTIGATIVE / ARTISTIC")
        prof_key = (
            f"{self.professional.primary_type.name} / "
            f"{self.professional.secondary_type.name} / "
            f"{self.professional.tertiary_type.name}"
        )

        return {
            # Основні драйвери (з SRME)
            "primary_driver": sorted_needs[0],
            "secondary_driver": sorted_needs[1],
            "scores": needs_map,
            
            # Тіньовий профіль
            "shadow_warning": shadow_warn,
            
            # Еротичний профіль
            "erotic_key": f"Гальма: {int(self.eros.brake*100)}% | Контекст: {self.eros.context_dependency.name}",
            
            # Професійний профіль
            "professional_key": prof_key,
            "interaction_style": prof_style,
            "resource_warning": resource_warning
        }