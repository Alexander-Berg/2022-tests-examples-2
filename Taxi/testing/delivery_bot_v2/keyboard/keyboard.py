from aiogram import types

themes = {
    "complaint": {"start_message": "Сообщить о нарушении",
                  "rude_courier": "Грубый курьер, хамство",
                  "courier_do_not_speak_russian": "Плохо говорит по-русски",
                  "courier_demand_payment": "Требовал доплату",
                  "untidy_courier": "Неопрятный курьер, грязная одежда",
                  "courier_without_heat_capacity": "Курьер без термоемкости, термокороба",
                  "thank_the_courier": "Поблагодарить курьера",
                  "back_to_menu": "Вернуться назад",
                  "send_comment": "Да",
                  "say_nothing": "Нет",
                  "feedback_back": "Назад",
                  },
    "order": {
        "order_status": "Статус заказа, когда будет доставлен",
        "damaged_product": "Товар испорчен или поврежден",
        "mixed_up_orders": "Перепутали заказы",
        "order_not_delivered": "Заказ не доставлен",
        "refund": "Оформить возврат товара, доставлять заказ не нужно",
        "back_to_menu": "Вернуться назад",
        "refund_confirmed": "Да",
        "no_refund": "Нет"
    },
    "order_cancel": {
        "no_need_to_deliver": "Доставлять не нужно/Отменено получателем",
        "delivered_by_another_courier": "Отвез другой курьер",
        "invalid_recipient_address": "Неверный адрес получателя",
        "courier_refused_to_pick_up": "Курьер отказался забирать заказ",
        "courier_didnt_arrive": "Курьер не приехал",
        "technical_error": "Техническая ошибка"
    },
    "cabinet": {
        "problem_with_logging": "Проблема с входом в Личный кабинет",
        "act_request": "Запрос акта сверки",
        "upload_closing_documents": "Выгрузить закрывающие документы",
        "request_for_new_access": "Запрос новых доступов",
        "top_up_account": "Пополнить счёт в ЛК",
        "client_activation": "Активация клиента",
        "service_not_active": "Сервис не активен",
        "no_money_received": "Не поступили деньги на баланс",
        "checking_the_cost": "Проверка стоимости заказов",
        "no_money_returned": "Не вернулись деньги на счёт",
    },
    "start": {
        "menu_complaint": "Оставить отзыв на курьера",
        "menu_order": "Помощь с заказом",
        "menu_cancel_order": "Отменить заказ",
        "menu_cabinet": "Личный кабинет и документы"
    },
    "start_lite": {
        "menu_complaint": "Оставить отзыв на курьера"
    }
}


