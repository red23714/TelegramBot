from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                           InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove)

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

mainMenu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='ПРОФИЛЬ')],
    [KeyboardButton(text='ПОДПИСКА')] 
],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню.')

rm = ReplyKeyboardRemove()


sub_inline_markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Месяц - 150 рублей", callback_data="submonth")],
],
                            resize_keyboard=True,
                            input_field_placeholder='Выберите пункт меню.')