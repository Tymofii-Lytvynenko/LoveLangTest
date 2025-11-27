import streamlit as st
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict

# Імпорт бази знань
from crnas_data import get_scenarios, EXPLANATIONS, ScenarioOption

# ==========================================
# 1. CORE DATA TYPES & ENUMS
# ==========================================

class AttachmentStyle(Enum):
    SECURE = "Надійний (Secure)"
    ANXIOUS = "Тривожний (Anxious-Preoccupied)"
    AVOIDANT = "Уникаючий (Dismissive-Avoidant)"
    DISORGANIZED = "Дезорганізований (Fearful-Avoidant)"

class ConflictResponse(Enum):
    FIGHT = "Напад (Fight) — Критика, агресія"
    FLIGHT = "Втеча (Flight) — Дистанціювання"
    FREEZE = "Завмирання (Freeze) — Shutdown, мовчання"
    FAWN = "Пристосування (Fawn) — Поступливість заради миру"

class RegulationMethod(Enum):
    CO_REGULATION = "Ко-регуляція (Заспокоєння через контакт з іншим)"
    AUTO_REGULATION = "Авто-регуляція (Заспокоєння на самоті)"

class ContextDependency(Enum):
    HIGH = "Висока (Потрібні специфічні умови, безпека, відсутність стресу)"
    LOW = "Низька (Збудження спонтанне, стрес не заважає)"

# ==========================================
# 2. LOGIC COMPONENTS (Architecture)
# ==========================================

@dataclass
class PsychometricsComponent:
    """
    Substrate Layer. Inputs 0-100 are normalized to 0.0-1.0 logic.
    """
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float
    has_adhd: bool = False
    has_asd: bool = False

    def __post_init__(self):
        # Normalize inputs immediately
        self.openness = self._norm(self.openness)
        self.conscientiousness = self._norm(self.conscientiousness)
        self.extraversion = self._norm(self.extraversion)
        self.agreeableness = self._norm(self.agreeableness)
        self.neuroticism = self._norm(self.neuroticism)

    def _norm(self, val):
        if val > 1.0: return val / 100.0
        return val

@dataclass
class ShadowComponent:
    attachment_style: AttachmentStyle
    conflict_response: ConflictResponse
    regulation_method: RegulationMethod

@dataclass
class ErosComponent:
    accelerator: float
    brake: float
    context_dependency: ContextDependency
    erotic_tags: List[str]

@dataclass
class RelationalNeedsComponent:
    """
    SRME Model Logic.
    """
    raw_safety: float = 0.0
    raw_resource: float = 0.0
    raw_resonance: float = 0.0
    raw_expansion: float = 0.0
    
    adjusted_safety: float = field(init=False)
    adjusted_resource: float = field(init=False)
    adjusted_resonance: float = field(init=False)
    adjusted_expansion: float = field(init=False)

    def calculate_adjustments(self, psycho: PsychometricsComponent):
        """
        Основний алгоритм корекції.
        Він бере "що користувач хоче" (Raw) і коригує на "що йому біологічно треба" (Adjusted).
        """
        
        # --- 1. SAFETY (Безпека) ---
        # Драйвер: Невротизм та стиль прив'язаності (тут спрощено через Невротизм)
        # Якщо у людини висока тривожність, потреба в безпеці висока, навіть якщо вона каже "я люблю ризик".
        n_weight = 0.65
        base_safety = self.raw_safety * (1.0 - n_weight)
        implicit_safety = psycho.neuroticism * n_weight
        
        if psycho.has_asd: 
            implicit_safety += 0.2  # РАС потребує високої передбачуваності
            
        self.adjusted_safety = min(base_safety + implicit_safety, 1.0)

        # --- 2. RESOURCE (Ресурс/Опора) ---
        # Драйвер: Виконавча функція (Сумлінність).
        # Якщо у людини низька Сумлінність або РДУГ, їй потрібен партнер, який "підстрахує" (зовнішній ресурс).
        # Формула: Дефіцит власних функцій = Потреба у зовнішніх.
        dysfunction_penalty = (1.0 - psycho.conscientiousness)
        if psycho.has_adhd: 
            dysfunction_penalty += 0.25 # Штраф за РДУГ
            
        # Ми беремо МАКСИМУМ між тим, що людина просить, і тим, що їй об'єктивно треба для виживання.
        self.adjusted_resource = max(self.raw_resource, min(dysfunction_penalty, 1.0))

        # --- 3. RESONANCE (Резонанс) ---
        # Драйвер: Відкритість та Приємність.
        # Висока Відкритість вимагає "Intellectual Resonance".
        cognitive_floor = 0.0
        if psycho.openness > 0.75: 
            cognitive_floor = 0.8 # Якщо ти дуже розумний/відкритий, ти не зможеш бути з "простим" партнером.
            
        self.adjusted_resonance = max(self.raw_resonance, cognitive_floor)

        # --- 4. EXPANSION (Експансія/Новизна) ---
        # Драйвер: Екстраверсія + Відкритість.
        # Це "дофаміновий голод".
        expansion_driver = (psycho.extraversion + psycho.openness) / 2
        
        # РДУГ додає потребу в новизні (stimulation seeking)
        if psycho.has_adhd:
            expansion_driver += 0.15
            
        self.adjusted_expansion = (self.raw_expansion + expansion_driver) / 2