def keyboard(key):
    keys = types.InlineKeyboardMarkup()
    if key == "complaint_start":
        keys.add(types.InlineKeyboardButton(text=themes["complaint"]["start_message"], callback_data="start_message"))
    elif key == "complaint_themes":
        keys.add(types.InlineKeyboardButton(text=themes["complaint"]["rude_courier"], callback_data="rude_courier"))
        keys.add(types.InlineKeyboardButton(text=themes["complaint"]["courier_do_not_speak_russian"],
                                            callback_data="courier_do_not_speak_russian"))
        keys.add(types.InlineKeyboardButton(text=themes["complaint"]["courier_demand_payment"],
                                            callback_data="courier_demand_payment"))
        keys.add(types.InlineKeyboardButton(text=themes["complaint"]["untidy_courier"], callback_data="untidy_courier"))
        keys.add(types.InlineKeyboardButton(text=themes["complaint"]["courier_without_heat_capacity"],
                                            callback_data="courier_without_heat_capacity"))
        keys.add(types.InlineKeyboardButton(text=themes["complaint"]["thank_the_courier"],
                                            callback_data="thank_the_courier"))
    elif key == "complaint_feedback_question":
        keys.add(types.InlineKeyboardButton(text=themes["complaint"]["send_comment"],
                                            callback_data="send_comment"))
        keys.add(types.InlineKeyboardButton(text=themes["complaint"]["say_nothing"], callback_data="say_nothing"))
        keys.add(types.InlineKeyboardButton(text=themes["complaint"]["feedback_back"], callback_data="feedback_back"))
    elif key == "start":
        keys.add(types.InlineKeyboardButton(text=themes["start"]["menu_complaint"],
                                            callback_data="menu_complaint"))
        keys.add(types.InlineKeyboardButton(text=themes["start"]["menu_order"], callback_data="menu_order"))
        keys.add(types.InlineKeyboardButton(text=themes["start"]["menu_cabinet"], callback_data="menu_cabinet"))
    elif key == "start_lite":
        keys.add(types.InlineKeyboardButton(text=themes["start_lite"]["menu_complaint"],
                                            callback_data="menu_complaint"))
    elif key == "start_private":
        keys.add(types.InlineKeyboardButton(text=themes["start"]["menu_complaint"],
                                            callback_data="menu_complaint"))
        keys.add(types.InlineKeyboardButton(text=themes["start"]["menu_order"], callback_data="menu_order"))
        keys.add(
            types.InlineKeyboardButton(text=themes["start"]["menu_cancel_order"], callback_data="menu_cancel_order"))
        keys.add(types.InlineKeyboardButton(text=themes["start"]["menu_cabinet"], callback_data="menu_cabinet"))
    elif key == "order_themes":
        keys.add(types.InlineKeyboardButton(text=themes["order"]["order_status"], callback_data="order_status"))
        keys.add(types.InlineKeyboardButton(text=themes["order"]["damaged_product"], callback_data="damaged_product"))
        keys.add(types.InlineKeyboardButton(text=themes["order"]["mixed_up_orders"],
                                            callback_data="mixed_up_orders"))
        keys.add(types.InlineKeyboardButton(text=themes["order"]["order_not_delivered"],
                                            callback_data="order_not_delivered"))
        keys.add(types.InlineKeyboardButton(text=themes["order"]["refund"],
                                            callback_data="refund"))
    elif key == "order_cancel_themes":
        keys.add(types.InlineKeyboardButton(text=themes["order_cancel"]["no_need_to_deliver"],
                                            callback_data="no_need_to_deliver"))
        keys.add(types.InlineKeyboardButton(text=themes["order_cancel"]["delivered_by_another_courier"],
                                            callback_data="delivered_by_another_courier"))
        keys.add(types.InlineKeyboardButton(text=themes["order_cancel"]["invalid_recipient_address"],
                                            callback_data="invalid_recipient_address"))
        keys.add(types.InlineKeyboardButton(text=themes["order_cancel"]["courier_refused_to_pick_up"],
                                            callback_data="courier_refused_to_pick_up"))
        keys.add(types.InlineKeyboardButton(text=themes["order_cancel"]["courier_didnt_arrive"],
                                            callback_data="courier_didnt_arrive"))
        keys.add(types.InlineKeyboardButton(text=themes["order_cancel"]["technical_error"],
                                            callback_data="technical_error"))
    elif key == "order_feedback_question":
        keys.add(types.InlineKeyboardButton(text=themes["order"]["refund_confirmed"],
                                            callback_data="refund_confirmed"))
        keys.add(types.InlineKeyboardButton(text=themes["order"]["no_refund"], callback_data="no_refund"))
    elif key == "cabinet_themes":
        keys.add(types.InlineKeyboardButton(text=themes["cabinet"]["problem_with_logging"],
                                            callback_data="problem_with_logging"))
        keys.add(types.InlineKeyboardButton(text=themes["cabinet"]["act_request"], callback_data="act_request"))
        keys.add(types.InlineKeyboardButton(text=themes["cabinet"]["upload_closing_documents"],
                                            callback_data="upload_closing_documents"))
        keys.add(types.InlineKeyboardButton(text=themes["cabinet"]["request_for_new_access"],
                                            callback_data="request_for_new_access"))
        keys.add(types.InlineKeyboardButton(text=themes["cabinet"]["top_up_account"],
                                            callback_data="top_up_account"))
        keys.add(
            types.InlineKeyboardButton(text=themes["cabinet"]["client_activation"], callback_data="client_activation"))
        keys.add(types.InlineKeyboardButton(text=themes["cabinet"]["service_not_active"],
                                            callback_data="service_not_active"))
        keys.add(
            types.InlineKeyboardButton(text=themes["cabinet"]["no_money_received"], callback_data="no_money_received"))
        keys.add(types.InlineKeyboardButton(text=themes["cabinet"]["checking_the_cost"],
                                            callback_data="checking_the_cost"))
        keys.add(
            types.InlineKeyboardButton(text=themes["cabinet"]["no_money_returned"], callback_data="no_money_returned"))
    return keys
