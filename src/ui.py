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

def _facet_slider(label: str, obj, attr_name: str, help_text: str, key_prefix: str):
    """
    Helper function to render a facet slider (0-20 scale).
    Now includes a unique KEY for state persistence.
    """
    # Get current normalized value (0.0-1.0) and convert to scale (0-20) for display
    current_val_norm = getattr(obj, attr_name)
    default_val_scaled = int(current_val_norm * 20.0)
    
    # Unique key based on prefix (domain) and attribute
    unique_key = f"facet_{key_prefix}_{attr_name}"
    
    # Render slider 0-20
    new_val_scaled = st.slider(label, 0, 20, default_val_scaled, help=help_text, key=unique_key)
    
    # Write back normalized value (0.0-1.0)
    setattr(obj, attr_name, new_val_scaled / 20.0)

def render_big_five_manual() -> PsychometricsComponent:
    st.header("1. Substrate Layer (Психометрія)")
    st.markdown(EXPLANATIONS["big_five_intro"])
    
    col1, col2 = st.columns(2)
    
    # --- Базове налаштування ---
    # Додаємо ключі (key="...") для збереження стану
    with col1:
        render_info_box("Openness", EXPLANATIONS["openness"])
        o = st.number_input("Openness (Загальний, 0-100)", 0, 100, 50, help="Відкритість до досвіду", key="psycho_o")
        
        render_info_box("Conscientiousness", EXPLANATIONS["conscientiousness"])
        c = st.number_input("Conscientiousness (Загальний, 0-100)", 0, 100, 50, help="Сумлінність", key="psycho_c")
        
        render_info_box("Extraversion", EXPLANATIONS["extraversion"])
        e = st.number_input("Extraversion (Загальний, 0-100)", 0, 100, 50, help="Екстраверсія", key="psycho_e")

    with col2:
        render_info_box("Agreeableness", EXPLANATIONS["agreeableness"])
        a = st.number_input("Agreeableness (Загальний, 0-100)", 0, 100, 50, help="Доброзичливість", key="psycho_a")
        
        render_info_box("Neuroticism", EXPLANATIONS["neuroticism"])
        n = st.number_input("Neuroticism (Загальний, 0-100)", 0, 100, 50, help="Невротизм", key="psycho_n")
        
        st.markdown("---")
        st.caption("Нейродівергентність впливає на алгоритми Resource та Safety.")
        adhd = st.checkbox("РДУГ (ADHD)", key="psycho_adhd")
        asd = st.checkbox("РАС (Autism Spectrum)", key="psycho_asd")

    # Створюємо базовий об'єкт. Всі фасети стають = загальному балу (нормалізованому).
    psycho = PsychometricsComponent.from_high_level_scores(o, c, e, a, n, adhd, asd)

    # --- Advanced: Детальне налаштування ---
    with st.expander("🔬 Advanced: Детальне налаштування (30 фасетів, шкала 0-20)"):
        st.info("Введіть свої 'сирі' бали по фасетах (0-20). Якщо ви їх не знаєте, залиште як є.")
        
        t_n, t_e, t_o, t_a, t_c = st.tabs(["Neuroticism", "Extraversion", "Openness", "Agreeableness", "Conscientiousness"])
        
        # Передаємо префікси для унікальних ключів
        with t_n:
            st.markdown("#### 🔴 Neuroticism")
            c1, c2 = st.columns(2)
            with c1:
                _facet_slider("Anxiety", psycho.neuroticism, "anxiety", "Тривожність", "neur")
                _facet_slider("Anger", psycho.neuroticism, "hostility", "Ворожість", "neur")
                _facet_slider("Depression", psycho.neuroticism, "depression", "Депресивність", "neur")
            with c2:
                _facet_slider("Self-Consciousness", psycho.neuroticism, "self_consciousness", "Сором'язливість", "neur")
                _facet_slider("Immoderation", psycho.neuroticism, "impulsiveness", "Імпульсивність", "neur")
                _facet_slider("Vulnerability", psycho.neuroticism, "vulnerability", "Вразливість", "neur")

        with t_e:
            st.markdown("#### 🟡 Extraversion")
            c1, c2 = st.columns(2)
            with c1:
                _facet_slider("Friendliness", psycho.extraversion, "warmth", "Теплота", "extr")
                _facet_slider("Gregariousness", psycho.extraversion, "gregariousness", "Стадність", "extr")
                _facet_slider("Assertiveness", psycho.extraversion, "assertiveness", "Асертивність", "extr")
            with c2:
                _facet_slider("Activity Level", psycho.extraversion, "activity", "Активність", "extr")
                _facet_slider("Excitement Seeking", psycho.extraversion, "excitement_seeking", "Пошук вражень", "extr")
                _facet_slider("Cheerfulness", psycho.extraversion, "positive_emotions", "Позитивні емоції", "extr")

        with t_o:
            st.markdown("#### 🟢 Openness")
            c1, c2 = st.columns(2)
            with c1:
                _facet_slider("Imagination", psycho.openness, "fantasy", "Уява", "open")
                _facet_slider("Artistic Interests", psycho.openness, "aesthetics", "Естетика", "open")
                _facet_slider("Emotionality", psycho.openness, "feelings", "Емоційність", "open")
            with c2:
                _facet_slider("Adventurousness", psycho.openness, "actions", "Дії", "open")
                _facet_slider("Intellect", psycho.openness, "ideas", "Ідеї", "open")
                _facet_slider("Liberalism", psycho.openness, "values", "Цінності", "open")

        with t_a:
            st.markdown("#### 🔵 Agreeableness")
            c1, c2 = st.columns(2)
            with c1:
                _facet_slider("Trust", psycho.agreeableness, "trust", "Довіра", "agre")
                _facet_slider("Morality", psycho.agreeableness, "straightforwardness", "Чесність", "agre")
                _facet_slider("Altruism", psycho.agreeableness, "altruism", "Альтруїзм", "agre")
            with c2:
                _facet_slider("Cooperation", psycho.agreeableness, "compliance", "Поступливість", "agre")
                _facet_slider("Modesty", psycho.agreeableness, "modesty", "Скромність", "agre")
                _facet_slider("Sympathy", psycho.agreeableness, "tender_mindedness", "Чуйність", "agre")

        with t_c:
            st.markdown("#### 🟣 Conscientiousness")
            c1, c2 = st.columns(2)
            with c1:
                _facet_slider("Self-Efficacy", psycho.conscientiousness, "competence", "Компетентність", "cons")
                _facet_slider("Orderliness", psycho.conscientiousness, "order", "Порядок", "cons")
                _facet_slider("Dutifulness", psycho.conscientiousness, "dutifulness", "Обов'язок", "cons")
            with c2:
                _facet_slider("Achievement", psycho.conscientiousness, "achievement", "Досягнення", "cons")
                _facet_slider("Self-Discipline", psycho.conscientiousness, "self_discipline", "Самодисципліна", "cons")
                _facet_slider("Cautiousness", psycho.conscientiousness, "deliberation", "Обережність", "cons")

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
            # Додаємо унікальний ключ
            ans = st.radio(" ", list(opts_map.keys()), key=f"shadow_q_{q.id}", label_visibility="collapsed")
            sel = opts_map[ans]
            sec += sel.scores[0]
            anx += sel.scores[1]
            avo += sel.scores[2]
            st.divider()
        comp.calculate_from_quiz((sec, anx, avo))

    with tab2:
        # Додаємо ключі
        comp.attachment_style = st.selectbox("Стиль прив'язаності:", [x for x in AttachmentStyle], format_func=lambda x: x.value, key="shadow_manual_att")
        comp.conflict_response = st.selectbox("Реакція на конфлікт:", [x for x in ConflictResponse], format_func=lambda x: x.value, key="shadow_manual_conf")
        comp.regulation_method = st.selectbox("Метод регуляції:", [x for x in RegulationMethod], format_func=lambda x: x.value, key="shadow_manual_reg")

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
            ans = st.radio(" ", list(opts_map.keys()), key=f"eros_q_{q.id}", label_visibility="collapsed")
            sel = opts_map[ans]
            acc_score += sel.scores[0]
            brk_score += sel.scores[1]
            st.divider()
        comp.calculate_from_quiz(min(acc_score, 1.0), min(brk_score, 1.0))
        st.metric("Акселератор", f"{comp.accelerator*100:.0f}%")
        st.metric("Гальма", f"{comp.brake*100:.0f}%")

    with tab2:
        # Слайдери для ручного вводу (додаємо keys)
        comp.accelerator = st.slider("Акселератор", 0, 100, 50, key="eros_manual_acc") / 100.0
        comp.brake = st.slider("Гальма", 0, 100, 50, key="eros_manual_brk") / 100.0
        comp.context_dependency = st.selectbox("Контекст:", [x for x in ContextDependency], format_func=lambda x: x.value, key="eros_manual_ctx")
    
    comp.erotic_tags = st.multiselect("Оберіть контекст збудження:", list(EROS_TAGS_EXPLANATIONS.keys()), key="eros_tags")
    return comp

