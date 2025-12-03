import streamlit as st
from .components import (
    PsychometricsComponent, ShadowComponent, ErosComponent, 
    RelationalNeedsComponent, ProfessionalComponent
)
from .enums import AttachmentStyle, ConflictResponse, RegulationMethod, ContextDependency, HollandCode
from .data import (
    EXPLANATIONS, get_scenarios,
    SHADOW_EXPLANATIONS, get_shadow_quiz,
    EROS_EXPLANATIONS, get_eros_quiz,
    PROFESSIONAL_EXPLANATIONS
)

def render_info_box(title: str, text: str):
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
        adhd = st.checkbox("РДУГ (ADHD)")
        asd = st.checkbox("РАС (Autism Spectrum)")
        
    return PsychometricsComponent(o, c, e, a, n, adhd, asd)

def render_shadow_form() -> ShadowComponent:
    st.header("2. Shadow Component (Захист)")
    # ВИПРАВЛЕНО: Використовуємо правильний словник і ключ
    st.markdown(SHADOW_EXPLANATIONS["intro"])
    
    tab1, tab2, tab3 = st.tabs(["🧩 Пройти тест", "⚙️ Ручне налаштування", "📚 Довідка"])
    comp = ShadowComponent()

    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(SHADOW_EXPLANATIONS["secure"])
            st.markdown(SHADOW_EXPLANATIONS["anxious"])
        with c2:
            st.markdown(SHADOW_EXPLANATIONS["avoidant"])
            st.markdown(SHADOW_EXPLANATIONS["disorganized"])

    with tab1:
        st.caption("Дайте відповідь на кілька питань:")
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
        att = st.selectbox("Стиль прив'язаності:", [x for x in AttachmentStyle], format_func=lambda x: x.value)
        conf = st.selectbox("Реакція на конфлікт:", [x for x in ConflictResponse], format_func=lambda x: x.value)
        reg = st.selectbox("Метод регуляції:", [x for x in RegulationMethod], format_func=lambda x: x.value)
        comp.attachment_style = att
        comp.conflict_response = conf
        comp.regulation_method = reg

    return comp

def render_eros_form() -> ErosComponent:
    st.header("3. Eros Component (Сексуальність)")
    # ВИПРАВЛЕНО: Використовуємо правильний словник і ключ
    st.markdown(EROS_EXPLANATIONS["intro"])
    
    tab1, tab2, tab3 = st.tabs(["🧩 Пройти тест", "⚙️ Ручне налаштування", "📚 Довідка"])
    comp = ErosComponent()

    with tab3:
        c1, c2 = st.columns(2)
        with c1: st.markdown(EROS_EXPLANATIONS["accelerator"])
        with c2: st.markdown(EROS_EXPLANATIONS["brake"])

    with tab1:
        st.caption("Оцініть свою реакцію:")
        quiz = get_eros_quiz()
        acc_s, brk_s = 0.0, 0.0
        for q in quiz:
            st.markdown(f"**{q.question}**")
            opts_map = {opt.text: opt for opt in q.options}
            ans = st.radio(" ", list(opts_map.keys()), key=f"eros_{q.id}", label_visibility="collapsed")
            sel = opts_map[ans]
            acc_s += sel.scores[0]
            brk_s += sel.scores[1]
            st.divider()
        
        final_acc = min(acc_s, 1.0)
        final_brk = min(brk_s, 1.0)
        comp.calculate_from_quiz(final_acc, final_brk)

    with tab2:
        acc = st.slider("Акселератор", 0, 100, 50) / 100.0
        brk = st.slider("Гальма", 0, 100, 50) / 100.0
        ctx = st.selectbox("Контекст:", [x for x in ContextDependency], format_func=lambda x: x.value)
        comp.accelerator = acc
        comp.brake = brk
        comp.context_dependency = ctx
    
    comp.erotic_tags = st.multiselect("Еротичні тригери:", 
                              ["Sapiosexual", "Demisexual", "Kinky", "Sensory", "Visual", "Service", "Praise"])
    return comp

def render_scenarios_engine() -> RelationalNeedsComponent:
    st.header("4. Context Layer (Сценарний аналіз)")
    st.info("Відповідайте інтуїтивно.")
    scenarios = get_scenarios()
    s, r, m, e = 0.0, 0.0, 0.0, 0.0
    
    for sc in scenarios:
        st.subheader(f"🔹 {sc.question}")
        st.caption(sc.description)
        opts_map = {opt.text: opt for opt in sc.options}
        choice_text = st.radio("Вибір:", list(opts_map.keys()), key=sc.id, label_visibility="collapsed")
        choice = opts_map[choice_text]
        s += choice.weights[0]
        r += choice.weights[1]
        m += choice.weights[2]
        e += choice.weights[3]
        st.markdown("---")

    def norm(val): return max(0.0, min(val / 2.0, 1.0))
    return RelationalNeedsComponent(norm(s), norm(r), norm(m), norm(e))

def render_professional_compass() -> ProfessionalComponent:
    st.header("5. Professional Layer (Компас Діяльності)")
    st.markdown(PROFESSIONAL_EXPLANATIONS["intro"])
    st.info(PROFESSIONAL_EXPLANATIONS["impact_warning"])
    
    # Використовуємо 3 колонки
    col1, col2, col3 = st.columns(3)
    
    # 1. Primary
    with col1:
        st.subheader("1️⃣ Домінанта")
        primary = st.selectbox(
            "Основний фокус:", 
            [x for x in HollandCode], 
            format_func=lambda x: x.value,
            key="prof_prim"
        )
        
    # 2. Secondary (виключаємо Primary)
    with col2:
        st.subheader("2️⃣ Допоміжний")
        secondary = st.selectbox(
            "Додатковий фокус:", 
            [x for x in HollandCode if x != primary], 
            format_func=lambda x: x.value,
            key="prof_sec"
        )

    # 3. Tertiary (виключаємо Primary та Secondary)
    with col3:
        st.subheader("3️⃣ Третинний")
        tertiary = st.selectbox(
            "Ситуативний фокус:", 
            [x for x in HollandCode if x not in (primary, secondary)], 
            format_func=lambda x: x.value,
            key="prof_tert"
        )

    st.markdown("---")
    st.subheader("⚖️ Баланс Work-Life")
    career_val = st.slider("Наскільки кар'єра є центральною частиною особистості?", 0, 100, 50) / 100.0
    
    if career_val > 0.8:
        st.warning("⚠️ Високий ризик дефіциту часу для партнера (Low Resource Availability).")

    return ProfessionalComponent(primary, secondary, tertiary, career_val)