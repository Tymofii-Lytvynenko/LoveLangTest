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
from src.services.bigfive_pdf_parser import FACET_SPECS, BigFivePdfParseError
from src.services.bigfive_state import (
    apply_bigfive_pdf_scores,
    clear_bigfive_state,
    get_bigfive_import_status,
    get_bigfive_upload_revision,
)
from src.services.form_state import collect_bank_responses
from src.services.scoring import QuestionnaireScorer


def _ensure_enum(enum_token: str | None, enum_class):
    if not enum_token:
        return None
    return enum_class[enum_token]


def _enum_display(enum_class, enum_token: str) -> str:
    return enum_class[enum_token].value


def _state_number(key: str, default: float) -> float:
    value = st.session_state.get(key, default)
    return float(value) if isinstance(value, (int, float)) else default


def render_info_box(title: str, text: str) -> None:
    with st.expander(f"Довідка: {title}"):
        st.markdown(text)


def _facet_slider(label: str, obj, attr_name: str, help_text: str, key_prefix: str) -> None:
    current_val_norm = getattr(obj, attr_name)
    default_val_scaled = int(current_val_norm * 20.0)
    unique_key = f"facet_{key_prefix}_{attr_name}"
    new_val_scaled = st.slider(label, 0, 20, default_val_scaled, help=help_text, key=unique_key)
    setattr(obj, attr_name, new_val_scaled / 20.0)


def _psychometrics_from_state(has_adhd: bool, has_asd: bool) -> PsychometricsComponent:
    psycho = PsychometricsComponent.from_high_level_scores(
        _state_number("psycho_o", 50.0),
        _state_number("psycho_c", 50.0),
        _state_number("psycho_e", 50.0),
        _state_number("psycho_a", 50.0),
        _state_number("psycho_n", 50.0),
        has_adhd,
        has_asd,
    )
    for spec in FACET_SPECS:
        value = st.session_state.get(spec.session_key)
        if isinstance(value, (int, float)):
            domain = getattr(psycho, spec.domain)
            setattr(domain, spec.attr_name, min(max(float(value) / 20.0, 0.0), 1.0))
    return psycho


def _render_bigfive_pdf_import() -> None:
    import_status = get_bigfive_import_status(st.session_state)
    upload_revision = get_bigfive_upload_revision(st.session_state)
    st.markdown("#### Рекомендовано: імпорт Big Five PDF")
    st.caption("Це найточніший шлях для 30 facets: PDF заповнює і загальні OCEAN-бали, і деталізовані шкали.")
    uploaded_file = st.file_uploader(
        "PDF результатів BigFive",
        type="pdf",
        key=f"bigfive_pdf_upload_{upload_revision}",
        help="Підтримується PDF з bigfive-test.com українською мовою. Значення фасетів мають бути у шкалі 0-20.",
    )
    import_col, clear_col = st.columns((2, 1))
    import_requested = import_col.button(
        "Імпортувати PDF",
        use_container_width=True,
        disabled=uploaded_file is None,
    )
    clear_requested = clear_col.button(
        "Скинути PDF-імпорт",
        use_container_width=True,
        disabled=not import_status.has_pdf_import,
    )

    if import_requested and uploaded_file is not None:
        try:
            imported_count = apply_bigfive_pdf_scores(
                st.session_state,
                uploaded_file.getvalue(),
                file_name=uploaded_file.name,
            )
        except BigFivePdfParseError as exc:
            st.error(f"Не вдалося розібрати Big Five PDF: {exc}")
        else:
            st.success(f"Імпортовано {imported_count} з 30 Big Five facets із `{uploaded_file.name}`.")
            st.rerun()

    if clear_requested:
        clear_bigfive_state(st.session_state)
        st.rerun()

    if import_status.has_pdf_import:
        file_suffix = f" із `{import_status.import_filename}`" if import_status.import_filename else ""
        st.info(f"Активний PDF-імпорт: {import_status.facet_count} з 30 facets{file_suffix}.")
    elif uploaded_file is not None:
        st.info(f"Файл `{uploaded_file.name}` готовий до імпорту.")
    else:
        st.info("Завантажте PDF, щоб не вводити 30 facets вручну.")


def _render_neurodivergence_flags() -> tuple[bool, bool]:
    st.markdown("#### Опційний контекст")
    st.caption("Прапорці нижче не є діагнозом. Вони лише коригують інтерпретацію сенсорики, структури та підтримки.")
    col_adhd, col_asd = st.columns(2)
    with col_adhd:
        has_adhd = st.checkbox("РДУГ / ADHD", key="psycho_adhd")
    with col_asd:
        has_asd = st.checkbox("Аутизм / ASD", key="psycho_asd")
    return has_adhd, has_asd


