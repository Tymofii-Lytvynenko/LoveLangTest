from pathlib import Path

from conftest import write_json
from src.question_bank import load_question_bank_from_path
from src.services.question_bank_quality import QuestionBankQualityGate


def _valid_generated_needs_bank() -> dict:
    return {
        "metadata": {
            "bank_id": "generated-needs",
            "version": "0.1.0",
            "module": "needs",
            "authoring_instructions": "Generate balanced scenario questions grounded in CRNAS theories.",
            "vector_labels": ["safety", "resource", "resonance", "expansion"],
        },
        "questions": [
            {
                "id": "safety_01",
                "question": "Після перевантаженого дня партнер хоче важку розмову. Що для вас критично?",
                "description": "Перевірка на передбачуваність, сенсорне навантаження та регуляцію.",
                "options": [
                    {"id": "opt_1", "text": "Спершу тиша і пауза, потім спокійна розмова.", "vector": [0.8, 0.1, 0.0, -0.1]},
                    {"id": "opt_2", "text": "Можемо говорити одразу, якщо є чіткий план розмови.", "vector": [0.4, 0.4, 0.1, 0.0]},
                    {"id": "opt_3", "text": "Краще змінити обстановку і прогулятись, щоб не застрягти.", "vector": [0.1, 0.0, 0.1, 0.7]},
                ],
            },
            {
                "id": "resource_01",
                "question": "Коли накопичуються дрібні побутові задачі, що найбільше допомагає?",
                "description": "Перевірка на зовнішні опори, логістику та побутове тертя.",
                "options": [
                    {"id": "opt_1", "text": "Спільний список і нагадування з розбиттям задач.", "vector": [0.1, 0.8, 0.0, -0.1]},
                    {"id": "opt_2", "text": "Партнер сам помічає, де мене підстрахувати, без хаосу.", "vector": [0.2, 0.6, 0.3, 0.0]},
                    {"id": "opt_3", "text": "Краще зробити все в останній момент і перетворити це на челендж.", "vector": [-0.2, -0.3, 0.0, 0.8]},
                ],
            },
            {
                "id": "resonance_01",
                "question": "Після неприємної робочої ситуації який відгук партнера найбільш точний для вас?",
                "description": "Перевірка на валідацію, спільний сенс і формат слухання.",
                "options": [
                    {"id": "opt_1", "text": "Щоб мене спершу вислухали і віддзеркалили, що я відчуваю.", "vector": [0.2, 0.0, 0.8, -0.1]},
                    {"id": "opt_2", "text": "Щоб допомогли з конкретним наступним кроком або листом.", "vector": [0.1, 0.6, 0.1, 0.0]},
                    {"id": "opt_3", "text": "Щоб ми обговорили, які нові висновки чи ідеї з цього можна взяти.", "vector": [0.0, 0.0, 0.4, 0.7]},
                ],
            },
            {
                "id": "expansion_01",
                "question": "Як ви ставитесь до нових спільних ритуалів або інтересів?",
                "description": "Перевірка на новизну, експерименти та безпечний темп змін.",
                "options": [
                    {"id": "opt_1", "text": "Мені потрібен повільний і передбачуваний темп змін.", "vector": [0.6, 0.1, 0.0, -0.2]},
                    {"id": "opt_2", "text": "Люблю пробувати нове, якщо є простір повернутись назад без тиску.", "vector": [0.1, 0.0, 0.2, 0.8]},
                    {"id": "opt_3", "text": "Класно, коли партнер сам приносить нові ідеї та драйв.", "vector": [0.0, 0.1, 0.1, 0.7]},
                ],
            },
            {
                "id": "safety_02",
                "question": "Що найсильніше знижує напругу після сварки?",
                "description": "Перевірка на відновлення зв'язку, тон і зниження відчуття загрози.",
                "options": [
                    {"id": "opt_1", "text": "Чути спокійний тон і чітке запевнення, що зв'язок не зникає.", "vector": [0.9, 0.0, 0.1, -0.1]},
                    {"id": "opt_2", "text": "Розібрати по кроках, що зламалось у процесі.", "vector": [0.2, 0.6, 0.2, 0.0]},
                    {"id": "opt_3", "text": "Змінити сцену, виїхати кудись і перезапустити настрій.", "vector": [0.0, 0.0, 0.1, 0.8]},
                ],
            },
            {
                "id": "resource_02",
                "question": "Як виглядає найбільш сумісний розподіл відповідальності вдома?",
                "description": "Перевірка на структуру, передбачуваність і побутову підтримку.",
                "options": [
                    {"id": "opt_1", "text": "Коли ролі узгоджені наперед і не треба все щоразу домовлятись з нуля.", "vector": [0.3, 0.8, 0.0, -0.1]},
                    {"id": "opt_2", "text": "Коли ми часто синхронізуємось і перерозподіляємо задачі вголос.", "vector": [0.1, 0.5, 0.4, 0.0]},
                    {"id": "opt_3", "text": "Коли можна імпровізувати щотижня і міняти ролі під настрій.", "vector": [-0.1, -0.2, 0.1, 0.8]},
                ],
            },
            {
                "id": "resonance_02",
                "question": "Що для вас означає бути по-справжньому почутим?",
                "description": "Перевірка на синхронізацію, спільне значення і формат контакту.",
                "options": [
                    {"id": "opt_1", "text": "Коли партнер уточнює сенс моїх слів, а не вгадує підтекст.", "vector": [0.2, 0.0, 0.8, 0.0]},
                    {"id": "opt_2", "text": "Коли мої потреби відразу перетворюються на план підтримки.", "vector": [0.1, 0.7, 0.2, 0.0]},
                    {"id": "opt_3", "text": "Коли розмова виростає в нову спільну ідею або досвід.", "vector": [0.0, 0.0, 0.4, 0.7]},
                ],
            },
            {
                "id": "expansion_02",
                "question": "Як ви переживаєте спонтанні запрошення або зміни плану?",
                "description": "Перевірка на конфлікт між новизною, відновленням і передбачуваністю.",
                "options": [
                    {"id": "opt_1", "text": "Мені легше, коли зміни мінімальні й є час переналаштуватись.", "vector": [0.7, 0.1, 0.0, -0.2]},
                    {"id": "opt_2", "text": "Можу підхопити імпровізацію, якщо партнер бере частину логістики на себе.", "vector": [0.1, 0.5, 0.1, 0.6]},
                    {"id": "opt_3", "text": "Спонтанність сама по собі мене заряджає і додає інтересу.", "vector": [0.0, -0.1, 0.0, 0.9]},
                ],
            },
        ],
    }


