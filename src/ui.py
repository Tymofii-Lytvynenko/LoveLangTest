from __future__ import annotations

import streamlit as st

from src.data import (
    EROS_EXPLANATIONS,
    EROS_TAGS_EXPLANATIONS,
    EXPLANATIONS,
    PROFESSIONAL_EXPLANATIONS,
    SHADOW_EXPLANATIONS,
)
from src.domain.eros import ErosComponent
from src.domain.needs import RelationalNeedsComponent
from src.domain.professional import ProfessionalComponent
from src.domain.psychometrics import PsychometricsComponent
from src.domain.shadow import ShadowComponent
from src.enums import (
    AttachmentStyle,
    ConflictResponse,
    ContextDependency,
    HollandCode,
    RegulationMethod,
)
from src.question_bank import QuestionBank, question_state_key
from src.services.bigfive_pdf_parser import BigFivePdfParseError, BigFivePdfParser, FACET_SPECS
from src.services.form_state import collect_bank_responses
from src.services.scoring import QuestionnaireScorer


def _ensure_enum(enum_token: str | None, enum_class):
    if not enum_token:
        return None
    return enum_class[enum_token]


def _enum_display(enum_class, enum_token: str) -> str:
    return enum_class[enum_token].value


def render_info_box(title: str, text: str) -> None:
    with st.expander(f"Довідка: {title}"):
        st.markdown(text)


def _facet_slider(label: str, obj, attr_name: str, help_text: str, key_prefix: str) -> None:
    current_val_norm = getattr(obj, attr_name)
    default_val_scaled = int(current_val_norm * 20.0)
    unique_key = f"facet_{key_prefix}_{attr_name}"
    new_val_scaled = st.slider(label, 0, 20, default_val_scaled, help=help_text, key=unique_key)
    setattr(obj, attr_name, new_val_scaled / 20.0)


def _apply_bigfive_pdf_scores_to_state(pdf_bytes: bytes) -> int:
    parsed = BigFivePdfParser.parse_pdf_bytes(pdf_bytes)
    for key, value in parsed.raw_scores.items():
        st.session_state[key] = value
    for key, value in parsed.high_level_scores.items():
        st.session_state[key] = value
    return len(parsed.raw_scores)


def _count_imported_bigfive_facets() -> int:
    return sum(1 for spec in FACET_SPECS if spec.session_key in st.session_state)


def _render_bank_questions(bank: QuestionBank) -> tuple[dict[str, str], list[str]]:
    for question in bank.questions:
        st.markdown(f"**{question.question}**")
        if question.description:
            st.caption(question.description)

        option_lookup = {option.id: option for option in question.options}
        st.radio(
            "Ваша відповідь:",
            list(option_lookup.keys()),
            index=None,
            format_func=lambda option_id, options=option_lookup: options[option_id].text,
            key=question_state_key(bank.module, question.id),
            label_visibility="collapsed",
        )
        st.divider()

    response_state = collect_bank_responses(bank, st.session_state)
    return response_state.responses, list(response_state.missing_questions)