def _render_high_level_bigfive_inputs() -> None:
    st.markdown("##### Загальні OCEAN-бали")
    col1, col2 = st.columns(2)
    with col1:
        render_info_box("Openness", EXPLANATIONS["openness"])
        st.number_input(
            "Openness (0-100)",
            0,
            100,
            int(_state_number("psycho_o", 50)),
            help="Відкритість до досвіду. Якщо PDF імпортовано, це середнє з відповідних фасетів.",
            key="psycho_o",
        )

        render_info_box("Conscientiousness", EXPLANATIONS["conscientiousness"])
        st.number_input(
            "Conscientiousness (0-100)",
            0,
            100,
            int(_state_number("psycho_c", 50)),
            help="Сумлінність, структура і саморегуляція.",
            key="psycho_c",
        )

        render_info_box("Extraversion", EXPLANATIONS["extraversion"])
        st.number_input(
            "Extraversion (0-100)",
            0,
            100,
            int(_state_number("psycho_e", 50)),
            help="Соціальна енергія, темп і позитивна активація.",
            key="psycho_e",
        )

    with col2:
        render_info_box("Agreeableness", EXPLANATIONS["agreeableness"])
        st.number_input(
            "Agreeableness (0-100)",
            0,
            100,
            int(_state_number("psycho_a", 50)),
            help="Довіра, кооперативність і м'якість у взаємодії.",
            key="psycho_a",
        )

        render_info_box("Neuroticism", EXPLANATIONS["neuroticism"])
        st.number_input(
            "Neuroticism (0-100)",
            0,
            100,
            int(_state_number("psycho_n", 50)),
            help="Чутливість до стресу, напруги й невизначеності.",
            key="psycho_n",
        )


def _render_facet_editor(psycho: PsychometricsComponent) -> None:
    st.caption("Фасети потрібні лише якщо ви хочете вручну перевірити або скоригувати PDF-імпорт.")
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
            _facet_slider("Self-Consciousness", psycho.neuroticism, "self_consciousness", "Сором'язливість", "neur")
            _facet_slider("Immoderation", psycho.neuroticism, "impulsiveness", "Імпульсивність", "neur")
            _facet_slider("Vulnerability", psycho.neuroticism, "vulnerability", "Вразливість", "neur")

    with tab_e:
        col_a, col_b = st.columns(2)
        with col_a:
            _facet_slider("Friendliness", psycho.extraversion, "warmth", "Теплота", "extr")
            _facet_slider("Gregariousness", psycho.extraversion, "gregariousness", "Компанійськість", "extr")
            _facet_slider("Assertiveness", psycho.extraversion, "assertiveness", "Асертивність", "extr")
        with col_b:
            _facet_slider("Activity Level", psycho.extraversion, "activity", "Активність", "extr")
            _facet_slider("Excitement Seeking", psycho.extraversion, "excitement_seeking", "Пошук вражень", "extr")
            _facet_slider("Cheerfulness", psycho.extraversion, "positive_emotions", "Позитивні емоції", "extr")

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
            _facet_slider("Morality", psycho.agreeableness, "straightforwardness", "Чесність", "agre")
            _facet_slider("Altruism", psycho.agreeableness, "altruism", "Альтруїзм", "agre")
        with col_b:
            _facet_slider("Cooperation", psycho.agreeableness, "compliance", "Поступливість", "agre")
            _facet_slider("Modesty", psycho.agreeableness, "modesty", "Скромність", "agre")
            _facet_slider("Sympathy", psycho.agreeableness, "tender_mindedness", "Чуйність", "agre")

    with tab_c:
        col_a, col_b = st.columns(2)
        with col_a:
            _facet_slider("Self-Efficacy", psycho.conscientiousness, "competence", "Компетентність", "cons")
            _facet_slider("Orderliness", psycho.conscientiousness, "order", "Порядок", "cons")
            _facet_slider("Dutifulness", psycho.conscientiousness, "dutifulness", "Обов'язок", "cons")
        with col_b:
            _facet_slider("Achievement", psycho.conscientiousness, "achievement", "Досягнення", "cons")
            _facet_slider("Self-Discipline", psycho.conscientiousness, "self_discipline", "Самодисципліна", "cons")
            _facet_slider("Cautiousness", psycho.conscientiousness, "deliberation", "Обережність", "cons")


