import traceback
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram import types
from keyboard.keyboard import keyboard, themes
from init_bot import dp, bot
from settings.settings import logger
from functions.get_state import update_state, get_state
from functions.personal_entity_id import pd
from functions.create_ticket import create_tracker_ticket
from functions.check_files import check_files
from functions.send_message_from_user import send_message
from functions.write_to_yt_table import write_to_yt_table
from functions.update_db_data_message import update_db_data_message
from functions.check_white_list import check_white_list
from functions.check_corp_type import check_corp_type
from functions.check_correctness_order import check_order
from middleware.antiflood import rate_limit
import json
from datetime import datetime


@dp.message_handler(lambda message: message.chat.type != 'private', commands=["start", "help"], state='*')
async def start(message: types.Message):
    try:
        await update_state(message.chat.id, 'start', '{}')
        if message.chat.username:
            user_login = pd('telegram_logins', message.chat.username)
        else:
            user_login = 'None'
        db_data = await update_db_data_message(message)
        json_data, state = db_data.values()
        json_data.update(user_login=str(user_login), chat_title=str(message.chat.title), chat_id=str(message.chat.id))
        await update_state(message.chat.id, 'start', json_data)
        await message.answer("Нажмите на кнопку, чтобы cообщить о нарушении", reply_markup=keyboard("start"))
    except Exception as e:
        logger.error(f'start group handler{e}')


@dp.message_handler(lambda message: message.chat.type == 'private', commands=["start", "help"], state='*')
async def start(message: types.Message):
    try:
        await update_state(message.chat.id, 'start', '{}')
        if message.chat.username:
            user_login = pd('telegram_logins', message.chat.username)
        else:
            user_login = 'None'

        db_data = await update_db_data_message(message)
        json_data, state = db_data.values()
        corp_type, corp_id = await check_corp_type(message)
        json_data.update(user_login=str(user_login), chat_title=str(message.chat.title), chat_id=str(message.chat.id),
                         corp_type=str(corp_type), corp_id=str(corp_id))
        await update_state(message.chat.id, 'start', json_data)
        white_list_user = await check_white_list(message)
        if white_list_user:
            await message.answer("Нажмите на кнопку, чтобы cообщить о нарушении",
                                 reply_markup=keyboard("start_private"))
        else:
            await message.answer("Нажмите на кнопку, чтобы cообщить о нарушении", reply_markup=keyboard("start_lite"))
    except Exception as e:
        logger.error(f'start private handler{e}')


@dp.message_handler(
    content_types=['audio', 'photo', 'voice', 'video', 'document', 'text', 'location', 'contact', 'sticker'])
async def check_state(message: types.Message):
    db_data = await update_db_data_message(message)
    json_data, state = db_data.values()
    try:
        if state == 'complaint_get_order':
            correct_order = False
            order_id = message.text.title()
            correct_order = await check_order(order_id, message.chat.username)
            if correct_order:
                json_data.update(order_id=str(order_id))
                update_status = await update_state(message.chat.id, 'complaint_themes', json_data)
                logger.info('update_status {}'.format(update_status))
                await message.answer("Выберите нарушение, о котором хотите сообщить:",
                                     reply_markup=keyboard("complaint_themes"))
            else:
                await message.answer(
                    "Здравствуйте! Нам не удалось найти ваш заказ. Возможно, вы ошиблись при вводе его номера. Пожалуйста, введите номер заказа из вашей системы.")
        elif state == 'order_get_order':
            correct_order = False
            order_id = message.text.title()
            correct_order = await check_order(order_id, message.chat.username)
            if correct_order:
                json_data.update(order_id=str(order_id))
                update_status = await update_state(message.chat.id, 'order_themes', json_data)
                logger.info('update_status {}'.format(update_status))
                await message.answer("Выберите категорию вопроса:",
                                     reply_markup=keyboard("order_themes"))
            else:
                await message.answer(
                    "Здравствуйте! Нам не удалось найти ваш заказ. Возможно, вы ошиблись при вводе его номера. Пожалуйста, введите номер заказа из вашей системы.")
        elif state == 'order_cancel_get_order':
            correct_order = False
            order_id = message.text.title()
            correct_order = await check_order(order_id, message.chat.username)
            if correct_order:
                json_data.update(order_id=str(order_id))
                update_status = await update_state(message.chat.id, 'order_cancel_themes', json_data)
                logger.info('update_status {}'.format(update_status))
                await message.answer("Выберите категорию вопроса:",
                                     reply_markup=keyboard("order_cancel_themes"))
            else:
                await message.answer(
                    "Здравствуйте! Нам не удалось найти ваш заказ. Возможно, вы ошиблись при вводе его номера. Пожалуйста, введите номер заказа из вашей системы.")
        elif state == 'cabinet_get_id':
            order_id = message.text.title()
            json_data.update(order_id=str(order_id))
            update_status = await update_state(message.chat.id, 'cabinet_themes', json_data)
            logger.info('update_status {}'.format(update_status))
            await message.answer("Выберите категорию вопроса:",
                                 reply_markup=keyboard("cabinet_themes"))
        elif state == 'cabinet_get_text':
            feedback_message = message.text
            json_data.update(feedback_message=str(feedback_message), time=datetime.now().isoformat(timespec='minutes'))
            file = await check_files(message)
            ticket = await create_tracker_ticket(data=json_data, category="cabinet", file=file)
            update_status = await update_state(message.chat.id, 'finish', json_data)
            logger.info(update_status)
            await write_to_yt_table(json_data, ticket, 'cabinet')
            await message.answer(
                'Мы получили ваш вопрос и уже взяли его в работу и постараемся вернуться с решением в ближайшие сроки.')
        else:
            file = await check_files(message)
            await send_message(message, file)
    except Exception as e:
        logger.error(f'message handler{e}')


