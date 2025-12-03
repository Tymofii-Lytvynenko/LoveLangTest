import streamlit as st
from .components import (
    PsychometricsComponent, 
    ShadowComponent, 
    ErosComponent, 
    RelationalNeedsComponent, 
    ProfessionalComponent
)
from .enums import (
    AttachmentStyle, 
    ConflictResponse, 
    RegulationMethod, 
    ContextDependency, 
    HollandCode
)
from .data import (
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
    """Helper to render scientific explanations cleanly."""
    with st.expander(f"ℹ️ Довідка: {title}"):
        st.markdown(text)

def render_big_five_manual() -> PsychometricsComponent:
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

def render_shadow_form() -> ShadowComponent:
    st.header("2. Shadow Component (Захист)")
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
        st.caption("Дайте відповідь на кілька питань, щоб алгоритм визначив ваш стиль.")
        quiz = get_shadow_quiz()
        sec, anx, avo = 0.0, 0.0, 0.0
        
        for q in quiz:
            st.markdown(f"**{q.question}**")
            opts_map = {opt.text: opt for opt in q.options}
            ans = st.radio(" ", list(opts_map.keys()), key=f"shadow_{q.id}", label_visibility="collapsed")
            
            sel_opt = opts_map[ans]
            sec += sel_opt.scores[0]
            anx += sel_opt.scores[1]
            avo += sel_opt.scores[2]
            st.divider()
        
        # Обчислюємо результат тесту
        comp.calculate_from_quiz((sec, anx, avo))

    with tab2:
        st.caption("Якщо ви точно знаєте свій тип, оберіть його тут.")
        att = st.selectbox("Стиль прив'язаності:", [x for x in AttachmentStyle], format_func=lambda x: x.value)
        conf = st.selectbox("Реакція на конфлікт:", [x for x in ConflictResponse], format_func=lambda x: x.value)
        reg = st.selectbox("Метод регуляції:", [x for x in RegulationMethod], format_func=lambda x: x.value)
        
        comp.attachment_style = att
        comp.conflict_response = conf
        comp.regulation_method = reg

    return comp

def render_eros_form() -> ErosComponent:
    st.header("3. Eros Component (Сексуальність)")
    st.markdown(EROS_EXPLANATIONS["intro"])
    
    tab1, tab2, tab3 = st.tabs(["🧩 Пройти тест", "⚙️ Ручне налаштування", "📚 Довідка (Теорія)"])
    
    comp = ErosComponent()

    with tab3:
        st.subheader("Акселератор та Гальма")
        c1, c2 = st.columns(2)
        with c1: st.markdown(EROS_EXPLANATIONS["accelerator"])
        with c2: st.markdown(EROS_EXPLANATIONS["brake"])
        
        st.divider()
        st.subheader("Контекстні Тригери (Ключі запалювання)")
        st.markdown(EROS_EXPLANATIONS["triggers_intro"])
        
        for tag, desc in EROS_TAGS_EXPLANATIONS.items():
            st.info(desc)

    with tab1:
        st.caption("Оцініть свою фізіологічну реакцію.")
        quiz = get_eros_quiz()
        acc_score, brk_score = 0.0, 0.0
        
        for q in quiz:
            st.markdown(f"**{q.question}**")
            opts_map = {opt.text: opt for opt in q.options}
            ans = st.radio(" ", list(opts_map.keys()), key=f"eros_{q.id}", label_visibility="collapsed")
            
            sel_opt = opts_map[ans]
            acc_score += sel_opt.scores[0]
            brk_score += sel_opt.scores[1]
            st.divider()
            
        final_acc = min(acc_score, 1.0)
        final_brk = min(brk_score, 1.0)
        
        st.metric("Акселератор", f"{final_acc*100:.0f}%")
        st.metric("Гальма (Чутливість до стресу)", f"{final_brk*100:.0f}%")
        
        comp.calculate_from_quiz(final_acc, final_brk)

    with tab2:
        acc = st.slider("Акселератор", 0, 100, 50) / 100.0
        brk = st.slider("Гальма", 0, 100, 50) / 100.0
        ctx = st.selectbox("Контекст:", [x for x in ContextDependency], format_func=lambda x: x.value)
        
        comp.accelerator = acc
        comp.brake = brk
        comp.context_dependency = ctx
    
    # Вибір тегів завжди доступний (поза табами)
    st.markdown("#### 🎯 Ваші тригери")
    st.caption("Що саме натискає на ваш 'Акселератор'? Оберіть топ-3.")
    
    tags_list = list(EROS_TAGS_EXPLANATIONS.keys())
    comp.erotic_tags = st.multiselect(
        "Оберіть контекст збудження:", 
        tags_list,
        help="Зайдіть у вкладку 'Довідка', щоб прочитати детальний опис кожного типу."
    )
    
    return comp

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
    
    col1, col2, col3 = st.columns(3)
    
    # Повний список опцій для всіх (уникнення конфліктів UI)
    all_codes = [x for x in HollandCode]

    with col1:
        st.subheader("1️⃣ Домінанта")
        primary = st.selectbox(
            "Основний фокус:", 
            all_codes, 
            format_func=lambda x: x.value,
            key="prof_prim",
            index=0
        )
        
    with col2:
        st.subheader("2️⃣ Допоміжний")
        secondary = st.selectbox(
            "Додатковий фокус:", 
            all_codes, 
            format_func=lambda x: x.value,
            key="prof_sec",
            index=1
        )

    with col3:
        st.subheader("3️⃣ Третинний")
        tertiary = st.selectbox(
            "Ситуативний фокус:", 
            all_codes, 
            format_func=lambda x: x.value,
            key="prof_tert",
            index=2
        )

    # Валідація дублікатів
    errors = []
    if primary == secondary:
        errors.append("⚠️ 'Допоміжний' тип збігається з 'Домінантою'.")
    if secondary == tertiary:
        errors.append("⚠️ 'Третинний' тип збігається з 'Допоміжним'.")
    if primary == tertiary:
        errors.append("⚠️ 'Третинний' тип збігається з 'Домінантою'.")
        
    if errors:
        for err in set(errors):
            st.error(err)

    st.markdown("---")
    st.subheader("⚖️ Баланс Work-Life")
    career_val = st.slider(
        "Наскільки кар'єра є центральною частиною особистості?", 
        min_value=0, max_value=100, value=50,
        help="0 = Робота тільки заради грошей. 100 = Робота — це моя місія."
    ) / 100.0
    
    if career_val > 0.8:
        st.warning("⚠️ Високий ризик дефіциту часу для партнера (Low Resource Availability).")

    return ProfessionalComponent(primary, secondary, tertiary, career_val)