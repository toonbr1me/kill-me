import sqlite3
import os
import time
import requests
import threading
import schedule
import json
import aiogram
import aiohttp
import asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

import pymysql

# Создаем подключение к базе данных
conn = pymysql.connect(host='3di.h.filess.io', 
                       port=3306, user='mydatabase_daughterdo', 
                       password='665102ebaf4b5bc5606316929ba1e751dd23955e', 
                       db='mydatabase_daughterdo')
cursor = conn.cursor()

def run_upd_script():
    os.system("python upd.py")

#pulled

# Словарь групп по курсам
groups = {
    '1': ['100', '101', '102', '104', '105', '108', '110', '112'],
    '2': ['Ф-202', 'Ю-208', 'СД/оз-202А', 'Ф-202', 'ПД-218', 'ПД-219', 'П-210', 'П-211', 'Д-212', 'СД-222', 'ОЛ-220'],
    '3': ['Ф-302', 'Ю-308', 'ОЛ-320', 'П-310', 'Д-312', 'СД-322', 'ПД-318', 'ПД-319', 'Ф-302', 'ОЛ-320'],
    '4': ['Ф-402', 'П-410', 'СД-422']
}

date_ids = {}
broadcast_message_id = None

bot = Bot(token='6812775820:AAH6_kvj9RAWdpdZRgNMtP4bk9A1JdDnSSs')
dp = Dispatcher(bot)

api_key = "yTu61ryW1izHrP2RYgSkvCkgmFODwbUykkcEdXab9fRhrtX5x0mAhE2zpPMj"
ADMIN_ID = 1315903018

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer('Привет, это обновленная версия бота, V2... его судьба плачевна. Зови этого бота V3.')
    await message.answer('Чтобы знать о обновлениях, подпишись на канал https://t.me/t1brime', disable_web_page_preview=True)
    await message.answer('Также, ты можешь связаться со мной, используя данную ссылку: https://t.me/requiemzxc_komaru', disable_web_page_preview=True)
    user_id = message.from_user.id
    cursor.execute("SELECT group_name FROM user_group WHERE user_id = %s", (user_id,))
    group_name = cursor.fetchone()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Погода']
    buttons.append('Отобразить')
    keyboard.add(*buttons)
    await message.answer('Выберите действие:', reply_markup=keyboard)

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

@dp.message_handler(lambda message: message.text == 'Отобразить')
async def process_display_choice(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT group_name FROM user_group WHERE user_id = %s", (user_id,))
    group_name = cursor.fetchone()
    keyboard = types.InlineKeyboardMarkup()
    if group_name is None:
        button = types.InlineKeyboardButton(text='Выбрать группу', callback_data='confirm_change')
        keyboard.add(button)
    else:
        button1 = types.InlineKeyboardButton(text='Изменить группу', callback_data='change_group')
        button2 = types.InlineKeyboardButton(text='Посмотреть расписание', callback_data='view_schedule')
        keyboard.add(button2)
        keyboard.add(button1)
    await message.answer('Выберите действие:', reply_markup=keyboard)
    
@dp.callback_query_handler(lambda c: c.data in ['1', '2', '3', '4'])
async def process_course_choice(callback_query: types.CallbackQuery):
    course = callback_query.data
    keyboard = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(text=group, callback_data=group) for group in groups[course]]
    for button in buttons:
        keyboard.add(button)  # Добавляем каждую кнопку отдельно
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text='Выберите группу:', reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data in sum(groups.values(), []))
async def process_group_choice(callback_query: types.CallbackQuery):
    group = callback_query.data.replace('-', '_').replace('/', '_')
    user_id = callback_query.from_user.id
    cursor.execute("INSERT OR REPLACE INTO user_group (user_id, group_name) VALUES (%s, %s)", (user_id, group))
    conn.commit()
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text='Изменить группу', callback_data='change_group')
    button2 = types.InlineKeyboardButton(text='Посмотреть расписание', callback_data='view_schedule')
    keyboard.add(button2)
    keyboard.add(button1)
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text='Выберите действие:', reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'change_group')
async def process_change_group(callback_query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    buttons = types.InlineKeyboardButton(text='Да', callback_data='confirm_change')
    buttons1 = types.InlineKeyboardButton(text='Нет', callback_data='cancel_change')
    keyboard.add(buttons, buttons1)
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text='Вы уверены?', reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'confirm_change')
async def process_confirm_change(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    cursor.execute("UPDATE user_group SET group_name = NULL WHERE user_id = %s", (user_id,))
    conn.commit()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton(text='1 курс', callback_data='1'),
        types.InlineKeyboardButton(text='2 курс', callback_data='2')
    )
    keyboard.row(
        types.InlineKeyboardButton(text='3 курс', callback_data='3'),
        types.InlineKeyboardButton(text='4 курс', callback_data='4')
    )
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text='Выберите курс:', reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'cancel_change')
async def process_cancel_change(callback_query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text='Изменить группу', callback_data='change_group')
    button2 = types.InlineKeyboardButton(text='Посмотреть расписание', callback_data='view_schedule')
    keyboard.add(button2)
    keyboard.add(button1)
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text='Выберите действие:', reply_markup=keyboard)

