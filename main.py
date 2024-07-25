import asyncio
import logging

import time
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, ContentType
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from apscheduler.schedulers.asyncio import AsyncIOScheduler

import app.keyboards as kb
from db import Database

from datetime import datetime, timedelta

from config import BOT_TOKEN, U_KASSA_TOKEN, CHAT_ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

db = Database('database.db')

class Reg(StatesGroup):
    name = State()

def days_to_seconds(days):
    return days * 24 * 60 * 60

def time_sub_day(get_time):
    time_now = int(time.time())
    middle_time = int(get_time) - time_now
    
    if middle_time <= 0:
        return False
    else:
        dt = str(timedelta(seconds=middle_time))
        dt = dt.replace("days", "дней")
        dt = dt.replace("day", "день")
        return dt

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    if(not db.user_exists(message.from_user.id)):
        db.add_user(message.from_user.id)
        await message.answer("Укажите ваш ник", reply_markup=kb.rm)
        await state.set_state(Reg.name)
    elif db.get_signup(message.from_user.id) != 'setnickname':
        await message.answer("Вы уже зарегистрированы!", reply_markup=kb.mainMenu)
    else:
        await message.answer("Укажите ваш ник", reply_markup=kb.rm)
        await state.set_state(Reg.name)

@dp.message(Reg.name)
async def reg_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    
    data = await state.get_data()
    
    if db.get_signup(message.from_user.id) == 'setnickname':
        if(len(message.text) > 15):
            await message.answer("Никнейм не должен превышать 15 символов")
            
        elif '@' in message.text or '/' in message.text:
            await message.answer('Вы ввели запрещенный символ')
        
        else:
            db.set_nickname(message.from_user.id, message.text)
            db.set_signup(message.from_user.id, "done")
            await message.answer(f'Спасибо, регистрация завершена.\n Имя: {data["name"]}', reply_markup=kb.mainMenu)
            await state.clear()
    else:
        await message.answer("Укажите ваш ник")

@dp.message(F.text == 'ПРОФИЛЬ')
async def get_profile(message: Message):
    if db.user_exists(message.from_user.id):
        user_sub = time_sub_day(db.get_time_sub(message.from_user.id))
        if user_sub == False:
            user_sub = "\nПодписка: Нет"
        else:
            user_sub = f"\nПодписка: {user_sub}"
        
        await message.reply(f'Ваш никнейм: {db.get_nickname(message.from_user.id)}' + user_sub, reply_markup=kb.mainMenu)
    else:
        await message.answer("У вас нету профиля, зарегестрируйтесь, пожалуйста")

@dp.message(F.text == 'ПОДПИСКА')
async def get_profile(message: Message):
    await message.answer("Описание возможностей подписки", reply_markup=kb.sub_inline_markup)


@dp.callback_query(F.data == 'submonth')
async def submonth(call: CallbackQuery):
    await call.message.delete()
    await bot.send_invoice(chat_id=call.from_user.id, 
                           title="Оформление подписки", 
                           description="Тестовое описание товара", 
                           payload="month_sub", 
                           provider_token=U_KASSA_TOKEN, 
                           currency="RUB",
                           start_parameter="test_bot", 
                           prices=[{"label":"Руб", "amount":150 * 100}]
                           )

@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def process_pay(message: Message):
    if message.successful_payment.invoice_payload == "month_sub":
        time_sub = int(time.time()) + days_to_seconds(30)
        db.set_time_sub(message.from_user.id, time_sub)
        await message.answer("Вам выдана подписка на месяц")
        date = datetime.now() + timedelta(days=1)
        link = await bot.create_chat_invite_link(chat_id=CHAT_ID, expire_date=date, member_limit=1)

        await message.answer(link.invite_link)
        await bot.unban_chat_member(chat_id=CHAT_ID, user_id=message.from_user.id, only_if_banned=True)

@dp.message(Command("show_all"))
async def show_all_database(message: Message):
    if message.from_user.id == 1377367433:
        await message.answer(text=''.join(str(x) for x in db.get_all_users()))

async def sched():
    for user in db.get_all_users():
        print("Hey", user)
        if user[3] <= 0 and user[1] != 1377367433:
            await bot.ban_chat_member(chat_id=CHAT_ID, user_id=user[1])
        else:
            new_time_sub = int(db.get_time_sub(user[1])) - 10 # days_to_seconds(1)
            db.set_time_sub(user[1], new_time_sub)

async def main():
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.add_job(sched, 'interval', seconds=10) #days = 1
    scheduler.start()

    await dp.start_polling(bot)
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')