def render_big_five_manual() -> PsychometricsComponent:
    st.header("1. Substrate Layer (Психометрія)")
    st.markdown(EXPLANATIONS["big_five_intro"])

    input_mode = st.radio(
        "Джерело Big Five:",
        options=["pdf", "manual"],
        index=0,
        format_func=lambda mode: "PDF імпорт 30 facets" if mode == "pdf" else "Ручне введення",
        key="psycho_input_mode",
        horizontal=True,
    )
    if input_mode == "pdf":
        uploaded_file = st.file_uploader(
            "PDF результатів BigFive",
            type="pdf",
            key="bigfive_pdf_upload",
            help="Завантажте PDF з bigfive-test.com. Фасети 0-20 будуть підтягнуті автоматично.",
        )
        if uploaded_file is not None:
            try:
                imported_count = _apply_bigfive_pdf_scores_to_state(uploaded_file.getvalue())
                st.success(f"Імпортовано {imported_count} з 30 Big Five facets.")
            except BigFivePdfParseError as exc:
                st.error(f"Не вдалося розібрати Big Five PDF: {exc}")
        else:
            imported_count = _count_imported_bigfive_facets()
            if imported_count:
                st.info(f"У стані вже є {imported_count} імпортованих facets.")
            else:
                st.info("Завантажте PDF, щоб не вводити 30 facets вручну.")

    col1, col2 = st.columns(2)
    with col1:
        render_info_box("Openness", EXPLANATIONS["openness"])
        openness = st.number_input(
            "Openness (загальний, 0-100)",
            0,
            100,
            50,
            help="Відкритість до досвіду",
            key="psycho_o",
        )

        render_info_box("Conscientiousness", EXPLANATIONS["conscientiousness"])
        conscientiousness = st.number_input(
            "Conscientiousness (загальний, 0-100)",
            0,
            100,
            50,
            help="Сумлінність",
            key="psycho_c",
        )

        render_info_box("Extraversion", EXPLANATIONS["extraversion"])
        extraversion = st.number_input(
            "Extraversion (загальний, 0-100)",
            0,
            100,
            50,
            help="Екстраверсія",
            key="psycho_e",
        )

    with col2:
        render_info_box("Agreeableness", EXPLANATIONS["agreeableness"])
        agreeableness = st.number_input(
            "Agreeableness (загальний, 0-100)",
            0,
            100,
            50,
            help="Доброзичливість",
            key="psycho_a",
        )

        render_info_box("Neuroticism", EXPLANATIONS["neuroticism"])
        neuroticism = st.number_input(
            "Neuroticism (загальний, 0-100)",
            0,
            100,
            50,
            help="Невротизм",
            key="psycho_n",
        )

        st.markdown("---")
        st.caption("Нейродивергентність модифікує алгоритми Safety та Resource.")
        has_adhd = st.checkbox("РДУГ (ADHD)", key="psycho_adhd")
        has_asd = st.checkbox("РАС (Autism Spectrum)", key="psycho_asd")
        st.info(
            "Ці прапорці опціональні. Вони не ставлять діагноз, а лише допомагають точніше "
            "інтерпретувати сенсорне навантаження, потребу в структурі та побутову підтримку."
        )

    psycho = PsychometricsComponent.from_high_level_scores(
        openness,
        conscientiousness,
        extraversion,
        agreeableness,
        neuroticism,
        has_adhd,
        has_asd,
    )

    with st.expander("Advanced: 30 фасетів (шкала 0-20)", expanded=input_mode == "pdf"):
        st.info(
            "Якщо у вас є деталізовані результати IPIP-NEO або схожого інструменту, "
            "ви можете скоригувати фасети вручну."
        )

        tab_n, tab_e, tab_o, tab_a, tab_c = st.tabs(
            ["Neuroticism", "Extraversion", "Openness", "Agreeableness", "Conscientiousness"]
        )

        with tab_n:
            col_a, col_b = st.columns(2)
            with col_a:
                _facet_slider("Anxiety", psycho.neuroticism, "anxiety", "Тривожність", "neur")
                _facet_slider("Anger", psycho.neuroticism, "hostility", "Ворожість", "neur")
                _facet_slider("Depression", psycho.neuroticism, "depression", "Депресивність", "neur")
            with col_b:
                _facet_slider(
                    "Self-Consciousness",
                    psycho.neuroticism,
                    "self_consciousness",
                    "Сором'язливість",
                    "neur",
                )
                _facet_slider("Immoderation", psycho.neuroticism, "impulsiveness", "Імпульсивність", "neur")
                _facet_slider("Vulnerability", psycho.neuroticism, "vulnerability", "Вразливість", "neur")

        with tab_e:
            col_a, col_b = st.columns(2)
            with col_a:
                _facet_slider("Friendliness", psycho.extraversion, "warmth", "Теплота", "extr")
                _facet_slider("Gregariousness", psycho.extraversion, "gregariousness", "Стадність", "extr")
                _facet_slider("Assertiveness", psycho.extraversion, "assertiveness", "Асертивність", "extr")
            with col_b:
                _facet_slider("Activity Level", psycho.extraversion, "activity", "Активність", "extr")
                _facet_slider(
                    "Excitement Seeking",
                    psycho.extraversion,
                    "excitement_seeking",
                    "Пошук вражень",
                    "extr",
                )
                _facet_slider(
                    "Cheerfulness",
                    psycho.extraversion,
                    "positive_emotions",
                    "Позитивні емоції",
                    "extr",
                )

        with tab_o:
            col_a, col_b = st.columns(2)
            with col_a:
                _facet_slider("Imagination", psycho.openness, "fantasy", "Уява", "open")
                _facet_slider("Artistic Interests", psycho.openness, "aesthetics", "Естетика", "open")
                _facet_slider("Emotionality", psycho.openness, "feelings", "Емоційність", "open")
            with col_b:
                _facet_slider("Adventurousness", psycho.openness, "actions", "Дії", "open")
                _facet_slider("Intellect", psycho.openness, "ideas", "Ідеї", "open")
                _facet_slider("Liberalism", psycho.openness, "values", "Цінності", "open")

        with tab_a:
            col_a, col_b = st.columns(2)
            with col_a:
                _facet_slider("Trust", psycho.agreeableness, "trust", "Довіра", "agre")
                _facet_slider(
                    "Morality",
                    psycho.agreeableness,
                    "straightforwardness",
                    "Чесність",
                    "agre",
                )
                _facet_slider("Altruism", psycho.agreeableness, "altruism", "Альтруїзм", "agre")
            with col_b:
                _facet_slider("Cooperation", psycho.agreeableness, "compliance", "Поступливість", "agre")
                _facet_slider("Modesty", psycho.agreeableness, "modesty", "Скромність", "agre")
                _facet_slider(
                    "Sympathy",
                    psycho.agreeableness,
                    "tender_mindedness",
                    "Чуйність",
                    "agre",
                )

        with tab_c:
            col_a, col_b = st.columns(2)
            with col_a:
                _facet_slider(
                    "Self-Efficacy",
                    psycho.conscientiousness,
                    "competence",
                    "Компетентність",
                    "cons",
                )
                _facet_slider("Orderliness", psycho.conscientiousness, "order", "Порядок", "cons")
                _facet_slider(
                    "Dutifulness",
                    psycho.conscientiousness,
                    "dutifulness",
                    "Обов'язок",
                    "cons",
                )
            with col_b:
                _facet_slider("Achievement", psycho.conscientiousness, "achievement", "Досягнення", "cons")
                _facet_slider(
                    "Self-Discipline",
                    psycho.conscientiousness,
                    "self_discipline",
                    "Самодисципліна",
                    "cons",
                )
                _facet_slider(
                    "Cautiousness",
                    psycho.conscientiousness,
                    "deliberation",
                    "Обережність",
                    "cons",
                )

    return psycho


