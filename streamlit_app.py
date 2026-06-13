from __future__ import annotations

import html
import json
import math

import streamlit as st

from src.profile import UserProfile
from src.question_bank import get_question_bank_registry
from src.services.adjustment import NeedsAdjustmentService
from src.services.compatibility import CompatibilityComparator
from src.services.profile_codec import ProfileCodec, ProfileCodecError
from src.services.profile_builder import QUESTIONNAIRE_MODE_KEY, build_user_profile_from_state, normalize_questionnaire_mode
from src.services.reporting import ReportGenerator
from src.services.sanitizer import StateSanitizer
from src.ui import (
    render_big_five_manual,
    render_eros_form,
    render_professional_compass,
    render_scenarios_engine,
    render_shadow_form,
)

CURRENT_VERSION = "4.0"

NEED_COLORS = {
    "Safety": "#2f80ed",
    "Resource": "#00a676",
    "Resonance": "#d65a31",
    "Expansion": "#8a5cf6",
}


def _pct(value: float) -> int:
    return round(max(0.0, min(1.0, float(value))) * 100)


def _short_need_label(label: str) -> str:
    if "Safety" in label:
        return "Safety"
    if "Resource" in label:
        return "Resource"
    if "Resonance" in label:
        return "Resonance"
    if "Expansion" in label:
        return "Expansion"
    return label


