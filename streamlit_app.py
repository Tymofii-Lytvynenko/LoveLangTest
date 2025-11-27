import streamlit as st
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Tuple

# ==========================================
# 1. CORE DATA TYPES & ENUMS
# ==========================================

class AttachmentStyle(Enum):
    SECURE = "Надійний (Secure)"
    ANXIOUS = "Тривожний (Anxious)"
    AVOIDANT = "Уникаючий (Avoidant)"
    DISORGANIZED = "Дезорганізований (Disorganized)"

class ConflictResponse(Enum):
    FIGHT = "Напад (Fight)"
    FLIGHT = "Відсторонення (Flight)"
    FREEZE = "Завмирання (Freeze)"
    FAWN = "Пристосування (Fawn)"

class RegulationMethod(Enum):
    CO_REGULATION = "Ко-регуляція (Потрібен партнер)"
    AUTO_REGULATION = "Авто-регуляція (Потрібна самотність)"

class ContextDependency(Enum):
    HIGH = "Висока (Потрібні специфічні умови)"
    LOW = "Низька (Спонтанність)"

# ==========================================
# 2. MODULE SPECIFICATIONS (Composition Components)
# ==========================================

@dataclass
class PsychometricsComponent:
    """
    Substrate Layer. Inputs are 0-100 (standard test scores), converted to 0.0-1.0 internally.
    """
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float
    has_adhd: bool = False
    has_asd: bool = False

    def __post_init__(self):
        # Normalize 0-100 to 0.0-1.0 just in case
        if self.openness > 1.0: self.openness /= 100.0
        if self.conscientiousness > 1.0: self.conscientiousness /= 100.0
        if self.extraversion > 1.0: self.extraversion /= 100.0
        if self.agreeableness > 1.0: self.agreeableness /= 100.0
        if self.neuroticism > 1.0: self.neuroticism /= 100.0

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
    SRME Model.
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
        # 1. Safety (Neuroticism Driver)
        n_weight = 0.65
        base_safety = self.raw_safety * (1.0 - n_weight)
        implicit_safety = psycho.neuroticism * n_weight
        # If ASD is present, Safety needs (predictability) increase
        if psycho.has_asd: implicit_safety += 0.2
        self.adjusted_safety = min(base_safety + implicit_safety, 1.0)

        # 2. Resource (Executive Function Driver)
        # Low Conscientiousness creates a deficit that needs Resource support
        dysfunction_penalty = (1.0 - psycho.conscientiousness)
        if psycho.has_adhd: dysfunction_penalty += 0.25
        # The final need is the MAX of self-reported desire OR biological necessity
        self.adjusted_resource = max(self.raw_resource, min(dysfunction_penalty, 1.0))

        # 3. Resonance (Openness/Agreeableness Driver)
        # High Openness demands Intellectual Resonance
        cognitive_floor = 0.0
        if psycho.openness > 0.75: cognitive_floor = 0.8
        self.adjusted_resonance = max(self.raw_resonance, cognitive_floor)

        # 4. Expansion (Extraversion/Openness Driver)
        # High O + High E = Extreme need for novelty
        expansion_driver = (psycho.extraversion + psycho.openness) / 2
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
        # Sort needs
        sorted_needs = sorted(needs_map.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_needs[0]
        secondary = sorted_needs[1]

        # Shadow Warning Logic
        shadow_warn = "Стабільний"
        if self.shadow.attachment_style == AttachmentStyle.AVOIDANT:
            shadow_warn = "Схильність до дистанціювання при стресі (Avoidant Strategy)"
        elif self.shadow.attachment_style == AttachmentStyle.ANXIOUS:
            shadow_warn = "Вимога постійного контакту/підтвердження (Anxious Strategy)"
        elif self.shadow.attachment_style == AttachmentStyle.DISORGANIZED:
            shadow_warn = "Хаотична реакція: «Іди геть — ні, стій» (Disorganized)"

        # Constraints
        safety_mech = "Базова"
        if self.needs.adjusted_safety > 0.75:
            safety_mech = "Висока потреба у вербалізації намірів та передбачуваності"
        
        resource_dep = "Автономний"
        if self.needs.adjusted_resource > 0.7:
            resource_dep = "Висока (Потрібен партнер-менеджер/скаффолдинг)"

        # Expansion Check
        expansion_note = "Комфорт у рутині"
        if self.needs.adjusted_expansion > 0.8:
            expansion_note = "Висока (Потреба у постійній новизні/дофаміні)"

        return {
            "primary_driver": primary,
            "secondary_driver": secondary,
            "constraints": {
                "safety": safety_mech,
                "resource": resource_dep,
                "expansion": expansion_note
            },
            "erotic_profile": f"{self.eros.context_dependency.value} / Гальма: {int(self.eros.brake*100)}%",
            "shadow_warning": shadow_warn,
            "scores": needs_map
        }

# ==========================================
# 3. SCENARIO ENGINE
# ==========================================

@dataclass
class ScenarioOption:
    text: str
    # Weights added to: (S, R, M, E)
    weights: Tuple[float, float, float, float] 

@dataclass
class Scenario:
    id: str
    question: str
    options: List[ScenarioOption]

def get_scenarios() -> List[Scenario]:
    return [
        Scenario("conf_logic", "Ви з партнером сперечаєтесь про політику чи філософію. Емоції наростають. Що для вас є провалом?", [
            ScenarioOption("Партнер починає плакати або кричати (Втрата безпеки/контролю)", (0.5, 0.0, 0.0, 0.0)),
            ScenarioOption("Партнер використовує логічні помилки і відмовляється це визнати (Втрата істини)", (0.0, 0.0, 0.5, 0.0)),
            ScenarioOption("Ми просто припиняємо розмову і йдемо в різні кімнати (Втрата контакту)", (0.2, 0.0, 0.3, 0.0))
        ]),
        Scenario("stress_support", "У вас жахливий день, ви виснажені. Партнер хоче допомогти. Що спрацює найкраще?", [
            ScenarioOption("Мовчки зробить чай, прибере в кімнаті і залишить мене в спокої (Acts of Service)", (0.1, 0.5, 0.0, 0.0)),
            ScenarioOption("Сяде поруч, обійме і скаже, що все буде добре (Emotional Safety)", (0.5, 0.0, 0.2, 0.0)),
            ScenarioOption("Вислухає і допоможе розкласти проблему на алгоритм вирішення (Cognitive Support)", (0.0, 0.2, 0.4, 0.0))
        ]),
        Scenario("boredom", "Субота. У вас немає планів. Партнер пропонує просидіти весь день вдома за серіалами. Ваша реакція?", [
            ScenarioOption("Чудово, я люблю передбачуваний відпочинок (Safety/Rest)", (0.4, 0.0, 0.0, -0.2)),
            ScenarioOption("Нудьга. Я запропоную піти гуляти або спробувати новий ресторан (Expansion)", (0.0, 0.0, 0.0, 0.5)),
            ScenarioOption("Згоден, якщо ми будемо обговорювати сюжет і аналізувати героїв (Resonance)", (0.0, 0.0, 0.3, 0.0))
        ]),
        Scenario("mistake", "Ви припустилися помилки, яка коштувала грошей (наприклад, купили непотрібну річ). Реакція партнера?", [
            ScenarioOption("«Нічого страшного, ми це виправимо». (Emotional Safety)", (0.5, 0.0, 0.0, 0.0)),
            ScenarioOption("«Давай подумаємо, як продати це назад або оптимізувати бюджет». (Functional Resource)", (0.0, 0.5, 0.0, 0.0)),
            ScenarioOption("Він аналізує, чому я це зробив, і ми шукаємо корінь моєї імпульсивності. (Deep Resonance)", (0.0, 0.0, 0.4, 0.0))
        ]),
        Scenario("growth", "Партнер отримав підвищення, але тепер працюватиме більше. Що ви відчуваєте?", [
            ScenarioOption("Тривогу. У нас буде менше часу разом. (Fear of Loss - Safety)", (0.4, 0.0, 0.0, 0.0)),
            ScenarioOption("Радість. Це більше ресурсів для нашої сім'ї. (Resource)", (0.0, 0.4, 0.0, 0.0)),
            ScenarioOption("Гордість. Я захоплююсь його/її розвитком і амбіціями. (Expansion/Resonance)", (0.0, 0.0, 0.2, 0.4))
        ]),
        Scenario("intimacy", "Що для вас є найвищою формою близькості?", [
            ScenarioOption("Відчуття, що мене повністю приймають таким, який я є, без критики (Safety)", (0.5, 0.0, 0.0, 0.0)),
            ScenarioOption("Момент, коли ми розуміємо складну ідею одне одного з півслова (Cognitive Resonance)", (0.0, 0.0, 0.5, 0.0)),
            ScenarioOption("Спільне переживання чогось екстремального або абсолютно нового (Expansion)", (0.0, 0.0, 0.0, 0.5))
        ]),
        Scenario("autonomy", "Партнер хоче поїхати у відпустку з друзями без вас на тиждень.", [
            ScenarioOption("Мені буде некомфортно/тривожно. Чому без мене? (Safety Priority)", (0.4, 0.0, 0.0, -0.2)),
            ScenarioOption("Чудово! Я нарешті займуся своїми проєктами/хобі наодинці. (Expansion/Autonomy)", (0.0, 0.0, 0.0, 0.5)),
            ScenarioOption("Нормально, якщо ми будемо зідзвонюватися і ділитися враженнями щовечора. (Compromise)", (0.1, 0.0, 0.1, 0.0))
        ]),
        Scenario("household", "Хто має мити посуд?", [
            ScenarioOption("Той, чия черга/хто вільний. Має бути чітка система. (Resource/Structure)", (0.2, 0.4, 0.0, 0.0)),
            ScenarioOption("Ми робимо це разом, розмовляючи і жартуючи. (Bonding)", (0.0, 0.0, 0.3, 0.0)),
            ScenarioOption("Краще купити посудомийку, щоб не витрачати на це час життя. (Expansion/Efficiency)", (0.0, 0.2, 0.0, 0.3))
        ])
    ]

# ==========================================
# 4. UI FUNCTIONS
# ==========================================

def render_big_five_manual():
    st.header("1. Substrate Layer (Психометрія)")
    st.markdown("Введіть результати тесту **Big Five (OCEAN)**. Використовуйте шкалу 0-100 (або T-бали).")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        o = st.number_input("Openness", 0, 100, 50, help="Інтелект, уява, відкритість до нового.")
    with col2:
        c = st.number_input("Conscientiousness", 0, 100, 50, help="Порядок, дисципліна, обов'язок.")
    with col3:
        e = st.number_input("Extraversion", 0, 100, 50, help="Енергійність, товариськість.")
    with col4:
        a = st.number_input("Agreeableness", 0, 100, 50, help="Альтруїзм, довіра, поступливість.")
    with col5:
        n = st.number_input("Neuroticism", 0, 100, 50, help="Тривожність, вразливість, емоційність.")
    
    st.caption("Додаткові нейро-маркери:")
    c_check1, c_check2 = st.columns(2)
    with c_check1:
        adhd = st.checkbox("Діагностовано/підозрюється РДУГ (ADHD)")
    with c_check2:
        asd = st.checkbox("Діагностовано/підозрюється РАС (Autism Spectrum)")
        
    return PsychometricsComponent(o, c, e, a, n, adhd, asd)

def render_scenarios_engine() -> RelationalNeedsComponent:
    st.header("4. Context Layer (Глибинний аналіз)")
    st.markdown("Оберіть варіант, який є найбільш природним для вас (навіть якщо він не ідеальний).")
    
    scenarios = get_scenarios()
    
    # Accumulators
    s_acc, r_acc, m_acc, e_acc = 0.0, 0.0, 0.0, 0.0
    
    for sc in scenarios:
        st.subheader(f"🔹 {sc.question}")
        # Create a mapping for radio buttons
        opts_map = {opt.text: opt for opt in sc.options}
        choice_text = st.radio("Ваш вибір:", list(opts_map.keys()), key=sc.id, label_visibility="collapsed")
        
        # Add weights
        choice = opts_map[choice_text]
        s_acc += choice.weights[0]
        r_acc += choice.weights[1]
        m_acc += choice.weights[2]
        e_acc += choice.weights[3]
        st.markdown("---")

    # Normalization (Simple Sigmoid-like clamp for prototype)
    # Assuming max possible score per category is around 3.0-4.0 based on 8 questions
    def clamp_norm(val):
        return max(0.0, min(val / 2.5, 1.0)) # 2.5 is an arbitrary scaling factor based on weights

    return RelationalNeedsComponent(
        raw_safety=clamp_norm(s_acc),
        raw_resource=clamp_norm(r_acc),
        raw_resonance=clamp_norm(m_acc),
        raw_expansion=clamp_norm(e_acc)
    )

# ==========================================
# 5. MAIN APP Logic
# ==========================================

def main():
    st.set_page_config(page_title="CRNAS v2.0", layout="wide", page_icon="🧬")
    
    st.title("🧬 CRNAS: Relationship Architecture System")
    st.markdown("""
    **Advanced Scientific Profiling.** Цей інструмент аналізує ваші стосунки не через абстрактні "мови любові", а через 
    поєднання нейробіології, теорії прихильності та функціональних потреб.
    """)
    st.info("ℹ️ Для точного результату будьте максимально чесними, особливо в секції Сценаріїв.")

    with st.form("main_form"):
        # 1. Hardware
        psycho = render_big_five_manual()
        st.divider()
        
        # 2. Shadow
        st.header("2. Shadow Component (Механізми захисту)")
        c1, c2, c3 = st.columns(3)
        with c1:
            att = st.selectbox("Стиль прив'язаності", [x for x in AttachmentStyle], format_func=lambda x: x.value)
        with c2:
            conf = st.selectbox("Реакція на конфлікт", [x for x in ConflictResponse], format_func=lambda x: x.value)
        with c3:
            reg = st.selectbox("Регуляція стресу", [x for x in RegulationMethod], format_func=lambda x: x.value)
        shadow = ShadowComponent(att, conf, reg)
        st.divider()

        # 3. Eros
        st.header("3. Eros Component (Сексуальний профіль)")
        ec1, ec2 = st.columns(2)
        with ec1:
            acc = st.slider("Акселератор (Збудження)", 0, 100, 50, help="Як легко ви збуджуєтесь?") / 100.0
            ctx = st.selectbox("Контекст", [x for x in ContextDependency], format_func=lambda x: x.value)
        with ec2:
            brk = st.slider("Гальма (Інгібіція)", 0, 100, 50, help="Як сильно стрес вбиває бажання?") / 100.0
            tags = st.multiselect("Тригери", ["Sapiosexual", "Demisexual", "Kinky", "Sensory", "Visual", "Auditory", "Service"])
        eros = ErosComponent(acc, brk, ctx, tags)
        st.divider()

        # 4. Scenarios
        needs = render_scenarios_engine()
        
        submit = st.form_submit_button("📊 Розрахувати архітектуру стосунків", type="primary")

    if submit:
        # Assembly
        user = UserProfile("Client", psycho, shadow, eros, needs)
        # Calculation
        user.needs.calculate_adjustments(user.psychometrics)
        # Report
        manual = user.generate_manual()
        
        st.success("Профіль успішно згенеровано.")
        
        # Dashboard
        col_res1, col_res2 = st.columns([1, 1])
        
        with col_res1:
            st.subheader("🏁 Драйвери (Drivers)")
            p_name, p_val = manual['primary_driver']
            s_name, s_val = manual['secondary_driver']
            
            st.metric(label="Домінантна потреба", value=p_name, delta=f"{p_val*100:.1f}%")
            st.metric(label="Вторинна потреба", value=s_name, delta=f"{s_val*100:.1f}%")
            
            st.markdown("#### Деталізація потреб (S.R.M.E.)")
            for k, v in manual['scores'].items():
                st.progress(v, text=f"{k}: {v*100:.0f}/100")

        with col_res2:
            st.subheader("⚠️ Операційні обмеження")
            st.warning(f"**Shadow Warning:** {manual['shadow_warning']}")
            
            with st.expander("Детальні інструкції для партнера (Readme)", expanded=True):
                st.markdown(f"""
                - **Безпека:** {manual['constraints']['safety']}
                - **Ресурс:** {manual['constraints']['resource']}
                - **Новизна:** {manual['constraints']['expansion']}
                - **Eros:** {manual['erotic_profile']}
                """)

if __name__ == "__main__":
    main()