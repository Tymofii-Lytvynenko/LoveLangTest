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

def render_big_five_manual() -> PsychometricsComponent:
    st.header("1. Substrate Layer (Психометрія)")
    st.markdown(EXPLANATIONS["big_five_intro"])
    
    col1, col2 = st.columns(2)
    
    # --- Базове налаштування (5 загальних слайдерів) ---
    with col1:
        render_info_box("Openness", EXPLANATIONS["openness"])
        o = st.number_input("Openness (0-100)", 0, 100, 50, help="Відкритість до досвіду")
        
        render_info_box("Conscientiousness", EXPLANATIONS["conscientiousness"])
        c = st.number_input("Conscientiousness (0-100)", 0, 100, 50, help="Сумлінність / Організованість")
        
        render_info_box("Extraversion", EXPLANATIONS["extraversion"])
        e = st.number_input("Extraversion (0-100)", 0, 100, 50, help="Екстраверсія")

    with col2:
        render_info_box("Agreeableness", EXPLANATIONS["agreeableness"])
        a = st.number_input("Agreeableness (0-100)", 0, 100, 50, help="Доброзичливість")
        
        render_info_box("Neuroticism", EXPLANATIONS["neuroticism"])
        n = st.number_input("Neuroticism (0-100)", 0, 100, 50, help="Невротизм / Емоційна нестабільність")
        
        st.markdown("---")
        st.caption("Нейродівергентність впливає на алгоритми Resource та Safety.")
        adhd = st.checkbox("РДУГ (ADHD)")
        asd = st.checkbox("РАС (Autism Spectrum)")

    # Створюємо базовий об'єкт (всі фасети за замовчуванням дорівнюють загальному балу)
    psycho = PsychometricsComponent.from_high_level_scores(o, c, e, a, n, adhd, asd)

    # --- Advanced: Детальне налаштування (30 фасетів) ---
    with st.expander("🔬 Advanced: Детальне налаштування (30 фасетів IPIP-NEO)"):
        st.info("За замовчуванням підкатегорії успадковують значення головної риси. Змінюйте їх, якщо знаєте свій детальний профіль.")
        
        # Використовуємо таби для компактності, бо 30 слайдерів - це багато
        t_n, t_e, t_o, t_a, t_c = st.tabs(["Neuroticism", "Extraversion", "Openness", "Agreeableness", "Conscientiousness"])
        
        # 1. Neuroticism Domain
        with t_n:
            st.markdown("#### 🔴 Neuroticism (Загроза та Реактивність)")
            c1, c2 = st.columns(2)
            with c1:
                psycho.neuroticism.anxiety = st.slider("Anxiety (Тривожність)", 0.0, 1.0, psycho.neuroticism.anxiety, help="Схильність хвилюватися про майбутнє.")
                psycho.neuroticism.hostility = st.slider("Anger (Ворожість)", 0.0, 1.0, psycho.neuroticism.hostility, help="Легкість виникнення роздратування та гніву.")
                psycho.neuroticism.depression = st.slider("Depression (Депресивність)", 0.0, 1.0, psycho.neuroticism.depression, help="Схильність до смутку, апатії та почуття провини.")
            with c2:
                psycho.neuroticism.self_consciousness = st.slider("Self-Consciousness (Сором'язливість)", 0.0, 1.0, psycho.neuroticism.self_consciousness, help="Чутливість до думки інших, страх ганьби.")
                psycho.neuroticism.impulsiveness = st.slider("Immoderation (Імпульсивність)", 0.0, 1.0, psycho.neuroticism.impulsiveness, help="Важкість у стримуванні бажань та спокус.")
                psycho.neuroticism.vulnerability = st.slider("Vulnerability (Вразливість)", 0.0, 1.0, psycho.neuroticism.vulnerability, help="Здатність справлятися зі стресом.")

        # 2. Extraversion Domain
        with t_e:
            st.markdown("#### 🟡 Extraversion (Енергія та Соціум)")
            c1, c2 = st.columns(2)
            with c1:
                psycho.extraversion.warmth = st.slider("Friendliness (Теплота)", 0.0, 1.0, psycho.extraversion.warmth, help="Щирий інтерес до людей, легкість у вираженні любові.")
                psycho.extraversion.gregariousness = st.slider("Gregariousness (Стадність)", 0.0, 1.0, psycho.extraversion.gregariousness, help="Потреба в компанії, нелюбов до самотності.")
                psycho.extraversion.assertiveness = st.slider("Assertiveness (Асертивність)", 0.0, 1.0, psycho.extraversion.assertiveness, help="Лідерство, домінантність, вміння відстоювати своє.")
            with c2:
                psycho.extraversion.activity = st.slider("Activity Level (Активність)", 0.0, 1.0, psycho.extraversion.activity, help="Темп життя, енергійність, постійна зайнятість.")
                psycho.extraversion.excitement_seeking = st.slider("Excitement Seeking (Пошук вражень)", 0.0, 1.0, psycho.extraversion.excitement_seeking, help="Потреба в драйві, ризику та стимуляції.")
                psycho.extraversion.positive_emotions = st.slider("Cheerfulness (Позитивні емоції)", 0.0, 1.0, psycho.extraversion.positive_emotions, help="Схильність відчувати радість та оптимізм.")

        # 3. Openness Domain
        with t_o:
            st.markdown("#### 🟢 Openness (Когнітивний стиль)")
            c1, c2 = st.columns(2)
            with c1:
                psycho.openness.fantasy = st.slider("Imagination (Уява)", 0.0, 1.0, psycho.openness.fantasy, help="Багатство внутрішнього світу та фантазій.")
                psycho.openness.aesthetics = st.slider("Artistic Interests (Естетика)", 0.0, 1.0, psycho.openness.aesthetics, help="Чутливість до краси, мистецтва, музики.")
                psycho.openness.feelings = st.slider("Emotionality (Емоційність)", 0.0, 1.0, psycho.openness.feelings, help="Глибина та усвідомлення власних емоцій.")
            with c2:
                psycho.openness.actions = st.slider("Adventurousness (Дії/Новизна)", 0.0, 1.0, psycho.openness.actions, help="Готовність пробувати нове (їжу, місця, хобі).")
                psycho.openness.ideas = st.slider("Intellect (Ідеї)", 0.0, 1.0, psycho.openness.ideas, help="Інтелектуальна допитливість, любов до філософських дебатів.")
                psycho.openness.values = st.slider("Liberalism (Цінності)", 0.0, 1.0, psycho.openness.values, help="Готовність переглядати соціальні, політичні та релігійні погляди.")

        # 4. Agreeableness Domain
        with t_a:
            st.markdown("#### 🔵 Agreeableness (Соціальна гармонія)")
            c1, c2 = st.columns(2)
            with c1:
                psycho.agreeableness.trust = st.slider("Trust (Довіра)", 0.0, 1.0, psycho.agreeableness.trust, help="Віра в чесність та добрі наміри інших людей.")
                psycho.agreeableness.straightforwardness = st.slider("Morality (Прямолінійність)", 0.0, 1.0, psycho.agreeableness.straightforwardness, help="Чесність, відвертість, нездатність до маніпуляцій.")
                psycho.agreeableness.altruism = st.slider("Altruism (Альтруїзм)", 0.0, 1.0, psycho.agreeableness.altruism, help="Активне бажання допомагати іншим.")
            with c2:
                psycho.agreeableness.compliance = st.slider("Cooperation (Поступливість)", 0.0, 1.0, psycho.agreeableness.compliance, help="Уникнення конфліктів, готовність йти на компроміс.")
                psycho.agreeableness.modesty = st.slider("Modesty (Скромність)", 0.0, 1.0, psycho.agreeableness.modesty, help="Небажання вихвалятися, применшення власних заслуг.")
                psycho.agreeableness.tender_mindedness = st.slider("Sympathy (Чуйність)", 0.0, 1.0, psycho.agreeableness.tender_mindedness, help="Емпатія, співчуття до чужого болю.")

        # 5. Conscientiousness Domain
        with t_c:
            st.markdown("#### 🟣 Conscientiousness (Виконавча функція)")
            c1, c2 = st.columns(2)
            with c1:
                psycho.conscientiousness.competence = st.slider("Self-Efficacy (Компетентність)", 0.0, 1.0, psycho.conscientiousness.competence, help="Віра в свою здатність справлятися з життєвими завданнями.")
                psycho.conscientiousness.order = st.slider("Orderliness (Порядок)", 0.0, 1.0, psycho.conscientiousness.order, help="Любов до чистоти, структури та організації простору.")
                psycho.conscientiousness.dutifulness = st.slider("Dutifulness (Обов'язок)", 0.0, 1.0, psycho.conscientiousness.dutifulness, help="Надійність, дотримання обіцянок та моральних принципів.")
            with c2:
                psycho.conscientiousness.achievement = st.slider("Achievement Striving (Досягнення)", 0.0, 1.0, psycho.conscientiousness.achievement, help="Амбіційність, орієнтація на успіх та кар'єру.")
                psycho.conscientiousness.self_discipline = st.slider("Self-Discipline (Самодисципліна)", 0.0, 1.0, psycho.conscientiousness.self_discipline, help="Здатність змусити себе працювати та доводити справи до кінця.")
                psycho.conscientiousness.deliberation = st.slider("Cautiousness (Обережність)", 0.0, 1.0, psycho.conscientiousness.deliberation, help="Схильність думати перед тим, як діяти.")

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