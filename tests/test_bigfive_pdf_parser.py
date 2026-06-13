import pytest

from src.services.bigfive_pdf_parser import BigFivePdfParseError, BigFivePdfParser, FACET_SPECS


def _sample_bigfive_text() -> str:
    scores = list(range(1, 21)) + list(range(1, 11))
    parts: list[str] = []
    for spec, score in zip(FACET_SPECS, scores):
        parts.append(spec.label_uk)
        if spec.label_uk == "Пригодницькість":
            parts.append("20 18 16 14 12 10 8 6 4 2 0 Уява Художні інтереси Емоційність")
        parts.append(f"Бали: {score} (neutral)")
        parts.append("Опис фасета.")
    return "\n".join(parts)


def test_parse_text_extracts_all_30_facets_with_chart_interruption() -> None:
    parsed = BigFivePdfParser.parse_text(_sample_bigfive_text())

    assert len(parsed.raw_scores) == 30
    assert parsed.raw_scores["facet_neur_anxiety"] == 1
    assert parsed.raw_scores["facet_open_actions"] == 16
    assert parsed.raw_scores["facet_cons_deliberation"] == 10
    assert parsed.normalized_scores["facet_open_actions"] == 0.8


def test_parse_text_builds_high_level_scores_from_facet_averages() -> None:
    parsed = BigFivePdfParser.parse_text(_sample_bigfive_text())

    assert parsed.high_level_scores == {
        "psycho_n": 18,
        "psycho_e": 48,
        "psycho_o": 78,
        "psycho_a": 41,
        "psycho_c": 38,
    }


def test_parse_text_rejects_incomplete_pdf_text() -> None:
    with pytest.raises(BigFivePdfParseError, match="Не знайдено фасет"):
        BigFivePdfParser.parse_text("Тривога\nБали: 17 (high)")
