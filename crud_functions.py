from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from config import *
import sqlite3
import time

bot = Bot(token = API)
dp = Dispatcher(bot, storage=MemoryStorage())

connection = sqlite3.connect("crud_functions.db")
cursor = connection.cursor()

def initiate_db():
    cursor.execute('''CREATE TABLE IF NOT EXISTS Products(id INTEGER PRIMARY KEY, title TEXT NOT Null, description TEXT NOT NULL, price INTEGER NOT NULL)''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_title ON Products (title)')
    cursor.execute("DELETE FROM Products")
    cursor.execute("INSERT INTO Products (title, description, price) VALUES (?, ?, ?)",
                   ("Product1", "коврик", "100"))
    cursor.execute("INSERT INTO Products (title, description, price) VALUES (?, ?, ?)",
                   ("Product2", "куртка", "200"))
    cursor.execute("INSERT INTO Products (title, description, price) VALUES (?, ?, ?)",
                   ("Product3", "спальник", "300"))
    cursor.execute("INSERT INTO Products (title, description, price) VALUES (?, ?, ?)",
                   ("Product4", "рюкзак", "400"))
    connection.commit()

initiate_db()

def get_all_products():
    cursor.execute('SELECT * FROM Products')
    products = cursor.fetchall()
    return products

products = get_all_products()

kb = InlineKeyboardMarkup(resize_keyboard=True)
button1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
button3 = InlineKeyboardButton(text='Купить')
kb.add(button1)
kb.add(button2)
kb.add(button3)

kb1 = InlineKeyboardMarkup(resize_keyboard=True)
button1 = InlineKeyboardButton(text='Product1', callback_data='product_buying')
button2 = InlineKeyboardButton(text='Product2', callback_data='product_buying')
button3 = InlineKeyboardButton(text='Product3', callback_data='product_buying')
button4 = InlineKeyboardButton(text='Product4', callback_data='product_buying')
kb1.add(button1)
kb1.add(button2)
kb1.add(button3)
kb1.add(button4)

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(text = ['Рассчитать'])
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb)

@dp.callback_query_handler(text = ['formulas'])
async def get_formulas(call):
    await call.message.answer('Суточная норма калорий = 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5')
    await call.answer()

@dp.callback_query_handler(text = ['calories'])
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()

@dp.message_handler(state = UserState.age)
async def set_growth(message, state):
    await state.update_data(age = message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state = UserState.growth)
async def set_growth(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def set_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    Cal = 10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) + 5
    await message.answer(f'Ваша суточная норма калорий: {Cal}')
    await state.finish()

@dp.message_handler(text = ['Купить'])
async def get_buying_list(message):
    for item in products:
        await message.answer(f'Название: {item[1]} | Описание: {item[2]} | Цена: {item[3]}')
        with open(f'{products.index(item) + 1}.jpg', 'rb') as img:
            await message.answer_photo(img)
            time.sleep(1)
    await message.answer('Выберите продукт для покупки:', reply_markup=kb1)

@dp.callback_query_handler(text = ['product_buying'])
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()

@dp.message_handler(commands = ['start'])
async def start(message):
    await message.answer('Привет!', reply_markup=kb)

@dp.message_handler(text = ['Информация'])
async def inform(message):
    await message.answer('Информация о боте')

@dp.message_handler()
async def all_massages(message):
    await message.answer('Введите команду /start, чтобы начать общение.')

connection.close()

if __name__ == "__main__":
    executor.start_polling(dp,skip_updates=True)