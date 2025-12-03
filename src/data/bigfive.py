"""
METHODOLOGY: BIG FIVE (OCEAN) INTERPRETATION LAYER
==================================================

Philosophy:
-----------
We treat the Big Five traits as the "Hardware" or "Operating System" of the user.
Unlike relationship needs (which are negotiated), psychometrics are relatively stable biological/psychological traits.

Rationale for Manual Input:
---------------------------
Conducting a valid psychometric assessment requires 40-100+ questions (e.g., IPIP-NEO). 
Shortened in-app versions often lack validity. Therefore, we rely on users importing 
their scores from professional external sources (Truity, IPIP, etc.) to ensure 
the integrity of the "Substrate Layer".

Interpretation Logic (Relational Impact):
-----------------------------------------
We do not judge traits as "Good" or "Bad". We map them to *Needs*:
1. Openness (O):
   - High: Needs Intellectual Resonance, Novelty (Expansion).
   - Low: Needs Predictability, Tradition (Safety).
   
2. Conscientiousness (C):
   - High: Offers Resource (stability), demands Order.
   - Low: Needs Resource (external scaffolding), offers Spontaneity.
   
3. Extraversion (E):
   - High: Needs Social Expansion, fast-paced stimuli.
   - Low: Needs Solitude (Regulation), deep 1-on-1 connection.
   
4. Agreeableness (A):
   - High: Offers Emotional Resonance, risk of Self-Sacrifice (Fawn response).
   - Low: Prioritizes Logic/Truth over Harmony (can hurt sensitive partners).
   
5. Neuroticism (N):
   - High: The primary driver for Safety needs. High sensitivity to tone/threat.
   - Low: Stable, but may lack empathy for a high-N partner's anxiety.
"""

EXPLANATIONS = {
    "big_five_intro": """
    **Модель Big Five (OCEAN)** — це "операційна система" вашої психіки.
    
    Ми не проводимо цей тест тут, оскільки він вимагає 50+ питань для точності. 
    Будь ласка, введіть свої **Т-бали (шкала 0-100)** з будь-якого професійного тесту.
    
    *Якщо ви не знаєте своїх показників, введіть інтуїтивно (50 = середньо).*
    """,
    
    "openness": """
    **Відкритість до досвіду (Openness)**
    *Це про вашу потребу в новій інформації та інтенсивності переживань.*
    
    * **Високий (>70):** Вам фізично боляче від рутини. Ви "сапіосексуал". Вам потрібні філософські розмови до ранку і постійна новизна.
    * **Низький (<30):** Ви цінуєте традиції, перевірені методи і конкретику. "Просто скажи, що робити, не треба філософії".
    """,
    
    "conscientiousness": """
    **Сумлінність (Conscientiousness)**
    *Це про здатність організовувати себе та простір (Виконавча функція).*
    
    * **Високий (>70):** Ви — людина-план. Надійність — ваша мова любові. Хаос партнера викликає у вас тривогу.
    * **Низький (<30):** Ви спонтанні і гнучкі, але можете забувати про обіцянки чи побутові дрібниці. Вам потрібен партнер, який не буде вас "пиляти", а допоможе структурувати життя.
    * *Примітка:* При РДУГ цей показник часто низький через біологію, а не лінь.
    """,
    
    "extraversion": """
    **Екстраверсія (Extraversion)**
    *Це про те, як ви заряджаєте свою "батарейку".*
    
    * **Високий (>70):** Ізоляція — це покарання. Ви хочете робити все *разом*. Активний відпочинок, гості, події.
    * **Низький (<30):** Люди (навіть кохані) витрачають вашу енергію. Вам життєво необхідний час наодинці ("печера"), щоб відновитися і знову любити.
    """,
    
    "agreeableness": """
    **Доброзичливість (Agreeableness)**
    *Це про пріоритет: Гармонія vs Істина.*
    
    * **Високий (>70):** Ви емпат. Ви часто поступаєтесь власними інтересами, аби уникнути конфлікту. Вам потрібен партнер, який не зловживатиме вашою добротою.
    * **Низький (<30):** Ви скептик і прагматик. Ви любите дебати і пряму критику. "Я кажу це, бо це правда". Партнери можуть вважати вас жорстким.
    """,
    
    "neuroticism": """
    **Невротизм (Neuroticism)**
    *Це чутливість вашої системи сигналізації про небезпеку.*
    
    * **Високий (>70):** Ви відчуваєте все *дуже глибоко*. Тон голосу, затримка відповіді, насуплені брови — все це реєструється як загроза. Ваша головна потреба — **Безпека**.
    * **Низький (<30):** Ви "скеля". Стрес вас не бере. Але вам може бути важко зрозуміти, чому партнер плаче через "дрібницю".
    """
}