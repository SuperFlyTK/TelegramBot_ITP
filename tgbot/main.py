import os
import telebot
import threading
from datetime import datetime
import requests
import random
from dotenv import load_dotenv  # Импортируем dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Получаем токен из переменной окружения
TOKEN = os.getenv("TOKEN")

# Проверяем, загружен ли токен
if not TOKEN:
    raise ValueError("Токен не найден! Проверьте .env файл.")

bot = telebot.TeleBot(TOKEN)

# Словарь для хранения дедлайнов
deadlines = {}

# Список мотивационных цитат
MOTIVATIONAL_QUOTES = [
    "Никогда не сдавайся! Великие вещи требуют времени.",
    "Сегодня — лучший день, чтобы начать! Ты можешь всё!",
    "Ошибки — это доказательство того, что ты пробуешь. Продолжай двигаться вперёд!",
    "Верь в себя! Ты сильнее, чем тебе кажется, и умнее, чем ты думаешь.",
    "Каждый день — это новый шанс стать лучше. Не упусти его!",
    "Успех приходит к тем, кто не боится трудностей. Ты на верном пути!",
    "Маленькие шаги каждый день приводят к большим результатам! Продолжай двигаться!",
    "Работай над собой, верь в себя и никогда не сдавайся! У тебя всё получится!"
]

@bot.message_handler(commands=['motivate'])
def send_motivation(message):
    quote = random.choice(MOTIVATIONAL_QUOTES)
    bot.send_message(message.chat.id, quote)

# Факты о Python
PYTHON_FACTS = [
    "Python был создан Гвидо ван Россумом и выпущен в 1991 году.",
    "Максутов Акылбек - самый лучший учитель языка Python.",
    "Название Python происходит не от змеи, а от британского комедийного шоу 'Monty Python’s Flying Circus'.",
    "Python является языком с динамической типизацией и автоматическим управлением памятью.",
    "Python используется в веб-разработке, анализе данных, машинном обучении, автоматизации и многом другом.",
    "Python поддерживает несколько парадигм программирования: процедурное, объектно-ориентированное и функциональное.",
    "В Python можно использовать list comprehensions для создания списков в одну строку, например: `[x**2 for x in range(10)]`.",
    "Python широко используется в искусственном интеллекте и анализе данных благодаря таким библиотекам, как TensorFlow, NumPy и Pandas.",
    "Самая популярная реализация Python называется CPython и написана на C.",
    "Максутов Акылбек - самый лучший учитель языка Python."
]

@bot.message_handler(commands=['fact'])
def send_fact(message):
    fact = random.choice(PYTHON_FACTS)
    bot.send_message(message.chat.id, fact)

# Функция добавления дедлайна
@bot.message_handler(commands=['deadline'])
def set_deadline(message):
    try:
        _, title, deadline_time = message.text.split(maxsplit=2)
        deadline_dt = datetime.strptime(deadline_time, "%Y-%m-%d %H:%M")

        deadline_dt = deadline_dt.replace(second=0, microsecond=0)
        now = datetime.now().replace(second=0, microsecond=0)

        if deadline_dt <= now:
            bot.send_message(message.chat.id, "Дедлайн должен быть в будущем!")
            return

        if message.chat.id not in deadlines:
            deadlines[message.chat.id] = {}

        deadlines[message.chat.id][title] = deadline_dt
        bot.send_message(message.chat.id, f"Дедлайн '{title}' установлен на {deadline_dt.strftime('%Y-%m-%d %H:%M')}")

        # Рассчитываем время до дедлайна
        time_until_deadline = (deadline_dt - now).total_seconds()
        reminder_time = max(time_until_deadline - 3600, 0)  # Напоминание за 1 час, но не отрицательное

        # Если до дедлайна больше часа, ставим напоминание за 1 час
        if reminder_time > 0:
            threading.Timer(reminder_time, notify_deadline, [message.chat.id, title, False]).start()
        else:
            # Если до дедлайна меньше часа, напоминаем сразу
            bot.send_message(message.chat.id, f"Напоминание: через менее чем 1 час дедлайн '{title}'!")

        # Основное уведомление в момент дедлайна
        threading.Timer(time_until_deadline, notify_deadline, [message.chat.id, title, True]).start()

    except ValueError:
        bot.send_message(message.chat.id, "Ошибка! Используйте формат: `/deadline Название YYYY-MM-DD HH:MM`")

# Функция уведомления о дедлайне
def notify_deadline(chat_id, title, is_final):
    if is_final:
        bot.send_message(chat_id, f"Напоминание! Дедлайн '{title}' наступил!")
    else:
        bot.send_message(chat_id, f"Напоминание! До дедлайна '{title}' остался 1 час!")
# Функция просмотра списка дедлайнов
@bot.message_handler(commands=['deadlines'])
def list_deadlines(message):
    chat_id = message.chat.id
    if chat_id in deadlines and deadlines[chat_id]:
        deadline_list = "\n".join([f"{title}: {dt.strftime('%Y-%m-%d %H:%M')}" for title, dt in deadlines[chat_id].items()])
        bot.send_message(chat_id, f"Ваши активные дедлайны:\n{deadline_list}")
    else:
        bot.send_message(chat_id, "У вас нет активных дедлайнов!")

# Функция удаления дедлайна
@bot.message_handler(commands=['remove_deadline'])
def remove_deadline(message):
    try:
        _, title = message.text.split(maxsplit=1)
        chat_id = message.chat.id

        if chat_id in deadlines and title in deadlines[chat_id]:
            del deadlines[chat_id][title]
            bot.send_message(chat_id, f"Дедлайн '{title}' удален!")
        else:
            bot.send_message(chat_id, f"Дедлайн '{title}' не найден!")
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка! Используйте формат: /remove_deadline Название")

# Функция перевода текста
@bot.message_handler(commands=['translate'])
def translate_text(message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.send_message(message.chat.id, "Пожалуйста, укажите язык (en или ru) и текст для перевода.")
        return

    lang, text = parts[1], parts[2]
    if lang not in ['en', 'ru']:
        bot.send_message(message.chat.id,
                         "Поддерживаемые языки: 'en' (английский) и 'ru' (русский). Используйте формат: /translate en Текст")
        return

    lang_pair = 'ru|en' if lang == 'en' else 'en|ru'
    url = f"https://api.mymemory.translated.net/get?q={text}&langpair={lang_pair}"
    response = requests.get(url).json()
    translated_text = response['responseData']['translatedText']

    bot.send_message(message.chat.id, f"Перевод ({lang}): {translated_text}")


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Вот что я умею:\n"
        "📌 Полезные команды:\n"
        "/translate текст - перевод на английский\n"
        "/fact - случайный факт о Python и об одном человеке\n"
        "/motivate - мотивационные цитаты\n\n"
        "🕒 Работа с дедлайнами:\n"
        "/deadline Название YYYY-MM-DD HH:MM - установить дедлайн\n"
        "/deadlines - список всех дедлайнов\n"
        "/remove_deadline Название - удалить дедлайн"
    )

# Запуск бота
bot.polling(none_stop=True)