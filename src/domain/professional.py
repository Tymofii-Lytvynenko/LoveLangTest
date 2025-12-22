from dataclasses import dataclass
from src.enums import HollandCode

@dataclass
class ProfessionalComponent:
    primary_type: HollandCode = HollandCode.REALISTIC
    secondary_type: HollandCode = HollandCode.INVESTIGATIVE
    tertiary_type: HollandCode = HollandCode.ARTISTIC
    career_centrality: float = 0.5
    
    def get_interaction_style(self) -> str:
        style_map = {
            HollandCode.REALISTIC: "Дія замість слів. 'Я полагодив кран' = 'Я тебе люблю'.",
            HollandCode.INVESTIGATIVE: "Аналіз замість емоцій. Потреба в інтелектуальному спарингу.",
            HollandCode.ARTISTIC: "Емоційні гойдалки та спонтанність. Рутина вбиває.",
            HollandCode.SOCIAL: "Гіпер-комунікація. Потреба постійного обговорення почуттів.",
            HollandCode.ENTERPRISING: "Стосунки як проєкт. Стратегічне планування.",
            HollandCode.CONVENTIONAL: "Ритуали та стабільність. Домовленості — це святе."
        }
        return style_map.get(self.primary_type, "")