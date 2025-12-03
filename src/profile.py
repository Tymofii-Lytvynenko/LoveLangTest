from dataclasses import dataclass
from typing import Dict
from .components import PsychometricsComponent, ShadowComponent, ErosComponent, RelationalNeedsComponent
from .enums import AttachmentStyle, RegulationMethod

@dataclass
class UserProfile:
    name: str
    psychometrics: PsychometricsComponent
    shadow: ShadowComponent
    eros: ErosComponent
    needs: RelationalNeedsComponent
    
    def generate_manual(self) -> Dict:
        needs_map = {
            "Безпека (Safety)": self.needs.adjusted_safety,
            "Ресурс (Resource)": self.needs.adjusted_resource,
            "Резонанс (Resonance)": self.needs.adjusted_resonance,
            "Експансія (Expansion)": self.needs.adjusted_expansion
        }
        sorted_needs = sorted(needs_map.items(), key=lambda x: x[1], reverse=True)
        
        # Логіка генерації текстових попереджень
        shadow_warn = "Стабільний"
        if self.shadow.attachment_style == AttachmentStyle.AVOIDANT:
            shadow_warn = "⚠️ Схильність до дистанціювання при стресі. Партнер може відчувати себе покинутим."
        elif self.shadow.attachment_style == AttachmentStyle.ANXIOUS:
            shadow_warn = "⚠️ Вимога постійного контакту. Загроза розриву викликає паніку."
        
        if self.shadow.regulation_method == RegulationMethod.AUTO_REGULATION:
            shadow_warn += " (Потребує часу на самоті для заспокоєння)."

        # Генерація словника
        return {
            "primary_driver": sorted_needs[0],
            "secondary_driver": sorted_needs[1],
            "shadow_warning": shadow_warn,
            "erotic_key": f"Гальма: {int(self.eros.brake*100)}% | Контекст: {self.eros.context_dependency.name}",
            "scores": needs_map
        }