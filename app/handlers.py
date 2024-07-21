from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb

router = Router()


class Reg(StatesGroup):
    name = State()
    number = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(f'Соси!\n Твой ID: {message.from_user.id}\n Имя: {message.from_user.first_name}', 
                        reply_markup=kb.main)


@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer('Это комманда /help')


@router.message(F.text == 'Как дела?')
async def how_are_you(message: Message):
    await message.answer('OK!')

@router.message(F.photo)
async def get_photo(message: Message):
    await message.answer(f'ID фото: {message.photo[-1].file_id}')

#В фото можно указывать не только айди картинки, но и ссылку на изображение
@router.message(Command('get_photo'))
async def get_photo(messgae: Message):
    await messgae.answer_photo(photo='AgACAgIAAxkBAAMQZpw3Ok5PmAVbnXrqyTjyd7D0xR8AAn3hMRuvnOhIXXSu57tPWNwBAAMCAAN5AAM1BA', caption='Это тестовое описание')


@router.callback_query(F.data == 'catalog')
async def catalog(callback: CallbackQuery):
    await callback.answer('Вы выбрали каталог') # Можно добавить show_alert=True для уведомления
    await callback.message.edit_text('Привет!', reply_markup=await kb.inline_cars())
    
@router.message(Command('reg'))
async def reg_one(message: Message, state: FSMContext):
    await state.set_state(Reg.name)
    await message.answer('Введите ваше имя')
    
@router.message(Reg.name)
async def reg_second(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.number)
    await message.answer('Введите номер телефона')
    
@router.message(Reg.number)
async def reg_three(message: Message, state: FSMContext):
    await state.update_data(number=message.text)
    data = await state.get_data()
    await message.answer(f'Спасибо, регистрация завершена.\n Имя: {data["name"]} \n Номер: {data["number"]}')
    await state.clear()