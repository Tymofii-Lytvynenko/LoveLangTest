import streamlit as st
from src.domain.psychometrics import PsychometricsComponent
from src.domain.shadow import ShadowComponent
from src.domain.eros import ErosComponent
from src.domain.needs import RelationalNeedsComponent
from src.domain.professional import ProfessionalComponent

from src.enums import (
    AttachmentStyle, 
    ConflictResponse, 
    RegulationMethod, 
    ContextDependency, 
    HollandCode
)
from src.data import (
    EXPLANATIONS, 
    get_scenarios,
    SHADOW_EXPLANATIONS, 
    get_shadow_quiz,
    EROS_EXPLANATIONS, 
    get_eros_quiz, 
    EROS_TAGS_EXPLANATIONS,
    PROFESSIONAL_EXPLANATIONS
)

def render_info_box(title: str, text: str):
    with st.expander(f"ℹ️ Довідка: {title}"):
        st.markdown(text)

def render_big_five_manual() -> PsychometricsComponent:
    st.header("1. Substrate Layer (Психометрія)")
    st.markdown(EXPLANATIONS["big_five_intro"])
    
    col1, col2 = st.columns(2)
    
    # Базові налаштування (як раніше)
    with col1:
        render_info_box("Openness", EXPLANATIONS["openness"])
        o = st.number_input("Openness (0-100)", 0, 100, 50)
        
        render_info_box("Conscientiousness", EXPLANATIONS["conscientiousness"])
        c = st.number_input("Conscientiousness (0-100)", 0, 100, 50)
        
        render_info_box("Extraversion", EXPLANATIONS["extraversion"])
        e = st.number_input("Extraversion (0-100)", 0, 100, 50)

    with col2:
        render_info_box("Agreeableness", EXPLANATIONS["agreeableness"])
        a = st.number_input("Agreeableness (0-100)", 0, 100, 50)
        
        render_info_box("Neuroticism", EXPLANATIONS["neuroticism"])
        n = st.number_input("Neuroticism (0-100)", 0, 100, 50)
        
        st.markdown("---")
        adhd = st.checkbox("РДУГ (ADHD)")
        asd = st.checkbox("РАС (Autism Spectrum)")

    # Створюємо базовий компонент
    psycho = PsychometricsComponent.from_high_level_scores(o, c, e, a, n, adhd, asd)

    # Advanced налаштування фасетів
    with st.expander("🔬 Advanced: Детальне налаштування (30 фасетів)"):
        st.caption("Змініть ці значення, якщо знаєте свій розширений профіль (IPIP-NEO).")
        
        # Neuroticism
        st.markdown("##### Neuroticism")
        psycho.neuroticism.anxiety = st.slider("Anxiety (Тривожність)", 0.0, 1.0, psycho.neuroticism.anxiety)
        psycho.neuroticism.hostility = st.slider("Anger (Ворожість)", 0.0, 1.0, psycho.neuroticism.hostility)
        psycho.neuroticism.vulnerability = st.slider("Vulnerability (Вразливість)", 0.0, 1.0, psycho.neuroticism.vulnerability)
        
        # Conscientiousness
        st.markdown("##### Conscientiousness")
        psycho.conscientiousness.order = st.slider("Order (Порядок)", 0.0, 1.0, psycho.conscientiousness.order)
        psycho.conscientiousness.self_discipline = st.slider("Self-Discipline", 0.0, 1.0, psycho.conscientiousness.self_discipline)
        psycho.conscientiousness.achievement = st.slider("Achievement", 0.0, 1.0, psycho.conscientiousness.achievement)
        
        # Openness
        st.markdown("##### Openness")
        psycho.openness.ideas = st.slider("Ideas (Інтелект)", 0.0, 1.0, psycho.openness.ideas)
        psycho.openness.feelings = st.slider("Feelings (Емоційність)", 0.0, 1.0, psycho.openness.feelings)

    return psycho

