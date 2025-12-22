import streamlit as st
import json
from datetime import datetime
from enum import Enum  # <--- Додано

from src.profile import UserProfile
from src.services.adjustment import NeedsAdjustmentService
from src.services.reporting import ReportGenerator
from src.services.sanitizer import StateSanitizer

# Імпорт UI компонентів
from src.ui import (
    render_big_five_manual, 
    render_shadow_form, 
    render_eros_form, 
    render_scenarios_engine,
    render_professional_compass
)

CURRENT_VERSION = "3.2"

def enum_serializer(obj):
    """Допоміжна функція для серіалізації Enum об'єктів у JSON"""
    if isinstance(obj, Enum):
        return obj.value
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def handle_save_load():
    """Логіка сайдбару для збереження/завантаження профілю"""
    with st.sidebar:
        st.header("💾 Управління даними")
        
        # 1. ЗАВАНТАЖЕННЯ (LOAD)
        uploaded_file = st.file_uploader("📂 Завантажити профіль (JSON)", type="json")
        if uploaded_file is not None:
            try:
                raw_data = json.load(uploaded_file)
                
                saved_context = raw_data.get("_context_snapshot", {})
                incoming_state = raw_data.get("state", raw_data)
                
                # --- SANITIZATION ---
                # Отримуємо чистий стан і список видаленого
                clean_state, removal_log = StateSanitizer.sanitize(incoming_state, saved_context)
                
                # Застосування до сесії
                changes_count = 0
                for key, value in clean_state.items():
                    if key in st.session_state:
                         if st.session_state[key] != value:
                            st.session_state[key] = value
                            changes_count += 1
                    else:
                        st.session_state[key] = value
                        changes_count += 1
                
                # --- WARNING BLOCK & FIX DOWNLOAD ---
                if removal_log:
                    st.warning(f"⚠️ Увага! Було скинуто {len(removal_log)} параметрів через невідповідність версій.")
                    
                    with st.expander("📝 Переглянути деталі змін"):
                        for log_item in removal_log:
                            st.write(f"- {log_item}")

                    # Генеруємо "чистий" файл прямо тут
                    cleaned_export = {
                        "_meta": {
                            "version": CURRENT_VERSION,
                            "timestamp": datetime.now().isoformat(),
                            "note": "Sanitized export"
                        },
                        "_context_snapshot": StateSanitizer.get_current_context_snapshot(),
                        "state": clean_state
                    }
                    # Використовуємо кастомний серіалізатор
                    cleaned_json = json.dumps(
                        cleaned_export, 
                        indent=4, 
                        ensure_ascii=False, 
                        default=enum_serializer  # <--- FIX
                    )
                    
                    st.download_button(
                        label="🛠️ Завантажити виправлений файл",
                        data=cleaned_json,
                        file_name=f"crnas_sanitized_{datetime.now().strftime('%H%M')}.json",
                        mime="application/json",
                        help="Цей файл містить тільки валідні дані. Використовуйте його надалі."
                    )
                
                if changes_count > 0:
                    st.success(f"✅ Успішно завантажено (оновлено {changes_count} полів).")
                    if st.button("🔄 Оновити інтерфейс"):
                        st.rerun()
                elif not removal_log:
                    st.info("Дані повністю ідентичні поточним.")
                    
            except Exception as e:
                st.error(f"Помилка обробки файлу: {e}")

        st.divider()

        # 2. ЗБЕРЕЖЕННЯ (SAVE)
        current_state = {
            k: v for k, v in st.session_state.items() 
            if k.startswith(("psycho_", "facet_", "shadow_", "eros_", "scenario_", "prof_"))
        }
        
        if current_state:
            context_snapshot = StateSanitizer.get_current_context_snapshot()
            
            export_data = {
                "_meta": {
                    "version": CURRENT_VERSION,
                    "timestamp": datetime.now().isoformat(),
                },
                "_context_snapshot": context_snapshot,
                "state": current_state
            }
            
            # Використовуємо кастомний серіалізатор
            json_data = json.dumps(
                export_data, 
                indent=4, 
                ensure_ascii=False, 
                default=enum_serializer  # <--- FIX
            )
            filename = f"crnas_profile_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            
            st.download_button(
                "💾 Зберегти поточний профіль",
                json_data,
                filename,
                "application/json",
                type="primary"
            )

def main():
    st.set_page_config(page_title="CRNAS v3.2", layout="wide", page_icon="🧬")
    
    handle_save_load()
    
    st.title("🧬 CRNAS: Comprehensive Relationship Needs Analysis System")
    
    with st.form("main_form"):
        psycho = render_big_five_manual()
        st.divider()
        shadow = render_shadow_form()
        st.divider()
        eros = render_eros_form()
        st.divider()
        raw_needs = render_scenarios_engine()
        st.divider()
        prof = render_professional_compass()
        st.markdown("---")
        submit = st.form_submit_button("📊 Розрахувати архітектуру", type="primary")

    if submit:
        user = UserProfile("User", psycho, shadow, eros, raw_needs, prof)
        user.needs = NeedsAdjustmentService.adjust_needs(user.needs, user.psychometrics)
        manual = ReportGenerator.generate_manual(user)
        
        st.success("Розрахунок завершено.")
        
        r1, r2 = st.columns(2)
        with r1:
            st.subheader("Ключові драйвери")
            st.metric("Домінанта", f"{manual['primary_driver'][0]}", f"{manual['primary_driver'][1]*100:.0f}%")
            st.metric("Вторинна", f"{manual['secondary_driver'][0]}", f"{manual['secondary_driver'][1]*100:.0f}%")
            
            st.write("#### Повний профіль потреб (Adjusted)")
            for k, v in manual['scores'].items():
                st.progress(v, text=f"{k}: {v*100:.1f}/100")
                
            st.write("---")
            st.subheader("🎒 Що ви приносите у стосунки (Provision)")
            p_scores = manual['provision_scores']
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Safety", f"{int(p_scores['Safety Provider (Надійність)']*100)}%")
            c2.metric("Resource", f"{int(p_scores['Resource Provider (Підтримка)']*100)}%")
            c3.metric("Resonance", f"{int(p_scores['Resonance Provider (Емпатія/Розуміння)']*100)}%")
            c4.metric("Expansion", f"{int(p_scores['Expansion Provider (Драйв/Натхнення)']*100)}%")
            
            st.success(f"💎 Ваша суперсила: **{manual['superpower'][0]}**")
                
        with r2:
            st.subheader("Операційні примітки")
            st.warning(manual['shadow_warning'])
            st.info(f"**Eros Profile:** {manual['erotic_key']}")
            st.info(f"**Professional Style:** {manual['professional_key']}")
            st.caption(f"Strategy: {manual['interaction_style']}")
            if manual['resource_warning']:
                st.error(manual['resource_warning'])

if __name__ == "__main__":
    main()