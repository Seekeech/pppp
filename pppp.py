import random
import json
import time
import os
import telebot
from PIL import Image, ImageDraw, ImageOps
from telebot import types
import io
import requests
import time
import threading
import shutil

# Загрузка карточек из файла
with open('cards.json', 'r', encoding='utf-8') as file:
    cards = json.load(file)

# Инициализация бота
bot = telebot.TeleBot("7762tHjgGXsPp3chKv1gs")

# Папка для хранения данных игроков
DATA_FOLDER = "user_data"
BACKGROUNDS_FILE = "backgrounds.json"
DEFAULT_BANNER = "black.jpg"
STICKER_RANGE_1 = "CAACAgIAAxkBAAEMsUlntNR3VHJvLkrSB0otE9izOwRD6QACuUAAAnv6SEkzZLuvkIG7MDYE"  # 99-999
STICKER_RANGE_2 = "CAACAgIAAxkBAAEMsUpntNR31UiNbOPV6KqVUUqJ_5kwDQACaUAAArGISUkfZ0gHO5ysQzYE"  # 1000-4999
STICKER_RANGE_3 = "CAACAgIAAxkBAAEMsUtntNR3DiGaX2_QhvKtVgasZaV-QAACLFEAAucRQUmOOfnyXaFCbTYE"  # 5000-9999
STICKER_RANGE_4 = "CAACAgIAAxkBAAEMsUxntNR3AS8dKAE_jmr-rkS2Gf_tnAACe00AAh_-QUlWY0PosQKs_TYE"  # 10000+
ADMINS_FILE = "admins.json"
# Словарь с доступными РП-действиями (будущее время → прошедшее время)
RP_ACTIONS = {
    "💞 Тактильность": {
        "обнять": "обнял",
        "поцеловать": "поцеловал",
        "погладить": "погладил",
        "облизать": "облизал",
        "флиртовать": "флиртовал",
        "прижать": "прижал",
        "укусить": "укусил",
        "оставить засос": "оставил засос",
        "согреть": "согрел",
        "простонать в ухо": "простонал в ухо",
        "поцеловать в макушку": "поцеловал в макушку",
        "засосать": "засосал",
        "подарить колечко": "подарил колечко"
    },
    "🔞 18+": {
        "выебать": "выебал",
        "трахнуть": "трахнул",
        "подрочить": "подрочил",
        "отсосать": "отсосал",
        "обкончать": "обкончал",
        "отлизать": "отлизал",
        "шлепнуть": "шлепнул",
        "раздеть": "раздел",
        "пустить по кругу": "пустил по кругу",
        "бухнуть": "бухнул",
        "пожмякать яички": "пожмякал яички",
        "пожмякать титьки": "пожмякал титьки",
        "зажать сиськами": "зажал сиськами"
    },
    "🔪 Жесть": {
        "убить": "убил",
        "кастрировать": "кастрировал",
        "расстрелять": "расстрелял",
        "ударить": "ударил",
        "задушить": "задушил",
        "связать": "связал",
        "продать меф": "продал меф",
        "расчленить": "расчленил",
        "выстрелить с танка": "выстрелил с танка",
        "сжечь": "сжег",
        "повесить": "повесил",
        "выкинуть в окно": "выкинул в окно",
        "казнить": "казнил",
        "переехать поездом": "переехал поездом"
    },
    "😜 Эмоции": {
        "похвалить": "похвалил",
        "подколоть": "подколол",
        "соблазнить": "соблазнил",
        "успокоить": "успокоил"
    },
    "🤷‍♂️ Разное": {
        "разбудить": "разбудил",
        "накормить": "накормил",
        "накуриться": "накурился",
        "забанить": "забанил",
        "замутить": "замутил",
        "предупредить": "предупредил",
        "спрятать в подвале": "спрятал в подвале",
        "поменять угли в кальяне": "поменял угли в кальяне",
        "дать вейп": "дал вейп",
        "арестовать": "арестовал",
        "посадить в тюрьму": "посадил в тюрьму"
    },
    "🤮 Мерзкое": {
        "обоссать": "обоссал",
        "обосрать": "обосрал"
    },
    "😻 Милое": {
        "подарить кота": "подарил кота",
        "подарить собаку": "подарил собаку"
    },
    "😵‍💫 Какой гений это придумывал?": {
        "рандом": "рандом",
        "сашенька": "сашенька"
    }
}
last_start_time = time.time()
hz = -1001921363567
PROMOCODES_FILE = "promocodes.json"
CASINO_SYMBOLS = ["🍒", "🍋", "🍊", "🍇", "🍉", "7️⃣", "🔔", "💎", "BAR"]
CASINO_MULTIPLIERS = {
    "3_same": 2.00,
    "2_same": 1.50,
    "all_different": 0.00,
    "1_bar": -0.50,
    "2_bars": -1.00,
    "3_bars": -2.00,
    "1_seven": 1.50,
    "2_sevens": 2.00,
    "3_sevens": 3.00
}

def migrate_user_data(user_id):
    data = load_user_data(user_id)
    
    # Автоматический расчет исторических данных
    new_fields = {
        'total_coins_earned': data.get('coins_from_messages', 0) + data.get('coins_from_transfers', 0),
        'total_coins_spent': data.get('coins_spent_transfers', 0),
        'coins_from_games': data.get('coins_from_games', 0),
        'coins_spent_games': data.get('coins_spent_games', 0),
        'casino_games_played': data.get('casino_games_played', 0),
        'roulette_games_played': data.get('roulette_games_played', 0),
        'last_cards': data.get('last_cards', [])[-5:]
    }
    
    for key, value in new_fields.items():
        if key not in data:
            data[key] = value
    
    save_user_data(user_id, data)

def migrate_all_users():
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith('.json'):
            user_id = filename.split('.')[0]
            migrate_user_data(user_id)

def generate_casino_result():
    """Генерирует случайный результат казино (3 символа)."""
    return [random.choice(CASINO_SYMBOLS) for _ in range(3)]

def calculate_multiplier(result):
    """Вычисляет множитель на основе результата казино."""
    multiplier = 1.00
    bars = result.count("BAR")
    sevens = result.count("7️⃣")
    unique_symbols = len(set(result))

    # Проверяем комбинации
    if unique_symbols == 1:  # Все 3 одинаковые
        multiplier = CASINO_MULTIPLIERS["3_same"]
    elif unique_symbols == 2:  # 2 одинаковых
        multiplier = CASINO_MULTIPLIERS["2_same"]
    else:  # Все разные
        multiplier = CASINO_MULTIPLIERS["all_different"]

    # Корректировка множителя на основе BAR и 7️⃣
    if bars == 1:
        multiplier += CASINO_MULTIPLIERS["1_bar"]
    elif bars == 2:
        multiplier += CASINO_MULTIPLIERS["2_bars"]
    elif bars == 3:
        multiplier += CASINO_MULTIPLIERS["3_bars"]

    if sevens == 1:
        multiplier += CASINO_MULTIPLIERS["1_seven"]
    elif sevens == 2:
        multiplier += CASINO_MULTIPLIERS["2_sevens"]
    elif sevens == 3:
        multiplier = CASINO_MULTIPLIERS["3_sevens"]  # Перезаписываем множитель

    return max(0.00, multiplier)  # Не может быть отрицательным

def backup_user_data():
    if not os.path.exists(DATA_FOLDER):
        return

    backup_folder = os.path.join(DATA_FOLDER, "backup")
    os.makedirs(backup_folder, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".json") and not filename.startswith("backup"):
            src = os.path.join(DATA_FOLDER, filename)
            dst = os.path.join(backup_folder, f"{timestamp}_{filename}")
            shutil.copy2(src, dst)

def migrate_promocodes():
    """Обновляет старые промокоды, добавляя недостающие поля."""
    promocodes = load_promocodes()
    changed = False
    
    for code, data in promocodes.items():
        if 'total_uses' not in data:
            data['total_uses'] = data.get('uses_left', 1)
            changed = True
        if 'used_by' not in data:
            data['used_by'] = []
            changed = True
        if 'creator_name' not in data:
            data['creator_name'] = "Unknown"
            changed = True
    
    if changed:
        save_promocodes(promocodes)
        print("Миграция промокодов выполнена успешно")

def notify_bot_started():
    global last_start_time
    last_start_time = time.time()  # Обновляем время запуска

    try:
        bot.send_message(hz, "🚀 Бот включен и готов к работе! ")
    except Exception as e:
        print(f"Ошибка при отправке сообщения в чат {hz}: {e}")

def ignore_old_messages(func):
    def wrapper(message, *args, **kwargs):
        global last_start_time
        
        if message.date < last_start_time:
            return
        
        return func(message, *args, **kwargs)
    
    return wrapper
    
# Функция для создания клавиатуры с кнопками "В себя" и "В манекен"
def create_shoot_keyboard(user_id):
    markup = types.InlineKeyboardMarkup()
    btn_self = types.InlineKeyboardButton('🙋‍♂️ В себя', callback_data=f'roulette_shoot_self_{user_id}')
    btn_dummy = types.InlineKeyboardButton('👤 В манекен', callback_data=f'roulette_shoot_dummy_{user_id}')
    markup.add(btn_self, btn_dummy)
    return markup

