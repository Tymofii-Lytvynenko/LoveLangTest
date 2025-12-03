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
   
3. Weighting Options:
   Options represent specific Needs priorities.
   Vector: (Safety, Resource, Resonance, Expansion).
"""

from .models import Scenario, ScenarioOption

def get_scenarios() -> list[Scenario]:
    return [
        # --- БЛОК 1: КОНФЛІКТИ ТА БЕЗПЕКА (SAFETY vs RESONANCE) ---
        
        Scenario(
            id="conf_01", question="Тон голосу під час сварки", 
            description="Перевірка на сенсорну чутливість та потребу в емоційній безпеці.",
            options=[
                ScenarioOption("Я можу слухати аргументи, тільки якщо голос спокійний. Крик мене паралізує.", (0.7, 0.0, 0.0, 0.0)),
                ScenarioOption("Емоції — це нормально. Крик показує, що людині не байдуже.", (0.0, 0.0, 0.3, 0.2)),
                ScenarioOption("Мене дратує тон, але я фокусуюсь на словах, щоб перемогти в суперечці.", (0.0, 0.0, 0.5, 0.0))
            ]
        ),
        Scenario(
            id="conf_02", question="Стратегія примирення", 
            description="Як ви відновлюєте зв'язок після розриву?",
            options=[
                ScenarioOption("Мені треба час на самоті (доба+), щоб охолонути.", (0.3, 0.0, -0.2, 0.2)),
                ScenarioOption("Ми маємо обійнятися і запевнити одне одного в любові якнайшвидше.", (0.6, 0.0, 0.2, 0.0)),
                ScenarioOption("Ми маємо проаналізувати ситуацію і домовитись, як уникнути цього в майбутньому.", (0.0, 0.3, 0.5, 0.0))
            ]
        ),
        Scenario(
            id="conf_03", question="Логіка проти Почуттів", 
            description="Класична дилема Resonance vs Safety.",
            options=[
                ScenarioOption("Якщо я правий логічно, партнер має це визнати, навіть якщо це боляче.", (0.0, 0.0, 0.7, 0.0)),
                ScenarioOption("Істина не важлива, якщо вона руйнує наші стосунки. Краще змовчати.", (0.6, 0.0, -0.2, 0.0)),
                ScenarioOption("Я хочу, щоб партнер валідував мої емоції, а не шукав рішення.", (0.4, 0.0, 0.4, 0.0))
            ]
        ),
        Scenario(
            id="conf_04", question="Критика на людях", 
            description="Рівень соціальної безпеки.",
            options=[
                ScenarioOption("Це абсолютна зрада. Ми маємо бути єдиним фронтом.", (0.8, 0.0, 0.0, 0.0)),
                ScenarioOption("Це неприємно, але якщо критика доречна — я прийму її.", (0.0, 0.0, 0.4, 0.0)),
                ScenarioOption("Я переведу це в жарт, мене це не чіпляє.", (0.1, 0.0, 0.0, 0.3))
            ]
        ),
        Scenario(
            id="conf_05", question="Минулі образи", 
            description="Накопичення vs Відпускання.",
            options=[
                ScenarioOption("Я часто згадую старі помилки партнера під час нових сварок.", (0.4, 0.0, 0.0, -0.2)),
                ScenarioOption("Ми вирішили — ми забули. Я не тягну багаж.", (0.0, 0.2, 0.3, 0.2)),
                ScenarioOption("Я пам'ятаю факти, щоб бачити патерни поведінки.", (0.0, 0.0, 0.5, 0.0))
            ]
        ),

        # --- БЛОК 2: РЕСУРС, ПОБУТ ТА ВИКОНАВЧА ФУНКЦІЯ (RESOURCE) ---

        Scenario(
            id="res_01", question="Розподіл бюджету", 
            description="Фінансова безпека vs Спонтанність.",
            options=[
                ScenarioOption("У нас має бути спільний чіткий бюджет і трекінг витрат.", (0.3, 0.5, 0.0, 0.0)),
                ScenarioOption("Головне — щоб вистачало. Я не люблю рахувати копійки.", (0.0, -0.3, 0.0, 0.4)),
                ScenarioOption("Я хочу, щоб партнер взяв на себе фінанси, я в цьому 'плаваю'.", (0.0, 0.8, 0.0, 0.0))
            ]
        ),
        Scenario(
            id="res_02", question="Безлад в домі", 
            description="Чутливість до ентропії (важливо для РДУГ/РАС).",
            options=[
                ScenarioOption("Візуальний шум (розкидані речі) викликає в мене тривогу/агресію.", (0.2, 0.5, 0.0, 0.0)),
                ScenarioOption("Я не помічаю безладу. Це творчий хаос.", (0.0, -0.2, 0.0, 0.3)),
                ScenarioOption("Мені соромно за свій безлад, я хочу, щоб партнер допомагав без докорів.", (0.2, 0.6, 0.0, 0.0))
            ]
        ),
        Scenario(
            id="res_03", question="Планування відпустки", 
            description="Потреба в контролі vs Пригоди.",
            options=[
                ScenarioOption("Я маю знати маршрут, готелі і таймінг за місяць.", (0.5, 0.3, 0.0, -0.3)),
                ScenarioOption("Беремо квитки і рюкзаки, розберемося на місці.", (0.0, -0.2, 0.0, 0.8)),
                ScenarioOption("Ми разом досліджуємо варіанти і складаємо 'гнучкий план'.", (0.1, 0.1, 0.4, 0.2))
            ]
        ),
        Scenario(
            id="res_04", question="Хвороба партнера", 
            description="Стиль піклування (Caregiving).",
            options=[
                ScenarioOption("Я організую ліки, їжу і запис до лікаря (Менеджер).", (0.0, 0.7, 0.0, 0.0)),
                ScenarioOption("Я буду сидіти поруч, тримати за руку і співчувати (Емпат).", (0.3, 0.0, 0.4, 0.0)),
                ScenarioOption("Я гублюся. Сподіваюсь, він/вона скаже чітко, що робити.", (0.0, 0.3, 0.0, 0.0))
            ]
        ),
        Scenario(
            id="res_05", question="Прийняття рішень", 
            description="Decision Fatigue (Втома від рішень).",
            options=[
                ScenarioOption("Я люблю лідирувати і вирішувати за двох.", (0.0, 0.4, 0.0, 0.3)),
                ScenarioOption("Я ненавиджу обирати. Хочу, щоб партнер просто сказав: 'Ми йдемо сюди'.", (0.2, 0.7, 0.0, 0.0)),
                ScenarioOption("Ми маємо досягти консенсусу, навіть якщо це займе 3 години.", (0.0, 0.0, 0.6, 0.0))
            ]
        ),
        
        # --- БЛОК 3: БЛИЗЬКІСТЬ, РЕЗОНАНС ТА СПІЛКУВАННЯ (RESONANCE) ---

        Scenario(
            id="res_deep_01", question="Ідеальний вечір розмов", 
            description="Тип інтелектуального зв'язку.",
            options=[
                ScenarioOption("Дебати про політику, науку чи філософію до ранку.", (0.0, 0.0, 0.8, 0.0)),
                ScenarioOption("Обговорення наших почуттів, мрій та стосунків.", (0.2, 0.0, 0.6, 0.0)),
                ScenarioOption("Просто бути поруч мовчки, кожен у своєму гаджеті (Parallel Play).", (0.3, 0.0, 0.2, 0.0))
            ]
        ),
        Scenario(
            id="res_deep_02", question="Спільні хобі", 
            description="Важливість спільних інтересів.",
            options=[
                ScenarioOption("Ми зобов'язані мати спільні пристрасті, інакше про що говорити?", (0.2, 0.0, 0.6, 0.0)),
                ScenarioOption("Він любить футбол, я оперу. Це ок, ми різні.", (0.0, 0.0, -0.2, 0.5)),
                ScenarioOption("Я спробую полюбити його хобі заради нього.", (0.4, 0.0, 0.2, 0.0))
            ]
        ),
        Scenario(
            id="res_deep_03", question="Гумор", 
            description="Синхронізація почуття гумору.",
            options=[
                ScenarioOption("Якщо ми не сміємось з одних мемів, це провал.", (0.0, 0.0, 0.7, 0.0)),
                ScenarioOption("Головне, щоб жарти не були образливими.", (0.4, 0.0, 0.0, 0.0)),
                ScenarioOption("Я люблю чорний/специфічний гумор, партнер має витримувати це.", (0.0, 0.0, 0.3, 0.3))
            ]
        ),
        Scenario(
            id="res_deep_04", question="Емоційна підтримка (Good News)", 
            description="Capitalization (реакція на успіх).",
            options=[
                ScenarioOption("Партнер має стрибати від радості разом зі мною.", (0.0, 0.0, 0.6, 0.2)),
                ScenarioOption("Достатньо простого 'Молодець'.", (0.2, 0.0, 0.0, 0.0)),
                ScenarioOption("Він має допомогти мені продумати наступні кроки кар'єри.", (0.0, 0.4, 0.2, 0.0))
            ]
        ),
        
        # --- БЛОК 4: ЕКСПАНСІЯ, НОВИЗНА ТА АВТОНОМІЯ (EXPANSION) ---

        Scenario(
            id="exp_01", question="Рутина", 
            description="Потреба в дофаміні (важливо для High Openness/ADHD).",
            options=[
                ScenarioOption("Стабільність — це щастя. Я люблю день бабака.", (0.6, 0.0, 0.0, -0.5)),
                ScenarioOption("Я починаю в'янути/депресувати без нових вражень.", (0.0, 0.0, 0.0, 0.8)),
                ScenarioOption("Рутина ок, якщо ми вносимо мікро-зміни (нова їжа, секс).", (0.2, 0.0, 0.2, 0.3))
            ]
        ),
        Scenario(
            id="exp_02", question="Соціальна активність", 
            description="Екстраверсія та соціальний ресурс.",
            options=[
                ScenarioOption("Ми маємо ходити в гості/на вечірки щотижня.", (0.0, 0.0, 0.0, 0.6)),
                ScenarioOption("Мій дім — моя фортеця. Гості тільки на свята.", (0.4, 0.0, 0.0, -0.2)),
                ScenarioOption("Я йду тусуватися сам, партнер залишається вдома (або навпаки).", (0.0, 0.0, 0.0, 0.5))
            ]
        ),
        Scenario(
            id="exp_03", question="Кар'єрний ризик", 
            description="Безпека проти Росту.",
            options=[
                ScenarioOption("Я кину стабільну роботу заради мрії/стартапу.", (0.0, -0.3, 0.0, 0.8)),
                ScenarioOption("Краще синиця в руках. Іпотека сама себе не виплатить.", (0.5, 0.4, 0.0, -0.3)),
                ScenarioOption("Ризик можливий, якщо у нас є фінансова подушка.", (0.2, 0.3, 0.0, 0.2))
            ]
        ),
        Scenario(
            id="exp_04", question="Особисті кордони (Паролі)", 
            description="Прозорість проти Приватності.",
            options=[
                ScenarioOption("У нас спільні паролі від усього. Секретів немає.", (0.6, 0.0, 0.0, -0.4)),
                ScenarioOption("Мій телефон — моя приватна територія. Не чіпати.", (0.0, 0.0, 0.0, 0.5)),
                ScenarioOption("Я дам пароль, якщо попросять, але перевірки мене ображають.", (0.2, 0.0, 0.3, 0.1))
            ]
        ),
        Scenario(
            id="exp_05", question="Відпустка нарізно", 
            description="Автономія.",
            options=[
                ScenarioOption("Це початок кінця стосунків.", (0.5, 0.0, 0.0, -0.5)),
                ScenarioOption("Це чудово! Можна скучити одне за одним.", (0.0, 0.0, 0.0, 0.7)),
                ScenarioOption("Тільки якщо це пов'язано з хобі/роботою, а не просто відпочинок.", (0.2, 0.0, 0.2, 0.0))
            ]
        ),

        # --- БЛОК 5: ЕРОС ТА ТІЛЕСНІСТЬ (EROS / INTIMACY) ---
        # Ці питання впливають на S/R/M/E, тому вони важливі навіть при наявності ErosComponent

        Scenario(
            id="sex_01", question="Ініціатива в сексі", 
            description="Динаміка бажання.",
            options=[
                ScenarioOption("Мені важливо відчувати себе бажаним (партнер ініціює).", (0.4, 0.0, 0.2, 0.0)),
                ScenarioOption("Я люблю завойовувати і спокушати.", (0.0, 0.0, 0.0, 0.5)),
                ScenarioOption("Це має статися само собою, без планування.", (0.0, 0.0, 0.3, 0.2))
            ]
        ),
        Scenario(
            id="sex_02", question="Експерименти", 
            description="Novelty in Bed.",
            options=[
                ScenarioOption("Я знаю, що мені подобається. Навіщо змінювати те, що працює?", (0.4, 0.0, 0.0, -0.2)),
                ScenarioOption("Я хочу спробувати все (іграшки, рольові ігри, місця).", (0.0, 0.0, 0.0, 0.8)),
                ScenarioOption("Я готовий до нового, якщо партнер повільно введе мене в це.", (0.2, 0.0, 0.3, 0.2))
            ]
        ),
        Scenario(
            id="sex_03", question="Після сексу", 
            description="Aftercare needs.",
            options=[
                ScenarioOption("Обійми, розмови, ніжність (Aftercare).", (0.5, 0.0, 0.3, 0.0)),
                ScenarioOption("Душ, їжа або сон. Енергія витрачена.", (0.0, 0.2, 0.0, 0.0)),
                ScenarioOption("Приплив енергії, хочеться щось робити.", (0.0, 0.0, 0.0, 0.4))
            ]
        ),
        Scenario(
            id="sex_04", question="Відмова", 
            description="Rejection Sensitivity.",
            options=[
                ScenarioOption("Якщо мені відмовляють, я відчуваю себе огидним/нелюбом.", (0.7, 0.0, 0.0, 0.0)),
                ScenarioOption("Ні то ні. Спробуємо завтра.", (0.0, 0.0, 0.2, 0.0)),
                ScenarioOption("Я намагаюся переконати партнера або ображаюсь.", (0.0, 0.0, 0.0, 0.3))
            ]
        ),

        # --- БЛОК 6: НЕЙРОВІДМІННІСТЬ (ADHD/ASD SPECIFIC) ---
        
        Scenario(
            id="nd_01", question="Тілесне подвоєння (Body Doubling)", 
            description="Потреба в пасивній присутності для продуктивності.",
            options=[
                ScenarioOption("Мені легше працювати/прибирати, коли партнер просто сидить поруч.", (0.0, 0.7, 0.3, 0.0)),
                ScenarioOption("Коли хтось дивиться, як я працюю, я не можу нічого робити.", (0.3, 0.0, 0.0, 0.2)),
                ScenarioOption("Мені байдуже, я фокусуюсь будь-де.", (0.0, 0.1, 0.0, 0.0))
            ]
        ),
        Scenario(
            id="nd_02", question="Сенсорне перевантаження", 
            description="Реакція на overstimulation.",
            options=[
                ScenarioOption("Коли я перевантажений, мене не можна чіпати (No touch).", (0.5, 0.0, 0.0, 0.0)),
                ScenarioOption("Мені потрібен 'глибокий тиск' (міцні обійми), щоб заземлитися.", (0.4, 0.0, 0.4, 0.0)),
                ScenarioOption("Мені треба відволіктися (відеоігри, скролінг).", (0.0, 0.0, 0.0, 0.3))
            ]
        ),
        Scenario(
            id="nd_03", question="Забудькуватість", 
            description="Реакція на помилки пам'яті.",
            options=[
                ScenarioOption("Якщо партнер забув про важливу дату — це означає, що він мене не любить.", (0.6, 0.0, 0.0, 0.0)),
                ScenarioOption("Я ставлю нагадування. Ми просто люди.", (0.0, 0.5, 0.0, 0.0)),
                ScenarioOption("Ми сміємося з цього. Хаос — це частина життя.", (0.0, 0.0, 0.3, 0.2))
            ]
        ),
        Scenario(
            id="nd_04", question="Інфодампінг (Info-dumping)", 
            description="Спосіб вираження любові через ділення фактами.",
            options=[
                ScenarioOption("Я люблю, коли мені 40 хвилин розповідають про лор 'Warhammer' / потяги.", (0.0, 0.0, 0.8, 0.0)),
                ScenarioOption("Це втомлює. Краще поговоримо про нас.", (0.0, 0.0, -0.3, 0.0)),
                ScenarioOption("Я слухаю з ввічливості, але не запам'ятовую.", (0.2, 0.0, 0.0, 0.0))
            ]
        )
    ]

def get_max_possible_scores() -> tuple[float, float, float, float]:
    """
    Динамічно обчислює теоретичний максимум балів для кожної категорії.
    Проходить по всіх питаннях і сумує максимальні ваги опцій.
    Повертає: (Max_Safety, Max_Resource, Max_Resonance, Max_Expansion)
    """
    scenarios = get_scenarios()
    max_s, max_r, max_m, max_e = 0.0, 0.0, 0.0, 0.0
    
    for sc in scenarios:
        # Для кожного питання шукаємо "найжирнішу" відповідь у кожній категорії
        # Наприклад, якщо в питанні є опції з Safety: 0.5, 0.0, 0.8 -> ми додаємо 0.8 до максимуму
        # Це працює, бо в радіо-кнопках можна обрати лише одну опцію.
        
        # weights[0] - Safety
        max_s += max(opt.weights[0] for opt in sc.options)
        # weights[1] - Resource
        max_r += max(opt.weights[1] for opt in sc.options)
        # weights[2] - Resonance
        max_m += max(opt.weights[2] for opt in sc.options)
        # weights[3] - Expansion
        max_e += max(opt.weights[3] for opt in sc.options)
        
    return max_s, max_r, max_m, max_e