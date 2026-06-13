import json

import streamlit as st

from src.profile import UserProfile
from src.question_bank import get_question_bank_registry
from src.services.adjustment import NeedsAdjustmentService
from src.services.profile_codec import ProfileCodec, ProfileCodecError
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
        st.sidebar.warning(f"Імпорт виконано з очищенням: {len(removal_log)} полів відкинуто.")
        with st.sidebar.expander("Деталі очищення"):
            for item in removal_log:
                st.write(f"- {item}")

    if changes_count > 0:
        st.sidebar.success(f"Профіль імпортовано. Оновлено полів: {changes_count}.")
    elif not removal_log:
        st.sidebar.info("Імпортований профіль уже збігається з поточним станом.")


def handle_profile_import() -> None:
    with st.sidebar:
        st.header("Профіль")
        encoded_payload = st.text_area(
            "Вставити рядок профілю",
            key="profile_transport_input",
            height=120,
            help="Основний спосіб перенесення профілю між сесіями.",
        )

        if st.button("Імпортувати рядок", use_container_width=True):
            try:
                payload = ProfileCodec.decode_string(encoded_payload)
                _import_payload_state(ProfileCodec.to_json_dict(payload))
            except ProfileCodecError as exc:
                st.error(f"Не вдалося декодувати рядок профілю: {exc}")

        uploaded_file = st.file_uploader(
            "Dev/debug: завантажити JSON payload",
            type="json",
            help="Допоміжний шлях для локального дебагу. Використовує ту саму схему, що і compact string.",
        )
        if uploaded_file is not None and st.button("Імпортувати JSON payload", use_container_width=True):
            try:
                _import_payload_state(json.load(uploaded_file))
            except (ProfileCodecError, json.JSONDecodeError) as exc:
                st.error(f"Не вдалося завантажити JSON payload: {exc}")


def render_profile_export(bank_fingerprint: str) -> None:
    current_state = StateSanitizer.extract_persistable_state(st.session_state)
    with st.sidebar:
        st.divider()
        if not current_state:
            st.caption("Після введення даних тут з'явиться рядок профілю для копіювання.")
            return

        payload = ProfileCodec.build_payload(
            state=current_state,
            bank_fingerprint=bank_fingerprint,
        )
        encoded_payload = ProfileCodec.encode_payload(payload)
        st.text_area(
            "Поточний рядок профілю",
            value=encoded_payload,
            height=140,
            help="Скопіюйте цей рядок і збережіть у будь-якому нотатнику чи месенджері.",
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


def main() -> None:
    st.set_page_config(page_title="CRNAS v4.0", layout="wide", page_icon="🧬")
    registry = get_question_bank_registry()

    handle_profile_import()
    st.title("🧬 CRNAS: Comprehensive Relationship Needs Analysis System")
    st.caption(f"App version {CURRENT_VERSION} | Bank fingerprint {registry.fingerprint}")

    with st.form("main_form"):
        psycho = render_big_five_manual()
        st.divider()
        shadow, shadow_missing = render_shadow_form(registry.get("shadow"))
        st.divider()
        eros, eros_missing = render_eros_form(registry.get("eros"))
        st.divider()
        raw_needs, needs_missing = render_scenarios_engine(registry.get("needs"))
        st.divider()
        professional = render_professional_compass()
        st.markdown("---")
        submit = st.form_submit_button("Розрахувати архітектуру", type="primary")

    render_profile_export(registry.fingerprint)

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

    st.success("Розрахунок завершено.")

    result_col, notes_col = st.columns(2)
    with result_col:
        st.subheader("Ключові драйвери")
        st.metric(
            "Домінанта",
            f"{manual['primary_driver'][0]}",
            f"{manual['primary_driver'][1] * 100:.0f}%",
        )
        st.metric(
            "Вторинна",
            f"{manual['secondary_driver'][0]}",
            f"{manual['secondary_driver'][1] * 100:.0f}%",
        )

        st.write("#### Повний профіль потреб (Adjusted)")
        for label, value in manual["scores"].items():
            st.progress(value, text=f"{label}: {value * 100:.1f}%")

        st.write("---")
        st.subheader("Що ви приносите у стосунки (Provision)")
        provision_scores = manual["provision_scores"]
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Safety", f"{int(provision_scores['Safety Provider (Надійність)'] * 100)}%")
        col2.metric("Resource", f"{int(provision_scores['Resource Provider (Підтримка)'] * 100)}%")
        col3.metric(
            "Resonance",
            f"{int(provision_scores['Resonance Provider (Емпатія/Розуміння)'] * 100)}%",
        )
        col4.metric(
            "Expansion",
            f"{int(provision_scores['Expansion Provider (Драйв/Натхнення)'] * 100)}%",
        )
        st.success(f"Ваша суперсила: **{manual['superpower'][0]}**")

    with notes_col:
        st.subheader("Операційні примітки")
        st.warning(manual["shadow_warning"])
        st.info(f"**Eros Profile:** {manual['erotic_key']}")
        st.info(f"**Professional Style:** {manual['professional_key']}")
        st.caption(f"Strategy: {manual['interaction_style']}")
        if manual["resource_warning"]:
            st.error(manual["resource_warning"])
        if manual["neurodivergence_context"]:
            st.write("#### Neurodivergent Context")
            st.caption(manual["context_disclaimer"])
            st.info(manual["neurodivergence_context"])
            for note in manual["support_notes"]:
                st.write(f"- {note}")


if __name__ == "__main__":
    main()