def get_dates(group):
    cursor.execute(f"SELECT date FROM schedule_{group}")
    dates = cursor.fetchall()
    return [date[0] for date in dates]

def get_schedule(group, date):
    cursor.execute(f"SELECT data FROM schedule_{group} WHERE date = %s", (date,))
    schedule = cursor.fetchone()
    return schedule[0] if schedule else None

@dp.callback_query_handler(lambda c: c.data == 'view_schedule')
async def process_view_schedule(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    cursor.execute("SELECT group_name FROM user_group WHERE user_id = %s", (user_id,))
    group = cursor.fetchone()[0]
    dates = get_dates(group)
    keyboard = types.InlineKeyboardMarkup()
    for date in dates:
        button = types.InlineKeyboardButton(text=date, callback_data=f"date_{date}")
        keyboard.row(button)
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text='Выберите дату:', reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('date_'))
async def process_date_choice(callback_query: types.CallbackQuery):
    date = callback_query.data[5:]
    user_id = callback_query.from_user.id
    cursor.execute("SELECT group_name FROM user_group WHERE user_id = %s", (user_id,))
    group = cursor.fetchone()[0]
    schedule = get_schedule(group, date)
    support_message = "\nПоддержи мой проект:\nhttps://new.donatepay.ru/@t1brimedev"
    await bot.send_message(chat_id=callback_query.from_user.id, text=schedule + support_message, disable_web_page_preview=True)

@dp.message_handler(commands=['broadcast'], user_id=ADMIN_ID)
async def broadcast_command(message: types.Message):
    # Создаем клавиатуру с кнопкой отмены
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Отмена', callback_data='cancel_broadcast'))
    # Запрашиваем у администратора сообщение или вложение для рассылки
    await message.answer('Напишите или отправьте вложение:', reply_markup=keyboard)

@dp.message_handler(user_id=ADMIN_ID)
async def broadcast_message(message: types.Message):
    # Получаем список всех пользователей
    cursor.execute("SELECT user_id FROM user_group")
    users = cursor.fetchall()
    # Отправляем сообщение всем пользователям
    for user in users:
        try:
            await bot.send_message(user[0], message.text, disable_notification=True)
        except Exception as e:
            print(f"Failed to send message to {user[0]}: {e}")
    await message.answer('Рассылка выполнена')

@dp.callback_query_handler(lambda c: c.data == 'cancel_broadcast')
async def process_cancel_broadcast(callback_query: types.CallbackQuery):
    global broadcast_message_id
    broadcast_message_id = None
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text='Рассылка отменена.')

displayed_donations = set()

# async def check_donations():
#     global displayed_donations
#     url = "https://donatepay.ru/api/v1/notifications"
#     params = {
#         "access_token": api_key,
#         "limit": 5,
#         "order": "DESC",
#         "type": "donation",
#         "view": "0"
#     }
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url, params=params) as resp:
#             data = await resp.json()
#             new_donations = [n for n in data['data'] if n['id'] not in displayed_donations]
#             for notification in sorted(new_donations, key=lambda n: n['id']):
#                 name = notification['vars']['name']
#                 comment = notification['vars']['comment']
#                 sum_donation = notification['vars']['sum']
#                 currency = notification['vars']['currency']
#                 message_text = f"Новый донат от: {name}, он задонил {sum_donation} {currency} на жизнь бота. Также он оставил коммент: {comment}"
#                 print(message_text)
#                 displayed_donations.add(notification['id'])
#                 # отправляем сообщение всем пользователям в списке
#                 cursor.execute("SELECT user_id FROM user_group")
#                 users = cursor.fetchall()
#                 # Отправляем сообщение всем пользователям
#                 for user in users:
#                     try:
#                         await bot.send_message(user[0], message_text, disable_notification=True)
#                     except Exception as e:
#                         print(f"Failed to send message to {user[0]}: {e}")

# async def schedule_check_donations(dp):
#     while True:
#         await check_donations()
#         await asyncio.sleep(20)  # wait for 10 seconds

# async def on_startup(dp):
#     asyncio.create_task(schedule_check_donations(dp))
    
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

schedule.every().monday.do(run_upd_script)

t = threading.Thread(target=run_schedule)
t.start()

if __name__ == '__main__':
    # executor.start_polling(dp, on_startup=on_startup)
    executor.start_polling(dp)