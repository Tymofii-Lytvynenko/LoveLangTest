from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
import re
import unicodedata


class BigFivePdfParseError(ValueError):
    """Raised when a Big Five PDF cannot be converted into all 30 facet scores."""


@dataclass(frozen=True)
class BigFiveFacetSpec:
    domain: str
    attr_name: str
    label_uk: str
    session_key: str


FACET_SPECS: tuple[BigFiveFacetSpec, ...] = (
    BigFiveFacetSpec("neuroticism", "anxiety", "Тривога", "facet_neur_anxiety"),
    BigFiveFacetSpec("neuroticism", "hostility", "Злість", "facet_neur_hostility"),
    BigFiveFacetSpec("neuroticism", "depression", "Депресія", "facet_neur_depression"),
    BigFiveFacetSpec("neuroticism", "self_consciousness", "Сором'язливість", "facet_neur_self_consciousness"),
    BigFiveFacetSpec("neuroticism", "impulsiveness", "Невгамовність", "facet_neur_impulsiveness"),
    BigFiveFacetSpec("neuroticism", "vulnerability", "Вразливість", "facet_neur_vulnerability"),
    BigFiveFacetSpec("extraversion", "warmth", "Дружелюбність", "facet_extr_warmth"),
    BigFiveFacetSpec("extraversion", "gregariousness", "Компанійськість", "facet_extr_gregariousness"),
    BigFiveFacetSpec("extraversion", "assertiveness", "Наполегливість", "facet_extr_assertiveness"),
    BigFiveFacetSpec("extraversion", "activity", "Рівень активності", "facet_extr_activity"),
    BigFiveFacetSpec("extraversion", "excitement_seeking", "Пошук збуджень", "facet_extr_excitement_seeking"),
    BigFiveFacetSpec("extraversion", "positive_emotions", "Життєрадісність", "facet_extr_positive_emotions"),
    BigFiveFacetSpec("openness", "fantasy", "Уява", "facet_open_fantasy"),
    BigFiveFacetSpec("openness", "aesthetics", "Художні інтереси", "facet_open_aesthetics"),
    BigFiveFacetSpec("openness", "feelings", "Емоційність", "facet_open_feelings"),
    BigFiveFacetSpec("openness", "actions", "Пригодницькість", "facet_open_actions"),
    BigFiveFacetSpec("openness", "ideas", "Інтелект", "facet_open_ideas"),
    BigFiveFacetSpec("openness", "values", "Лібералізм", "facet_open_values"),
    BigFiveFacetSpec("agreeableness", "trust", "Довіра", "facet_agre_trust"),
    BigFiveFacetSpec("agreeableness", "straightforwardness", "Моральність", "facet_agre_straightforwardness"),
    BigFiveFacetSpec("agreeableness", "altruism", "Альтруїзм", "facet_agre_altruism"),
    BigFiveFacetSpec("agreeableness", "compliance", "Співпраця", "facet_agre_compliance"),
    BigFiveFacetSpec("agreeableness", "modesty", "Скромність", "facet_agre_modesty"),
    BigFiveFacetSpec("agreeableness", "tender_mindedness", "Співчуття", "facet_agre_tender_mindedness"),
    BigFiveFacetSpec("conscientiousness", "competence", "Самоефективність", "facet_cons_competence"),
    BigFiveFacetSpec("conscientiousness", "order", "Організованість", "facet_cons_order"),
    BigFiveFacetSpec("conscientiousness", "dutifulness", "Відповідальність", "facet_cons_dutifulness"),
    BigFiveFacetSpec("conscientiousness", "achievement", "Прагнення до досягнень", "facet_cons_achievement"),
    BigFiveFacetSpec("conscientiousness", "self_discipline", "Самодисципліна", "facet_cons_self_discipline"),
    BigFiveFacetSpec("conscientiousness", "deliberation", "Обачність", "facet_cons_deliberation"),
)

HIGH_LEVEL_SESSION_KEYS = {
    "openness": "psycho_o",
    "conscientiousness": "psycho_c",
    "extraversion": "psycho_e",
    "agreeableness": "psycho_a",
    "neuroticism": "psycho_n",
}


@dataclass(frozen=True)
class ParsedBigFiveFacets:
    raw_scores: dict[str, int]

    @property
    def normalized_scores(self) -> dict[str, float]:
        return {key: value / 20.0 for key, value in self.raw_scores.items()}

    @property
    def high_level_scores(self) -> dict[str, int]:
        scores: dict[str, list[int]] = {domain: [] for domain in HIGH_LEVEL_SESSION_KEYS}
        for spec in FACET_SPECS:
            scores[spec.domain].append(self.raw_scores[spec.session_key])
        return {
            HIGH_LEVEL_SESSION_KEYS[domain]: round((sum(values) / len(values)) * 5)
            for domain, values in scores.items()
        }


class BigFivePdfParser:
    @staticmethod
    def parse_pdf_bytes(pdf_bytes: bytes) -> ParsedBigFiveFacets:
        try:
            from pypdf import PdfReader
        except ImportError as exc:  # pragma: no cover - covered by dependency contract
            raise BigFivePdfParseError("Для PDF-імпорту потрібна залежність `pypdf`.") from exc

        try:
            reader = PdfReader(BytesIO(pdf_bytes))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:  # noqa: BLE001 - pypdf can raise several parser exceptions
            raise BigFivePdfParseError(f"Не вдалося прочитати PDF: {exc}") from exc

        return BigFivePdfParser.parse_text(text)

    @staticmethod
    def parse_text(text: str) -> ParsedBigFiveFacets:
        normalized_text = BigFivePdfParser._normalize_text(text)
        raw_scores: dict[str, int] = {}
        cursor = 0

        for spec in FACET_SPECS:
            label_match = BigFivePdfParser._find_label(normalized_text, spec.label_uk, cursor)
            if label_match is None:
                raise BigFivePdfParseError(f"Не знайдено фасет '{spec.label_uk}' у PDF.")

            score_match = re.search(r"Бали:\s*(\d{1,2})\s*\(", normalized_text[label_match.end() : label_match.end() + 2500])
            if score_match is None:
                raise BigFivePdfParseError(f"Не знайдено бал для фасета '{spec.label_uk}'.")

            score = int(score_match.group(1))
            if not 0 <= score <= 20:
                raise BigFivePdfParseError(f"Бал фасета '{spec.label_uk}' поза шкалою 0-20: {score}.")

            raw_scores[spec.session_key] = score
            cursor = label_match.end() + score_match.end()

        return ParsedBigFiveFacets(raw_scores=raw_scores)

    @staticmethod
    def _normalize_text(text: str) -> str:
        normalized = unicodedata.normalize("NFKC", text)
        normalized = normalized.replace("ʼ", "'").replace("’", "'").replace("`", "'")
        return re.sub(r"\s+", " ", normalized)

    @staticmethod
    def _find_label(text: str, label: str, cursor: int) -> re.Match[str] | None:
        normalized_label = BigFivePdfParser._normalize_text(label)
        escaped = re.escape(normalized_label)
        escaped = escaped.replace(r"\ ", r"\s+")
        escaped = escaped.replace("'", r"\s*['ʼ’]\s*")
        return re.compile(escaped, flags=re.IGNORECASE).search(text, pos=cursor)
