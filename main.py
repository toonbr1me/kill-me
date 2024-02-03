import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types

db = sqlite3.connect("mydatabase.db")

token_bot = "6741685282:AAFdWgJ_I9T6IhWDnG828y-MYnbhKdKiaOQ"
admin_id = ""

bot = Bot(token=token_bot)
dp = Dispatcher(bot)

# Обработчик команды /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
        keyboard=[
            [types.KeyboardButton("Показать")],
            [types.KeyboardButton("Погода")],
        ]
    ))

# Обработчик кнопки "Показать"
@dp.message_handler(text="Показать")
async def show_schedule(message: types.Message):
    await message.answer("Выберите курс:", reply_markup=types.InlineKeyboardMarkup(
        row_width=2,
        inline_keyboard=[
            [types.InlineKeyboardButton("1 курс", callback_data="1_course")],
            [types.InlineKeyboardButton("2 курс", callback_data="2_course")],
        ]
    ))

# Обработчик инлайн кнопки "1 курс"
@dp.callback_query_handler(text="1_course")
async def show_group_101(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text("Выберите группу:", reply_markup=types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton("101", callback_data="group_101")]]
    ))

# Обработчик инлайн кнопки "2 курс"
@dp.callback_query_handler(text="2_course")
async def show_groups_210_218(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text("Выберите группу:", reply_markup=types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton("210", callback_data="group_210")],
            [types.InlineKeyboardButton("218", callback_data="group_218")],
        ]
    ))

# Обработчик инлайн кнопки "Номер группы"
@dp.callback_query_handler(lambda call: call.data.startswith("group_"))
async def show_dates(call: types.CallbackQuery):
    group_id = int(call.data.split("_")[1])
    dates = get_dates_for_group(group_id)
    await call.answer()
    await call.message.edit_text("Выберите дату:", reply_markup=types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(date, callback_data=f"date_{date}") for date in dates]]
    ))

# Обработчик инлайн кнопки "Дата"
@dp.callback_query_handler(lambda call: call.data.startswith("date_"))
async def show_schedule(call: types.CallbackQuery):
    date = call.data.split("_")[1]
    group_id = int(call.data.split("_")[2])
    schedule = get_schedule_for_date(group_id, date)
    await call.answer()
    await call.message.edit_text(f"Расписание на {date}:\n{schedule}")

def get_dates_for_group(group_id):
    cursor = db.cursor()
    cursor.execute(f"SELECT date FROM schedule_{group_id}")
    dates = [date[0] for date in cursor.fetchall()]
    cursor.close()
    return dates

def get_schedule_for_date(group_id, date):
    cursor = db.cursor()
    cursor.execute(f"SELECT schedule_raw FROM schedule_{group_id} WHERE date = ?", (date,))
    schedule = cursor.fetchone()[0]
    cursor.close()
    return schedule

async def main():
    await dp.start_polling()
    
if __name__ == "__main__":
    asyncio.run(main())
