"""
METHODOLOGY: DUAL CONTROL MODEL QUIZ GENERATION
===============================================

Theoretical Basis:
------------------
Based on Emily Nagoski's work ("Come As You Are"). 
Sexual temperament consists of two independent systems: SES (Accelerator) and SIS (Brakes).

Question Formulation Guidelines:
--------------------------------
1. Dimension Separation: Do not mix "turn-ons" with "turn-offs" in the same scale.
   They must be measured independently.

2. The Accelerator (SES) Questions:
   - Focus on: Spontaneous desire, ease of arousal, reaction to visual/sensory stimuli.
   - High score: "I get turned on easily."
   - Low score: "I need specific context/preparation." (Responsive desire).

3. The Brake (SIS) Questions:
   - Focus on: INHIBITORS. Stress, body image issues, performance anxiety, noise, mess.
   - High score: "Stress stops sex." (Sensitive brakes).
   - Low score: "Sex relieves stress." (Low brakes).

Scoring Logic:
--------------
Vector: (Accelerator_Score, Brake_Score) -> Each 0.0 to 1.0.
"""

from .models import QuizQuestion, QuizOption

EROS_EXPLANATIONS = {
    "intro": """
    **Eros Component** базується на Моделі Подвійного Контролю (Dual Control Model) Емілі Нагоскі.
    Сексуальний темперамент складається з двох незалежних систем:
    1.  **Акселератор (SES):** Як легко ви помічаєте еротичні стимули?
    2.  **Гальма (SIS):** Наскільки сильно стрес, брудний посуд чи шум блокують збудження?
    """,
    "accelerator": """
    **🔥 Акселератор (SES)**
    Як швидко ваш мозок реагує на еротичні стимули?
    * **Високий:** Ви можете збудитися миттєво.
    * **Низький:** Вам потрібен час і "розігрів".
    """,
    "brake": """
    **🛑 Гальма (SIS)**
    Як мозок реагує на загрози (стрес, втому)?
    * **Чутливі:** Стрес вбиває бажання.
    * **Низькі:** Секс можливий навіть під час стресу.
    """
}

def get_eros_quiz() -> list[QuizQuestion]:
    return [
        QuizQuestion(
            id="eros_01", 
            question="Вплив стресу (робота, гроші) на бажання:",
            options=[
                QuizOption("Стрес повністю вбиває моє лібідо.", (0.0, 1.0)), # High Brake
                QuizOption("Секс допомагає мені розслабитися.", (0.5, 0.0)), # Low Brake
                QuizOption("Залежить від рівня стресу.", (0.0, 0.5)) 
            ]
        ),
        QuizQuestion(
            id="eros_02", 
            question="Спонтанне збудження:",
            options=[
                QuizOption("Я часто відчуваю збудження 'нізвідки'.", (1.0, 0.0)), # High Accel
                QuizOption("Мені потрібен контекст (романтика), щоб відчути бажання.", (0.3, 0.0)), 
                QuizOption("Я рідко думаю про секс, поки партнер не ініціює.", (0.0, 0.0)) 
            ]
        ),
        QuizQuestion(
            id="eros_03", 
            question="Умови для сексу (Контекст):",
            options=[
                QuizOption("Має бути ідеально: чисто, тихо, ніяких відволікань.", (0.0, 0.8)), 
                QuizOption("Ми можемо це зробити де завгодно, умови не важливі.", (0.8, 0.0)), 
                QuizOption("Мені важливо відчувати емоційний зв'язок, решта — деталі.", (0.5, 0.2)) 
            ]
        )
    ]