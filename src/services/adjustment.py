from src.domain.psychometrics import PsychometricsComponent
from src.domain.needs import RelationalNeedsComponent

class NeedsAdjustmentService:
    @staticmethod
    def adjust_needs(raw_needs: RelationalNeedsComponent, psycho: PsychometricsComponent) -> RelationalNeedsComponent:
        """
        Pure function: Приймає сирі потреби + психометрію, повертає скориговані потреби.
        Використовує детальні фасети (30 sub-traits) для точної корекції.
        """
        adjusted = RelationalNeedsComponent(
            raw_safety=raw_needs.raw_safety,
            raw_resource=raw_needs.raw_resource,
            raw_resonance=raw_needs.raw_resonance,
            raw_expansion=raw_needs.raw_expansion
        )

        # 1. SAFETY ADJUSTMENT
        # Safety драйвиться страхом (Anxiety) і вразливістю (Vulnerability).
        # Ворожість (Hostility) не збільшує потребу в безпеці, а змінює конфліктний стиль.
        safety_drivers = (psycho.neuroticism.anxiety + psycho.neuroticism.vulnerability) / 2
        
        n_weight = 0.7
        base_safety = raw_needs.raw_safety * (1.0 - n_weight)
        implicit_safety = safety_drivers * n_weight
        
        if psycho.has_asd:
            implicit_safety += 0.2
            
        adjusted.adjusted_safety = min(base_safety + implicit_safety, 1.0)

        # 2. RESOURCE ADJUSTMENT
        # Використовуємо саме Order (порядок) та Self-Discipline, а не всю Conscientiousness.
        # Achievement (амбіції) тут не допомагає в побуті.
        exec_function = (psycho.conscientiousness.order + psycho.conscientiousness.self_discipline) / 2
        dysfunction_penalty = (1.0 - exec_function)
        
        if psycho.has_adhd:
            dysfunction_penalty += 0.25
            
        adjusted.adjusted_resource = min(max(raw_needs.raw_resource, min(dysfunction_penalty, 1.0)), 1.0)

        # 3. RESONANCE ADJUSTMENT
        # Розділяємо типи резонансу на основі фасетів Openness
        # O:Ideas драйвить когнітивний резонанс.
        # O:Feelings + A:Tender-mindedness драйвить емоційний резонанс.
        
        cognitive_capacity = psycho.openness.ideas
        emotional_capacity = (psycho.openness.feelings + psycho.agreeableness.tender_mindedness) / 2
        
        # Якщо людина має високий запит на резонанс, але низькі фасети Feelings/Ideas,
        # ми піднімаємо "підлогу", щоб показати потребу в розвитку цих навичок.
        resonance_floor = 0.0
        if cognitive_capacity > 0.8 or emotional_capacity > 0.8:
            resonance_floor = 0.6
            
        adjusted.adjusted_resonance = min(max(raw_needs.raw_resonance, resonance_floor), 1.0)

        # 4. EXPANSION ADJUSTMENT
        # E:Excitement Seeking та O:Actions (готовність пробувати нове)
        novelty_driver = (psycho.extraversion.excitement_seeking + psycho.openness.actions) / 2
        
        if psycho.has_adhd:
            novelty_driver += 0.2 # "Dopamine hunger"
            
        val = (raw_needs.raw_expansion + novelty_driver) / 2
        adjusted.adjusted_expansion = min(val, 1.0)

        return adjusted