@dp.callback_query_handler(text="menu_complaint")
async def get_order(call: types.CallbackQuery):
    try:
        db_data = await update_db_data_message(call)
        json_data, state = db_data.values()
        await update_state(call.message.chat.id, 'complaint_get_order', json_data)
        await call.message.answer("Введите номер заказа, по которому хотите сообщить о нарушении:")
    except Exception as e:
        logger.error('menu_complaint {}'.format(e))


@dp.callback_query_handler(text="menu_order")
async def get_order(call: types.CallbackQuery):
    try:
        db_data = await update_db_data_message(call)
        json_data, state = db_data.values()
        await update_state(call.message.chat.id, 'order_get_order', json_data)
        await call.message.answer("Введите номер заказа, по которому необходима информация или помощь:")
    except Exception as e:
        logger.error('menu_order {}'.format(e))


@dp.callback_query_handler(text="menu_cancel_order")
async def get_order(call: types.CallbackQuery):
    try:
        db_data = await update_db_data_message(call)
        json_data, state = db_data.values()
        await update_state(call.message.chat.id, 'order_cancel_get_order', json_data)
        await call.message.answer("Введите номер заказа, по которому необходима информация или помощь:")
    except Exception as e:
        logger.error('menu_cancel_order {}'.format(e))


@dp.callback_query_handler(text="menu_cabinet")
async def get_order(call: types.CallbackQuery):
    try:
        db_data = await update_db_data_message(call)
        json_data, state = db_data.values()
        await update_state(call.message.chat.id, 'cabinet_get_id', json_data)
        await call.message.answer("Введите номер договора, по которому необходима информация или помощь:")
    except Exception as e:
        logger.error('menu_cabinet {}'.format(e))


@dp.callback_query_handler(text=[*themes['complaint'].keys()])
async def get_theme(call: types.CallbackQuery):
    try:
        db_data = await update_db_data_message(call)
        json_data, state = db_data.values()
        json_data.update(theme=str(call.data), time=datetime.now().isoformat(timespec='minutes'), feedback_message="")
        ticket = await create_tracker_ticket(data=json_data, category="complaint", file=None)
        update_status = await update_state(call.message.chat.id, 'finish', json_data)
        logger.info(update_status)
        await write_to_yt_table(json_data, ticket, 'complaint')
        await call.message.answer("Спасибо за обратную связь")
    except Exception as e:
        logger.error('complaint themes {}'.format(e))


