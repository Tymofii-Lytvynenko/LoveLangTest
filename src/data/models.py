from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class QuizOption:
    text: str
    scores: Tuple[float, ...] 

@dataclass
class QuizQuestion:
    id: str
    question: str
    options: List[QuizOption]

@dataclass
class ScenarioOption:
    text: str
    # Weights: (Safety, Resource, Resonance, Expansion)
    weights: Tuple[float, float, float, float] 

@dataclass
class Scenario:
    id: str
    question: str
    description: str
    options: List[ScenarioOption]