def render_scenarios_engine() -> RelationalNeedsComponent:
    st.header("4. Context Layer (Сценарний аналіз)")
    scenarios = get_scenarios()
    s_acc, r_acc, m_acc, e_acc = 0.0, 0.0, 0.0, 0.0
    
    for sc in scenarios:
        st.subheader(f"🔹 {sc.question}")
        opts_map = {opt.text: opt for opt in sc.options}
        # Ключі для сценаріїв вже унікальні (sc.id), але переконаємось, що вони не конфліктують
        choice_text = st.radio("Ваш вибір:", list(opts_map.keys()), key=f"scenario_{sc.id}", label_visibility="collapsed")
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
    # Додаємо ключі
    with c1: p = st.selectbox("Основний фокус:", all_codes, index=0, format_func=lambda x: x.value, key="prof_primary")
    with c2: s = st.selectbox("Додатковий фокус:", all_codes, index=1, format_func=lambda x: x.value, key="prof_secondary")
    with c3: t = st.selectbox("Ситуативний фокус:", all_codes, index=2, format_func=lambda x: x.value, key="prof_tertiary")
    
    career_val = st.slider("Наскільки кар'єра важлива? (Work-Life Balance)", 0, 100, 50, key="prof_centrality") / 100.0
    return ProfessionalComponent(p, s, t, career_val)
