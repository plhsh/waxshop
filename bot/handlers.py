from aiogram import types
from aiogram.types.message import ContentType
from aiogram.types.labeled_price import LabeledPrice

from create_bot import bot, dp
from config import Config
from aiogram.dispatcher.filters import Command
from keyboards import ikbrd
from alchemy import cart_len, cart_add, cart_empty, invoice_issue, invoice_pay
import asyncio
from contextlib import suppress
from aiogram.utils.exceptions import (MessageToEditNotFound, MessageCantBeEdited, MessageCantBeDeleted,
                                      MessageToDeleteNotFound)
import time

PAYMENTS_TOKEN = Config.PAYMENTS_TOKEN
BOT_MODE_ON = True

# checks if user is trying to place an order within working hours
def working_hours():
    current_hour = time.localtime().tm_hour
    current_minute = time.localtime().tm_min
    current_weekday = time.localtime().tm_wday
    if current_weekday in (5, 6):
        return (current_hour > Config.START_HOUR + Config.W_END_MORNING_ADJ or
                (current_hour == Config.START_HOUR + Config.W_END_MORNING_ADJ and current_minute >= Config.START_MINUTE))\
               and (current_hour < Config.END_HOUR or (current_hour == Config.END_HOUR and current_minute <= Config.END_MINUTE))
    return (current_hour > Config.START_HOUR or (current_hour == Config.START_HOUR and current_minute >= Config.START_MINUTE)) \
           and (current_hour < Config.END_HOUR or (current_hour == Config.END_HOUR and current_minute <= Config.END_MINUTE))


# returns data to be sent to the payment provider to be used in the receipt
async def prvdr_data(prices):
    items = []
    for i in prices:
        items.append({"description": i.label,
         "quantity": "1",
         "amount": {
             "value": i.amount/100,
             "currency": "RUB"},
         "vat_code": 1})
    provider_data = {"receipt": {"items": items}}
    # print(str(provider_data), len(str(provider_data).encode('utf-8')))
    return provider_data