def render_shadow_form(bank: QuestionBank) -> tuple[ShadowComponent | None, list[str]]:
    st.header("2. Shadow Component (Захист)")
    st.markdown(SHADOW_EXPLANATIONS["intro"])

    input_mode = st.radio(
        "Режим введення:",
        options=["quiz", "manual"],
        format_func=lambda mode: "Пройти тест" if mode == "quiz" else "Ручне налаштування",
        key="shadow_input_mode",
        horizontal=True,
    )

    if input_mode == "quiz":
        responses, missing_questions = _render_bank_questions(bank)
        if missing_questions:
            return None, missing_questions
        return QuestionnaireScorer.build_shadow_component(bank, responses), []

    attachment_style = st.selectbox(
        "Стиль прив'язаності:",
        options=[style.name for style in AttachmentStyle],
        index=None,
        format_func=lambda token: _enum_display(AttachmentStyle, token),
        key="shadow_manual_att",
        placeholder="-- оберіть стиль --",
    )
    conflict_response = st.selectbox(
        "Реакція на конфлікт:",
        options=[response.name for response in ConflictResponse],
        index=None,
        format_func=lambda token: _enum_display(ConflictResponse, token),
        key="shadow_manual_conf",
        placeholder="-- оберіть реакцію --",
    )
    regulation_method = st.selectbox(
        "Метод регуляції:",
        options=[method.name for method in RegulationMethod],
        index=None,
        format_func=lambda token: _enum_display(RegulationMethod, token),
        key="shadow_manual_reg",
        placeholder="-- оберіть метод --",
    )

    missing = []
    if attachment_style is None:
        missing.append("Стиль прив'язаності")
    if conflict_response is None:
        missing.append("Реакція на конфлікт")
    if regulation_method is None:
        missing.append("Метод регуляції")
    if missing:
        return None, missing

    component = ShadowComponent(
        attachment_style=_ensure_enum(attachment_style, AttachmentStyle),
        conflict_response=_ensure_enum(conflict_response, ConflictResponse),
        regulation_method=_ensure_enum(regulation_method, RegulationMethod),
    )
    return component, []


