# Фасад для даних

from .bigfive import EXPLANATIONS, FACETS_EXPLANATIONS
from .needs import get_scenarios, get_max_possible_scores
from .shadow import get_shadow_quiz, SHADOW_EXPLANATIONS
from .eros import get_eros_quiz, EROS_EXPLANATIONS, EROS_TAGS_EXPLANATIONS
from .professional import PROFESSIONAL_EXPLANATIONS
from .models import Scenario, ScenarioOption, QuizQuestion, QuizOption