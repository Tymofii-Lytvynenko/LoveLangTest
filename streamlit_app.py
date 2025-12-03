import streamlit as st
from src.profile import UserProfile
from src.ui import (
    render_big_five_manual, 
    render_shadow_form, 
    render_eros_form, 
    render_scenarios_engine
)

def main():
    st.set_page_config(page_title="CRNAS v2.1", layout="wide", page_icon="🧬")
    st.title("🧬 CRNAS: Comprehensive Relationship Needs Analysis System")
    
    with st.form("main_form"):
        # 1. Hardware Layer
        psycho = render_big_five_manual()
        st.divider()
        
        # 2. Defense Layer
        shadow = render_shadow_form()
        st.divider()
        
        # 3. Sexual Layer
        eros = render_eros_form()
        st.divider()
        
        # 4. Context Layer (Data Collection)
        needs = render_scenarios_engine()
        
        submit = st.form_submit_button("📊 Розрахувати архітектуру", type="primary")

    if submit:
        # Composition: Збираємо профіль
        user = UserProfile("User", psycho, shadow, eros, needs)
        
        # Calculation: Запускаємо алгоритм нормалізації через взаємодію компонентів
        user.needs.calculate_adjustments(user.psychometrics)
        
        # Output: Генерація звіту
        manual = user.generate_manual()
        
        # Display Results
        st.success("Розрахунок завершено.")
        
        r1, r2 = st.columns(2)
        with r1:
            st.subheader("Ключові драйвери")
            st.metric("Домінанта", f"{manual['primary_driver'][0]}", f"{manual['primary_driver'][1]*100:.0f}%")
            st.metric("Вторинна", f"{manual['secondary_driver'][0]}", f"{manual['secondary_driver'][1]*100:.0f}%")
            
            st.write("#### Повний профіль потреб (Adjusted)")
            for k, v in manual['scores'].items():
                st.progress(v, text=f"{k}: {v*100:.1f}/100")
                
        with r2:
            st.subheader("Операційні примітки")
            st.warning(manual['shadow_warning'])
            st.info(f"**Eros Profile:** {manual['erotic_key']}")

if __name__ == "__main__":
    main()