def render_eros_form(bank: QuestionBank) -> tuple[ErosComponent | None, list[str]]:
    st.header("3. Eros Component (Сексуальність)")
    st.markdown(EROS_EXPLANATIONS["intro"])

    input_mode = st.radio(
        "Режим введення:",
        options=["quiz", "manual"],
        format_func=lambda mode: "Пройти тест" if mode == "quiz" else "Ручне налаштування",
        key="eros_input_mode",
        horizontal=True,
    )

    erotic_tags = st.multiselect(
        "Оберіть додаткові тригери/контексти:",
        list(EROS_TAGS_EXPLANATIONS.keys()),
        key="eros_tags",
    )

    if input_mode == "quiz":
        responses, missing_questions = _render_bank_questions(bank)
        if missing_questions:
            return None, missing_questions
        component = QuestionnaireScorer.build_eros_component(bank, responses, erotic_tags=erotic_tags)
        st.metric("Accelerator", f"{component.accelerator * 100:.0f}%")
        st.metric("Brake", f"{component.brake * 100:.0f}%")
        return component, []

    accelerator = st.slider("Accelerator", 0.0, 1.0, 0.5, 0.01, key="eros_manual_acc")
    brake = st.slider("Brake", 0.0, 1.0, 0.5, 0.01, key="eros_manual_brk")
    context_dependency = st.selectbox(
        "Контекст:",
        options=[item.name for item in ContextDependency],
        index=None,
        format_func=lambda token: _enum_display(ContextDependency, token),
        key="eros_manual_ctx",
        placeholder="-- оберіть контекст --",
    )

    if context_dependency is None:
        return None, ["Контекст Eros"]

    component = ErosComponent(
        accelerator=accelerator,
        brake=brake,
        context_dependency=_ensure_enum(context_dependency, ContextDependency),
        erotic_tags=erotic_tags,
    )
    return component, []


def render_scenarios_engine(bank: QuestionBank) -> tuple[RelationalNeedsComponent | None, list[str]]:
    st.header("4. Context Layer (Сценарний аналіз)")
    responses, missing_questions = _render_bank_questions(bank)
    if missing_questions:
        return None, missing_questions
    return QuestionnaireScorer.build_needs_component(bank, responses), []


def render_professional_compass() -> ProfessionalComponent:
    st.header("5. Professional Layer (Компас Діяльності)")
    st.markdown(PROFESSIONAL_EXPLANATIONS["intro"])

    all_codes = [code.name for code in HollandCode]
    col1, col2, col3 = st.columns(3)
    with col1:
        primary_type = st.selectbox(
            "Основний фокус:",
            all_codes,
            index=0,
            format_func=lambda token: _enum_display(HollandCode, token),
            key="prof_primary",
        )
    with col2:
        secondary_type = st.selectbox(
            "Додатковий фокус:",
            all_codes,
            index=1,
            format_func=lambda token: _enum_display(HollandCode, token),
            key="prof_secondary",
        )
    with col3:
        tertiary_type = st.selectbox(
            "Ситуативний фокус:",
            all_codes,
            index=2,
            format_func=lambda token: _enum_display(HollandCode, token),
            key="prof_tertiary",
        )

    career_centrality = st.slider(
        "Наскільки кар'єра важлива? (Work-Life Balance)",
        0.0,
        1.0,
        0.5,
        0.01,
        key="prof_centrality",
    )

    return ProfessionalComponent(
        primary_type=_ensure_enum(primary_type, HollandCode),
        secondary_type=_ensure_enum(secondary_type, HollandCode),
        tertiary_type=_ensure_enum(tertiary_type, HollandCode),
        career_centrality=career_centrality,
    )
