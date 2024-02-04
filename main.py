import sqlite3
import os
import time
import requests
import threading
import schedule
import json
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Создаем подключение к базе данных
conn = sqlite3.connect('mydatabase.db')
cursor = conn.cursor()

admin_id = "1315903018"
bot_token = "6741685282:AAFdWgJ_I9T6IhWDnG828y-MYnbhKdKiaOQ"

# Создаем экземпляры бота и диспетчера
bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

def update_database():
    os.system("python upd.py")
 
# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer('Привет, это обновленная версия бота. Зови его V2. Тут добалены новые возможности. Добавлено запоминание твоей группы и инста-просмотр')
    await message.answer('Чтобы знать о обновлениях, подпишись на канал https://t.me/t1brime', disable_web_page_preview=True)
    await message.answer('Также, ты можешь связаться со мной, используя данную ссылку: https://t.me/requiemzxc_komaru', disable_web_page_preview=True)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton('Показать'), types.KeyboardButton('Погода'))
    await message.answer('Выберите действие:', reply_markup=keyboard)

# Создаем таблицу пользователей, если она еще не существует
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    course TEXT,
    group_number TEXT
)
""")

# Обработчик кнопки "Показать"
@dp.message_handler(lambda message: message.text == 'Показать')
async def show_handler(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT course, group_number FROM users WHERE user_id=?", (user_id,))
    user_info = cursor.fetchone()
    # Получаем информацию о курсе и группе пользователя из базы данных
    if user_info is None:
        # Если информация о пользователе еще не сохранена в базе данных, показываем ему меню выбора курса
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('1 курс', callback_data='course_1'),
                     types.InlineKeyboardButton('2 курс', callback_data='course_2'),)
        keyboard.add(types.InlineKeyboardButton('3 курс', callback_data='course_3'),
                     types.InlineKeyboardButton('4 курс', callback_data='course_4'),)
        await message.answer('Выберите курс:', reply_markup=keyboard)
    else:
        # Если информация о пользователе уже сохранена в базе данных, показываем ему меню с кнопками "Посмотреть расписание" и "Изменить группу"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Посмотреть расписание', callback_data='show_schedule'))
        keyboard.add(types.InlineKeyboardButton('Изменить группу', callback_data='change_group'),)
        await message.answer('Выберите действие:', reply_markup=keyboard)

# Обработчик выбора действия
@dp.callback_query_handler(lambda c: c.data in ['show_schedule', 'change_group'])
async def action_handler(callback_query: types.CallbackQuery):
    action = callback_query.data
    user_id = callback_query.from_user.id
    if action == 'show_schedule':
        # Если пользователь выбрал "Посмотреть расписание", показываем ему расписание его группы
        cursor.execute("SELECT group_number FROM users WHERE user_id=?", (user_id,))
        group = cursor.fetchone()[0]
        cursor.execute(f"SELECT date FROM schedule_{group}")
        dates = cursor.fetchall()
        keyboard = types.InlineKeyboardMarkup()
        for date in dates:
            keyboard.add(types.InlineKeyboardButton(date[0], callback_data=f"{group}__{date[0]}"))
        await callback_query.message.answer('Выберите дату:', reply_markup=keyboard)
    else:
        # Если пользователь выбрал "Изменить группу", показываем ему меню выбора курса
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('1 курс', callback_data='course_1'),
                     types.InlineKeyboardButton('2 курс', callback_data='course_2'),)
        keyboard.add(types.InlineKeyboardButton('3 курс', callback_data='course_3'),
                     types.InlineKeyboardButton('4 курс', callback_data='course_4'),)
        await callback_query.message.answer('Выберите курс:', reply_markup=keyboard)
        
# Обработчик кнопки "Погода"
@dp.message_handler(lambda message: message.text == 'Погода')
async def weather_handler(message: types.Message):
    api_key = " fdb88f8f513a4d7cad075312242401" # weatherapi api токен
    location = "Chelyabinsk"
    response = requests.get(f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&lang=ru")
    data = json.loads(response.text)
    current_temp = data["current"]["temp_c"]
    current_condition = data["current"]["condition"]["text"]
    current_wind = data["current"]["wind_kph"]
    await message.answer(f"Сейчас в Челябинске {current_temp}°C, {current_condition}, ветер {current_wind} км/ч")

# Обработчик выбора курса
@dp.callback_query_handler(lambda c: c.data in ['course_1', 'course_2', 'course_3', 'course_4'])
async def course_handler(callback_query: types.CallbackQuery):
    course = callback_query.data
    if course == 'course_1':
        groups = ['100', '101', '102', '104', '105', '108', '110', '112']
    elif course == 'course_2':
        groups = ['Ф-202', 'Ю-208', 'СД/оз-202А', 'Ф-202', 'П-210', 'П-211', 'Д-212', 'СД-222']
    elif course == 'course_3':
        groups = ['Ф-302', 'Ю-308', 'ОЛ-320', 'П-310', 'Д-312', 'СД-322', 'ПД-318', 'ПД-319', 'Ф-302']
    else:
        groups = ['ОЛ-220', 'П-410', 'СД-422', 'Ф-402']
    keyboard = types.InlineKeyboardMarkup()
    for group in groups:
        keyboard.add(types.InlineKeyboardButton(group, callback_data=group))
    await callback_query.message.answer('Выберите группу:', reply_markup=keyboard)

# Обработчик выбора группы
@dp.callback_query_handler(lambda c: c.data not in ['course_1', 'course_2', 'course_3', 'course_4', 'show_schedule', 'change_group'])
async def group_handler(callback_query: types.CallbackQuery):
    group = callback_query.data.replace("-", "_").replace("/", "_")
    user_id = callback_query.from_user.id
    course = group[0]  # Первый символ номера группы - это номер курса

    # Проверяем, существует ли пользователь в базе данных
    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    user_exists = cursor.fetchone()

    if user_exists is None:
        # Если пользователя нет в базе данных, вставляем новую запись
        cursor.execute("INSERT INTO users (user_id, course, group_number) VALUES (?, ?, ?)", 
                       (user_id, course, group))
    else:
        # Если пользователь уже существует, обновляем его запись
        cursor.execute("UPDATE users SET course = ?, group_number = ? WHERE user_id = ?", 
                       (course, group, user_id))

    conn.commit()

    # Define the keyboard here
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Группа выбрана'))

    await callback_query.message.answer('Группа выбрана:', reply_markup=keyboard)
    
# Обработчик выбора даты
@dp.callback_query_handler(lambda c: c.data and "__" in c.data)
async def date_handler(callback_query: types.CallbackQuery):
    # Получаем user_id из callback_query
    user_id = callback_query.from_user.id

    # Получаем номер группы из базы данных
    cursor.execute("SELECT group_number FROM users WHERE user_id=?", (user_id,))
    group = cursor.fetchone()[0]

    # Получаем дату из callback_query
    _, date = callback_query.data.split("__")

    # Затем получаем расписание на эту дату
    cursor.execute(f"SELECT schedule FROM schedule_{group} WHERE date=?", (date,))
    schedule = cursor.fetchone()
    if schedule is not None:
        await callback_query.message.answer(f'Расписание на {date}: {schedule[0]}')
    else:
        await callback_query.message.answer('No schedule found for this date.')
        
# Обработчик команды /broadcast
@dp.message_handler(commands=['broadcast'], user_id=admin_id)
async def broadcast_command(message: types.Message):
    # Создаем клавиатуру с кнопкой отмены
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Отмена', callback_data='cancel_broadcast'))
    # Запрашиваем у администратора сообщение или вложение для рассылки
    await message.answer('Напишите или отправьте вложение:', reply_markup=keyboard)

# Обработчик кнопки "Отмена"
@dp.callback_query_handler(lambda c: c.data == 'cancel_broadcast', user_id=admin_id)
async def cancel_broadcast(callback_query: types.CallbackQuery):
    await callback_query.message.answer('Рассылка отменена')

# Обработчик текстовых сообщений от администратора после команды /broadcast
@dp.message_handler(user_id=admin_id)
async def broadcast_message(message: types.Message):
    # Получаем список всех пользователей
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    # Отправляем сообщение всем пользователям
    for user in users:
        try:
            await bot.send_message(user[0], message.text, disable_notification=True)
        except Exception as e:
            print(f"Failed to send message to {user[0]}: {e}")
    await message.answer('Рассылка выполнена')

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)
        
schedule_thread = threading.Thread(target=run_schedule)
schedule_thread.start()

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp)