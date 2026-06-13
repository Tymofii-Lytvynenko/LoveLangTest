from pathlib import Path

from conftest import write_json
from src.question_bank import load_question_bank_from_path
from src.services.question_bank_quality import QuestionBankQualityGate


def _valid_strict_needs_bank() -> dict:
    return {
        "metadata": {
            "bank_id": "strict-needs",
            "version": "0.1.0",
            "module": "needs",
            "authoring_instructions": "Generate balanced scenario questions grounded in CRNAS theories.",
            "vector_labels": ["safety", "resource", "resonance", "expansion"],
        },
        "questions": [
            {
                "id": "safety_01",
                "family": "absolute",
                "dimension": "safety",
                "response_type": "single_choice",
                "question": "Після важкого дня наскільки вам потрібні тиша й спокій для відновлення?",
                "description": "Потреба у тиші після перевантаження.",
                "options": [
                    {"id": "opt_1", "text": "Майже не потрібно.", "vector": [0.0, 0.0, 0.0, 0.0]},
                    {"id": "opt_2", "text": "Іноді корисно.", "vector": [0.33, 0.0, 0.0, 0.0]},
                    {"id": "opt_3", "text": "Важливо.", "vector": [0.66, 0.0, 0.0, 0.0]},
                    {"id": "opt_4", "text": "Критично.", "vector": [1.0, 0.0, 0.0, 0.0]},
                ],
            },
            {
                "id": "resource_01",
                "family": "absolute",
                "dimension": "resource",
                "response_type": "single_choice",
                "question": "Коли накопичуються справи, наскільки вам потрібен чіткий план і список?",
                "description": "Потреба у плануванні побуту.",
                "options": [
                    {"id": "opt_1", "text": "Майже не потрібно.", "vector": [0.0, 0.0, 0.0, 0.0]},
                    {"id": "opt_2", "text": "Іноді корисно.", "vector": [0.0, 0.33, 0.0, 0.0]},
                    {"id": "opt_3", "text": "Важливо.", "vector": [0.0, 0.66, 0.0, 0.0]},
                    {"id": "opt_4", "text": "Критично.", "vector": [0.0, 1.0, 0.0, 0.0]},
                ],
            },
            {
                "id": "resonance_01",
                "family": "absolute",
                "dimension": "resonance",
                "response_type": "single_choice",
                "question": "Коли ви засмучені, наскільки вам потрібне глибоке емоційне розуміння від партнера?",
                "description": "Потреба в емоційній валідації.",
                "options": [
                    {"id": "opt_1", "text": "Майже не потрібно.", "vector": [0.0, 0.0, 0.0, 0.0]},
                    {"id": "opt_2", "text": "Іноді корисно.", "vector": [0.0, 0.0, 0.33, 0.0]},
                    {"id": "opt_3", "text": "Важливо.", "vector": [0.0, 0.0, 0.66, 0.0]},
                    {"id": "opt_4", "text": "Критично.", "vector": [0.0, 0.0, 1.0, 0.0]},
                ],
            },
            {
                "id": "expansion_01",
                "family": "absolute",
                "dimension": "expansion",
                "response_type": "single_choice",
                "question": "Наскільки вам важливі спільні нові відкриття та експерименти?",
                "description": "Потреба у новизні та русі вперед.",
                "options": [
                    {"id": "opt_1", "text": "Майже не потрібно.", "vector": [0.0, 0.0, 0.0, 0.0]},
                    {"id": "opt_2", "text": "Іноді корисно.", "vector": [0.0, 0.0, 0.0, 0.33]},
                    {"id": "opt_3", "text": "Важливо.", "vector": [0.0, 0.0, 0.0, 0.66]},
                    {"id": "opt_4", "text": "Критично.", "vector": [0.0, 0.0, 0.0, 1.0]},
                ],
            },
            {
                "id": "priority_01",
                "family": "priority",
                "response_type": "best_worst",
                "question": "Що для вас найважливіше після сварки, а що найменш критично?",
                "description": "Пріоритети відновлення після конфлікту.",
                "options": [
                    {"id": "opt_safety", "text": "Повернути спокій і безпеку.", "vector": [1.0, 0.0, 0.0, 0.0]},
                    {"id": "opt_resource", "text": "Розподілити логістику.", "vector": [0.0, 1.0, 0.0, 0.0]},
                    {"id": "opt_resonance", "text": "Обговорити переживання.", "vector": [0.0, 0.0, 1.0, 0.0]},
                    {"id": "opt_expansion", "text": "Спробувати щось нове.", "vector": [0.0, 0.0, 0.0, 1.0]},
                ],
            },
            {
                "id": "priority_02",
                "family": "priority",
                "response_type": "best_worst",
                "question": "Як виглядає найкращий спільний вечір для вас?",
                "description": "Пріоритети спільного дозвілля.",
                "options": [
                    {"id": "opt_safety", "text": "Спокійний вечір вдома.", "vector": [1.0, 0.0, 0.0, 0.0]},
                    {"id": "opt_resource", "text": "Організація побутових справ.", "vector": [0.0, 1.0, 0.0, 0.0]},
                    {"id": "opt_resonance", "text": "Глибока розмова про почуття.", "vector": [0.0, 0.0, 1.0, 0.0]},
                    {"id": "opt_expansion", "text": "Спонтанна поїздка в нове місце.", "vector": [0.0, 0.0, 0.0, 1.0]},
                ],
            },
            {
                "id": "priority_03",
                "family": "priority",
                "response_type": "best_worst",
                "question": "Що ви очікуєте від партнера під час життєвих змін?",
                "description": "Пріоритети підтримки під час змін.",
                "options": [
                    {"id": "opt_safety", "text": "Запевнення у стабільності зв'язку.", "vector": [1.0, 0.0, 0.0, 0.0]},
                    {"id": "opt_resource", "text": "Допомога з щоденними задачами.", "vector": [0.0, 1.0, 0.0, 0.0]},
                    {"id": "opt_resonance", "text": "Розуміння моєї тривоги.", "vector": [0.0, 0.0, 1.0, 0.0]},
                    {"id": "opt_expansion", "text": "Разом рухатися до нових цілей.", "vector": [0.0, 0.0, 0.0, 1.0]},
                ],
            },
            {
                "id": "priority_04",
                "family": "priority",
                "response_type": "best_worst",
                "question": "Який аспект побуту є найважливішим для вас?",
                "description": "Пріоритети побутової взаємодії.",
                "options": [
                    {"id": "opt_safety", "text": "Передбачуваність і тиша.", "vector": [1.0, 0.0, 0.0, 0.0]},
                    {"id": "opt_resource", "text": "Ясний розподіл обов'язків.", "vector": [0.0, 1.0, 0.0, 0.0]},
                    {"id": "opt_resonance", "text": "Емпатія та підтримка.", "vector": [0.0, 0.0, 1.0, 0.0]},
                    {"id": "opt_expansion", "text": "Експерименти на кухні.", "vector": [0.0, 0.0, 0.0, 1.0]},
                ],
            },
        ],
    }


