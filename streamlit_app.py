import streamlit as st
from src.profile import UserProfile
from src.services.adjustment import NeedsAdjustmentService
from src.services.reporting import ReportGenerator

# Імпорт UI компонентів
from src.ui import (
    render_big_five_manual, 
    render_shadow_form, 
    render_eros_form, 
    render_scenarios_engine,
    render_professional_compass
)

def main():
    st.set_page_config(page_title="CRNAS v3.0 (DDD Refactor)", layout="wide", page_icon="🧬")
    st.title("🧬 CRNAS: Comprehensive Relationship Needs Analysis System")
    
    with st.form("main_form"):
        # 1. Hardware Layer (Psychometrics 30-facet)
        psycho = render_big_five_manual()
        st.divider()
        
        # 2. Defense Layer
        shadow = render_shadow_form()
        st.divider()
        
        # 3. Sexual Layer
        eros = render_eros_form()
        st.divider()
        
        # 4. Context Layer (Needs Collection)
        raw_needs = render_scenarios_engine()
        st.divider()

        # 5. Professional Layer
        prof = render_professional_compass()
        
        st.markdown("---")
        submit = st.form_submit_button("📊 Розрахувати архітектуру", type="primary")

    if submit:
        # A. Створення профілю з "сирими" даними
        # Зверни увагу: raw_needs ще не скориговані
        user = UserProfile("User", psycho, shadow, eros, raw_needs, prof)
        
        # B. Виклик Сервісу Корекції (Adjustment Service)
        # Це pure function: бере вхідні дані -> повертає нові скориговані потреби
        user.needs = NeedsAdjustmentService.adjust_needs(user.needs, user.psychometrics)
        
        # C. Виклик Сервісу Звітності (Reporting Service)
        manual = ReportGenerator.generate_manual(user)
        
        # Display Results
        st.success("Розрахунок завершено (v3.0 Logic Applied).")
        
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
            
            prov_cols = st.columns(4)
            p_scores = manual['provision_scores']
            prov_cols[0].metric("Safety", f"{int(p_scores['Safety Provider (Надійність)']*100)}%")
            prov_cols[1].metric("Resource", f"{int(p_scores['Resource Provider (Підтримка)']*100)}%")
            prov_cols[2].metric("Resonance", f"{int(p_scores['Resonance Provider (Емпатія/Розуміння)']*100)}%")
            prov_cols[3].metric("Expansion", f"{int(p_scores['Expansion Provider (Драйв/Натхнення)']*100)}%")
            
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