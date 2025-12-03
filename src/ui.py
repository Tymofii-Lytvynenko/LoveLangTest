import streamlit as st
from .components import PsychometricsComponent, ShadowComponent, ErosComponent, RelationalNeedsComponent
from .enums import AttachmentStyle, ConflictResponse, RegulationMethod, ContextDependency
from .data import EXPLANATIONS, get_scenarios
from .enums import HollandCode
from .components import ProfessionalComponent
from .data import PROFESSIONAL_EXPLANATIONS

def render_info_box(title: str, text: str):
    """Helper to render scientific explanations cleanly."""
    with st.expander(f"ℹ️ Довідка: {title}"):
        st.markdown(text)

def render_big_five_manual():
    st.header("1. Substrate Layer (Психометрія)")
    st.markdown(EXPLANATIONS["big_five_intro"])
    
    col1, col2 = st.columns(2)
    
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
        st.markdown("**Нейродівергентність:**")
        st.caption("Ці прапорці змінюють алгоритм розрахунку потреб у Ресурсі (допомога з хаосом) та Новизні.")
        adhd = st.checkbox("РДУГ (ADHD)")
        asd = st.checkbox("РАС (Autism Spectrum)")
        
    return PsychometricsComponent(o, c, e, a, n, adhd, asd)

def render_shadow_form():
    st.header("2. Shadow Component (Захист)")
    st.markdown(EXPLANATIONS["shadow_intro"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Стиль прив'язаності**")
        st.caption("Ваша стратегія виживання у близькості.")
        att = st.selectbox("Оберіть тип:", [x for x in AttachmentStyle], format_func=lambda x: x.value)
        
        st.markdown("**Регуляція**")
        st.caption("Як ви заспокоюєтесь?")
        reg = st.selectbox("Оберіть метод:", [x for x in RegulationMethod], format_func=lambda x: x.value)
        
    with col2:
        st.markdown("**Реакція на конфлікт**")
        st.caption("Ваш 'автопілот' під час сварки.")
        conf = st.selectbox("Оберіть реакцію:", [x for x in ConflictResponse], format_func=lambda x: x.value)

    return ShadowComponent(att, conf, reg)

def render_eros_form():
    st.header("3. Eros Component (Сексуальність)")
    st.markdown(EXPLANATIONS["eros_intro"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Акселератор (Gas Pedal)")
        st.caption("Як легко вас збудити в ідеальних умовах?")
        acc = st.slider("Чутливість", 0, 100, 50) / 100.0
        
        st.markdown("#### Контекст")
        st.caption("Чи впливають умови (світло, звуки, час) на здатність отримати оргазм?")
        ctx = st.selectbox("Залежність:", [x for x in ContextDependency], format_func=lambda x: x.value)
        
    with col2:
        st.markdown("#### Гальма (Brake Pedal)")
        st.caption("Як сильно стрес 'вимикає' вас? (Високе значення = стрес вбиває секс)")
        brk = st.slider("Інгібіція", 0, 100, 50) / 100.0
        
        st.markdown("#### Тригери")
        tags = st.multiselect("Що натискає на газ?", 
                              ["Інтелект (Sapiosexual)", "Емоції (Demisexual)", "Влада/Біль (Kinky)", 
                               "Сенсорика (Sensory)", "Візуал", "Служіння (Service)"])
    
    return ErosComponent(acc, brk, ctx, tags)

def render_scenarios_engine() -> RelationalNeedsComponent:
    st.header("4. Context Layer (Сценарний аналіз)")
    st.info("Відповідайте інтуїтивно. Алгоритм зчитує не те, що ви 'любите', а те, чого вам бракує в дефіциті.")
    
    scenarios = get_scenarios()
    s_acc, r_acc, m_acc, e_acc = 0.0, 0.0, 0.0, 0.0
    
    for sc in scenarios:
        st.subheader(f"🔹 {sc.question}")
        st.caption(sc.description)
        
        opts_map = {opt.text: opt for opt in sc.options}
        choice_text = st.radio("Ваш вибір:", list(opts_map.keys()), key=sc.id, label_visibility="collapsed")
        
        choice = opts_map[choice_text]
        s_acc += choice.weights[0]
        r_acc += choice.weights[1]
        m_acc += choice.weights[2]
        e_acc += choice.weights[3]
        st.markdown("---")

    def norm(val): return max(0.0, min(val / 2.0, 1.0))

    return RelationalNeedsComponent(
        raw_safety=norm(s_acc),
        raw_resource=norm(r_acc),
        raw_resonance=norm(m_acc),
        raw_expansion=norm(e_acc)
    )

def render_professional_compass() -> ProfessionalComponent:
    st.header("5. Professional Layer (Компас Діяльності)")
    st.markdown(PROFESSIONAL_EXPLANATIONS["intro"])
    st.info(PROFESSIONAL_EXPLANATIONS["impact_warning"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🧭 Основний вектор")
        st.caption("Чим ви займаєтесь 80% часу?")
        primary = st.selectbox(
            "Оберіть домінуючий тип:", 
            [x for x in HollandCode], 
            format_func=lambda x: x.value,
            key="prof_prim"
        )
        
    with col2:
        st.subheader("Стиль")
        st.caption("Додатковий фокус (наприклад, Програміст (I) + Тімлід (E))")
        secondary = st.selectbox(
            "Оберіть вторинний тип:", 
            [x for x in HollandCode if x != primary], # Виключаємо вже обраний
            format_func=lambda x: x.value,
            key="prof_sec"
        )

    st.markdown("---")
    st.subheader("⚖️ Баланс Work-Life")
    career_val = st.slider(
        "Наскільки кар'єра є центральною частиною вашої особистості?",
        min_value=0, max_value=100, value=50,
        help="0 = Робота тільки заради грошей. 100 = Робота — це моя місія і сенс життя."
    ) / 100.0
    
    if career_val > 0.8:
        st.warning("⚠️ Високий ризик дефіциту часу для партнера (Low Resource Availability).")

    return ProfessionalComponent(primary, secondary, career_val)