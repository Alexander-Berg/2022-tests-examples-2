from settings.settings import logger, tracker
from keyboard import keyboard
import suptech


async def create_tracker_ticket(data, category, file=None):
    """
    Создание тикета в очереди DVCORPBOT.
    :param data: данные из хранилища state, должны быть order_id, theme, feedback_message, time, chat_title, chat_id, user_login
    :param category: параметр отвечает за выбранный блок (complaint, order или cabinet). Служит для хранения тематики обращения.
    :param file:
    :return:
    """
    category_rus = {
        'complaint': 'Жалоба на курьера',
        'order': 'Заказ',
        'order_cancel': 'Отмена заказа',
        'cabinet': 'Кабинет'
    }
    if category in ('complaint', 'order', 'order_cancel'):
        description_title = 'заказа'
    else:
        description_title = 'кабинета'

    corp_type = data.get('corp_type', 'Неизвестен')
    corp_id = data.get('corp_id', 'Неизвестно')

    description = 'Номер {}: {}\nТематика: {}\nОтзыв: {}\nВремя обращения: {}\nНазвание чата: {}\nТип корпа:{}'.format(
        description_title,
        data['order_id'],
        data['theme'],
        data['feedback_message'],
        data['time'],
        data['chat_title'],
        corp_type)

    ticket_data = {
        'queue': 'DVCORPBOT',
        'summary': 'Бот Доставки: {} "{}/{}"'.format(data['order_id'], category_rus.get(category, ''),
                                                     keyboard.themes[category][data['theme']]),
        'description': description,
        'parkDbId': str(data['chat_id']),
        'nazvanieChata': str(data['chat_title']),
        'taximeterVersion': '{}_{}'.format(category, data['theme']),
        'OrderId': str(data['order_id']),
        'CorpCompanyName': corp_type,
        'corpClientId': corp_id,
        'tags': ['delivery_corp_bot_223_test', 'delivery_corp_bot_223_test_{}'.format(category), 'не_в_крутилку',
                 '{}_{}'.format(category, data['theme'])],
        'add_user_email': 'robot-delivery-sup@yandex-team.ru',
        'add_support_email': 'dvbot@yandex-taxi.yaconnect.com'
    }

    try:
        if file:
            ticket_data['attachmentIds'] = file
        ticket = tracker.create_issue(ticket_data)
        logger.info(ticket)
        return ticket["key"]
    except Exception as e:
        logger.error(e)