def render_app_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --crnas-ink: #17212b;
            --crnas-muted: #5f6f7b;
            --crnas-line: #dfe7ec;
            --crnas-panel: #f7faf8;
            --crnas-panel-strong: #edf5f2;
            --crnas-accent: #007c72;
            --crnas-warm: #d65a31;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 4rem;
            max-width: 1180px;
        }
        .crnas-hero {
            border: 1px solid var(--crnas-line);
            background:
                linear-gradient(135deg, rgba(237, 245, 242, 0.95), rgba(255, 248, 240, 0.92)),
                repeating-linear-gradient(135deg, rgba(0, 124, 114, .05) 0 1px, transparent 1px 16px);
            border-radius: 8px;
            padding: 1.1rem 1.2rem;
            margin-bottom: 1rem;
        }
        .crnas-hero h1 {
            margin: 0 0 .35rem 0;
            color: var(--crnas-ink);
            font-size: 2rem;
            line-height: 1.12;
            letter-spacing: 0;
        }
        .crnas-hero p {
            margin: 0;
            color: var(--crnas-muted);
            max-width: 820px;
            font-size: 1rem;
        }
        .crnas-meta {
            display: flex;
            flex-wrap: wrap;
            gap: .45rem;
            margin-top: .8rem;
        }
        .crnas-pill {
            border: 1px solid var(--crnas-line);
            border-radius: 999px;
            background: rgba(255, 255, 255, .75);
            color: var(--crnas-muted);
            padding: .22rem .62rem;
            font-size: .82rem;
        }
        .crnas-card-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: .8rem;
            margin: .4rem 0 1rem 0;
        }
        .crnas-card {
            border: 1px solid var(--crnas-line);
            border-radius: 8px;
            background: #ffffff;
            padding: .95rem;
        }
        .crnas-card strong {
            display: block;
            color: var(--crnas-ink);
            font-size: 1.05rem;
            margin-bottom: .2rem;
        }
        .crnas-card span {
            color: var(--crnas-muted);
            font-size: .9rem;
        }
        .crnas-kpi {
            font-size: 1.9rem;
            line-height: 1.1;
            color: var(--crnas-accent);
            font-weight: 700;
            margin-top: .35rem;
        }
        .crnas-bars {
            border: 1px solid var(--crnas-line);
            border-radius: 8px;
            padding: 1rem;
            background: #ffffff;
        }
        .crnas-bar-row {
            display: grid;
            grid-template-columns: minmax(120px, 180px) 1fr 56px;
            align-items: center;
            gap: .75rem;
            margin: .62rem 0;
        }
        .crnas-bar-label {
            color: var(--crnas-ink);
            font-weight: 650;
        }
        .crnas-bar-track {
            height: .7rem;
            border-radius: 999px;
            background: #edf1f3;
            overflow: hidden;
        }
        .crnas-bar-fill {
            height: 100%;
            border-radius: 999px;
        }
        .crnas-bar-value {
            color: var(--crnas-muted);
            font-variant-numeric: tabular-nums;
            text-align: right;
        }
        .crnas-note {
            border-left: 4px solid var(--crnas-accent);
            background: var(--crnas-panel);
            border-radius: 6px;
            padding: .8rem .95rem;
            color: var(--crnas-ink);
            margin: .65rem 0;
        }
        .crnas-compare-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: .8rem;
        }
        @media (max-width: 760px) {
            .crnas-card-grid,
            .crnas-compare-grid {
                grid-template-columns: 1fr;
            }
            .crnas-bar-row {
                grid-template-columns: 1fr 52px;
                gap: .35rem .6rem;
            }
            .crnas-bar-track {
                grid-column: 1 / -1;
                grid-row: 2;
            }
            .crnas-hero h1 {
                font-size: 1.55rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(bank_fingerprint: str) -> None:
    st.markdown(
        f"""
        <section class="crnas-hero">
          <h1>CRNAS: матриця партнерської сумісності</h1>
          <p>
            Інструмент насамперед призначений для порівняння двох профілів: він шукає збіги,
            потенційні тертя і теми для чесної розмови. Одиночний результат описує позицію
            в межах поточного банку питань, а не середній percentile між людьми.
          </p>
          <div class="crnas-meta">
            <span class="crnas-pill">v{html.escape(CURRENT_VERSION)}</span>
            <span class="crnas-pill">Bank {html.escape(bank_fingerprint[:12])}</span>
            <span class="crnas-pill">Основний шлях: PDF Big Five + анкета</span>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _apply_imported_state(clean_state: dict) -> int:
    changes_count = 0
    for key, value in clean_state.items():
        if st.session_state.get(key) != value:
            st.session_state[key] = value
            changes_count += 1
    return changes_count


def _import_payload_state(raw_payload: dict) -> None:
    payload = ProfileCodec.from_json_dict(raw_payload)
    clean_state, removal_log = StateSanitizer.sanitize(
        payload.state,
        incoming_bank_fingerprint=payload.bank_fingerprint,
    )
    changes_count = _apply_imported_state(clean_state)

    if removal_log:
        st.warning(f"Імпорт виконано з очищенням: відкинуто полів {len(removal_log)}.")
        with st.expander("Деталі очищення"):
            for item in removal_log:
                st.write(f"- {item}")

    if changes_count > 0:
        st.success(f"Профіль імпортовано. Оновлено полів: {changes_count}.")
    elif not removal_log:
        st.info("Імпортований профіль уже збігається з поточним станом.")


def render_profile_import_tab() -> None:
    st.caption("Вставте збережений рядок профілю, якщо продовжуєте стару сесію або отримали профіль партнера.")
    encoded_payload = st.text_area(
        "Рядок профілю",
        key="profile_transport_input",
        height=110,
        help="Compact base64url-рядок. Він містить лише стан анкети, без серверного збереження даних.",
    )

    if st.button("Імпортувати рядок", use_container_width=True):
        try:
            payload = ProfileCodec.decode_string(encoded_payload)
            _import_payload_state(ProfileCodec.to_json_dict(payload))
        except ProfileCodecError as exc:
            st.error(f"Не вдалося декодувати рядок профілю: {exc}")

    with st.expander("Dev/debug: JSON payload"):
        uploaded_file = st.file_uploader(
            "Завантажити JSON payload",
            type="json",
            help="Допоміжний формат для локального дебагу. Використовує ту саму схему, що й compact string.",
        )
        if uploaded_file is not None and st.button("Імпортувати JSON payload", use_container_width=True):
            try:
                _import_payload_state(json.load(uploaded_file))
            except (ProfileCodecError, json.JSONDecodeError) as exc:
                st.error(f"Не вдалося завантажити JSON payload: {exc}")


def render_profile_export_tab(bank_fingerprint: str) -> None:
    current_state = StateSanitizer.extract_persistable_state(st.session_state)
    if not current_state:
        st.caption("Після введення даних тут з'явиться рядок профілю для збереження або порівняння.")
        return

    payload = ProfileCodec.build_payload(
        state=current_state,
        bank_fingerprint=bank_fingerprint,
    )
    encoded_payload = ProfileCodec.encode_payload(payload)
    st.text_area(
        "Поточний рядок профілю",
        value=encoded_payload,
        height=120,
        help="Цей рядок можна зберегти у нотатнику або надіслати іншій людині для порівняння.",
    )

    json_payload = json.dumps(
        ProfileCodec.to_json_dict(payload),
        indent=2,
        ensure_ascii=False,
    )
    st.download_button(
        "Dev/debug: завантажити JSON payload",
        data=json_payload,
        file_name="crnas_profile_payload.json",
        mime="application/json",
        use_container_width=True,
    )


def _render_missing_inputs(section_name: str, missing_items: list[str]) -> None:
    if not missing_items:
        return
    st.error(f"{section_name}: заповніть усі обов'язкові поля.")
    with st.expander(f"{section_name}: що саме пропущено"):
        for item in missing_items:
            st.write(f"- {item}")


def _render_report_items(title: str, items, empty_text: str, tone: str) -> None:
    st.write(f"#### {title}")
    if not items:
        st.info(empty_text)
        return

    for item in items:
        if tone == "good":
            st.success(f"**{item.title}**\n\n{item.detail}")
        elif tone == "risk":
            st.warning(f"**{item.title}**\n\n{item.detail}")
        else:
            st.info(f"**{item.title}**\n\n{item.detail}")


def render_partner_comparison_tab(bank_fingerprint: str) -> None:
    partner_string = st.text_area(
        "Рядок профілю партнера",
        key="partner_profile_transport_input",
        height=110,
        help="Вставте compact string іншої людини, щоб підсвітити потенційні збіги та розбіжності.",
    )
    compare = st.button("Порівняти профілі", use_container_width=True)

    if not compare:
        st.caption("Порівняння не зберігається: усе рахується локально з рядка, який ви вставили.")
        return

    registry = get_question_bank_registry()
    try:
        partner_payload = ProfileCodec.decode_string(partner_string)
    except ProfileCodecError as exc:
        st.error(f"Не вдалося декодувати профіль партнера: {exc}")
        return

    current_state = StateSanitizer.extract_persistable_state(st.session_state)
    partner_state, partner_removals = StateSanitizer.sanitize(
        partner_payload.state,
        incoming_bank_fingerprint=partner_payload.bank_fingerprint,
    )

    current_profile = build_user_profile_from_state(current_state, registry, name="Ваш профіль")
    partner_profile = build_user_profile_from_state(partner_state, registry, name="Профіль партнера")

    if not current_profile.is_complete:
        st.error("Порівняння недоступне: ваш поточний профіль ще не повністю заповнений.")
        _render_missing_inputs("Ваш профіль", list(current_profile.missing_inputs[:12]))
        return
    if not partner_profile.is_complete:
        st.error("Порівняння недоступне: профіль партнера неповний або створений для іншої версії анкети.")
        _render_missing_inputs("Профіль партнера", list(partner_profile.missing_inputs[:12]))
        return

    report = CompatibilityComparator.compare(current_profile.user, partner_profile.user)
    st.markdown(
        f"""
        <div class="crnas-card-grid">
          <div class="crnas-card">
            <span>Орієнтовна сумісність</span>
            <div class="crnas-kpi">{_pct(report.score)}%</div>
          </div>
          <div class="crnas-card">
            <span>Режими анкет</span>
            <strong>{html.escape(current_profile.mode)} / {html.escape(partner_profile.mode)}</strong>
            <span>Скринінг розбіжностей, не вирок стосункам.</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if partner_removals:
        st.warning(f"Профіль партнера очищено від несумісних або застарілих полів: {len(partner_removals)}.")

    col_a, col_b = st.columns(2)
    with col_a:
        _render_report_items(
            "Потенційно сильні місця",
            report.strengths,
            "Явних сильних збігів за поточними порогами не знайдено.",
            "good",
        )
    with col_b:
        _render_report_items(
            "Потенційні розбіжності",
            report.tensions,
            "Великих розбіжностей за поточними порогами не знайдено.",
            "risk",
        )
    if report.notes:
        _render_report_items("Примітки", report.notes, "", "note")


def render_profile_workspace(bank_fingerprint: str) -> None:
    with st.expander("Профіль, експорт і порівняння", expanded=False):
        st.caption("Сервісні дії з профілем винесені сюди, щоб не заважати проходженню анкети.")
        import_tab, export_tab, compare_tab = st.tabs(["Імпорт", "Експорт", "Порівняння"])
        with import_tab:
            render_profile_import_tab()
        with export_tab:
            render_profile_export_tab(bank_fingerprint)
        with compare_tab:
            render_partner_comparison_tab(bank_fingerprint)


def render_questionnaire_mode() -> str:
    return st.radio(
        "Режим анкети",
        options=["simple", "extended"],
        index=0 if normalize_questionnaire_mode(st.session_state.get(QUESTIONNAIRE_MODE_KEY)) == "simple" else 1,
        format_func=lambda mode: "Простий: 40 core questions" if mode == "simple" else "Розширений: 72 core questions",
        key=QUESTIONNAIRE_MODE_KEY,
        horizontal=True,
        help="Розширений режим обраний за замовчуванням: він довший, але стабільніше покриває життєві сценарії.",
    )


def _render_bar_rows(scores: dict[str, float]) -> str:
    rows = []
    for label, value in scores.items():
        short_label = _short_need_label(label)
        percent = _pct(value)
        color = NEED_COLORS.get(short_label, "#007c72")
        rows.append(
            f"""
            <div class="crnas-bar-row">
              <div class="crnas-bar-label">{html.escape(short_label)}</div>
              <div class="crnas-bar-track">
                <div class="crnas-bar-fill" style="width: {percent}%; background: {color};"></div>
              </div>
              <div class="crnas-bar-value">{percent}%</div>
            </div>
            """
        )
    return "\n".join(rows)


def _radar_svg(scores: dict[str, float]) -> str:
    values = {
        _short_need_label(label): max(0.0, min(1.0, float(value)))
        for label, value in scores.items()
    }
    order = ["Safety", "Resource", "Resonance", "Expansion"]
    center = 115
    radius = 82
    angles = [-90, 0, 90, 180]
    points = []
    for label, angle in zip(order, angles):
        radians = math.radians(angle)
        value_radius = radius * values.get(label, 0.0)
        x = center + value_radius * math.cos(radians)
        y = center + value_radius * math.sin(radians)
        points.append(f"{x:.1f},{y:.1f}")

    return f"""
    <svg viewBox="0 0 230 230" role="img" aria-label="Need profile radar" style="width: 100%; max-width: 280px;">
      <polygon points="115,33 197,115 115,197 33,115" fill="#f3f7f6" stroke="#d7e2e1" />
      <polygon points="115,61 169,115 115,169 61,115" fill="none" stroke="#d7e2e1" />
      <line x1="115" y1="33" x2="115" y2="197" stroke="#d7e2e1" />
      <line x1="33" y1="115" x2="197" y2="115" stroke="#d7e2e1" />
      <polygon points="{' '.join(points)}" fill="rgba(0, 124, 114, .28)" stroke="#007c72" stroke-width="3" />
      <circle cx="115" cy="115" r="3" fill="#007c72" />
      <text x="115" y="20" text-anchor="middle" font-size="13" fill="#17212b">Safety</text>
      <text x="215" y="119" text-anchor="end" font-size="13" fill="#17212b">Resource</text>
      <text x="115" y="218" text-anchor="middle" font-size="13" fill="#17212b">Resonance</text>
      <text x="16" y="119" text-anchor="start" font-size="13" fill="#17212b">Expansion</text>
    </svg>
    """


def render_result_dashboard(manual: dict) -> None:
    primary_label, primary_value = manual["primary_driver"]
    secondary_label, secondary_value = manual["secondary_driver"]

    st.success("Розрахунок завершено.")
    st.caption(
        "Одиночний профіль є self-description у межах цієї анкети. Найкорисніша інтерпретація з'являється "
        "при порівнянні з профілем іншої людини; відсотки не означають percentile або середнє по популяції."
    )

    st.markdown(
        f"""
        <div class="crnas-card-grid">
          <div class="crnas-card">
            <span>Домінантний драйвер</span>
            <strong>{html.escape(str(primary_label))}</strong>
            <div class="crnas-kpi">{_pct(primary_value)}%</div>
          </div>
          <div class="crnas-card">
            <span>Вторинний драйвер</span>
            <strong>{html.escape(str(secondary_label))}</strong>
            <div class="crnas-kpi" style="color: var(--crnas-warm);">{_pct(secondary_value)}%</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    chart_col, needs_col = st.columns((0.9, 1.25))
    with chart_col:
        st.markdown(_radar_svg(manual["scores"]), unsafe_allow_html=True)
    with needs_col:
        st.markdown(
            f"""
            <div class="crnas-bars">
              <strong>Профіль потреб</strong>
              {_render_bar_rows(manual["scores"])}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("#### Що ви приносите у стосунки")
    st.markdown(
        f"""
        <div class="crnas-bars">
          {_render_bar_rows(manual["provision_scores"])}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="crnas-note"><strong>Суперсила:</strong> {html.escape(str(manual["superpower"][0]))}</div>',
        unsafe_allow_html=True,
    )

    notes_tab, neuro_tab = st.tabs(["Операційні примітки", "Нейродивергентний контекст"])
    with notes_tab:
        st.warning(manual["shadow_warning"])
        st.info(f"**Eros profile:** {manual['erotic_key']}")
        st.info(f"**Professional style:** {manual['professional_key']}")
        st.caption(f"Strategy: {manual['interaction_style']}")
        if manual["resource_warning"]:
            st.error(manual["resource_warning"])
    with neuro_tab:
        st.caption(manual["context_disclaimer"])
        if manual["neurodivergence_context"]:
            st.info(manual["neurodivergence_context"])
            for note in manual["support_notes"]:
                st.write(f"- {note}")
        else:
            st.info("Прапорці РДУГ/РАС не обрані, тому додатковий нейродивергентний контекст не застосовано.")


def main() -> None:
    st.set_page_config(page_title="CRNAS v4.0", layout="wide", page_icon="🧬")
    render_app_styles()
    registry = get_question_bank_registry()

    render_header(registry.fingerprint)
    render_profile_workspace(registry.fingerprint)
    questionnaire_mode = render_questionnaire_mode()
    needs_bank = registry.get("needs").for_mode(questionnaire_mode)
    shadow_bank = registry.get("shadow").for_mode(questionnaire_mode)
    eros_bank = registry.get("eros").for_mode(questionnaire_mode)
    psycho = render_big_five_manual()

    with st.form("main_form"):
        st.divider()
        shadow, shadow_missing = render_shadow_form(shadow_bank)
        st.divider()
        eros, eros_missing = render_eros_form(eros_bank)
        st.divider()
        raw_needs, needs_missing = render_scenarios_engine(needs_bank)
        st.divider()
        professional = render_professional_compass()
        st.markdown("---")
        submit = st.form_submit_button("Розрахувати профіль", type="primary")

    if not submit:
        return

    has_missing_inputs = any((shadow_missing, eros_missing, needs_missing))
    if has_missing_inputs:
        st.error("Розрахунок заблоковано: дайте явну відповідь на всі питання активних анкет.")
        _render_missing_inputs("Shadow", shadow_missing)
        _render_missing_inputs("Eros", eros_missing)
        _render_missing_inputs("Needs", needs_missing)
        return

    user = UserProfile("User", psycho, shadow, eros, raw_needs, professional)
    user.needs = NeedsAdjustmentService.adjust_needs(user.needs, user.psychometrics)
    manual = ReportGenerator.generate_manual(user)
    render_result_dashboard(manual)


if __name__ == "__main__":
    main()
