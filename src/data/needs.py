"""
METHODOLOGY: SRME SCENARIO GENERATION (RELATIONAL NEEDS)
========================================================

Theoretical Basis:
------------------
Custom model mapping needs to 4 dimensions:
- Safety (S): Predictability, emotional regulation.
- Resource (R): Executive function support, acts of service.
- Resonance (M): Cognitive/Emotional mirroring, shared meaning.
- Expansion (E): Novelty, autonomy, growth.

Question Formulation Guidelines:
--------------------------------
1. Forced Choice (Trade-offs): 
   Do not ask "Do you like X?". Everyone likes safety AND fun.
   Ask: "When X clashes with Y, what do you choose?".
   
2. The Scenario:
   Place the user in a situation of *deficit* or *conflict*.
   Example: "A free weekend" (Resource vs Expansion).

3. Weighting Options:
   Options should rarely be pure (1.0, 0, 0, 0). Real choices are nuanced.
   - Option A: Prioritizes Stability (Safety++) but sacrifices Novelty (Expansion-).
   - Option B: Prioritizes Intensity (Resonance++) but risks Conflict (Safety-).
   
   Avoid "Correct" answers. All options must be valid relationship preferences.

Scoring Logic:
--------------
Vector: (Safety, Resource, Resonance, Expansion).
"""

from .models import Scenario, ScenarioOption

def get_scenarios() -> list[Scenario]:
    return [
        Scenario(
            id="conf_01", 
            question="Тон голосу під час сварки", 
            description="Перевірка на сенсорну чутливість та потребу в емоційній безпеці.",
            options=[
                ScenarioOption(
                    "Я можу слухати аргументи, тільки якщо голос спокійний.", 
                    (0.7, 0.0, 0.0, 0.0)
                ),
                ScenarioOption(
                    "Емоції — це нормально. Крик показує небайдужість.", 
                    (0.0, 0.0, 0.3, 0.2)
                ),
                ScenarioOption(
                    "Мене дратує тон, але я фокусуюсь на словах.", 
                    (0.0, 0.0, 0.5, 0.0)
                )
            ]
        ),
        # ... (Вставте сюди повний список сценаріїв з попередніх кроків) ...
    ]