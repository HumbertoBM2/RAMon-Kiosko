"""
data/places_content.py
Contenido multilingüe de cada lugar turístico de Monterrey.
Para agregar idiomas: añadir clave con código ISO 639-1 en cada bloque.
"""
from config import PLACES

# ─────────────────────────────────────────────────────────────────────────────
# TEXTOS DEL SISTEMA (UI + narración de RAMon)
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_TEXTS: dict[str, dict] = {
    # ── Pantalla de bienvenida ─────────────────────────────────────────────
    "welcome_title": {
        "en": "Wave to Start!",
        "es": "¡Saluda para Comenzar!",
        "fr": "Faites signe pour commencer!",
        "ja": "手を振ってスタート！",
        "ko": "손을 흔들어 시작하세요!",
        "pl": "Pomachaj, aby zacząć!",
        "sv": "Vinka för att börja!",
        "uk": "Помахайте, щоб почати!",
    },
    "welcome_subtitle": {
        "en": "Show your open hand (5 fingers) for 2 seconds",
        "es": "Muestra tu mano abierta (5 dedos) por 2 segundos",
        "fr": "Montrez votre main ouverte (5 doigts) pendant 2 secondes",
        "ja": "手のひらを2秒間見せてください（5本指）",
        "ko": "손바닥을 2초간 보여주세요 (손가락 5개)",
        "pl": "Pokaż otwartą dłoń (5 palców) przez 2 sekundy",
        "sv": "Visa din öppna hand (5 fingrar) i 2 sekunder",
        "uk": "Покажіть відкриту долоню (5 пальців) протягом 2 секунд",
    },

    # ── Saludo de RAMon ────────────────────────────────────────────────────
    "ramon_greeting": {
        "en": "Hello! I'm RAMon, your guide to Nuevo León! "
              "Please choose your language to continue.",
        "es": "¡Hola! ¡Soy RAMon, tu guía de Nuevo León! "
              "Por favor elige tu idioma para continuar.",
        "fr": "Bonjour! Je suis RAMon, votre guide du Nuevo León! "
              "Choisissez votre langue pour continuer.",
        "ja": "こんにちは！ヌエボレオン観光ガイド、RAMonです！"
              "言語を選んでください。",
        "ko": "안녕하세요! 저는 누에보레온 가이드 RAMon입니다! "
              "언어를 선택해주세요.",
        "pl": "Hej! Jestem RAMon, twój przewodnik po Nuevo León! "
              "Wybierz swój język.",
        "sv": "Hej! Jag är RAMon, din guide till Nuevo León! "
              "Välj ditt språk.",
        "uk": "Привіт! Я RAMon, ваш гід по Нуево Леон! "
              "Виберіть свою мову.",
    },

    # ── Selección de idioma ────────────────────────────────────────────────
    "language_instruction": {
        "en": "Hold up the number of fingers for your language:",
        "es": "Levanta los dedos según tu idioma:",
        "fr": "Levez les doigts pour votre langue:",
        "ja": "言語の番号の指を立ててください：",
        "ko": "언어 번호만큼 손가락을 드세요:",
        "pl": "Pokaż liczbę palców dla swojego języka:",
        "sv": "Håll upp fingrar för ditt språk:",
        "uk": "Підніміть пальці за номером мови:",
    },

    # ── Intro del recorrido ────────────────────────────────────────────────
    "tour_intro": {
        "en": "Welcome to Monterrey, a city full of culture, history, and passion! "
              "I'll take you on a tour of 4 amazing places. "
              "If you visit all of them, there'll be a special prize! "
              "Use your fingers to choose where to go.",
        "es": "¡Bienvenido a Monterrey, una ciudad llena de cultura, historia y pasión! "
              "Te llevaré a conocer 4 lugares increíbles. "
              "¡Si los visitas todos, habrá un premio especial!  "
              "Usa tus dedos para elegir a dónde ir.",
        "fr": "Bienvenue à Monterrey, une ville pleine de culture, d'histoire et de passion! "
              "Je vous emmène visiter 4 endroits incroyables. "
              "Si vous les visitez tous, il y aura un prix spécial! ",
        "ja": "情熱と文化の街、モンテレーへようこそ！"
              "4か所の素晴らしい場所をご案内します。"
              "全部訪れると特別なプレゼントがあります！",
        "ko": "문화와 역사의 도시 몬테레이에 오신 것을 환영합니다! "
              "4곳의 놀라운 장소를 안내해 드립니다. "
              "모든 곳을 방문하면 특별한 상품이 있습니다! ",
        "pl": "Witaj w Monterrey, mieście pełnym kultury, historii i pasji! "
              "Zabiorę cię do 4 niesamowitych miejsc. "
              "Jeśli odwiedzisz je wszystkie, czeka cię specjalna nagroda! ",
        "sv": "Välkommen till Monterrey, en stad full av kultur, historia och passion! "
              "Jag tar dig med på en tur till 4 fantastiska platser. "
              "Om du besöker dem alla väntar ett specialpris! ",
        "uk": "Ласкаво просимо до Монтеррей, міста, сповненого культури, історії та пристрасті! "
              "Я проведу вас 4 дивовижними місцями. "
              "Якщо відвідаєте все — чекає особливий приз! ",
    },

    # ── Menú de lugares ────────────────────────────────────────────────────
    "places_menu_title": {
        "en": "Choose a Place to Visit",
        "es": "Elige un Lugar para Visitar",
        "fr": "Choisissez un Endroit à Visiter",
        "ja": "訪れる場所を選んでください",
        "ko": "방문할 장소를 선택하세요",
        "pl": "Wybierz miejsce do odwiedzenia",
        "sv": "Välj en plats att besöka",
        "uk": "Виберіть місце для відвідування",
    },
    "places_menu_end": {
        "en": "5 fingers → End Session",
        "es": "5 dedos → Finalizar Sesión",
        "fr": "5 doigts → Terminer la session",
        "ja": "5本指 → セッション終了",
        "ko": "손가락 5개 → 세션 종료",
        "pl": "5 palców → Zakończ sesję",
        "sv": "5 fingrar → Avsluta session",
        "uk": "5 пальців → Завершити сесію",
    },

    # ── Preguntas ──────────────────────────────────────────────────────────
    "qa_prompt": {
        "en": "Ask me anything about this place! Speak now...",
        "es": "¡Pregúntame lo que quieras sobre este lugar! Habla ahora...",
        "fr": "Posez-moi des questions sur cet endroit! Parlez maintenant...",
        "ja": "この場所について何でも聞いてください！話してください...",
        "ko": "이 장소에 대해 무엇이든 물어보세요! 지금 말하세요...",
        "pl": "Zapytaj mnie o to miejsce! Mów teraz...",
        "sv": "Fråga mig vad som helst om den här platsen! Prata nu...",
        "uk": "Запитайте мене про це місце! Говоріть зараз...",
    },
    "qa_again": {
        "en": "1 finger → Ask again   |   2 fingers → Back to Menu",
        "es": "1 dedo → Preguntar de nuevo   |   2 dedos → Volver al Menú",
        "fr": "1 doigt → Poser une autre question   |   2 doigts → Retour au Menu",
        "ja": "1本指 → もう一度聞く   |   2本指 → メニューに戻る",
        "ko": "손가락 1개 → 다시 질문   |   손가락 2개 → 메뉴로 돌아가기",
        "pl": "1 palec → Zadaj pytanie ponownie   |   2 palce → Powrót do Menu",
        "sv": "1 finger → Fråga igen   |   2 fingrar → Tillbaka till Menyn",
        "uk": "1 палець → Запитати знову   |   2 пальці → Повернутися до Меню",
    },

    # ── Premio / Foto ──────────────────────────────────────────────────────
    "prize_title": {
        "en": "*** Congratulations! You visited all 4 places!",
        "es": "*** ¡Felicidades! ¡Visitaste los 4 lugares!",
        "fr": "*** Félicitations! Vous avez visité les 4 endroits!",
        "ja": "*** おめでとうございます！4か所すべて訪問しました！",
        "ko": "*** 축하합니다! 4곳을 모두 방문했습니다!",
        "pl": "*** Gratulacje! Odwiedziłeś wszystkie 4 miejsca!",
        "sv": "*** Grattis! Du besökte alla 4 platser!",
        "uk": "*** Вітаємо! Ви відвідали всі 4 місця!",
    },
    "photo_prompt": {
        "en": "Show 5 fingers to take a photo with RAMon!\nScan the QR to receive it by email.",
        "es": "¡Muestra 5 dedos para tomarte una foto con RAMon!\nEscanea el QR para recibirla por correo.",
        "fr": "Montrez 5 doigts pour prendre une photo avec RAMon!\nScannez le QR pour la recevoir par email.",
        "ja": "5本指でRAMonと写真を撮ろう！\nQRをスキャンしてメールで受け取る。",
        "ko": "5손가락으로 RAMon과 사진 찍기!\nQR을 스캔하여 이메일로 받으세요.",
        "pl": "Pokaż 5 palców, aby zrobić zdjęcie z RAMonem!\nZeskanuj QR, aby otrzymać je e-mailem.",
        "sv": "Visa 5 fingrar för att ta ett foto med RAMon!\nSkanna QR-koden för att få det via e-post.",
        "uk": "Покажіть 5 пальців для фото з RAMonом!\nСкануйте QR щоб отримати на пошту.",
    },

    # ── Despedida ──────────────────────────────────────────────────────────
    "farewell": {
        "en": "Thank you for visiting! See you at the World Cup! [soccer][MX]",
        "es": "¡Gracias por visitarnos! ¡Nos vemos en el Mundial! [soccer][MX]",
        "fr": "Merci pour votre visite! À bientôt à la Coupe du Monde! [soccer][MX]",
        "ja": "ありがとうございました！ワールドカップでお会いしましょう！[soccer][MX]",
        "ko": "방문해 주셔서 감사합니다! 월드컵에서 만나요! [soccer][MX]",
        "pl": "Dziękujemy za wizytę! Do zobaczenia na Mistrzostwach Świata! [soccer][MX]",
        "sv": "Tack för ditt besök! Vi ses på VM! [soccer][MX]",
        "uk": "Дякуємо за відвідування! До зустрічі на Чемпіонаті Світу! [soccer][MX]",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# CONTENIDO DE LUGARES
# ─────────────────────────────────────────────────────────────────────────────

PLACES_CONTENT: dict[str, dict] = {

    # ── 1. Barrio Antiguo ──────────────────────────────────────────────────
    "barrio_antiguo": {
        "finger": 1,
        "name": {
            "en": "Barrio Antiguo",
            "es": "Barrio Antiguo",
            "fr": "Quartier Ancien",
            "ja": "バリオ・アンティグオ",
            "ko": "바리오 안티구오",
            "pl": "Stara Dzielnica",
            "sv": "Gamla Kvarteret",
            "uk": "Старий район",
        },
        "description": {
            "en": (
                "Barrio Antiguo is the historic heart of Monterrey, "
                "dating back to the 17th century. "
                "Its cobblestone streets, colonial architecture, "
                "colorful murals, art galleries, craft shops, and "
                "vibrant restaurants make it the cultural epicenter of the city. "
                "Every weekend it transforms into an open-air festival "
                "with live music, street food, and local art."
            ),
            "es": (
                "El Barrio Antiguo es el corazón histórico de Monterrey, "
                "con raíces que datan del siglo XVII. "
                "Sus calles empedradas, arquitectura colonial, "
                "murales coloridos, galerías de arte, tiendas de artesanías "
                "y restaurantes vibrantes lo convierten en el epicentro cultural de la ciudad. "
                "Los fines de semana se transforma en un festival al aire libre "
                "con música en vivo, comida callejera y arte local."
            ),
            "fr": (
                "Le Barrio Antiguo est le cœur historique de Monterrey, "
                "datant du XVIIe siècle. Ses rues pavées, son architecture coloniale, "
                "ses murales colorées et ses galeries d'art en font "
                "l'épicentre culturel de la ville."
            ),
            "ja": (
                "バリオ・アンティグオはモンテレーの歴史的な中心地で、17世紀にさかのぼります。"
                "石畳の道、植民地時代の建築、カラフルな壁画、"
                "アートギャラリー、クラフトショップがあり、"
                "週末には野外フェスティバルが開催されます。"
            ),
            "ko": (
                "바리오 안티구오는 17세기부터 시작된 몬테레이의 역사적 중심지입니다. "
                "자갈길, 식민지 건축물, 화려한 벽화, 미술관, "
                "공예품 가게와 식당이 가득하며, "
                "주말마다 야외 축제가 열립니다."
            ),
            "pl": (
                "Barrio Antiguo to historyczne serce Monterrey, "
                "sięgające XVII wieku. Brukowane uliczki, kolonialna architektura, "
                "kolorowe murale i galerie sztuki czynią je kulturalnym centrum miasta."
            ),
            "sv": (
                "Barrio Antiguo är Monterreys historiska hjärta från 1600-talet. "
                "Kullerstensgatorna, koloniala arkitekturen, "
                "färgglada muralmålningar och konstgallerier "
                "gör det till stadens kulturella epicentrum."
            ),
            "uk": (
                "Барріо Антігуо — це історичне серце Монтеррея, що датується XVII століттям. "
                "Бруковані вулиці, колоніальна архітектура, яскраві фрески "
                "та художні галереї роблять його культурним центром міста."
            ),
        },
        "highlights": {
            "en": ["Cobblestone streets", "Art galleries", "Street food", "Live music on weekends", "Colonial architecture"],
            "es": ["Calles empedradas", "Galerías de arte", "Comida callejera", "Música en vivo los fines de semana", "Arquitectura colonial"],
            "fr": ["Rues pavées", "Galeries d'art", "Street food", "Musique live le week-end", "Architecture coloniale"],
            "ja": ["石畳の道", "アートギャラリー", "ストリートフード", "週末のライブ音楽", "植民地建築"],
            "ko": ["자갈길", "미술관", "길거리 음식", "주말 라이브 음악", "식민지 건축"],
            "pl": ["Brukowane uliczki", "Galerie sztuki", "Street food", "Muzyka na żywo w weekendy", "Kolonialna architektura"],
            "sv": ["Kullerstensgatorna", "Konstgallerier", "Gatumat", "Livemusik på helgerna", "Koloniala arkitekturen"],
            "uk": ["Бруковані вулиці", "Художні галереї", "Вулична їжа", "Жива музика у вихідні", "Колоніальна архітектура"],
        },
        "images": [
            "aesthetic/Lugares/barrio.jpeg",
        ],
        "background_video": "",
        "background_image": "aesthetic/Fondos/fundidora1.png",
    },

    # ── 2. Fashion Drive ───────────────────────────────────────────────────
    "fashion_drive": {
        "finger": 2,
        "name": {
            "en": "Fashion Drive",
            "es": "Fashion Drive",
            "fr": "Fashion Drive",
            "ja": "ファッションドライブ",
            "ko": "패션 드라이브",
            "pl": "Fashion Drive",
            "sv": "Fashion Drive",
            "uk": "Фешн Драйв",
        },
        "description": {
            "en": (
                "Fashion Drive is Monterrey's premier luxury shopping destination, "
                "located in the exclusive San Pedro Garza García district. "
                "It features flagship stores of top international brands, "
                "gourmet restaurants, exclusive art installations, "
                "and green open-air promenades. "
                "It's the perfect blend of haute couture and gastronomy "
                "in a sophisticated urban setting."
            ),
            "es": (
                "Fashion Drive es el destino de compras de lujo más exclusivo de Monterrey, "
                "ubicado en San Pedro Garza García. "
                "Cuenta con tiendas insignia de las mejores marcas internacionales, "
                "restaurantes gourmet, instalaciones artísticas exclusivas "
                "y paseos al aire libre con áreas verdes. "
                "Es la mezcla perfecta de alta costura y gastronomía."
            ),
            "fr": (
                "Fashion Drive est la principale destination de shopping de luxe de Monterrey. "
                "Il accueille les boutiques des plus grandes marques internationales, "
                "des restaurants gastronomiques et des installations artistiques exclusives."
            ),
            "ja": (
                "ファッションドライブはモンテレーの最高級ショッピングエリアです。"
                "国際一流ブランドの旗艦店、グルメレストラン、"
                "そして美しいアート作品が並ぶ洗練された空間です。"
            ),
            "ko": (
                "패션 드라이브는 몬테레이의 대표적인 명품 쇼핑 목적지입니다. "
                "세계 유명 브랜드, 고메 레스토랑, "
                "독점 예술 설치물이 있는 세련된 공간입니다."
            ),
            "pl": (
                "Fashion Drive to główne centrum zakupów luksusowych w Monterrey. "
                "Znajdziesz tu sklepy flagowe najlepszych marek, "
                "restauracje gourmet i ekskluzywne instalacje artystyczne."
            ),
            "sv": (
                "Fashion Drive är Monterreys finaste lyxshoppingdestination. "
                "Här hittar du flaggskeppsbutiker, gourmetrestauranger "
                "och exklusiva konstinstallationer i en sofistikerad miljö."
            ),
            "uk": (
                "Fashion Drive — найпрестижніший торговий квартал Монтеррея. "
                "Тут є флагманські магазини відомих брендів, "
                "гурме-ресторани та ексклюзивні арт-інсталяції."
            ),
        },
        "highlights": {
            "en": ["Luxury brands", "Gourmet restaurants", "Art installations", "Open-air promenade", "San Pedro Garza García"],
            "es": ["Marcas de lujo", "Restaurantes gourmet", "Instalaciones artísticas", "Paseo al aire libre", "San Pedro Garza García"],
            "fr": ["Marques de luxe", "Restaurants gastronomiques", "Installations artistiques", "Promenade en plein air", "San Pedro GG"],
            "ja": ["高級ブランド", "グルメレストラン", "アート", "屋外プロムナード", "サンペドロ"],
            "ko": ["명품 브랜드", "고메 레스토랑", "아트 설치물", "야외 산책로", "산페드로"],
            "pl": ["Luksusowe marki", "Restauracje gourmet", "Instalacje artystyczne", "Sala na świeżym powietrzu", "San Pedro GG"],
            "sv": ["Lyxmärken", "Gourmetrestauranger", "Konstinstallationer", "Utomhuspromenad", "San Pedro GG"],
            "uk": ["Преміум бренди", "Гурме-ресторани", "Арт-інсталяції", "Прогулянкова зона", "Сан-Педро"],
        },
        "images": [
            "aesthetic/Lugares/fashion.jpg",
        ],
        "background_video": "",
        "background_image": "aesthetic/Fondos/Fashion Drive 1.png",
    },

    # ── 3. Estadio BBVA ────────────────────────────────────────────────────
    "estadio_bbva": {
        "finger": 3,
        "name": {
            "en": "Estadio BBVA",
            "es": "Estadio BBVA",
            "fr": "Stade BBVA",
            "ja": "BBVAスタジアム",
            "ko": "BBVA 스타디움",
            "pl": "Stadion BBVA",
            "sv": "BBVA Stadion",
            "uk": "Стадіон BBVA",
        },
        "description": {
            "en": (
                "Estadio BBVA, home of Club de Fútbol Monterrey (Rayados), "
                "is one of the most modern and impressive football stadiums in the world. "
                "With capacity for 53,000 fans, it features stunning views of the "
                "iconic Cerro de la Silla mountain rising directly behind the south end. "
                "During the FIFA World Cup 2026 it will host international matches, "
                "making it the center of global football in Monterrey."
            ),
            "es": (
                "El Estadio BBVA, hogar del Club de Fútbol Monterrey (Rayados), "
                "es uno de los estadios de fútbol más modernos e impresionantes del mundo. "
                "Con capacidad para 53,000 aficionados, tiene vistas impresionantes de la "
                "icónica Silla de Monterrey al fondo. "
                "Durante el Mundial 2026 será sede de partidos internacionales, "
                "convirtiéndose en el centro del fútbol mundial en Monterrey."
            ),
            "fr": (
                "Le Stade BBVA, domicile du CF Monterrey, est l'un des stades de football "
                "les plus modernes au monde avec une capacité de 53 000 fans. "
                "Pendant la Coupe du Monde 2026, il accueillera des matchs internationaux."
            ),
            "ja": (
                "BBVAスタジアムはモンテレーFCの本拠地で、世界で最も近代的なスタジアムの一つです。"
                "53,000人収容。2026年ワールドカップの試合会場になります。"
            ),
            "ko": (
                "BBVA 스타디움은 몬테레이 FC의 홈구장으로, 세계에서 가장 현대적인 축구 경기장 중 하나입니다. "
                "5만 3천명 수용. 2026년 월드컵 경기가 열릴 예정입니다."
            ),
            "pl": (
                "Stadion BBVA, dom CF Monterrey, jest jednym z najnowocześniejszych stadionów "
                "piłkarskich na świecie, mieszczącym 53 000 fanów. "
                "Podczas Mistrzostw Świata 2026 będzie gospodarzem międzynarodowych meczów."
            ),
            "sv": (
                "BBVA Stadion, hem för CF Monterrey, är en av världens modernaste fotbollsarenor "
                "med plats för 53 000 fans. Under VM 2026 arrangeras internationella matcher här."
            ),
            "uk": (
                "Стадіон BBVA — домашня арена CF Monterrey, один із найсучасніших стадіонів світу "
                "місткістю 53 000 глядачів. Під час ЧС-2026 тут пройдуть міжнародні матчі."
            ),
        },
        "highlights": {
            "en": ["World Cup 2026 venue", "53,000 capacity", "Cerro de la Silla view", "Club Rayados", "State-of-the-art facilities"],
            "es": ["Sede del Mundial 2026", "53,000 capacidad", "Vista a la Silla de Monterrey", "Club Rayados", "Instalaciones de primer nivel"],
            "fr": ["Stade du Mondial 2026", "Capacité 53 000", "Vue sur Cerro de la Silla", "Club Rayados", "Équipements modernes"],
            "ja": ["W杯2026会場", "5.3万人収容", "シリャ山の眺め", "ラジャドスFC", "最新設備"],
            "ko": ["2026 월드컵 경기장", "53,000명 수용", "세로 데 라 시야 전망", "라야도스 FC", "최신 시설"],
            "pl": ["Stadion Mistrzostw 2026", "53 000 miejsc", "Widok na Cerro de la Silla", "Club Rayados", "Nowoczesne udogodnienia"],
            "sv": ["VM 2026-arena", "53 000 platser", "Utsikt mot Cerro de la Silla", "Club Rayados", "Moderna faciliteter"],
            "uk": ["Арена ЧС-2026", "53 000 місць", "Вид на Серро-де-ла-Сілья", "Клуб Раядос", "Сучасна інфраструктура"],
        },
        "images": [
            "aesthetic/Lugares/bbva.jpg",
        ],
        "background_video": "",
        "background_image": "aesthetic/Fondos/Estadio BBVA 1.png",
    },

    # ── 4. Santiago Pueblo Mágico ──────────────────────────────────────────
    "santiago_pm": {
        "finger": 4,
        "name": {
            "en": "Santiago Pueblo Mágico",
            "es": "Santiago Pueblo Mágico",
            "fr": "Santiago Village Magique",
            "ja": "サンティアゴ・マジックタウン",
            "ko": "산티아고 마법 마을",
            "pl": "Santiago Magiczne Miasteczko",
            "sv": "Santiago Magiska Byn",
            "uk": "Сантьяго — Магічне місто",
        },
        "description": {
            "en": (
                "Nestled in the Sierra Madre mountains just 45 minutes from Monterrey, "
                "Santiago is a certified 'Pueblo Mágico' (Magic Town) that will take your "
                "breath away. Famous for Cola de Caballo waterfall, extreme outdoor adventures "
                "like rappelling and zip-lining, traditional street food, "
                "and its peaceful colonial town center. "
                "A perfect escape from the city into nature and Mexican tradition."
            ),
            "es": (
                "Enclavado en la Sierra Madre a solo 45 minutos de Monterrey, "
                "Santiago es un Pueblo Mágico certificado que te dejará sin aliento. "
                "Famoso por la Cascada Cola de Caballo, aventuras extremas como rapel y tirolesa, "
                "comida típica callejera y su tranquilo centro colonial. "
                "Un escape perfecto de la ciudad hacia la naturaleza y la tradición mexicana."
            ),
            "fr": (
                "Niché dans la Sierra Madre à 45 minutes de Monterrey, "
                "Santiago est un 'Pueblo Mágico' certifié. "
                "Célèbre pour la cascade Cola de Caballo, les aventures de plein air "
                "et sa gastronomie traditionnelle."
            ),
            "ja": (
                "モンテレーから45分のシエラマドレ山中にあるサンティアゴは「マジックタウン」認定の町です。"
                "コラ・デ・カバジョの滝や山岳アドベンチャー、"
                "伝統的な街並みが楽しめます。"
            ),
            "ko": (
                "몬테레이에서 45분 거리의 시에라마드레 산속에 위치한 산티아고는 "
                "'마법 마을' 인증을 받은 곳입니다. "
                "콜라 데 카바요 폭포, 액티비티, 전통 음식으로 유명합니다."
            ),
            "pl": (
                "Ukryte w górach Sierra Madre 45 minut od Monterrey, "
                "Santiago to certyfikowane 'Magiczne Miasteczko'. "
                "Słynne z wodospadu Cola de Caballo i przygód na świeżym powietrzu."
            ),
            "sv": (
                "Beläget i Sierra Madre-bergen 45 minuter från Monterrey, "
                "Santiago är ett certifierat 'Magiskt Samhälle'. "
                "Känt för vattenfallet Cola de Caballo och äventyrsupplevelser."
            ),
            "uk": (
                "Розташований у горах Сьєрра-Мадре за 45 хвилин від Монтеррея, "
                "Сантьяго — сертифіковане 'Магічне місто'."
                "Відомий водоспадом Кола-де-Кабальо та пригодами на природі."
            ),
        },
        "highlights": {
            "en": ["Cola de Caballo Waterfall", "Rappelling & Zip-line", "Traditional food", "Colonial architecture", "45 min from Monterrey"],
            "es": ["Cascada Cola de Caballo", "Rapel y Tirolesa", "Comida típica", "Arquitectura colonial", "45 min de Monterrey"],
            "fr": ["Cascade Cola de Caballo", "Rappel & Tyrolienne", "Gastronomie locale", "Architecture coloniale", "45 min de Monterrey"],
            "ja": ["コラ・デ・カバジョの滝", "ラペリング・ジップライン", "伝統料理", "植民地建築", "モンテレーから45分"],
            "ko": ["콜라 데 카바요 폭포", "래펠링&집라인", "전통 음식", "식민지 건축", "몬테레이에서 45분"],
            "pl": ["Wodospad Cola de Caballo", "Rappel i tyrolka", "Tradycyjne jedzenie", "Architektura kolonialna", "45 min od Monterrey"],
            "sv": ["Vattenfall Cola de Caballo", "Klättring & Zipline", "Traditionell mat", "Koloniala arkitekturen", "45 min från Monterrey"],
            "uk": ["Водоспад Кола-де-Кабальо", "Рапел і зіплайн", "Традиційна їжа", "Колоніальна архітектура", "45 хв від Монтеррея"],
        },
        "images": [
            "aesthetic/Lugares/santiago.jpeg",
        ],
        "background_video": "",
        "background_image": "aesthetic/Fondos/Santiago1.png",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_text(key: str, lang: str, fallback: str = "en") -> str:
    """Obtiene texto del sistema por clave e idioma con fallback."""
    block = SYSTEM_TEXTS.get(key, {})
    return block.get(lang) or block.get(fallback, key)


def get_place(place_id: str, lang: str, fallback: str = "en") -> dict:
    """Retorna el contenido de un lugar con todos los textos en el idioma dado."""
    place = PLACES_CONTENT.get(place_id, {})
    return {
        "id":          place_id,
        "finger":      place.get("finger", 0),
        "name":        (place.get("name") or {}).get(lang)
                        or (place.get("name") or {}).get(fallback, place_id),
        "description": (place.get("description") or {}).get(lang)
                        or (place.get("description") or {}).get(fallback, ""),
        "highlights":  (place.get("highlights") or {}).get(lang)
                        or (place.get("highlights") or {}).get(fallback, []),
        "images":      place.get("images", []),
        "bg_video":    place.get("background_video", ""),
        "bg_image":    place.get("background_image", ""),
    }