def test_quality_gate_accepts_balanced_generated_needs_bank(tmp_path: Path) -> None:
    path = write_json(tmp_path, "generated_needs.json", _valid_generated_needs_bank())
    bank = load_question_bank_from_path(path)

    report = QuestionBankQualityGate.evaluate(bank, expected_question_count=8, strict_generated_bank=True)

    assert report.passed, report.errors


def test_quality_gate_rejects_pseudoscientific_terms(tmp_path: Path) -> None:
    payload = _valid_generated_needs_bank()
    payload["questions"][0]["question"] = "Який знак зодіаку найкраще знижує вашу тривогу?"
    path = write_json(tmp_path, "invalid_needs.json", payload)
    bank = load_question_bank_from_path(path)

    report = QuestionBankQualityGate.evaluate(bank, expected_question_count=8, strict_generated_bank=True)

    assert not report.passed
    assert any("banned" in error.lower() or "pseudo" in error.lower() for error in report.errors)


def test_quality_gate_rejects_non_ukrainian_user_facing_text(tmp_path: Path) -> None:
    payload = _valid_generated_needs_bank()
    payload["questions"][0]["description"] = "This item checks recovery after conflict."
    path = write_json(tmp_path, "english_needs.json", payload)
    bank = load_question_bank_from_path(path)

    report = QuestionBankQualityGate.evaluate(bank, expected_question_count=8, strict_generated_bank=True)

    assert not report.passed
    assert any("ukrainian" in error.lower() or "latin" in error.lower() for error in report.errors)


def test_quality_gate_rejects_unbalanced_shadow_bank(tmp_path: Path) -> None:
    payload = {
        "metadata": {
            "bank_id": "generated-shadow",
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

    report = QuestionBankQualityGate.evaluate(bank, expected_question_count=4, strict_generated_bank=True)

    assert not report.passed
    assert any("one-hot" in error.lower() or "equally" in error.lower() for error in report.errors)
