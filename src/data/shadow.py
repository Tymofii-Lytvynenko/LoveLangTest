"""
METHODOLOGY: ATTACHMENT STYLE QUIZ GENERATION
=============================================

Theoretical Basis:
------------------
Based on Bowlby & Ainsworth's Attachment Theory and adult attachment research (Hazan & Shaver).
The core metric is the response to "separation distress" and "intimacy regulation".

Question Formulation Guidelines:
--------------------------------
1. The Trigger: Each question must present a scenario involving stress, conflict, or distance.
   Attachment systems are dormant in calm waters; they activate only under threat.
   
2. The Options Mapping:
   - Option A (Anxious/Preoccupied): Hyperactivation strategies. 
     Keywords: Clinging, protest behavior, demanding reassurance, fear of abandonment, "fighting for contact".
     
   - Option B (Avoidant/Dismissive): Deactivation strategies.
     Keywords: Withdrawal, shutting down, valuing independence over connection, suppressing feelings, "flight".
     
   - Option C (Secure): Constructive regulation.
     Keywords: Open communication, ability to self-soothe, trust, balance between autonomy and intimacy.

Scoring Logic:
--------------
Vector: (Secure, Anxious, Avoidant) -> Normalized to 1.0 sum per question.
"""

from .models import QuizQuestion, QuizOption

SHADOW_EXPLANATIONS = {
    "intro": """
    **Тіньовий компонент** базується на Теорії Прив'язаності (Боулбі/Ейнсворт) та дослідженні конфліктів (Готтман).
    Це те, як ви поводитесь, коли ви **налякані, втомлені або злі**.
    """,
    "secure": """
    **🟢 Надійний тип (Secure)**
    Ви комфортно почуваєтесь у близькості. Ви вірите, що ваші потреби будуть задоволені.
    """,
    "anxious": """
    **🔴 Тривожний тип (Anxious-Preoccupied)**
    Ваша нервова система "сканує" партнера на предмет ознак віддалення. Будь-яка зміна тону викликає паніку.
    """,
    "avoidant": """
    **🔵 Уникаючий тип (Dismissive-Avoidant)**
    Близькість асоціюється з втратою себе. Коли емоцій забагато, ви "вимикаєтесь".
    """,
    "disorganized": """
    **🟣 Дезорганізований тип (Fearful-Avoidant)**
    Ви хочете близькості, але вона вас лякає. "Іди сюди — ні, йди геть".
    """
}

def get_shadow_quiz() -> list[QuizQuestion]:
    return [
        QuizQuestion(
            id="att_01", 
            question="Коли партнер поводиться холодно або відсторонено:",
            options=[
                QuizOption("Я панікую і намагаюся з'ясувати, що сталося, негайно.", (0.0, 1.0, 0.0)),
                QuizOption("Мені байдуже. Я займаюся своїми справами.", (0.0, 0.0, 1.0)),
                QuizOption("Я запитаю, чи все гаразд, але дам йому простір.", (1.0, 0.0, 0.0))
            ]
        ),
        QuizQuestion(
            id="att_02", 
            question="Як ви ставитесь до залежності від партнера?",
            options=[
                QuizOption("Я боюся залежати від когось. Я маю бути самодостатнім.", (0.0, 0.0, 1.0)),
                QuizOption("Я хочу злитися з партнером в одне ціле.", (0.0, 1.0, 0.0)),
                QuizOption("Мені комфортно покладатися на партнера.", (1.0, 0.0, 0.0))
            ]
        ),
        QuizQuestion(
            id="att_03", 
            question="Під час серйозного конфлікту:",
            options=[
                QuizOption("Я хочу втекти або замовкнути, щоб не погіршити ситуацію.", (0.0, 0.0, 1.0)),
                QuizOption("Я не можу заспокоїтися, поки ми все не вирішимо. Я можу кричати.", (0.0, 1.0, 0.0)),
                QuizOption("Ми можемо взяти паузу, але я знаю, що ми повернемось до розмови.", (1.0, 0.0, 0.0))
            ]
        )
    ]