@dataclass
class UserProfile:
    name: str
    psychometrics: PsychometricsComponent
    shadow: ShadowComponent
    eros: ErosComponent
    needs: RelationalNeedsComponent
    
    def generate_manual(self) -> Dict:
        needs_map = {
            "Безпека (Safety)": self.needs.adjusted_safety,
            "Ресурс (Resource)": self.needs.adjusted_resource,
            "Резонанс (Resonance)": self.needs.adjusted_resonance,
            "Експансія (Expansion)": self.needs.adjusted_expansion
        }
        sorted_needs = sorted(needs_map.items(), key=lambda x: x[1], reverse=True)
        
        # Логіка генерації текстових попереджень
        shadow_warn = "Стабільний"
        if self.shadow.attachment_style == AttachmentStyle.AVOIDANT:
            shadow_warn = "⚠️ Схильність до дистанціювання при стресі. Партнер може відчувати себе покинутим."
        elif self.shadow.attachment_style == AttachmentStyle.ANXIOUS:
            shadow_warn = "⚠️ Вимога постійного контакту. Загроза розриву викликає паніку."
        
        if self.shadow.regulation_method == RegulationMethod.AUTO_REGULATION:
            shadow_warn += " (Потребує часу на самоті для заспокоєння)."

        # Генерація словника
        return {
            "primary_driver": sorted_needs[0],
            "secondary_driver": sorted_needs[1],
            "shadow_warning": shadow_warn,
            "erotic_key": f"Гальма: {int(self.eros.brake*100)}% | Контекст: {self.eros.context_dependency.name}",
            "scores": needs_map
        }

# ==========================================
# 3. UI RENDERING FUNCTIONS
# ==========================================

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
        st.caption(sc.description) # Показуємо наукове пояснення питання
        
        opts_map = {opt.text: opt for opt in sc.options}
        choice_text = st.radio("Ваш вибір:", list(opts_map.keys()), key=sc.id, label_visibility="collapsed")
        
        choice = opts_map[choice_text]
        s_acc += choice.weights[0]
        r_acc += choice.weights[1]
        m_acc += choice.weights[2]
        e_acc += choice.weights[3]
        st.markdown("---")

    # Нормалізація результатів (обрізаємо до 1.0)
    def norm(val): return max(0.0, min(val / 2.0, 1.0))

    return RelationalNeedsComponent(
        raw_safety=norm(s_acc),
        raw_resource=norm(r_acc),
        raw_resonance=norm(m_acc),
        raw_expansion=norm(e_acc)
    )

# ==========================================
# 4. MAIN APP ENTRY POINT
# ==========================================

def main():
    st.set_page_config(page_title="CRNAS v2.1", layout="wide", page_icon="🧬")
    st.title("🧬 CRNAS: Comprehensive Relationship Needs Analysis System")
    
    with st.form("main_form"):
        psycho = render_big_five_manual()
        st.divider()
        shadow = render_shadow_form()
        st.divider()
        eros = render_eros_form()
        st.divider()
        needs = render_scenarios_engine()
        
        submit = st.form_submit_button("📊 Розрахувати архітектуру", type="primary")

    if submit:
        # Create user profile
        user = UserProfile("User", psycho, shadow, eros, needs)
        # Apply normalization algorithm
        user.needs.calculate_adjustments(user.psychometrics)
        # Generate report
        manual = user.generate_manual()
        
        # Display Results
        st.success("Розрахунок завершено.")
        
        r1, r2 = st.columns(2)
        with r1:
            st.subheader("Ключові драйвери")
            st.metric("Домінанта", f"{manual['primary_driver'][0]}", f"{manual['primary_driver'][1]*100:.0f}%")
            st.metric("Вторинна", f"{manual['secondary_driver'][0]}", f"{manual['secondary_driver'][1]*100:.0f}%")
            
            st.write("#### Повний профіль потреб (Adjusted)")
            for k, v in manual['scores'].items():
                st.progress(v, text=f"{k}: {v*100:.1f}/100")
                
        with r2:
            st.subheader("Операційні примітки")
            st.warning(manual['shadow_warning'])
            st.info(f"**Eros Profile:** {manual['erotic_key']}")

if __name__ == "__main__":
    main()