def test_quality_gate_accepts_balanced_strict_needs_bank(tmp_path: Path) -> None:
    path = write_json(tmp_path, "strict_needs.json", _valid_strict_needs_bank())
    bank = load_question_bank_from_path(path)

    report = QuestionBankQualityGate.evaluate(bank, expected_question_count=8, strict_content_checks=True)

    assert report.passed, report.errors


def test_quality_gate_rejects_pseudoscientific_terms(tmp_path: Path) -> None:
    payload = _valid_strict_needs_bank()
    payload["questions"][0]["question"] = "Який знак зодіаку найкраще знижує вашу тривогу?"
    path = write_json(tmp_path, "invalid_needs.json", payload)
    bank = load_question_bank_from_path(path)

    report = QuestionBankQualityGate.evaluate(bank, expected_question_count=8, strict_content_checks=True)

    assert not report.passed
    assert any("banned" in error.lower() or "pseudo" in error.lower() for error in report.errors)


def test_quality_gate_rejects_non_ukrainian_user_facing_text(tmp_path: Path) -> None:
    payload = _valid_strict_needs_bank()
    payload["questions"][0]["description"] = "This item checks recovery after conflict."
    path = write_json(tmp_path, "english_needs.json", payload)
    bank = load_question_bank_from_path(path)

    report = QuestionBankQualityGate.evaluate(bank, expected_question_count=8, strict_content_checks=True)

    assert not report.passed
    assert any("ukrainian" in error.lower() or "latin" in error.lower() for error in report.errors)