@dp.callback_query_handler(text="refund")
async def refund_request(call: types.CallbackQuery):
    try:
        db_data = await update_db_data_message(call)
        json_data, state = db_data.values()
        update_status = await update_state(call.message.chat.id, 'order_refund_question', json_data)
        logger.info(update_status)
        await call.message.answer(
            "Обратите внимание, в этом случае мы попросим курьера вернуть заказ отправителю и отменить возврат будет невозможно. Вы подтверждаете оформление возврата?",
            reply_markup=keyboard("order_feedback_question"))
    except Exception as e:
        logger.error('refund {}'.format(e))


@dp.callback_query_handler(text="refund_confirmed")
async def refund_request(call: types.CallbackQuery):
    try:
        db_data = await update_db_data_message(call)
        json_data, state = db_data.values()
        json_data.update(theme=str(call.data), time=datetime.now().isoformat(timespec='minutes'),
                         feedback_message="Запрос рефанда")
        update_status = await update_state(call.message.chat.id, state, json_data)
        logger.info(update_status)
        ticket = await create_tracker_ticket(data=json_data, category="order", file=None)
        update_status = await update_state(call.message.chat.id, 'finish', json_data)
        logger.info(update_status)
        await write_to_yt_table(json_data, ticket, 'order')
        await call.message.answer("Мы получили ваш вопрос и уже взяли его в работу. "
                                  "Пожалуйста, подождите решения и не создавайте повторных запросов об одном заказе, "
                                  "это не ускорит его решения.")
    except Exception as e:
        logger.error('refund_confirmed {}'.format(e))


@dp.callback_query_handler(text="no_refund")
async def refund_request(call: types.CallbackQuery):
    try:
        db_data = await update_db_data_message(call)
        json_data, state = db_data.values()
        update_status = await update_state(call.message.chat.id, 'finish', json_data)
        logger.info(update_status)
        await call.message.answer("Запрос отменен. Хорошего дня!")
    except Exception as e:
        logger.error('no_refund {}'.format(e))


@dp.callback_query_handler(text=[*filter(lambda x: x != "refund", themes['order'].keys())])
async def get_theme(call: types.CallbackQuery):
    try:
        db_data = await update_db_data_message(call)
        json_data, state = db_data.values()
        json_data.update(theme=str(call.data), time=datetime.now().isoformat(timespec='minutes'), feedback_message="")
        ticket = await create_tracker_ticket(data=json_data, category="order", file=None)
        update_status = await update_state(call.message.chat.id, 'finish', json_data)
        logger.info(update_status)
        await write_to_yt_table(json_data, ticket, 'order')
        await call.message.answer("Мы получили ваш вопрос и уже взяли его в работу. "
                                  "Пожалуйста, подождите решения и не создавайте повторных запросов об одном заказе, "
                                  "это не ускорит его решения.")
    except Exception as e:
        logger.error('order themes {}'.format(e))


@dp.callback_query_handler(text=[*themes['order_cancel'].keys()])
async def get_theme(call: types.CallbackQuery):
    try:
        db_data = await update_db_data_message(call)
        json_data, state = db_data.values()
        json_data.update(theme=str(call.data), time=datetime.now().isoformat(timespec='minutes'), feedback_message="")
        ticket = await create_tracker_ticket(data=json_data, category="order_cancel", file=None)
        update_status = await update_state(call.message.chat.id, 'finish', json_data)
        logger.info(update_status)
        await write_to_yt_table(json_data, ticket, 'order_cancel')
        await call.message.answer("Мы получили ваш вопрос и уже взяли его в работу. "
                                  "Пожалуйста, подождите решения и не создавайте повторных запросов об одном заказе, "
                                  "это не ускорит его решения.")
    except Exception as e:
        logger.error(e)


@dp.callback_query_handler(text=[*themes['cabinet'].keys()])
async def get_theme(call: types.CallbackQuery):
    try:
        db_data = await update_db_data_message(call)
        json_data, state = db_data.values()
        json_data.update(theme=str(call.data))
        update_status = await update_state(call.message.chat.id, 'cabinet_get_text', json_data)
        logger.info(update_status)
        await call.message.answer("Пожалуйста, оставьте описание вопроса или комментарий:")
    except Exception as e:
        logger.error('cabinet themes {}'.format(e))


@dp.errors_handler(exception=Exception)
async def errors_handler(update: types.Update, exception: Exception):
    try:
        raise Exception
    except Exception as e:
        print(e)
        logger.error(
            f'Получено исключение {e}\n'
            f'{traceback.format_exc()}',
        )
    return True