def load_json_with_defaults(file_path):
    """Загружает JSON-файл и добавляет поле 'exclusive_to' со значением null, если оно отсутствует."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for item in data:
        if 'exclusive_to' not in item:
            item['exclusive_to'] = None  # По умолчанию доступно всем
    
    return data

def get_top_messages():
    """Возвращает топ 10 игроков по количеству сообщений."""
    user_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.json')]
    top_users = []

    for user_file in user_files:
        user_id = user_file.split('.')[0]
        data = load_user_data(user_id)
        message_count = data.get('message_count', 0)
        top_users.append({'user_id': user_id, 'value': message_count})

    # Сортируем по убыванию
    top_users.sort(key=lambda x: x['value'], reverse=True)
    return top_users[:10]

def get_top_coins():
    """Возвращает топ 10 игроков по количеству коинов."""
    user_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.json')]
    top_users = []

    for user_file in user_files:
        user_id = user_file.split('.')[0]
        data = load_user_data(user_id)
        balance = data.get('balance', 0)
        top_users.append({'user_id': user_id, 'value': balance})

    # Сортируем по убыванию
    top_users.sort(key=lambda x: x['value'], reverse=True)
    return top_users[:10]

def get_top_cases():
    """Возвращает топ 10 игроков по количеству открытых кейсов."""
    user_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.json')]
    top_users = []

    for user_file in user_files:
        user_id = user_file.split('.')[0]
        data = load_user_data(user_id)
        case_count = data.get('case_count', 0)
        top_users.append({'user_id': user_id, 'value': case_count})

    # Сортируем по убыванию
    top_users.sort(key=lambda x: x['value'], reverse=True)
    return top_users[:10]

def get_top_cards():
    """Возвращает топ 10 игроков по лучшей карточке."""
    user_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.json')]
    top_users = []

    for user_file in user_files:
        user_id = user_file.split('.')[0]
        data = load_user_data(user_id)
        best_card = data.get('best_card')
        if best_card:
            top_users.append({'user_id': user_id, 'value': best_card['q_coins'], 'card_name': best_card['name']})

    # Сортируем по убыванию
    top_users.sort(key=lambda x: x['value'], reverse=True)
    return top_users[:10]

def show_frame_by_index(message, frame_index):
    user_id = str(message.from_user.id)
    data = load_user_data(user_id)
    frame_info = frames[frame_index]
    
    markup = create_frame_keyboard(frame_index, user_id)
    avatar_file = get_user_avatar(bot, user_id)
    
    image_blob = create_framed_image(
        data['current_banner'], 
        avatar_file or "avatar.png", 
        frame_info['filename']
    )
    
    bot.send_photo(
        message.chat.id,
        image_blob,
        caption=format_frame_message(frame_info, frame_index),
        reply_markup=markup,
        parse_mode="Markdown"
    )

def show_banner_by_index(message, banner_index):
    user_id = str(message.from_user.id)
    data = load_user_data(user_id)
    banner_info = backgrounds[banner_index]
    
    markup = create_banner_keyboard(banner_index, user_id)
    avatar_file = get_user_avatar(bot, user_id)
    
    image_blob = create_framed_image(
        banner_info['filename'], 
        avatar_file or "avatar.png", 
        None
    )
    
    bot.send_photo(
        message.chat.id,
        image_blob,
        caption=format_banner_message(banner_info, banner_index),
        reply_markup=markup,
        parse_mode="Markdown"
    )

def show_underframe_by_index(message, underframe_index):
    user_id = str(message.from_user.id)
    data = load_user_data(user_id)
    underframe_info = underframes[underframe_index]
    
    markup = create_underframe_keyboard(underframe_index, user_id)
    avatar_file = get_user_avatar(bot, user_id)
    
    image_blob = create_banner_with_all(
        data['current_banner'],
        avatar_file or "avatar.png",
        data.get('current_frame'),
        underframe_info['filename']
    )
    
    bot.send_photo(
        message.chat.id,
        image_blob,
        caption=format_underframe_message(underframe_info, underframe_index),
        reply_markup=markup,
        parse_mode="Markdown"
    )
        
def get_all_rp_actions():
    all_actions = {}
    for category, actions in RP_ACTIONS.items():
        all_actions.update(actions)
    return all_actions

def load_admins():
    """Загружает список администраторов из файла."""
    if not os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"owner_id": "ВАШ_АЙДИ", "admins": [], "promo_admins": []}, f, ensure_ascii=False, indent=4)
    with open(ADMINS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Добавляем проверку на промо-админа
def is_promo_admin(user_id):
    """Проверяет, является ли пользователь промо-админом или владельцем"""
    admins_data = load_admins()
    user_id = str(user_id)
    return (user_id == admins_data["owner_id"] or 
            user_id in admins_data.get("promo_admins", []))

def load_promocodes():
    """Загружает промокоды с проверкой структуры"""
    if not os.path.exists(PROMOCODES_FILE):
        return {}
    
    try:
        with open(PROMOCODES_FILE, 'r', encoding='utf-8') as f:
            promocodes = json.load(f)
            
        # Валидация структуры каждого промокода
        valid_promocodes = {}
        for code, data in promocodes.items():
            if not isinstance(data, dict):
                continue
                
            valid_data = {
                'amount': int(data.get('amount', 0)),
                'uses_left': int(data.get('uses_left', 0)),
                'total_uses': int(data.get('total_uses', data.get('uses_left', 0))),
                'created_by': str(data.get('created_by', '0')),
                'created_at': data.get('created_at', time.time()),
                'used_by': list(data.get('used_by', [])),
                'creator_name': str(data.get('creator_name', 'Unknown'))
            }
            
            # Удаляем использованные промокоды (uses_left <= 0)
            if valid_data['uses_left'] > 0:
                valid_promocodes[code] = valid_data
                
        return valid_promocodes
        
    except Exception as e:
        print(f"Ошибка загрузки промокодов: {e}")
        return {}

def save_promocodes(promocodes):
    """Сохраняет промокоды, удаляя использованные"""
    # Фильтруем промокоды, оставляя только те, у которых uses_left > 0
    active_promocodes = {
        code: data for code, data in promocodes.items() 
        if data.get('uses_left', 1) > 0
    }
    
    with open(PROMOCODES_FILE, 'w', encoding='utf-8') as f:
        json.dump(active_promocodes, f, ensure_ascii=False, indent=4)

def save_admins(data):
    """Сохраняет список администраторов в файл."""
    with open(ADMINS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def is_owner(user_id):
    """Проверяет, является ли пользователь владельцем."""
    admins_data = load_admins()
    return str(user_id) == admins_data["owner_id"]

def is_admin(user_id):
    """Проверяет, является ли пользователь администратором."""
    admins_data = load_admins()
    return str(user_id) in admins_data["admins"] or is_owner(user_id)

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Загрузка данных из JSON-файлов с добавлением поля 'exclusive_to'
backgrounds = load_json_with_defaults('backgrounds.json')
frames = load_json_with_defaults('frames.json')
underframes = load_json_with_defaults('underframes.json')

def load_user_data(user_id):
    file_path = os.path.join(DATA_FOLDER, f"{user_id}.json")
    defaults = {
        'balance': 0,
        'case_count': 0,
        'best_card': None,
        'last_case_time': 0,
        'last_gift_time': 0,
        'purchased_banners': [],
        'current_banner': DEFAULT_BANNER,
        'purchased_frames': [],
        'current_frame': None,
        'purchased_underframes': [],
        'current_underframe': None,
        'message_count': 0,
        'last_roulette_time': 0,
        'used_promocodes': [],
        'total_coins_earned': 0,
        'coins_from_messages': 0,
        'coins_from_transfers': 0,
        'coins_from_games': 0,
        'total_coins_spent': 0,
        'coins_spent_transfers': 0,
        'coins_spent_games': 0,
        'casino_games_played': 0,
        'roulette_games_played': 0,
        'last_cards': []
    }

    if not os.path.exists(file_path):
        return defaults

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # Проверяем, что данные - словарь
            if not isinstance(data, dict):
                raise ValueError("Invalid data format")
            
            # Восстанавливаем недостающие поля
            for key, default_value in defaults.items():
                if key not in data:
                    data[key] = default_value
            
            return data

    except (json.JSONDecodeError, ValueError, IOError) as e:
        print(f"⚠️ Ошибка загрузки данных пользователя {user_id}: {e}. Восстанавливаю defaults.")
        return defaults

# Функция для сохранения данных игрока
def save_user_data(user_id, data):
    file_path = os.path.join(DATA_FOLDER, f"{user_id}.json")
    temp_path = f"{file_path}.tmp"

    try:
        # Сначала пишем во временный файл
        with open(temp_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        
        # Затем атомарно заменяем старый файл
        if os.path.exists(file_path):
            os.replace(temp_path, file_path)
        else:
            os.rename(temp_path, file_path)

    except Exception as e:
        print(f"⚠️ Ошибка сохранения данных пользователя {user_id}: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)

# Функция для выбора случайной карточки с учетом шансов
def get_random_card(user_id):
    """Выбирает случайную карточку с учетом шансов (без улучшений)."""
    # Веса карточек остаются стандартными
    weighted_cards = [(card, card['chance']) for card in cards]
    cards_list, weights = zip(*weighted_cards)
    return random.choices(cards_list, weights=weights, k=1)[0]

# Функция для получения времени до следующего кейса
def get_time_until_next_case(user_id):
    """Возвращает время до следующего кейса (без улучшений)."""
    data = load_user_data(user_id)
    last_case_time = data.get('last_case_time', 0)  # Время последнего открытия кейса
    current_time = time.time()
    remaining_time = max(0, 600 - (current_time - last_case_time))  # Всегда 10 минут (600 секунд)
    
    # Преобразуем оставшееся время в минуты и секунды
    minutes = int(remaining_time // 60)
    seconds = int(remaining_time % 60)
    return f"{minutes:02d}:{seconds:02d}"

def get_time_until_next_gift(user_id):
    data = load_user_data(user_id)
    last_gift_time = data.get('last_gift_time', 0)
    current_time = time.time()
    remaining_time = max(0, 86400 - (current_time - last_gift_time))  # 24 часа = 86400 секунд
    hours = int(remaining_time // 3600)
    minutes = int((remaining_time % 3600) // 60)
    seconds = int(remaining_time % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def get_user_avatar(bot, user_id):
    """Получает аватарку пользователя из Telegram и возвращает io.BytesIO объект."""
    try:
        photos = bot.get_user_profile_photos(user_id, limit=1).photos
        if photos:
            photo = photos[0][-1]  # Берем самую большую фотографию профиля
            file_info = bot.get_file(photo.file_id)
            file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
            response = requests.get(file_url)
            response.raise_for_status()
            avatar_image = io.BytesIO(response.content)
            return avatar_image
        else:
            return None  # У пользователя нет аватарки
    except Exception as e:
        print(f"Ошибка при получении аватарки: {e}")
        return None

def create_banner_with_all(banner_filename, avatar_file, frame_filename, underframe_filename):
    try:
        banner = Image.open(banner_filename).resize((750, 500))

        # Открываем и обрабатываем аватар
        avatar = Image.open(io.BytesIO(avatar_file.read())) if hasattr(avatar_file, 'read') else Image.open(avatar_file)
        avatar = avatar.resize((200, 200))

        # Создаем круглую маску для аватара
        mask = Image.new('L', (200, 200), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, 200, 200), fill=255)
        avatar = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
        avatar.putalpha(mask)

        # Накладываем аватар на баннер
        banner.paste(avatar, (275, 150), avatar) # Use avatar as mask
        
        # Накладываем подрамник (если он есть)
        if underframe_filename:
            underframe = Image.open(underframe_filename).resize((750, 500))
            banner = Image.alpha_composite(banner.convert("RGBA"), underframe.convert("RGBA"))  # Combine with alpha

        # Накладываем рамку (если она есть)
        if frame_filename:
            frame = Image.open(frame_filename).resize((750, 500)).convert("RGBA")
            banner = Image.alpha_composite(banner.convert("RGBA"), frame)

        # Конвертируем в байты для отправки
        img_byte_arr = io.BytesIO()
        banner.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr

    except Exception as e:
        print(f"Ошибка при создании изображения: {e}")
        return None
        
def create_framed_image(banner_filename, avatar_file, frame_filename):
       try:
           with Image(filename=banner_filename, resolution=300) as banner:
               banner.resize(750, 500)

               with Image(file=avatar_file) as avatar:
                   avatar.resize(200, 200)

                   # Создаем маску в форме круга
                   with Image(width=200, height=200, background=Color('transparent')) as mask:
                       with Drawing() as draw:
                           draw.fill_color = Color('white')
                           draw.circle((100, 100), (100, 0))  # Круг в центре изображения
                           draw(mask)

                       # Применяем маску к аватарке
                       avatar.composite(mask, left=0, top=0, operator='dst_in')

                   # Накладываем аватар на баннер
                   banner.composite(avatar, left=275, top=150)

               # Накладываем рамку на баннер
               if frame_filename:
                   with Image(filename=frame_filename) as frame:
                       frame.resize(750, 500)
                       banner.composite(frame, left=0, top=0)

               banner.format = 'png'
               return banner.make_blob()

       except Exception as e:
           print(f"Ошибка при создании изображения с рамкой: {e}")
           return None
           
def format_frame_message(frame_info, frame_index):
    return (
        f"🔲 *Рамка #`{frame_index + 1}` \"{frame_info['name']}\"*\n\n\n"
        f"💰 _Цена – {frame_info.get('price', 0)} Q коинов_\n\n"
        f"© _Автор – `{frame_info.get('author', 'Неизвестен')}`_\n\n"
        f"📖 _Описание:_\n"
        f"_{frame_info['description']}_"
    )
    
def create_frame_keyboard(frame_index, user_id):
    data = load_user_data(user_id)
    frame_info = frames[frame_index]
    frame_filename = frame_info['filename']
    is_purchased = frame_filename in data['purchased_frames']

    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton('⬅️', callback_data=f'frame_back_{frame_index}_{user_id}')

    # Проверяем, доступна ли рамка для покупки
    if frame_info.get('exclusive_to') is None or str(frame_info['exclusive_to']) == user_id:
        if is_purchased:
            btn_buy = types.InlineKeyboardButton('✅', callback_data=f'frame_wear_{frame_index}_{user_id}')
        else:
            btn_buy = types.InlineKeyboardButton(f'💰', callback_data=f'frame_buy_{frame_index}_{user_id}')
    else:
        # Если рамка эксклюзивная и не для этого пользователя, кнопка "Купить" не отображается
        btn_buy = types.InlineKeyboardButton('🔒', callback_data='no_access')

    btn_next = types.InlineKeyboardButton('➡️', callback_data=f'frame_next_{frame_index}_{user_id}')
    markup.add(btn_back, btn_buy, btn_next)
    return markup
    
def create_framed_image(banner_filename, avatar_file, frame_filename):
    try:
        # Открываем баннер
        banner = Image.open(banner_filename).resize((750, 500))

        # Открываем аватар
        avatar = Image.open(io.BytesIO(avatar_file.read())) if hasattr(avatar_file, 'read') else Image.open(avatar_file)
        avatar = avatar.resize((200, 200))

        # Создаем круглую маску для аватара
        mask = Image.new('L', (200, 200), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, 200, 200), fill=255)
        avatar = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
        avatar.putalpha(mask)

        # Накладываем аватар на баннер
        banner.paste(avatar, (275, 150), avatar)

        # Накладываем рамку (если она есть)
        if frame_filename:
            frame = Image.open(frame_filename).resize((750, 500)).convert("RGBA")
            banner = Image.alpha_composite(banner.convert("RGBA"), frame)

        # Конвертируем в байты для отправки
        img_byte_arr = io.BytesIO()
        banner.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr

    except Exception as e:
        print(f"Ошибка при создании изображения с рамкой: {e}")
        return None
        
def give_coins(bot, message):
    """Обработчик команды передачи Q коинов."""

    if not message.reply_to_message:
        bot.reply_to(message, "⚠️Эта команда должна быть ответом на сообщение игрока, которому вы хотите передать коины.")
        return

    # Добавить в начало функции:
    giver_id = str(message.from_user.id)
    giver_data = load_user_data(giver_id)  #     Загрузка данных отправителя
    receiver_id = str(message.reply_to_message.from_user.id)
    receiver_data = load_user_data(receiver_id)

    if giver_id == receiver_id:
        bot.reply_to(message, "⚠️Нельзя передавать коины самому себе.")
        return

    # Извлекаем сумму из сообщения
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "⚠️Укажите сумму для передачи (например, 'дать 1000' или 'дать все').")
        return

    amount_str = parts[1].lower()
    

    # Сохраняем данные
    giver_data['coins_spent_transfers'] += amount
    giver_data['total_coins_spent'] += amount
    receiver_data['coins_from_transfers'] += amount
    receiver_data['total_coins_earned'] += amount


    if amount_str == 'все' or amount_str == 'всё':
        amount = giver_balance  # Передаем все доступные коины
    else:
        try:
            amount = int(amount_str)
            if amount <= 0:
                bot.reply_to(message, "⚠️Сумма должна быть положительным числом.")
                return
        except ValueError:
            bot.reply_to(message, "⚠️Некорректная сумма. Укажите число или 'все/всё'.")
            return

    if giver_balance < amount:
        bot.reply_to(message, "❌Недостаточно Q коинов на балансе для передачи.")
        return

    # Загружаем данные получателя
    receiver_data = load_user_data(receiver_id)

    # Обновляем балансы
    giver_data['balance'] -= amount
    receiver_data['balance'] += amount
    
    save_user_data(giver_id, giver_data)
    save_user_data(receiver_id, receiver_data)

    # Определяем стикер
    if 99 <= amount <= 999:
        sticker = STICKER_RANGE_1
    elif 1000 <= amount <= 4999:
        sticker = STICKER_RANGE_2
    elif 5000 <= amount <= 9999:
        sticker = STICKER_RANGE_3
    else:
        sticker = STICKER_RANGE_4

    # Формируем сообщение
    giver_name = message.from_user.first_name
    receiver_name = message.reply_to_message.from_user.first_name
    response_message = f"🎉Поздравляю! {receiver_name}!\n\n🎁Ты получил подарок от {giver_name} в размере {amount} Q коинов"

    # Отправляем стикер и сообщение получателю
    bot.send_sticker(message.chat.id, sticker, reply_to_message_id=message.reply_to_message.message_id)
    bot.send_message(message.chat.id, response_message, reply_to_message_id=message.reply_to_message.message_id)
    
RANK_DEFINITIONS = {
    "Новичок": (0, 149),
    "Активный": (150, 499),
    "Продвинутый": (500, 999),
    "Знакомый Себастьяна": (1000, 4999),
    "Знакомый Пеинтера": (5000, 7499),
    "Любопытный свет": (7500, 9499),
    "Озорной свет": (9500, 12999),
    "Путеводный свет": (13000, 19999),
    "Друг Себастьяна": (20000, 49999),
    "Друг Пеинтера": (50000, 99999),
    "Ангел-хранитель чата": (100000, float('inf'))  # Бесконечность
}

def get_user_rank(message_count):
    """Определяет ранг пользователя на основе количества сообщений."""
    for rank, (min_messages, max_messages) in RANK_DEFINITIONS.items():
        if min_messages <= message_count <= max_messages:
            return rank
    return "Неизвестный ранг"  # На всякий случай

def update_message_count(user_id):
    """Обновляет счетчик сообщений пользователя."""
    user_id = str(user_id)
    data = load_user_data(user_id)
    if 'message_count' not in data:
        data['message_count'] = 0
    data['message_count'] += 1
    save_user_data(user_id, data)

    return data['message_count']

def give_coins_for_message(user_id, message_text):
    user_id = str(user_id)
    data = load_user_data(user_id)
    coins_to_add = len(message_text) // 2
    
    data['balance'] += coins_to_add
    data['coins_from_messages'] += coins_to_add
    data['total_coins_earned'] += coins_to_add  # Важно!
    save_user_data(user_id, data)  # Сохраняем сразу
    
    return coins_to_add   

def format_underframe_message(underframe_info, underframe_index):
    return (
        f"🧱 *Подрамка #`{underframe_index + 1}` \"{underframe_info['name']}\"*\n\n\n"
        f"💰 _Цена – {underframe_info.get('price', 0)} Q коинов_\n\n"
        f"© _Автор – `{underframe_info.get('author', 'Неизвестен')}`_\n\n"
        f"📖 _Описание:_\n"
        f"_{underframe_info['description']}_"
    )

def create_underframe_keyboard(underframe_index, user_id):
    data = load_user_data(user_id)
    underframe_info = underframes[underframe_index]
    underframe_filename = underframe_info['filename']
    is_purchased = underframe_filename in data['purchased_underframes']

    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton('⬅️', callback_data=f'underframe_back_{underframe_index}_{user_id}')

    # Проверяем, доступен ли подрамник для покупки
    if underframe_info.get('exclusive_to') is None or str(underframe_info['exclusive_to']) == user_id:
        if is_purchased:
            btn_buy = types.InlineKeyboardButton('✅', callback_data=f'underframe_wear_{underframe_index}_{user_id}')
        else:
            btn_buy = types.InlineKeyboardButton(f'💰', callback_data=f'underframe_buy_{underframe_index}_{user_id}')
    else:
        # Если подрамник эксклюзивный и не для этого пользователя, кнопка "Купить" не отображается
        btn_buy = types.InlineKeyboardButton('🔒', callback_data='no_access')

    btn_next = types.InlineKeyboardButton('➡️', callback_data=f'underframe_next_{underframe_index}_{user_id}')
    markup.add(btn_back, btn_buy, btn_next)
    return markup
    
def create_help_message():
    """Создает сообщение помощи с описанием всех команд бота."""
    help_message = """
