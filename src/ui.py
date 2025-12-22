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

def _facet_slider(label: str, obj, attr_name: str, help_text: str):
    """
    Helper function to render a facet slider (0-20 scale).
    Internally converts 0-20 integer input to 0.0-1.0 float model value.
    """
    # Get current normalized value (0.0-1.0) and convert to scale (0-20) for display
    current_val_norm = getattr(obj, attr_name)
    default_val_scaled = int(current_val_norm * 20.0)
    
    # Render slider 0-20
    new_val_scaled = st.slider(label, 0, 20, default_val_scaled, help=help_text)
    
    # Write back normalized value (0.0-1.0)
    setattr(obj, attr_name, new_val_scaled / 20.0)

def render_big_five_manual() -> PsychometricsComponent:
    st.header("1. Substrate Layer (Психометрія)")
    st.markdown(EXPLANATIONS["big_five_intro"])
    
    col1, col2 = st.columns(2)
    
    # --- Базове налаштування (Загальні бали залишаємо 0-100 для зручності T-scores) ---
    with col1:
        render_info_box("Openness", EXPLANATIONS["openness"])
        o = st.number_input("Openness (Загальний, 0-100)", 0, 100, 50, help="Відкритість до досвіду")
        
        render_info_box("Conscientiousness", EXPLANATIONS["conscientiousness"])
        c = st.number_input("Conscientiousness (Загальний, 0-100)", 0, 100, 50, help="Сумлінність / Організованість")
        
        render_info_box("Extraversion", EXPLANATIONS["extraversion"])
        e = st.number_input("Extraversion (Загальний, 0-100)", 0, 100, 50, help="Екстраверсія")

    with col2:
        render_info_box("Agreeableness", EXPLANATIONS["agreeableness"])
        a = st.number_input("Agreeableness (Загальний, 0-100)", 0, 100, 50, help="Доброзичливість")
        
        render_info_box("Neuroticism", EXPLANATIONS["neuroticism"])
        n = st.number_input("Neuroticism (Загальний, 0-100)", 0, 100, 50, help="Невротизм / Емоційна нестабільність")
        
        st.markdown("---")
        st.caption("Нейродівергентність впливає на алгоритми Resource та Safety.")
        adhd = st.checkbox("РДУГ (ADHD)")
        asd = st.checkbox("РАС (Autism Spectrum)")

    # Створюємо базовий об'єкт. Всі фасети стають = загальному балу (нормалізованому).
    psycho = PsychometricsComponent.from_high_level_scores(o, c, e, a, n, adhd, asd)

    # --- Advanced: Детальне налаштування (30 фасетів, шкала 0-20) ---
    with st.expander("🔬 Advanced: Детальне налаштування (30 фасетів, шкала 0-20)"):
        st.info("Введіть свої 'сирі' бали по фасетах (0-20). Якщо ви їх не знаєте, залиште як є (вони розраховані з загальних балів).")
        
        t_n, t_e, t_o, t_a, t_c = st.tabs(["Neuroticism", "Extraversion", "Openness", "Agreeableness", "Conscientiousness"])
        
        # 1. Neuroticism Domain
        with t_n:
            st.markdown("#### 🔴 Neuroticism")
            c1, c2 = st.columns(2)
            with c1:
                _facet_slider("Anxiety (Тривожність)", psycho.neuroticism, "anxiety", "Схильність хвилюватися про майбутнє.")
                _facet_slider("Anger (Ворожість)", psycho.neuroticism, "hostility", "Легкість виникнення роздратування.")
                _facet_slider("Depression (Депресивність)", psycho.neuroticism, "depression", "Схильність до смутку.")
            with c2:
                _facet_slider("Self-Consciousness (Сором'язливість)", psycho.neuroticism, "self_consciousness", "Страх осуду.")
                _facet_slider("Immoderation (Імпульсивність)", psycho.neuroticism, "impulsiveness", "Важкість у стримуванні бажань.")
                _facet_slider("Vulnerability (Вразливість)", psycho.neuroticism, "vulnerability", "Реакція на стрес.")

        # 2. Extraversion Domain
        with t_e:
            st.markdown("#### 🟡 Extraversion")
            c1, c2 = st.columns(2)
            with c1:
                _facet_slider("Friendliness (Теплота)", psycho.extraversion, "warmth", "Легкість у вираженні любові.")
                _facet_slider("Gregariousness (Стадність)", psycho.extraversion, "gregariousness", "Потреба в компанії.")
                _facet_slider("Assertiveness (Асертивність)", psycho.extraversion, "assertiveness", "Лідерство.")
            with c2:
                _facet_slider("Activity Level (Активність)", psycho.extraversion, "activity", "Темп життя.")
                _facet_slider("Excitement Seeking (Пошук вражень)", psycho.extraversion, "excitement_seeking", "Потреба в драйві.")
                _facet_slider("Cheerfulness (Позитивні емоції)", psycho.extraversion, "positive_emotions", "Оптимізм.")

        # 3. Openness Domain
        with t_o:
            st.markdown("#### 🟢 Openness")
            c1, c2 = st.columns(2)
            with c1:
                _facet_slider("Imagination (Уява)", psycho.openness, "fantasy", "Багатство фантазій.")
                _facet_slider("Artistic Interests (Естетика)", psycho.openness, "aesthetics", "Любов до мистецтва.")
                _facet_slider("Emotionality (Емоційність)", psycho.openness, "feelings", "Глибина почуттів.")
            with c2:
                _facet_slider("Adventurousness (Дії/Новизна)", psycho.openness, "actions", "Готовність пробувати нове.")
                _facet_slider("Intellect (Ідеї)", psycho.openness, "ideas", "Інтелектуальна допитливість.")
                _facet_slider("Liberalism (Цінності)", psycho.openness, "values", "Гнучкість поглядів.")

        # 4. Agreeableness Domain
        with t_a:
            st.markdown("#### 🔵 Agreeableness")
            c1, c2 = st.columns(2)
            with c1:
                _facet_slider("Trust (Довіра)", psycho.agreeableness, "trust", "Віра в людей.")
                _facet_slider("Morality (Прямолінійність)", psycho.agreeableness, "straightforwardness", "Чесність.")
                _facet_slider("Altruism (Альтруїзм)", psycho.agreeableness, "altruism", "Бажання допомагати.")
            with c2:
                _facet_slider("Cooperation (Поступливість)", psycho.agreeableness, "compliance", "Уникнення конфліктів.")
                _facet_slider("Modesty (Скромність)", psycho.agreeableness, "modesty", "Відсутність зарозумілості.")
                _facet_slider("Sympathy (Чуйність)", psycho.agreeableness, "tender_mindedness", "Емпатія.")

        # 5. Conscientiousness Domain
        with t_c:
            st.markdown("#### 🟣 Conscientiousness")
            c1, c2 = st.columns(2)
            with c1:
                _facet_slider("Self-Efficacy (Компетентність)", psycho.conscientiousness, "competence", "Віра в свої сили.")
                _facet_slider("Orderliness (Порядок)", psycho.conscientiousness, "order", "Любов до порядку.")
                _facet_slider("Dutifulness (Обов'язок)", psycho.conscientiousness, "dutifulness", "Надійність.")
            with c2:
                _facet_slider("Achievement Striving (Досягнення)", psycho.conscientiousness, "achievement", "Амбіції.")
                _facet_slider("Self-Discipline (Самодисципліна)", psycho.conscientiousness, "self_discipline", "Сила волі.")
                _facet_slider("Cautiousness (Обережність)", psycho.conscientiousness, "deliberation", "Думання перед дією.")

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