from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import Menu


ib_m4 = InlineKeyboardButton('Оформить заказ 👍', callback_data='button_buy')
ib_m5 = InlineKeyboardButton('Очистить корзину', callback_data='button_ec')
ib_m6 = InlineKeyboardButton('Главное меню', callback_data='button_mm')


def ikbrd(menu_codes, *args):
    ikbrd = InlineKeyboardMarkup()
    if menu_codes == 0:
        menu_level0 = Menu.menu_dicts[0]
        print(menu_level0)
        for k, v in menu_level0.items():
            ikbrd.add(InlineKeyboardButton(text=v, callback_data=k))
            print(k + '_' + v)
    elif len(menu_codes) == 1:
        menu_level1 = Menu.menu_dicts[1]
        for k, v in menu_level1.items():
            if k.startswith(menu_codes):
                ikbrd.add(InlineKeyboardButton(text=v, callback_data=str(k)))
                print(k + '_' + v)
    elif len(menu_codes) == 3:
        menu_level2 = Menu.menu_dicts[2]
        for k, v in menu_level2.items():
            if str(k).startswith(menu_codes):
                ikbrd.add(InlineKeyboardButton(text=v, callback_data=str(k)))
                print(str(k) + '_' + v)
    ikbrd.add(ib_m4).add(ib_m5)
    if menu_codes != 0:
        ikbrd.add(ib_m6)
    return ikbrd