**__Команды бота на данный момент:**__    

### **Команды для баланса и профиля:**
**__Баланс:__**  
– `био`; `балик`; `баланс`; `бал`; `проф`; `профиль`; `кто я`

---

### **Команды для открытия кейса:**
**__Кейсы:__**  
– `кейс`; `к`; `касик`; `кейсик`; `открыть кейс`; `кейс открыть`; `кейс, пожалуйста`; `паинтер`; `/crate`; `/case`; `/crate@BotPAInter_Q_bot`

---

### **Команды для ежедневного бонуса:**
**__Бонус:__**  
– `бонус`; `приз`; `гифт`; `подарок`; `/gift`

---

### **Команды для рулетки:**
**__Рулетка:__**  
– `рл`; `рулетка`; `рулет`  
– `.рл стоп`; `.рл остановить`; `.рл забрать`  
– `.рулетка стоп`; `.рулетка остановить`; `.рулетка забрать`  
– `.рулет стоп`; `.рулет остановить`; `.рулет забрать`

---

### **Команды для баннеров:**
**__Баннеры:__**  
– `банер`; `баннер`; `фон`; `бг`; `бекграунд`; `/banner`

---

### **Команды для рамок:**
**__Рамки:__**  
– `рамки`; `рамка`; `/frame`

---

### **Команды для подрамников:**
**__Подрамники:__**  
– `подрамники`; `подрамник`; `подрамка`; `подрамки`

---

### **Команды для передачи коинов:**
**__Передача коинов:__**  
– `отдать`; `передать`; `дать`; `подарить`; `гив`  
Пример: `дать 1000` или `гив все/всё`

---

### **Команды для администраторов:**
**__Администраторы:__**  
– `+адм`; `+админ` (добавить администратора)  
– `-адм`; `-админ` (удалить администратора)  
– `админы`; `кто админ`; `стафф` (список администраторов)