def _render_bank_questions(bank: QuestionBank):
    for question in bank.questions:
        st.markdown(f"**{question.question}**")
        if question.description:
            st.caption(question.description)

        option_lookup = {option.id: option for option in question.options}
        if question.is_best_worst:
            st.radio(
                "Найважливіше для вас:",
                list(option_lookup.keys()),
                index=None,
                format_func=lambda option_id, options=option_lookup: options[option_id].text,
                key=question_state_key(bank.module, question.id, "best"),
            )
            st.radio(
                "Найменш критичне для вас:",
                list(option_lookup.keys()),
                index=None,
                format_func=lambda option_id, options=option_lookup: options[option_id].text,
                key=question_state_key(bank.module, question.id, "worst"),
            )
        else:
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
    st.header("1. Big Five і нейродивергентний контекст")
    st.markdown(EXPLANATIONS["big_five_intro"])

    import_status = get_bigfive_import_status(st.session_state)
    input_mode = st.radio(
        "Як заповнити Big Five",
        options=["pdf", "manual"],
        index=0,
        format_func=lambda mode: "Рекомендовано: PDF імпорт" if mode == "pdf" else "Опційно: ручне внесення",
        key="psycho_input_mode",
        horizontal=True,
    )

    if input_mode == "pdf":
        _render_bigfive_pdf_import()
    else:
        st.info("Ручне внесення корисне, якщо PDF недоступний або потрібно швидко наблизити профіль.")

    has_adhd, has_asd = _render_neurodivergence_flags()
    psycho = _psychometrics_from_state(has_adhd, has_asd)
    show_manual = input_mode == "manual" or import_status.has_pdf_import

    if show_manual:
        with st.expander("Опційне ручне уточнення Big Five", expanded=input_mode == "manual"):
            _render_high_level_bigfive_inputs()
            psycho = _psychometrics_from_state(has_adhd, has_asd)
            st.divider()
            _render_facet_editor(psycho)
    else:
        st.caption("Ручні OCEAN-поля та 30 facets приховані, доки ви не оберете ручний режим або не імпортуєте PDF.")

    return psycho


def render_shadow_form(bank: QuestionBank) -> tuple[ShadowComponent | None, list[str]]:
    st.header("2. Захисні реакції та прив'язаність")
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
    st.header("3. Eros і тілесний контекст")
    st.markdown(EROS_EXPLANATIONS["intro"])

    input_mode = st.radio(
        "Режим введення:",
        options=["quiz", "manual"],
        format_func=lambda mode: "Пройти тест" if mode == "quiz" else "Ручне налаштування",
        key="eros_input_mode",
        horizontal=True,
    )

    erotic_tags = st.multiselect(
        "Додаткові тригери/контексти:",
        list(EROS_TAGS_EXPLANATIONS.keys()),
        key="eros_tags",
        help="Опційний словник контекстів, які можуть пояснювати потяг або комфорт.",
    )

    if input_mode == "quiz":
        responses, missing_questions = _render_bank_questions(bank)
        if missing_questions:
            return None, missing_questions
        component = QuestionnaireScorer.build_eros_component(bank, responses, erotic_tags=erotic_tags)
        col_a, col_b = st.columns(2)
        col_a.metric("Accelerator", f"{component.accelerator * 100:.0f}%")
        col_b.metric("Brake", f"{component.brake * 100:.0f}%")
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
    st.header("4. Життєві сценарії партнерства")
    st.caption("Цей блок вимірює не абстрактні риси, а типові ситуації: побут, підтримку, конфлікти, темп і близькість.")
    responses, missing_questions = _render_bank_questions(bank)
    if missing_questions:
        return None, missing_questions
    return QuestionnaireScorer.build_needs_component(bank, responses), []


def render_professional_compass() -> ProfessionalComponent:
    st.header("5. Робота, ритм і життєвий стиль")
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
        "Наскільки кар'єра впливає на ваш побут і рішення?",
        0.0,
        1.0,
        0.5,
        0.01,
        key="prof_centrality",
        help="0 означає, що робота майже не визначає стиль життя; 1 означає, що кар'єра сильно структурує час, ресурси й пріоритети.",
    )

    return ProfessionalComponent(
        primary_type=_ensure_enum(primary_type, HollandCode),
        secondary_type=_ensure_enum(secondary_type, HollandCode),
        tertiary_type=_ensure_enum(tertiary_type, HollandCode),
        career_centrality=career_centrality,
    )


def render_provision_form(bank: QuestionBank) -> tuple[dict[str, Any] | None, list[str]]:
    st.header("6. Ваша місткість (Provision / Capacity)")
    st.caption("Цей блок вимірює те, що ви реально та стабільно можете віддавати або забезпечувати для партнера.")
    responses, missing_questions = _render_bank_questions(bank)
    return responses, missing_questions


def render_calibration_form(bank: QuestionBank) -> tuple[dict[str, Any] | None, list[str]]:
    st.header("7. Консистенція та Калібрування (Calibration)")
    st.caption("Цей блок допомагає виявити розбіжності та вплив стресу чи контексту на ваші відповіді.")
    responses, missing_questions = _render_bank_questions(bank)
    return responses, missing_questions
