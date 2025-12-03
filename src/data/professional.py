"""
METHODOLOGY: PROFESSIONAL COMPASS (RIASEC)
===========================================

Theoretical Basis:
------------------
John Holland's Theory of Career Choice (RIASEC).
People and environments are classified into 6 types. 
Relationship compatibility correlates with the distance on the RIASEC hexagon.

Relational Impact:
------------------
1. Realistic (Doers): Value shared activities over long talks. Low emotional expression.
   - Offers: Resource (Fixing things).
   - Needs: Autonomy.
   
2. Investigative (Thinkers): Value logic. Can be emotionally detached.
   - Offers: Intellectual Resonance.
   - Needs: Mental space (Solitude).
   
3. Artistic (Creators): Value expression. High emotional lability.
   - Offers: Novelty (Expansion).
   - Needs: Emotional Resonance + Tolerance for chaos.
   
4. Social (Helpers): Value connection.
   - Offers: Emotional Safety & Care.
   - Needs: Communication.
   
5. Enterprising (Persuaders): Value status and goals. Workaholic tendency.
   - Offers: Resources (Money/Status).
   - Needs: Support for ambitions (Cheerleading).
   
6. Conventional (Organizers): Value predictability.
   - Offers: Stability (Safety).
   - Needs: Clear rules/plans.
"""

from .models import QuizQuestion, QuizOption

PROFESSIONAL_EXPLANATIONS = {
    "intro": """
    **Професійний Компас (RIASEC)**
    Ваша робота формує ваш стиль мислення. 
    * **R (Realistic):** "Я роблю руками/кодом". Інженери, агрономи, механіки.
    * **I (Investigative):** "Я думаю/аналізую". Науковці, аналітики, розробники архітектури.
    * **A (Artistic):** "Я створюю/виражаю". Дизайнери, письменники, актори.
    * **S (Social):** "Я допомагаю/вчу". Лікарі, вчителі, психологи, HR.
    * **E (Enterprising):** "Я керую/продаю". Бізнесмени, менеджери, політики.
    * **C (Conventional):** "Я організовую/рахую". Бухгалтери, адміністратори, QA.
    """,
    "impact_warning": """
    ⚠️ **Увага:** Протилежні типи на компасі (наприклад, Митець vs Системний) часто мають найсильніше "тертя" в побуті, але можуть ідеально доповнювати одне одного, якщо є повага.
    """
}