---

### **Команды для репортов:**
**__Репорт:__**  
– `репорт` (в ответ на сообщение пользователя)

---

### **Команды для РП-действий:**
**__РП-действия:__**  
– `рп` (в ответ на сообщение пользователя)  
– `действия` (список доступных РП-действий)

---

### **Команды для информации:**
**__Информация:__**  
– `паинтер инфа`; `паинтер вероятность`; `принтер инфа`; `принтер вероятность`  
Пример: `паинтер инфа я стану миллионером`
"""
    return help_message
    
def format_banner_message(banner_info, banner_index):
    return (
        f"🗺 *Баннер #`{banner_index + 1}` \"{banner_info['name']}\"*\n\n\n"
        f"💰 _Цена – {banner_info.get('price', 0)} Q коинов_\n\n"
        f"© _Автор – `{banner_info.get('author', 'Неизвестен')}`_\n\n"
        f"📖 _Описание:_\n"
        f"{banner_info['description']}"
    )

@bot.callback_query_handler(func=lambda call: call.data == 'no_access')
def handle_no_access(call):
    """Обрабатывает нажатие на кнопку "🔒 Эксклюзив"."""
    bot.answer_callback_query(call.id, "⚠️ Этот элемент доступен только для определенных пользователей.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('underframe_'))
def underframe_callback_handler(call):
    try:
        # Разделяем callback_data на части
        action, underframe_index, user_id_str = call.data.split('_')[1], int(call.data.split('_')[2]), call.data.split('_')[3]
        user_id = str(call.from_user.id)

        # Проверяем, является ли пользователь тем, кому предназначена кнопка
        if user_id != user_id_str:
            bot.answer_callback_query(call.id, "⚠️ Эта кнопка не для вас!")
            return

        data = load_user_data(user_id)
        underframe_index = int(underframe_index)
        num_underframes = len(underframes)

        if action == 'back':
            underframe_index = (underframe_index - 1) % num_underframes
        elif action == 'next':
            underframe_index = (underframe_index + 1) % num_underframes
        elif action == 'buy':
            underframe_info = underframes[underframe_index]
            if data['balance'] >= underframe_info['price']:
                data['balance'] -= underframe_info['price']
                underframe_filename = underframe_info['filename']
                if 'purchased_underframes' not in data:
                    data['purchased_underframes'] = []
                if underframe_filename not in data['purchased_underframes']:
                    data['purchased_underframes'].append(underframe_filename)
                save_user_data(user_id, data)
                bot.answer_callback_query(call.id, "Подрамник успешно куплен!")
            else:
                bot.answer_callback_query(call.id, "Недостаточно Q коинов!")
        elif action == 'wear':
            underframe_info = underframes[underframe_index]
            underframe_filename = underframe_info['filename']
            data['current_underframe'] = underframe_filename
            save_user_data(user_id, data)
            bot.answer_callback_query(call.id, "Подрамник успешно одет!")

        markup = create_underframe_keyboard(underframe_index, user_id)
        underframe_info = underframes[underframe_index]
        underframe_filename = underframe_info['filename']
        avatar_file = get_user_avatar(bot, user_id)

        banner_filename = data['current_banner']
        frame_filename = data.get('current_frame')

        if avatar_file:
            image_blob = create_banner_with_all(banner_filename, avatar_file, frame_filename, underframe_filename)
        else:
            image_blob = create_banner_with_all(banner_filename, "avatar.png", frame_filename, underframe_filename)

        if image_blob:
            bot.edit_message_media(
                media=types.InputMediaPhoto(image_blob, caption=format_underframe_message(underframe_info)),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        else:
            bot.answer_callback_query(call.id, "Ошибка при создании изображения!")

    except Exception as e:
        print(f"Ошибка в underframe_callback_handler: {e}")
        bot.answer_callback_query(call.id, "⚠️ Произошла ошибка.")

@bot.message_handler(func=lambda message: message.text.lower() in ['подрамники', 'подрамник', 'подрамка', 'подрамки'])
@ignore_old_messages
def show_underframe_menu(message):
    user_id = str(message.from_user.id)
    data = load_user_data(user_id)
    current_underframe_index = 0
    markup = create_underframe_keyboard(current_underframe_index, user_id)
    underframe_info = underframes[current_underframe_index]
    underframe_filename = underframe_info['filename']

    avatar_file = get_user_avatar(bot, user_id)

    banner_filename = data['current_banner']
    frame_filename = data.get('current_frame')

    if avatar_file:
        image_blob = create_banner_with_all(banner_filename, avatar_file, frame_filename, underframe_filename)
    else:
        image_blob = create_banner_with_all(banner_filename, "avatar.png", frame_filename, underframe_filename)

    if image_blob:
        bot.send_photo(message.chat.id, image_blob, caption=format_underframe_message(underframe_info), reply_markup=markup)
    else:
        bot.reply_to(message, "Ошибка при создании изображения!")

@bot.message_handler(func=lambda message: message.text.lower().startswith(('подрамники', 'подрамник', 'подрамка', 'подрамки')))
@ignore_old_messages
def handle_underframe_command(message):
    """Обрабатывает команды вида 'подрамник 2'."""
    parts = message.text.lower().split()
    if len(parts) == 2 and parts[1].isdigit():
        underframe_index = int(parts[1]) - 1  # Нумерация с 1 для пользователя
        show_underframe_by_index(message, underframe_index)
    else:
        show_underframe_menu(message)

# Регистрируем обработчик команды помощи
@bot.message_handler(commands=['help'])
@ignore_old_messages
def help_command(message):
    bot.reply_to(message, create_help_message(), parse_mode="Markdown")

# Регистрируем обработчик текстовых команд помощи
@bot.message_handler(func=lambda message: message.text.lower() in ['хелп', 'помощь', 'помогите'])
@ignore_old_messages
def text_help_command(message):
    bot.reply_to(message, create_help_message(), parse_mode="Markdown")
    
@bot.message_handler(func=lambda message: message.reply_to_message and message.text.lower().startswith(('отдать', 'передать', 'дать', 'подарить', 'гив')))
@ignore_old_messages
def handle_give_coins(message):
    give_coins(bot, message)

@bot.message_handler(func=lambda message: message.text.lower() in ['рамки', 'рамка', '/frame'])
@ignore_old_messages
def show_frame_menu(message):
    user_id = str(message.from_user.id)
    data = load_user_data(user_id)
    current_frame_index = 0
    markup = create_frame_keyboard(current_frame_index, user_id)
    frame_info = frames[current_frame_index]
    frame_filename = frame_info['filename']

    avatar_file = get_user_avatar(bot, user_id)

    if avatar_file:
        image_blob = create_framed_image(data['current_banner'], avatar_file, frame_filename)
    else:
        image_blob = create_framed_image(data['current_banner'], "avatar.png", frame_filename)

    if image_blob:
        bot.send_photo(message.chat.id, image_blob, caption=format_frame_message(frame_info), reply_markup=markup)
    else:
        bot.reply_to(message, "⚠️ Ошибка при создании изображения с рамкой.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('frame_'))
def frame_callback_handler(call):
    try:
        # Разделяем callback_data на части
        action, frame_index, user_id_str = call.data.split('_')[1], int(call.data.split('_')[2]), call.data.split('_')[3]
        user_id = str(call.from_user.id)

        # Проверяем, является ли пользователь тем, кому предназначена кнопка
        if user_id != user_id_str:
            bot.answer_callback_query(call.id, "⚠️ Эта кнопка не для вас!")
            return

        data = load_user_data(user_id)
        frame_index = int(frame_index)
        num_frames = len(frames)

        # Обрабатываем действия
        if action == 'back':
            frame_index = (frame_index - 1) % num_frames
        elif action == 'next':
            frame_index = (frame_index + 1) % num_frames
        elif action == 'buy':
            frame_info = frames[frame_index]
            if data['balance'] >= frame_info['price']:
                data['balance'] -= frame_info['price']
                frame_filename = frame_info['filename']
                if 'purchased_frames' not in data:
                    data['purchased_frames'] = []
                if frame_filename not in data['purchased_frames']:
                    data['purchased_frames'].append(frame_filename)
                save_user_data(user_id, data)
                bot.answer_callback_query(call.id, "Рамка успешно куплена!")
            else:
                bot.answer_callback_query(call.id, "Недостаточно Q коинов!")
                return
        elif action == 'wear':
            frame_info = frames[frame_index]
            frame_filename = frame_info['filename']
            data['current_frame'] = frame_filename
            save_user_data(user_id, data)
            bot.answer_callback_query(call.id, "Рамка успешно одета!")

        # Получаем текущие данные для сравнения
        frame_info = frames[frame_index]
        markup = create_frame_keyboard(frame_index, user_id)
        new_caption = format_frame_message(frame_info)
        
        # Проверяем текущее состояние сообщения
        current_caption = call.message.caption
        current_markup = call.message.reply_markup

        # Если ничего не изменилось, просто убираем "часики"
        if (current_caption == new_caption and 
            str(current_markup) == str(markup)):
            bot.answer_callback_query(call.id)
            return

        # Генерируем новое изображение
        avatar_file = get_user_avatar(bot, user_id)
        frame_filename = frame_info['filename']
        
        if avatar_file:
            image_blob = create_framed_image(data['current_banner'], avatar_file, frame_filename)
        else:
            image_blob = create_framed_image(data['current_banner'], "avatar.png", frame_filename)

        if not image_blob:
            bot.answer_callback_query(call.id, "⚠️ Ошибка создания изображения")
            return

        # Пытаемся обновить сообщение
        try:
            bot.edit_message_media(
                media=types.InputMediaPhoto(image_blob, caption=new_caption),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        except Exception as edit_error:
            print(f"Ошибка редактирования сообщения: {edit_error}")
            try:
                # Если не получилось изменить, отправляем новое
                bot.send_photo(
                    chat_id=call.message.chat.id,
                    photo=image_blob,
                    caption=new_caption,
                    reply_markup=markup
                )
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception as send_error:
                print(f"Ошибка отправки нового сообщения: {send_error}")
                bot.answer_callback_query(call.id, "⚠️ Ошибка обновления")

    except Exception as e:
        print(f"Критическая ошибка в frame_callback_handler: {e}")
        try:
            bot.answer_callback_query(call.id, "⚠️ Произошла ошибка")
        except:
            pass
        
@bot.message_handler(func=lambda message: message.text.lower().startswith(('рамка', 'рамки', '/frame')))
@ignore_old_messages
def handle_frame_command(message):
    """Обрабатывает команды вида 'рамка 6'."""
    parts = message.text.lower().split()
    if len(parts) == 2 and parts[1].isdigit():
        frame_index = int(parts[1]) - 1  # Нумерация с 1 для пользователя
        show_frame_by_index(message, frame_index)
    else:
        show_frame_menu(message)

@bot.message_handler(func=lambda message: message.text.lower() in ['б', 'био', 'баланс', 'балик', 'бал', 'проф', 'профиль', 'кто я'])
@ignore_old_messages
def send_balance(message):
    user_id = str(message.from_user.id)
    data = load_user_data(user_id)
    best_card = data.get('best_card')
    time_until_next_case = get_time_until_next_case(user_id)
    message_count = data.get('message_count', 0)
    rank = get_user_rank(message_count)

    # Форматируем текст профиля
    profile_text = (
        f"💰 *Баланс игрока {rank} {message.from_user.first_name} [*`{user_id}`*]:*\n\n\n"
        f"💸 _Q коины – {data['balance']}_\n\n"
        f"💬 _Написано сообщений – {message_count}_\n\n"
        f"📦 _Открыто кейсов – {data['case_count']}_\n\n"
        f"🎴 _Наилучшая карточка – {best_card['name'] if best_card else 'Нет'}_\n\n"
        f"⏳ _До следующего кейса – {time_until_next_case}_\n\n\n"
        f"❗️ *Подробная информация в команде* `инфа`."
    )

    # Генерируем изображение профиля
    avatar_file = get_user_avatar(bot, user_id)
    image_blob = create_banner_with_all(
        data['current_banner'],
        avatar_file or "avatar.png",
        data.get('current_frame'),
        data.get('current_underframe')
    )

    if image_blob:
        bot.send_photo(message.chat.id, image_blob, caption=profile_text, parse_mode="Markdown")
    else:
        bot.reply_to(message, profile_text, parse_mode="Markdown")

def get_item_info(filename, items_list):
    """Возвращает название и цену элемента по имени файла"""
    if not filename:
        return None, None
    for item in items_list:
        if item['filename'] == filename:
            return item['name'], item.get('price')
    return "Стандартный", 0

@bot.message_handler(func=lambda message: message.text.lower() in ['кейс', 'к', 'касик', 'кейсик', 'открыть кейс', 'кейс открыть', 'кейс, пожалуйста', 'паинтер', '/crate', '/case', '/crate@BotPAInter_Q_bot'])
@ignore_old_messages
def open_case(message):
    user_id = str(message.from_user.id)
    current_time = time.time()
    data = load_user_data(user_id)
    
    # Проверка кулдауна
    last_case_time = data.get('last_case_time', 0)
    if current_time - last_case_time < 600:
        remaining_time = 600 - (current_time - last_case_time)
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        bot.reply_to(message, f"⏳ Кейс можно открывать только раз в 10 минут. Осталось: {minutes:02d}:{seconds:02d}.")
        return

    # Получение карточки
    card = get_random_card(user_id)
    time_until_next_case = get_time_until_next_case(user_id)
    rank = get_user_rank(data['message_count'])
    
    # Обновление данных
    data['last_case_time'] = current_time
    data['balance'] += card['q_coins']
    data['case_count'] += 1
    data['total_coins_earned'] += card['q_coins']
    
    # Обновление лучшей карты
    if not data['best_card'] or card['q_coins'] > data['best_card']['q_coins']:
        data['best_card'] = card
    
    # Сохранение последних карт
    data['last_cards'] = data.get('last_cards', [])[-4:] + [card]
    save_user_data(user_id, data)  # Важно сохранить перед отправкой
    
    # Формирование сообщения
    response = (
        f"🎴 *{rank} {message.from_user.first_name}, вы открыли кейс и получили карточку \"{card['name']}\"!*\n\n\n"
        f"💸 _Она принесла тебе {card['q_coins']} Q коинов_\n\n"
        f"🧬 _Её редкость – {card['rarity']}_\n\n"
        f"📦 _Это твой {data['case_count']} кейс по счету_\n\n"
        f"⏳ _До следующего кейса – {time_until_next_case}_"
    )
    
    # Повторные попытки отправки
    max_attempts = 3
    success = False
    file_path = os.path.join(os.path.dirname(__file__), card['filename'])
    
    for attempt in range(1, max_attempts+1):
        try:
            if card['type'] == 'photo':
                with open(file_path, 'rb') as photo:
                    bot.send_photo(message.chat.id, photo, caption=response, parse_mode="Markdown")
            elif card['type'] == 'video':
                with open(file_path, 'rb') as video:
                    bot.send_video(message.chat.id, video, caption=response, parse_mode="Markdown")
            
            success = True
            break
        except Exception as e:
            print(f"Попытка {attempt}/{max_attempts} ошибка: {str(e)}")
            if attempt < max_attempts:
                time.sleep(5)  # Пауза между попытками
    
    # Обработка неудачи
    if not success:
        error_msg = (
            f"⚠️ *Техническая ошибка!*\n\n"
            f"Карточка: {card['name']} ({card['rarity']})\n"
            f"Q коины: +{card['q_coins']} были зачислены\n"
            f"Попробуйте позже или обратитесь к администратору"
        )
        bot.reply_to(message, error_msg, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text.lower() in ['бонус', 'приз', 'гифт', 'подарок', '/gift'])
@ignore_old_messages
def get_daily_gift(message):
    user_id = str(message.from_user.id)
    data = load_user_data(user_id)
    current_time = time.time()
    last_gift_time = data.get('last_gift_time', 0)

    # Проверяем, прошло ли 24 часа с последнего получения бонуса
    if current_time - last_gift_time < 86400:
        remaining_time = 86400 - (current_time - last_gift_time)
        hours = int(remaining_time // 3600)
        minutes = int((remaining_time % 3600) // 60)
        seconds = int(remaining_time % 60)
        bot.reply_to(message, f"⏳Вы уже забирали ежедневный приз, приходите через {hours:02d}:{minutes:02d}:{seconds:02d}.")
        return

    # Генерируем случайное количество коинов
    gift_amount = random.randint(100, 1000)  # Например, от 50 до 200
    data['balance'] += gift_amount
    data['last_gift_time'] = current_time
    save_user_data(user_id, data)

    bot.reply_to(message, f"🎁Вы забрали ежедневный подарок в размере {gift_amount} Q коинов!")

@bot.message_handler(func=lambda message: message.text.lower() in ['банер', 'баннер', 'фон', 'бг', 'бекграунд', '/banner'])
@ignore_old_messages
def show_banner_menu(message):
    user_id = str(message.from_user.id)
    data = load_user_data(user_id)
    current_banner_index = 0  # Добавлен индекс текущего баннера
    markup = create_banner_keyboard(current_banner_index, user_id)
    banner_info = backgrounds[current_banner_index]
    banner_filename = banner_info['filename']

    avatar_file = get_user_avatar(bot, user_id)

    if avatar_file:
        image_blob = create_framed_image(banner_filename, avatar_file, None)
    else:
        image_blob = create_framed_image(banner_filename, "avatar.png", None)

    if image_blob:
        # Передаем banner_index в format_banner_message
        bot.send_photo(
            message.chat.id,
            image_blob,
            caption=format_banner_message(banner_info, current_banner_index),
            reply_markup=markup
        )
    else:
        bot.reply_to(message, "⚠️ Ошибка при создании изображения баннера.")

# Функция для создания клавиатуры баннера
def create_banner_keyboard(banner_index, user_id):
    data = load_user_data(user_id)
    banner_info = backgrounds[banner_index]
    banner_filename = banner_info['filename']
    is_purchased = banner_filename in data['purchased_banners'] or banner_filename == 'default_banner.jpg'

    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton('⬅️', callback_data=f'banner_back_{banner_index}_{user_id}')

    # Проверяем, доступен ли баннер для покупки
    if banner_info.get('exclusive_to') is None or str(banner_info['exclusive_to']) == user_id:
        if is_purchased:
            btn_buy = types.InlineKeyboardButton('✅Одеть', callback_data=f'banner_wear_{banner_index}_{user_id}')
        else:
            btn_buy = types.InlineKeyboardButton(f'💰Купить ({banner_info["price"]} Q)', callback_data=f'banner_buy_{banner_index}_{user_id}')
    else:
        # Если баннер эксклюзивный и не для этого пользователя, кнопка "Купить" не отображается
        btn_buy = types.InlineKeyboardButton('🔒 Эксклюзив', callback_data='no_access')

    btn_next = types.InlineKeyboardButton('➡️', callback_data=f'banner_next_{banner_index}_{user_id}')
    markup.add(btn_back, btn_buy, btn_next)
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('banner_'))
def banner_callback_handler(call):
    try:
        action, banner_index, user_id_str = call.data.split('_')[1], int(call.data.split('_')[2]), call.data.split('_')[3]
        user_id = str(call.from_user.id)

        if user_id != user_id_str:
            bot.answer_callback_query(call.id, "⚠️ Эта кнопка не для вас!")
            return

        data = load_user_data(user_id)
        banner_index = int(banner_index)
        num_banners = len(backgrounds)

        if action == 'back':
            banner_index = (banner_index - 1) % num_banners
        elif action == 'next':
            banner_index = (banner_index + 1) % num_banners
        elif action == 'buy':
            banner_info = backgrounds[banner_index]
            if data['balance'] >= banner_info['price']:
                data['balance'] -= banner_info['price']
                banner_filename = banner_info['filename']
                if banner_filename not in data['purchased_banners']:
                    data['purchased_banners'].append(banner_filename)
                save_user_data(user_id, data)
                bot.answer_callback_query(call.id, "Баннер успешно куплен!")
            else:
                bot.answer_callback_query(call.id, "Недостаточно Q коинов!")
        elif action == 'wear':
            banner_info = backgrounds[banner_index]
            banner_filename = banner_info['filename']
            data['current_banner'] = banner_filename
            save_user_data(user_id, data)
            bot.answer_callback_query(call.id, "Баннер успешно одет!")

        markup = create_banner_keyboard(banner_index, user_id)
        banner_info = backgrounds[banner_index]
        avatar_file = get_user_avatar(bot, user_id)

        if avatar_file:
            image_blob = create_banner_with_all(banner_info['filename'], avatar_file, None, None)
        else:
            image_blob = create_banner_with_all(banner_info['filename'], "avatar.png", None, None)

        if image_blob:
            # Добавлен banner_index в вызов функции
            bot.edit_message_media(
                media=types.InputMediaPhoto(
                    image_blob, 
                    caption=format_banner_message(banner_info, banner_index)  # Исправлено здесь
                ),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        else:
            bot.answer_callback_query(call.id, "⚠️ Ошибка при создании изображения!")

    except Exception as e:
        print(f"Ошибка в banner_callback_handler: {e}")
        bot.answer_callback_query(call.id, "⚠️ Произошла ошибка.")

@bot.message_handler(func=lambda message: message.text.lower().startswith(('банер', 'баннер', 'фон', 'бг', 'бекграунд', '/banner')))
@ignore_old_messages
def handle_banner_command(message):
    """Обрабатывает команды вида 'баннер 3'."""
    parts = message.text.lower().split()
    if len(parts) == 2 and parts[1].isdigit():
        banner_index = int(parts[1]) - 1  # Нумерация с 1 для пользователя
        show_banner_by_index(message, banner_index)
    else:
        show_banner_menu(message)
        
@bot.message_handler(func=lambda message: message.text.lower().startswith(('+адм', '+админ')))
@ignore_old_messages
def add_admin(message):
    """Добавляет администратора."""
    user_id = str(message.from_user.id)
    if not is_owner(user_id):
        bot.reply_to(message, "⚠️ Только владелец может добавлять администраторов.")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Эта команда должна быть ответом на сообщение пользователя.")
        return

    new_admin_id = str(message.reply_to_message.from_user.id)
    admins_data = load_admins()

    if new_admin_id in admins_data["admins"]:
        bot.reply_to(message, "⚠️ Этот пользователь уже является администратором.")
    else:
        admins_data["admins"].append(new_admin_id)
        save_admins(admins_data)
        bot.reply_to(message, f"✅ Пользователь {message.reply_to_message.from_user.first_name} добавлен в список администраторов.")

@bot.message_handler(func=lambda message: message.text.lower().startswith(('-адм', '-админ')))
@ignore_old_messages
def remove_admin(message):
    """Удаляет администратора."""
    user_id = str(message.from_user.id)
    if not is_owner(user_id):
        bot.reply_to(message, "⚠️ Только владелец может удалять администраторов.")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Эта команда должна быть ответом на сообщение пользователя.")
        return

    admin_id = str(message.reply_to_message.from_user.id)
    admins_data = load_admins()

    if admin_id not in admins_data["admins"]:
        bot.reply_to(message, "⚠️ Этот пользователь не является администратором.")
    else:
        admins_data["admins"].remove(admin_id)
        save_admins(admins_data)
        bot.reply_to(message, f"✅ Пользователь {message.reply_to_message.from_user.first_name} удален из списка администраторов.")

@bot.message_handler(func=lambda message: message.text.lower() in ['админы', 'кто админ', 'стафф'])
@ignore_old_messages
def list_admins(message):
    """Показывает список администраторов."""
    admins_data = load_admins()
    owner = bot.get_chat(admins_data["owner_id"])
    admins_list = [bot.get_chat(admin_id).first_name for admin_id in admins_data["admins"]]

    response = f"👑 Владелец: {owner.first_name}\n"
    if admins_list:
        response += "👮 Администраторы:\n" + "\n".join(admins_list)
    else:
        response += "👮 Администраторы отсутствуют."

    bot.reply_to(message, response)
    
@bot.message_handler(func=lambda message: message.text.lower().startswith('репорт'))
@ignore_old_messages
def report_message(message):
    """Обрабатывает команду репорт."""
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Эта команда должна быть ответом на сообщение пользователя.")
        return

    # Получаем причину репорта
    reason = message.text[len('репорт'):].strip()
    if not reason:
        bot.reply_to(message, "⚠️ Укажите причину репорта.")
        return

    # Получаем информацию о пользователях
    reporter = message.from_user
    reported_user = message.reply_to_message.from_user
    reported_message = message.reply_to_message

    # Формируем ссылку на сообщение
    chat_id = reported_message.chat.id
    message_id = reported_message.message_id
    message_link = f"https://t.me/c/{str(chat_id).replace('-100', '')}/{message_id}"

    # Формируем сообщение для администраторов
    report_text = (
        f"❗ Пользователь {reporter.first_name} (@{reporter.username}) репортнул сообщение:\n"
        f"{message_link}\n"
        f"От пользователя {reported_user.first_name} (@{reported_user.username})\n"
        f"Причина: {reason}\n\n"
        f"Просьба принять меры, если репорт был не ложным."
    )

    # Отправляем сообщение всем администраторам
    admins_data = load_admins()
    for admin_id in admins_data["admins"] + [admins_data["owner_id"]]:
        try:
            bot.send_message(admin_id, report_text)
        except Exception as e:
            print(f"Ошибка при отправке сообщения администратору {admin_id}: {e}")

    # Отправляем подтверждение пользователю
    bot.reply_to(message, "❗ Репорт отправлен администраторам.")
    
# Обработчик команды "рп"
@bot.message_handler(func=lambda message: message.text.lower().startswith('рп '))
@ignore_old_messages
def handle_rp_command(message):
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Эта команда должна быть ответом на сообщение другого пользователя.")
        return

    # Получаем действие из команды
    action = message.text[3:].strip().lower()  # Убираем "рп " и приводим к нижнему регистру

    # Получаем имена пользователей
    sender_name = message.from_user.first_name
    target_name = message.reply_to_message.from_user.first_name

    # Получаем все доступные действия
    all_actions = get_all_rp_actions()

    # Если действие "рандом", выбираем случайное действие
    if action == "рандом":
        action = random.choice(list(all_actions.keys()))
    elif action not in all_actions:
        # Если действие не найдено, отправляем список доступных действий
        bot.reply_to(message, "⚠️ Действие не найдено. Используйте команду `действия`, чтобы увидеть список доступных действий.", parse_mode="Markdown")
        return

    # Получаем прошедшее время для действия
    past_action = all_actions[action]

    # Формируем сообщение
    rp_message = f"👤 {sender_name} {past_action} {target_name}."

    # Отправляем сообщение в ответ на сообщение, на которое вы ответили
    bot.reply_to(message.reply_to_message, rp_message)
    
# Обработчик команды "рп действия"
@bot.message_handler(func=lambda message: message.text.lower() == 'действия')
@ignore_old_messages
def show_rp_actions(message):
    # Формируем список всех действий
    actions_list = []
    for category, actions in RP_ACTIONS.items():
        actions_list.append(f"**{category}:**\n" + "\n".join([f"`{action}`" for action in actions.keys()]))

    # Отправляем сообщение с действиями
    bot.reply_to(message, "📜 Доступные РП-действия:\n\n" + "\n\n".join(actions_list), parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text.lower().startswith(('паинтер инфа', 'паинтер вероятность', 'принтер инфа', 'принтер вероятность')))
@ignore_old_messages
def printer_info(message):
    # Получаем текст сообщения
    text = message.text.lower()

    # Извлекаем часть сообщения после команды
    if text.startswith('паинтер инфа'):
        command = 'паинтер инфа'
    elif text.startswith('паинтер вероятность'):
        command = 'паинтер вероятность'
    elif text.startswith('принтер инфа'):
        command = 'принтер инфа'
    elif text.startswith('принтер вероятность'):
        command = 'принтер вероятность'
    else:
        return  # Если команда не распознана, ничего не делаем

    # Убираем команду из текста
    info_text = message.text[len(command):].strip()

    # Если текст после команды пустой, отправляем сообщение с ошибкой
    if not info_text:
        bot.reply_to(message, "⚠️ Пожалуйста, укажите, что вы хотите узнать. Например: `паинтер инфа я стану миллионером`.")
        return

    # Генерируем случайный процент от 0 до 100
    probability = random.randint(0, 100)

    # Формируем ответное сообщение
    response = f"🤔 {message.from_user.first_name}, я думаю, что шанс на то, что {info_text} составляет {probability}%."

    # Отправляем сообщение
    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: message.text.lower() in ['топ', 'лидеры', 'лучшие'])
@ignore_old_messages
def show_top_menu(message):
    """Показывает меню с выбором топа."""
    markup = types.InlineKeyboardMarkup()
    btn_messages = types.InlineKeyboardButton('📊 Сообщения', callback_data='top_messages')
    btn_coins = types.InlineKeyboardButton('💰 Коины', callback_data='top_coins')
    btn_cases = types.InlineKeyboardButton('🎴 Открытые кейсы', callback_data='top_cases')
    btn_cards = types.InlineKeyboardButton('🃏 Лучшая карточка', callback_data='top_cards')
    markup.add(btn_messages, btn_coins, btn_cases, btn_cards)

    bot.send_message(message.chat.id, "📊 Какой топ вы хотите посмотреть?", reply_markup=markup)
    
@bot.callback_query_handler(func=lambda call: call.data.startswith('top_'))
def handle_top_callback(call):
    """Обрабатывает выбор топа."""
    try:
        top_type = call.data.split('_')[1]
        user_id = str(call.from_user.id)
        user_data = load_user_data(user_id)

        if top_type == 'messages':
            top_users = get_top_messages()
            title = "📊 Топ 10 игроков по сообщениям:"
            user_value = user_data.get('message_count', 0)
        elif top_type == 'coins':
            top_users = get_top_coins()
            title = "💰 Топ 10 игроков по :"
            user_value = user_data.get('balance', 0)
        elif top_type == 'cases':
            top_users = get_top_cases()
            title = "🎴 Топ 10 игроков по открытым кейсам:"
            user_value = user_data.get('case_count', 0)
        elif top_type == 'cards':
            top_users = get_top_cards()
            title = "🃏 Топ 10 игроков по лучшей карточке:"
            user_value = user_data.get('best_card', {}).get('q_coins', 0)
        else:
            bot.answer_callback_query(call.id, "⚠️ Неизвестный тип топа.")
            return

        # Формируем текст топа
        top_text = title + "\n\n"
        for i, user in enumerate(top_users):
            user_id = user['user_id']
            try:
                # Пытаемся получить имя пользователя
                user_name = bot.get_chat(user_id).first_name
            except Exception as e:
                # Если не удалось получить имя, используем user_id
                print(f"Ошибка при получении имени пользователя {user_id}: {e}")
                user_name = f"Пользователь {user_id}"

            value = user['value']
            if i == 0:
                top_text += f"🥇 {user_name} – {value}\n"
            elif i == 1:
                top_text += f"🥈 {user_name} – {value}\n"
            elif i == 2:
                top_text += f"🥉 {user_name} – {value}\n"
            else:
                top_text += f"🎖️ {user_name} – {value}\n"

        # Добавляем информацию о текущем игроке
        user_name = call.from_user.first_name
        top_text += f"\n👤 {user_name} – {user_value}"

        # Отправляем топ новым сообщением
        bot.send_message(call.message.chat.id, top_text)

        # Подтверждаем обработку callback-запроса (убираем индикатор загрузки)
        bot.answer_callback_query(call.id)

    except Exception as e:
        print(f"Ошибка в handle_top_callback: {e}")
        bot.answer_callback_query(call.id, "⚠️ Произошла ошибка.")

@bot.message_handler(func=lambda message: message.text.lower().startswith(('бр ', 'бакшот роулет ', 'рл ', 'рулетка ')))
@ignore_old_messages
def start_roulette(message):
    user_id = str(message.from_user.id)
    data = load_user_data(user_id)
    balance = data['balance']

    # Проверяем кулдаун
    current_time = time.time()
    last_roulette_time = data.get('last_roulette_time', 0)
    cooldown = 600  # 10 минут в секундах

    if current_time - last_roulette_time < cooldown:
        remaining_time = cooldown - (current_time - last_roulette_time)
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        bot.reply_to(message, f"⏳ Вы сможете сыграть в рулетку через {minutes:02d}:{seconds:02d}.")
        return

    # Извлекаем ставку из сообщения
    parts = message.text.lower().split()
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Укажите ставку. Например: `рулетка 1000` или `рулетка все`.", parse_mode="Markdown")
        return

    bet_str = parts[1].lower()

    # Обрабатываем ставку "все" или "всё"
    if bet_str in ['все', 'всё']:
        bet = min(balance, 10000000000)  # Лимит 10 миллиардов
    elif bet_str.endswith('к'):
        try:
            bet = int(bet_str[:-1]) * 1000
        except ValueError:
            bot.reply_to(message, "⚠️ Некорректная ставка. Укажите число или 'все/всё'.")
            return
    elif bet_str.endswith('кк') or bet_str.endswith('м'):
        try:
            bet = int(bet_str[:-2]) * 1000000
        except ValueError:
            bot.reply_to(message, "⚠️ Некорректная ставка. Укажите число или 'все/всё'.")
            return
    elif bet_str.endswith('мк'):
        try:
            bet = int(bet_str[:-2]) * 1000000000
        except ValueError:
            bot.reply_to(message, "⚠️ Некорректная ставка. Укажите число или 'все/всё'.")
            return
    else:
        try:
            bet = int(bet_str)
        except ValueError:
            bot.reply_to(message, "⚠️ Некорректная ставка. Укажите число или 'все/всё'.")
            return

    # Проверяем, что ставка в пределах допустимого
    if bet < 100:
        bot.reply_to(message, "⚠️ Минимальная ставка – 100 Q коинов.")
        return
    elif bet > 10000000000:
        bot.reply_to(message, "❗ Ставка слишком большая! Максимальная ставка – 10.000.000.000.")
        return
    elif bet > balance:
        bot.reply_to(message, "❌ Недостаточно Q коинов на балансе для такой ставки.")
        return

    # Генерируем пули (от 3 до 8)
    total_bullets = random.randint(3, 8)
    live_bullets = random.randint(3, total_bullets - 3)
    blank_bullets = total_bullets - live_bullets

    # Формирование начального сообщения
    rank = get_user_rank(data['message_count'])
    initial_text = (
        f"🔫 *{rank} {message.from_user.first_name}, вы решились сыграть в рулетку.*\n\n\n"
        f"💰 _Ваша ставка – {bet} Q коинов_\n\n"
        f"✖️ _Множитель – ×{1.00}_\n\n"
        f"💊 *Пули:*\n\n"
        f"🔴 _Заряженные – {live_bullets}_\n\n"
        f"🔵 _Холостые – {blank_bullets}_\n\n\n"
        f"❗️ *Запомни количество пуль! Во время игры они не будут показаны.*"
    )

    markup = types.InlineKeyboardMarkup()
    btn_rules = types.InlineKeyboardButton('📖 Правила', callback_data='roulette_rules')
    btn_start = types.InlineKeyboardButton('▶️ Старт', callback_data=f'roulette_start_{user_id}')
    markup.add(btn_rules, btn_start)

    bot.send_message(message.chat.id, initial_text, 
                    parse_mode="Markdown", 
                    reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'roulette_rules')
def show_rules(call):
    rules_text = (
        "📖 *Правила игры в рулетку:*\n\n"
        "👨 *Кнопка \"В себя\"*\n"
        "🔴 _Заряженным – проигрыш_\n"
        "🔵 _Холостым – +×0.20 к множителю ставки_\n\n"
        "👤 *Кнопка \"В манекен\"*\n"
        "🔴 _Заряженным – +×0.30 к множителю ставки_\n"
        "🔵 _Холостым – -×0.30 от множителя ставки_"
    )
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, rules_text, parse_mode="Markdown")

# Обработчик для кнопки "▶️ Старт"
@bot.callback_query_handler(func=lambda call: call.data.startswith('roulette_start_'))
def start_game(call):
    user_id = call.data.split('_')[2]
    if str(call.from_user.id) != user_id:
        bot.answer_callback_query(call.id, "⚠️ Эта кнопка не для вас!")
        return

    data = load_user_data(user_id)
    roulette_data = data['roulette']

    # Создаем клавиатуру с кнопками "В себя" и "В манекен"
    markup = create_shoot_keyboard(user_id)

    response = (
        f"🔫 *СТРЕЛЯЙ! Но... В манекена или себя?*\n\n\n"
        f"✖️ Множитель: x{roulette_data['multiplier']:.2f}"
    )

    bot.edit_message_text(response, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('roulette_shoot_self_'))
def handle_shoot_self(call):
    user_id = call.data.split('_')[3]
    if str(call.from_user.id) != user_id:
        bot.answer_callback_query(call.id, "⚠️ Эта кнопка не для вас!")
        return

    data = load_user_data(user_id)
    roulette_data = data['roulette']

    # Выбираем случайную пулю
    if roulette_data['remaining_live'] > 0 and roulette_data['remaining_blank'] > 0:
        bullet_type = random.choice(['live', 'blank'])
    elif roulette_data['remaining_live'] > 0:
        bullet_type = 'live'
    else:
        bullet_type = 'blank'

    # Обновляем оставшиеся пули
    if bullet_type == 'live':
        roulette_data['remaining_live'] -= 1
    else:
        roulette_data['remaining_blank'] -= 1
    roulette_data['remaining_bullets'] -= 1

    # Обновляем множитель в зависимости от типа пули
    if bullet_type == 'blank':
        roulette_data['multiplier'] += 0.20
        result_message = "😮‍💨 *Холостой в себя! +×0.20 к множителю ставки.*"
    else:
        roulette_data['multiplier'] = 0
        result_message = "🤕 *Вы попали в себя заряженным патроном! Вся ставка сгорела.*\n\n\n⏳ _Попробуйте еще раз через 10 минут_"
        
        # Принудительно завершаем игру
        final_multiplier = 0
        bet = roulette_data['bet']
        winnings = 0  # Проигрыш всей ставки

        # Обновляем баланс
        data['balance'] -= bet
        del data['roulette']
        save_user_data(user_id, data)

        # Удаляем сообщение и отправляем результат
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, result_message)
        return  # Важно: завершаем функцию здесь

    # Сохраняем обновленные данные (только для холостой пули)
    data['roulette'] = roulette_data
    save_user_data(user_id, data)

    # Проверяем, закончились ли пули (только для холостой пули)
    if roulette_data['remaining_bullets'] == 0:
        final_multiplier = roulette_data['multiplier']
        bet = roulette_data['bet']
        winnings = int(bet * final_multiplier)

        if final_multiplier > 1.00:
            result_message = f"🎊 Поздравляю, {call.from_user.first_name}! Ваш множитель – ×{final_multiplier:.2f}. Выигрыш {winnings} Q коинов!"
        else:
            result_message = f"😥 Сожалею, {call.from_user.first_name}. Ваш множитель – ×{final_multiplier:.2f}. Проигрыш {bet - winnings} Q коинов."

        data['balance'] += winnings - bet
        del data['roulette']
        save_user_data(user_id, data)

        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, result_message)
    else:
        markup = create_shoot_keyboard(user_id)
        response = (
            f"✖️ Множитель: ×{roulette_data['multiplier']:.2f}\n"
            f"{result_message}"
        )
        bot.edit_message_text(response, call.message.chat.id, call.message.message_id, reply_markup=markup)

# Обработчик для кнопки "👤 В манекен"
@bot.callback_query_handler(func=lambda call: call.data.startswith('roulette_shoot_dummy_'))
def handle_shoot_dummy(call):
    user_id = call.data.split('_')[3]
    if str(call.from_user.id) != user_id:
        bot.answer_callback_query(call.id, "⚠️ Эта кнопка не для вас!")
        return

    data = load_user_data(user_id)
    roulette_data = data['roulette']

    # Выбираем случайную пулю
    if roulette_data['remaining_live'] > 0 and roulette_data['remaining_blank'] > 0:
        bullet_type = random.choice(['live', 'blank'])
    elif roulette_data['remaining_live'] > 0:
        bullet_type = 'live'
    else:
        bullet_type = 'blank'

    # Обновляем оставшиеся пули
    if bullet_type == 'live':
        roulette_data['remaining_live'] -= 1
    else:
        roulette_data['remaining_blank'] -= 1
    roulette_data['remaining_bullets'] -= 1

    # Обновляем множитель в зависимости от типа пули
    if bullet_type == 'blank':
        roulette_data['multiplier'] -= 0.30
        result_message = "😒 *Холостой в манекена! -×0.30 от множителя ставки.*"
    else:
        roulette_data['multiplier'] += 0.30
        result_message = "🤯 *Заряженный в манекена! +×0.30 к множителю ставки.*"

    # Сохраняем обновленные данные
    data['roulette'] = roulette_data
    save_user_data(user_id, data)

    # Проверяем, закончились ли пули
    if roulette_data['remaining_bullets'] == 0:
        # Игра закончена, подсчитываем результат
        final_multiplier = roulette_data['multiplier']
        bet = roulette_data['bet']
        winnings = int(bet * final_multiplier)

        if final_multiplier > 1.00:
            result_message = f"🎊 Поздравляю, {call.from_user.first_name}! Вы закончили игру в рулетку, ваш множитель – ×{final_multiplier:.2f}. Вы выиграли {winnings} Q коинов!"
        else:
            result_message = f"😥 Сожалею, {call.from_user.first_name}. Вы закончили игру в рулетку, ваш множитель – ×{final_multiplier:.2f}. Вы проиграли {bet - winnings} Q коинов."

        # Обновляем баланс игрока
        data['balance'] += winnings - bet
        data['roulette_games_played'] += 1
        del data['roulette']  # Удаляем данные игры
        save_user_data(user_id, data)

        # Удаляем сообщение с игрой и отправляем результат
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, result_message)
    else:
        # Обновляем сообщение с игрой
        markup = create_shoot_keyboard(user_id)  # Используем функцию для создания клавиатуры

        response = (
            f"🔫 *СТРЕЛЯЙ! Но... В манекена или себя?*\n\n\n"
            f"✖️ Множитель: ×{roulette_data['multiplier']:.2f}\n\n"
            f"{result_message}"
        )

        bot.edit_message_text(response, call.message.chat.id, call.message.message_id, reply_markup=markup)
        
# Обработчик команды для использования промокода
@bot.message_handler(func=lambda message: message.text.lower().startswith(('промо ', 'промокод ', 'промик ')))
@ignore_old_messages
def use_promocode(message):
    user_id = str(message.from_user.id)
    data = load_user_data(user_id)
    promocodes = load_promocodes()  # Загружаем уже очищенные промокоды

    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Укажите промокод. Например: `промокод FREE100`")
        return

    promo = parts[1].upper()

    if promo not in promocodes:
        bot.reply_to(message, "❌ Такого промокода не существует.")
        return

    promo_data = promocodes[promo]

        # Проверяем, не использовал ли уже пользователь этот промокод
    if user_id in promo_data['used_by']:
        bot.reply_to(message, "❌ Вы уже активировали этот промокод ранее.")
        return

    # Начисляем деньги
    amount = promo_data['amount']
    data['balance'] += amount
    
    # Обновляем данные промокода
    promo_data['uses_left'] -= 1
    promo_data['used_by'].append(user_id)
    save_user_data(user_id, data)

    # Сохраняем промокоды (автоматически удалятся использованные)
    promocodes[promo] = promo_data
    save_promocodes(promocodes)

    # Уведомление создателю
    if promo_data['uses_left'] > 0:
        try:
            creator_id = promo_data['created_by']
            used = promo_data['total_uses'] - promo_data['uses_left']
            user_info = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
            
            bot.send_message(
                creator_id,
                f"🔔 Использован промокод {promo}\n"
                f"━━━━━━━━━━━━━━\n"
                f"👤 Пользователь: {user_info}\n"
                f"📊 Активаций: {used}/{promo_data['total_uses']}"
            )
        except Exception as e:
            print(f"Ошибка уведомления: {e}")

    bot.reply_to(message, f"🎉 Вы получили {amount} Q коинов!")

def save_promocodes(promocodes):
    """Сохраняет только активные промокоды"""
    active_promocodes = {
        code: data for code, data in promocodes.items()
        if data['uses_left'] > 0
    }
    
    try:
        with open(PROMOCODES_FILE, 'w', encoding='utf-8') as f:
            json.dump(active_promocodes, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка сохранения промокодов: {e}")

@bot.message_handler(func=lambda message: message.text.lower().startswith(('+промо ', '+промокод ', '+промик ')))
@ignore_old_messages
def create_promocode(message):
    user_id = str(message.from_user.id)
    
    if not is_promo_admin(user_id):
        bot.reply_to(message, "⚠️ Только промо-админы могут создавать промокоды")
        return

    parts = message.text.split()
    if len(parts) < 4:
        bot.reply_to(message, "⚠️ Формат команды: `+промокод [КОД] [СУММА] [ИСПОЛЬЗОВАНИЯ]`\nПример: `+промокод FREE100 1000 10`")
        return

    try:
        promo = parts[1].upper()
        amount = int(parts[2])
        uses = int(parts[3])
        
        if amount <= 0 or uses <= 0:
            bot.reply_to(message, "⚠️ Сумма и количество использований должны быть больше 0.")
            return

        promocodes = load_promocodes()

        if promo in promocodes:
            bot.reply_to(message, f"⚠️ Промокод `{promo}` уже существует.")
            return

        # Создаем промокод с обязательным полем total_uses
        promocodes[promo] = {
            'amount': amount,
            'uses_left': uses,
            'total_uses': uses,  # Обязательное поле
            'created_by': user_id,
            'created_at': time.time(),
            'used_by': [],
            'creator_name': message.from_user.first_name
        }
        save_promocodes(promocodes)

        bot.reply_to(message, f"""