# deletes message after the set delay
async def delete_message(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()


# deletes message after the set delay using message id
async def delete_message_by_id(chat_id, message_id: int, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await bot.delete_message(chat_id=chat_id, message_id=message_id)


@dp.callback_query_handler(lambda cq: cq.data.startswith('0'))
async def process_callback_ml0(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(ikbrd(0))
    await callback.answer()


@dp.callback_query_handler(lambda cq: len(cq.data) == 1)
async def process_callback_ml1(callback: types.CallbackQuery):
    print(callback.data)
    await callback.message.edit_reply_markup(ikbrd(callback.data))
    await callback.answer()


@dp.callback_query_handler(lambda cq: len(cq.data) == 3)
async def process_callback_ml1(callback: types.CallbackQuery):
    print(callback.data)
    await callback.message.edit_reply_markup(ikbrd(str(callback.data)))
    await callback.answer()


@dp.callback_query_handler(lambda cq: len(cq.data) == 4)
async def process_callback_ml2(callback: types.CallbackQuery):
    if await cart_len(callback.message.chat.id) < Config.MAX_ORDER:
        await cart_add(callback.message.chat.id, callback.data)
        await callback.answer('Добавлено в корзину')
    else:
        await callback.answer('Превышено максимальное количество позиций')


@dp.callback_query_handler(text='button_buy')
async def buy(callback: types.callback_query):
    if working_hours() and BOT_MODE_ON:
        if PAYMENTS_TOKEN.split(':')[1] == 'TEST':
            await bot.send_message(callback.message.chat.id, "Тестовый платеж!!!")
        prices, payload = await invoice_issue(callback.message.chat.id)

        if prices:
            provider_data = await prvdr_data(prices)
            print(provider_data)
            msg1 = await bot.send_message(callback.message.chat.id, "Совершая покупку, Вы выражаете свое согласее на обработку"
                                                             " персональных данных. Подробнее:"
                                                             " Главное меню => Согласие на обработку персональных данных")
            asyncio.create_task(delete_message(msg1, 10))
            msg2 = await bot.send_message(callback.message.chat.id, "Счет действителен в течении 5 минут")
            asyncio.create_task(delete_message(msg2, 15))
            msg3 = await bot.send_invoice(callback.message.chat.id,
                                          #Test for paymaster
                                          title=f"Клиент: {callback.message.chat.first_name}",
                                          description=(f"Заказ № {payload}"),
                                          provider_token=PAYMENTS_TOKEN,
                                          currency="RU",
                                          prices=prices,
                                          is_flexible=False,
                                          payload=payload,
                                         # Live for youkassa
                                         # title=f"Клиент: {callback.message.chat.first_name}",
                                         # description=(f"Заказ № {payload}"),
                                         # provider_token=PAYMENTS_TOKEN,
                                         # currency="RUB",
                                         # need_email=True,
                                         # send_email_to_provider=True,
                                         # provider_data=provider_data,
                                         # reply_to_message_id=None,
                                         # allow_sending_without_reply=True,
                                         # prices=prices,
                                         # payload=payload
                                          )
            await invoice_pay(payload)
            # message_id = msg.message_id
            # chat_id = msg.chat.id
            # # print("Invoice message ID:", message_id)
            # await asyncio.sleep(300)  # invoice disappears in 1 minute in any case
            # await bot.delete_message(chat_id=chat_id, message_id=message_id)
            await cart_empty(callback.message.chat.id)
            await callback.answer()
            asyncio.create_task(delete_message(msg3, 300))
        else:
            await callback.answer('Корзина пуста')
    else:
        await callback.answer('Сейчас мы не принимаем заказы')


@dp.callback_query_handler(text='button_ec')
async def process_callback_button_mm(callback: types.CallbackQuery):
    await cart_empty(callback.message.chat.id)
    await callback.answer('Корзина очищена')


@dp.callback_query_handler(text='button_mm')
async def process_callback_button_mm(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(ikbrd(0))
    await callback.answer()


@dp.message_handler(Command('start'), chat_type=['private']) # bot starts only in private chats
async def board_handler(message: types.Message):
    # await bot.send_message(message.chat.id, f"Самое время заказать кофе с собой.\n", reply_markup=types.ReplyKeyboardRemove())
    await message.answer(f"Самое время заказать кофе с собой.\n"
                         "Готовность три минуты.\n", reply_markup=ikbrd(0))
    asyncio.create_task(delete_message(message, 10))


@dp.message_handler(Command('bot_off'), chat_type=['private']) # only OWNERS turn bot off
async def bot_off(message: types.Message):
    print(message)
    if message.chat.id in Config.OWNERS:
        print(message.chat.id)
        global BOT_MODE_ON
        BOT_MODE_ON = False
        asyncio.create_task(delete_message(message, 30))


@dp.message_handler(Command('bot_on'), chat_type=['private']) # only OWNERS turn bot on
async def bot_on(message: types.Message):
    print(message)
    if message.chat.id in Config.OWNERS:
        print(message.chat.id)
        global BOT_MODE_ON
        BOT_MODE_ON = True
        asyncio.create_task(delete_message(message, 30))

# pre checkout  (must be answered in 10 seconds)
@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# successful payment
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):

    print("SUCCESSFUL PAYMENT:")
    payment_info = message.successful_payment.to_python()
    invoice_id = payment_info['invoice_payload']
    # for k, v in payment_info.items():
    #     print(f"{k} = {v}")
    # print(payment_info['invoice_payload'])
    successful_order = await invoice_pay(invoice_id)
    successful_order_msg = [f'Оплачен заказ № {invoice_id}']
    successful_order_msg.extend([f'{k}: {v}' for k, v in successful_order.items()])
    successful_order_msg = '\n'.join(successful_order_msg)
    await bot.send_message(Config.ADM_CHT_ID, successful_order_msg)
    msg = await bot.send_message(message.chat.id, f"Платеж на сумму {message.successful_payment.total_amount // 100} "
                                            f"{message.successful_payment.currency} прошел успешно!!!\n"
                                            f"Начали готовить твой кофе. Забирай пока не остыл!!!")
    await cart_empty(message.chat.id)
    asyncio.create_task(delete_message_by_id(msg.chat.id, msg.message_id-1, 10))
    asyncio.create_task(delete_message(msg, 150))

    # await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
    # await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id - 1)
    # await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id - 2)
    # await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id - 3)



