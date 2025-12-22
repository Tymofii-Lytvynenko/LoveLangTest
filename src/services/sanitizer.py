import streamlit as st
from src.data import get_scenarios, get_shadow_quiz, get_eros_quiz
from src.enums import HollandCode, AttachmentStyle, ConflictResponse, RegulationMethod

class StateSanitizer:
    
    @staticmethod
    def get_current_context_snapshot() -> dict:
        """
        Створює 'зліпок' поточних питань системи.
        """
        snapshot = {}
        
        # 1. Scenarios Context
        for s in get_scenarios():
            snapshot[f"scenario_{s.id}"] = s.question
            
        # 2. Shadow Context
        for q in get_shadow_quiz():
            snapshot[f"shadow_q_{q.id}"] = q.question
            
        # 3. Eros Context
        for q in get_eros_quiz():
            snapshot[f"eros_q_{q.id}"] = q.question
            
        return snapshot

    @staticmethod
    def sanitize(incoming_state: dict, saved_context: dict = None) -> tuple[dict, list[str]]:
        """
        Очищує вхідний стан від застарілих даних.
        Повертає: (clean_state, removal_log)
        """
        clean_state = {}
        removal_log = []
        
        # Отримуємо актуальні дані системи
        current_context = StateSanitizer.get_current_context_snapshot()
        active_scenarios_opts = {f"scenario_{s.id}": [opt.text for opt in s.options] for s in get_scenarios()}
        
        for key, value in incoming_state.items():
            
            # --- ПЕРЕВІРКА: ПИТАННЯ ВИДАЛЕНЕ? ---
            # Якщо це сценарій/тест, але його немає в current_context - це "сирота"
            is_question_key = key.startswith(("scenario_", "shadow_q_", "eros_q_"))
            if is_question_key and key not in current_context:
                removal_log.append(f"❌ Питання видалене з системи: ID {key}")
                continue

            # --- ПЕРЕВІРКА: ТЕКСТ ЗМІНИВСЯ? ---
            if key in current_context:
                if saved_context and key in saved_context:
                    saved_text = saved_context[key]
                    current_text = current_context[key]
                    
                    if saved_text != current_text:
                        removal_log.append(f"📝 Текст змінився (було: '{saved_text[:30]}...', стало: '{current_text[:30]}...') -> Відповідь скинуто.")
                        continue
                elif saved_context is None:
                    # Якщо це старий файл без контексту, ми не можемо гарантувати валідність,
                    # але зазвичай приймаємо (або можна додати strict mode)
                    pass

            # --- ВАЛІДАЦІЯ ЗНАЧЕНЬ (OPTIONS) ---
            
            # 1. Scenarios (check if option text still exists)
            if key.startswith("scenario_"):
                if key in active_scenarios_opts:
                    if value in active_scenarios_opts[key]:
                        clean_state[key] = value
                    else:
                        removal_log.append(f"⚠️ Опція більше не існує: '{value}' (ID {key})")
                continue

            # 2. Quizzes (Radio keys already validated via current_context check above)
            if key.startswith("shadow_q_") or key.startswith("eros_q_"):
                if key in current_context:
                    clean_state[key] = value
                continue

            # 3. Enums & Sliders
            if key.startswith("prof_") and "centrality" not in key:
                if StateSanitizer._is_valid_enum(value, HollandCode):
                    clean_state[key] = value
                continue
            
            if key == "shadow_manual_att" and StateSanitizer._is_valid_enum(value, AttachmentStyle):
                clean_state[key] = value
                continue
            if key == "shadow_manual_conf" and StateSanitizer._is_valid_enum(value, ConflictResponse):
                clean_state[key] = value
                continue
            if key == "shadow_manual_reg" and StateSanitizer._is_valid_enum(value, RegulationMethod):
                clean_state[key] = value
                continue

            # Allow tracking keys and sliders passed through
            clean_state[key] = value
            
        return clean_state, removal_log

    @staticmethod
    def _is_valid_enum(value: str, enum_class) -> bool:
        return value in [e.value for e in enum_class]