def test_quality_gate_rejects_unbalanced_shadow_bank(tmp_path: Path) -> None:
    payload = {
        "metadata": {
            "bank_id": "strict-shadow",
            "version": "0.1.0",
            "module": "shadow",
            "authoring_instructions": "Generate attachment questions.",
            "vector_labels": ["secure", "anxious", "avoidant", "disorganized"],
        },
        "questions": [
            {
                "id": "att_01",
                "question": "Що ви робите після конфлікту?",
                "description": "Перевірка на відновлення зв'язку.",
                "options": [
                    {"id": "opt_1", "text": "Шукаю контакт.", "vector": [1.0, 0.0, 0.0, 0.0]},
                    {"id": "opt_2", "text": "Панічно пишу багато повідомлень.", "vector": [0.0, 1.0, 0.0, 0.0]},
                    {"id": "opt_3", "text": "Віддаляюсь і зникаю.", "vector": [0.0, 0.0, 1.0, 0.0]},
                    {"id": "opt_4", "text": "Теж віддаляюсь і зникаю.", "vector": [0.0, 0.0, 1.0, 0.0]},
                ],
            },
            {
                "id": "att_02",
                "question": "Як ви реагуєте на дистанцію?",
                "description": "Перевірка на близькість та страх.",
                "options": [
                    {"id": "opt_1", "text": "Говорю прямо.", "vector": [1.0, 0.0, 0.0, 0.0]},
                    {"id": "opt_2", "text": "Тривожусь.", "vector": [0.0, 1.0, 0.0, 0.0]},
                    {"id": "opt_3", "text": "Відключаюсь.", "vector": [0.0, 0.0, 1.0, 0.0]},
                    {"id": "opt_4", "text": "Заморожуюсь, але хочу близькості.", "vector": [0.0, 0.0, 0.0, 0.5]},
                ],
            },
            {
                "id": "att_03",
                "question": "Що відчуваєте у напруженні?",
                "description": "Перевірка на стрес.",
                "options": [
                    {"id": "opt_1", "text": "Шукаю ремонт зв'язку.", "vector": [1.0, 0.0, 0.0, 0.0]},
                    {"id": "opt_2", "text": "Боюсь, що мене покинуть.", "vector": [0.0, 1.0, 0.0, 0.0]},
                    {"id": "opt_3", "text": "Стаю холодним.", "vector": [0.0, 0.0, 1.0, 0.0]},
                    {"id": "opt_4", "text": "Плутаюсь між втечею і потягом.", "vector": [0.0, 0.0, 0.0, 0.0]},
                ],
            },
            {
                "id": "att_04",
                "question": "Як для вас виглядає відновлення зв'язку після розриву?",
                "description": "Перевірка на відновлення зв'язку.",
                "options": [
                    {"id": "opt_1", "text": "Можна повернутись у контакт.", "vector": [1.0, 0.0, 0.0, 0.0]},
                    {"id": "opt_2", "text": "Потрібно більше підтверджень.", "vector": [0.0, 1.0, 0.0, 0.0]},
                    {"id": "opt_3", "text": "Хочу більше дистанції.", "vector": [0.0, 0.0, 1.0, 0.0]},
                    {"id": "opt_4", "text": "Не знаю, чого хочу.", "vector": [0.0, 0.0, 0.0, 0.0]},
                ],
            },
        ],
    }
    path = write_json(tmp_path, "invalid_shadow.json", payload)
    bank = load_question_bank_from_path(path)

    report = QuestionBankQualityGate.evaluate(bank, expected_question_count=4, strict_content_checks=True)

    assert not report.passed
    assert any("one-hot" in error.lower() or "equally" in error.lower() for error in report.errors)