def render_shadow_form() -> ShadowComponent:
    st.header("2. Shadow Component (Захист)")
    st.markdown(SHADOW_EXPLANATIONS["intro"])
    
    tab1, tab2 = st.tabs(["🧩 Пройти тест", "⚙️ Ручне налаштування"])
    
    comp = ShadowComponent()

    with tab1:
        quiz = get_shadow_quiz()
        sec, anx, avo = 0.0, 0.0, 0.0
        for q in quiz:
            st.markdown(f"**{q.question}**")
            opts_map = {opt.text: opt for opt in q.options}
            ans = st.radio(" ", list(opts_map.keys()), key=f"shadow_{q.id}", label_visibility="collapsed")
            sel = opts_map[ans]
            sec += sel.scores[0]
            anx += sel.scores[1]
            avo += sel.scores[2]
            st.divider()
        comp.calculate_from_quiz((sec, anx, avo))

    with tab2:
        comp.attachment_style = st.selectbox("Стиль прив'язаності:", [x for x in AttachmentStyle], format_func=lambda x: x.value)
        comp.conflict_response = st.selectbox("Реакція на конфлікт:", [x for x in ConflictResponse], format_func=lambda x: x.value)
        comp.regulation_method = st.selectbox("Метод регуляції:", [x for x in RegulationMethod], format_func=lambda x: x.value)

    return comp

def render_eros_form() -> ErosComponent:
    st.header("3. Eros Component (Сексуальність)")
    st.markdown(EROS_EXPLANATIONS["intro"])
    
    tab1, tab2 = st.tabs(["🧩 Пройти тест", "⚙️ Ручне налаштування"])
    comp = ErosComponent()

    with tab1:
        quiz = get_eros_quiz()
        acc_score, brk_score = 0.0, 0.0
        for q in quiz:
            st.markdown(f"**{q.question}**")
            opts_map = {opt.text: opt for opt in q.options}
            ans = st.radio(" ", list(opts_map.keys()), key=f"eros_{q.id}", label_visibility="collapsed")
            sel = opts_map[ans]
            acc_score += sel.scores[0]
            brk_score += sel.scores[1]
            st.divider()
        comp.calculate_from_quiz(min(acc_score, 1.0), min(brk_score, 1.0))
        st.metric("Акселератор", f"{comp.accelerator*100:.0f}%")
        st.metric("Гальма", f"{comp.brake*100:.0f}%")

    with tab2:
        comp.accelerator = st.slider("Акселератор", 0, 100, 50) / 100.0
        comp.brake = st.slider("Гальма", 0, 100, 50) / 100.0
        comp.context_dependency = st.selectbox("Контекст:", [x for x in ContextDependency], format_func=lambda x: x.value)
    
    comp.erotic_tags = st.multiselect("Оберіть контекст збудження:", list(EROS_TAGS_EXPLANATIONS.keys()))
    return comp

def render_scenarios_engine() -> RelationalNeedsComponent:
    st.header("4. Context Layer (Сценарний аналіз)")
    scenarios = get_scenarios()
    s_acc, r_acc, m_acc, e_acc = 0.0, 0.0, 0.0, 0.0
    
    for sc in scenarios:
        st.subheader(f"🔹 {sc.question}")
        opts_map = {opt.text: opt for opt in sc.options}
        choice_text = st.radio("Ваш вибір:", list(opts_map.keys()), key=sc.id, label_visibility="collapsed")
        choice = opts_map[choice_text]
        s_acc += choice.weights[0]
        r_acc += choice.weights[1]
        m_acc += choice.weights[2]
        e_acc += choice.weights[3]
        st.markdown("---")
    
    return RelationalNeedsComponent(raw_safety=s_acc, raw_resource=r_acc, raw_resonance=m_acc, raw_expansion=e_acc)

def render_professional_compass() -> ProfessionalComponent:
    st.header("5. Professional Layer (Компас Діяльності)")
    st.markdown(PROFESSIONAL_EXPLANATIONS["intro"])
    all_codes = [x for x in HollandCode]
    
    c1, c2, c3 = st.columns(3)
    with c1: p = st.selectbox("Основний фокус:", all_codes, index=0, format_func=lambda x: x.value)
    with c2: s = st.selectbox("Додатковий фокус:", all_codes, index=1, format_func=lambda x: x.value)
    with c3: t = st.selectbox("Ситуативний фокус:", all_codes, index=2, format_func=lambda x: x.value)
    
    career_val = st.slider("Наскільки кар'єра важлива? (Work-Life Balance)", 0, 100, 50) / 100.0
    return ProfessionalComponent(p, s, t, career_val)