✅ Промокод успешно создан!
━━━━━━━━━━━━━━
🎫 Код: `{promo}`
💰 Сумма: {amount} Q
🔄 Использований: {uses}
📌 Вы будете получать уведомления о его использовании.
        """, parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка: {str(e)}")

@bot.message_handler(func=lambda message: any(
    message.text.lower().startswith(cmd) 
    for cmd in ['мои промокоды', '.промокоды', '.промо']
))
@ignore_old_messages
def my_promocodes(message):
    user_id = str(message.from_user.id)
    if not is_promo_admin(user_id):
        bot.reply_to(message, "⚠️ Эта команда доступна только промо-админам.")
        return

    promocodes = load_promocodes()
    user_promos = {k:v for k,v in promocodes.items() if v.get('created_by') == user_id}

    if not user_promos:
        bot.reply_to(message, "ℹ️ Вы еще не создали ни одного промокода.")
        return

    response = ["📊 Ваши промокоды:"]
    for code, data in user_promos.items():
        # Обработка старых промокодов, где нет total_uses
        total_uses = data.get('total_uses', data.get('uses_left', 0))  # Для старых промокодов
        used = total_uses - data['uses_left'] if 'uses_left' in data else 0
        total = data.get('total_uses', data.get('uses_left', 0))
        
        # Формируем информацию об использовании
        usage_info = f"🔄 Использовано: {used}/{total}"
        
        # Получаем последние 3 использования (если есть)
        last_used = []
        if 'used_by' in data and data['used_by']:
            last_used = data['used_by'][-3:]
            last_used = [str(u) for u in last_used]
        
        response.append(
            f"━━━━━━━━━━━━━━\n"
            f"🎫 Код: `{code}`\n"
            f"💰 Сумма: {data.get('amount', 0)} Q коинов\n"
            f"{usage_info}\n"
            f"👤 Последние использования: {', '.join(last_used) or 'нет'}"
        )

    bot.reply_to(message, "\n".join(response), parse_mode="Markdown")

@bot.message_handler(func=lambda message: any(
    message.text.lower().startswith(cmd) 
    for cmd in ['казик', 'казино', 'каз', 'кш', 'азино']
))
@ignore_old_messages
def casino_handler(message):
    user_id = str(message.from_user.id)
    data = load_user_data(user_id)
    balance = data['balance']

    # Проверяем ставку
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Укажите ставку. Например: `казино 500` или `каз все`")
        return

    bet_str = parts[1].lower()

    # Обработка ставки
    if bet_str in ['все', 'всё']:
        bet = balance
    elif bet_str.endswith('к'):
        bet = int(bet_str[:-1]) * 1000
    elif bet_str.endswith('кк') or bet_str.endswith('м'):
        bet = int(bet_str[:-2]) * 1000000
    else:
        try:
            bet = int(bet_str)
        except ValueError:
            bot.reply_to(message, "⚠️ Некорректная ставка. Укажите число или 'все'.")
            return

    # Валидация ставки
    if bet < 100:
        bot.reply_to(message, "⚠️ Минимальная ставка — 100 Q коинов.")
        return
    if bet > balance:
        bot.reply_to(message, "❌ Недостаточно Q коинов для ставки.")
        return

    # Игровой процесс
    result = generate_casino_result()
    multiplier = calculate_multiplier(result)
    win_amount = int(bet * multiplier)
    net_result = win_amount - bet

    # Обновление статистики
    data['balance'] += net_result
    data['casino_games_played'] += 1
    
    if net_result > 0:
        data['coins_from_games'] += net_result
        data['total_coins_earned'] += net_result
    else:
        data['coins_spent_games'] += abs(net_result)
        data['total_coins_spent'] += abs(net_result)
    
    save_user_data(user_id, data)  # Сохраняем все изменения

    # Форматирование ответа
    result_display = " | ".join(result)
    if multiplier > 1.00:
        emoji = "💰🎉"
        result_text = f"Вы выиграли {win_amount} Q коинов!"
    elif multiplier == 1.00:
        emoji = "😐"
        result_text = "Ваша ставка возвращена."
    else:
        emoji = "😵‍💫"
        result_text = f"Вы проиграли {abs(net_result)} Q коинов."

    response = (
        f"🎰 *Результат казино* 🎰\n\n"
        f"➡️ {result_display}\n\n"
        f"✖️ Множитель: x{multiplier:.2f}\n"
        f"💸 Ставка: {bet} Q\n"
        f"🏆 {result_text}\n\n"
        f"💰 Новый баланс: {data['balance']} Q коинов {emoji}"
    )

    bot.reply_to(message, response, parse_mode="Markdown")
    
# В обработчике команды инфа
@bot.message_handler(func=lambda m: m.text.lower().split()[0] in ['инфа', 'инфо', 'информация', 'info', '/info'])
@ignore_old_messages
def user_info_command(message):
    user_id = str(message.from_user.id)
    data = load_user_data(user_id)
    
    # Определение статуса
    status = []
    if is_owner(user_id):
        status.append("Владелец")
    if is_admin(user_id):
        status.append("Админ")
    if is_promo_admin(user_id):  # Используем вашу проверку для разработчиков
        status.append("Разработчик")
    
    status_text = " | ".join(status) if status else "Игрок"

    # Последние 5 карточек
    last_cards = []
    for card in data.get('last_cards', [])[-5:]:
        card_entry = f"{card['name']} // {card['rarity']} // {card['q_coins']} Q"
        last_cards.append(card_entry)

    # Получаем информацию об оформлении
    banner_name, banner_price = get_item_info(data['current_banner'], backgrounds)
    frame_name, frame_price = get_item_info(data.get('current_frame'), frames)
    underframe_name, underframe_price = get_item_info(data.get('current_underframe'), underframes)
    
    total_cost = sum(filter(None, [banner_price, frame_price, underframe_price]))
        
    # Полный текст ответа
    response = (
        f"📖 *Информация о игроке ({get_user_rank(data['message_count'])}) {message.from_user.first_name}*\n\n\n"
        f"🔰 _Статус – {status_text}_\n\n"
        f"💸 _Получено Q коинов за символы – {data['coins_from_messages']}_\n\n\n"
        f"💬 _Написано сообщений – {data['message_count']}_\n\n\n"
        f"🖼 *Оформление:*\n\n"
        f"🗺 _Баннер – {banner_name} // {banner_price or 'Бесплатно'}_\n\n"
        f"🔲 _Рамка – {frame_name or 'Нет'} // {frame_price or 'Бесплатно'}_\n\n"
        f"🧱 _Подрамка – {underframe_name or 'Нет'} // {underframe_price or 'Бесплатно'}_\n\n"
        f"💸 _Итоговая стоимость – {total_cost} Q коинов_\n\n\n"
        f"💸 *Деньги:*\n\n"
        f"📈 _Получено Q коинов за все время – {data['total_coins_earned']}_\n\n"
        f"📈 _Получено Q коинов от других игроков – {data['coins_from_transfers']}_\n\n"
        f"📈 _Получено Q коинов с игр – {data['coins_from_games']}_\n\n"
        f"📉 _Потрачено Q коинов за все время – {data['total_coins_spent']}_\n\n"
        f"📉 _Потрачено Q коинов другим игрокам – {data['coins_spent_transfers']}_\n\n"
        f"📉 _В игры – {data['coins_spent_games']}_\n\n\n"
        f"🎮 *Игры:*\n\n"
        f"🎰 _Сыграно игр в казино шанса – {data['casino_games_played']}_\n\n"
        f"🔫 _Сыграно игр в рулетку – {data['roulette_games_played']}_\n\n"
        f"🎴 _Последние 5 полученных карточек:_\n" + "\n".join(last_cards)
    )

    bot.send_message(message.chat.id, response, parse_mode="Markdown")

# В функциях проверки прав
def is_promo_admin(user_id):
    """Проверяет принадлежность к вашей команде разработчиков"""
    admins_data = load_admins()
    return str(user_id) in admins_data.get("promo_admins", [])

@bot.message_handler(func=lambda message: True) # Ловит все сообщения
def message_handler(message):
    update_message_count(message.from_user.id)
    coins_earned = give_coins_for_message(message.from_user.id, message.text)

if __name__ == "__main__":
    migrate_all_users()
    backup_user_data()
    migrate_promocodes()
    notify_bot_started()
    bot.infinity_polling(none_stop=True)
