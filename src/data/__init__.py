# Цей файл робить змінні доступними прямо з пакету src.data
# Це "Фасад", який збирає все з підфайлів

from .bigfive import EXPLANATIONS
from .needs import get_scenarios
from .shadow import get_shadow_quiz, SHADOW_EXPLANATIONS
from .eros import get_eros_quiz, EROS_EXPLANATIONS
from .professional import PROFESSIONAL_EXPLANATIONS
from .models import Scenario, ScenarioOption, QuizQuestion, QuizOption