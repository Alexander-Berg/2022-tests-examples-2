# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import datetime

from google.protobuf import timestamp_pb2
import mission_pb2


X_REQUEST_APPLICATION_HEADER = (
    'app_brand=yataxi,app_ver2=21,platform_ver1=12,app_ver1=5,'
    'app_name=iphone,app_build=release,platform_ver2=1,'
    'app_ver3=43204,platform_ver3=2'
)

NEW_MISSION = mission_pb2.MissionStatus.MISSION_STATUS_NOT_ACCEPTED
MISSION_IN_PROGRESS = mission_pb2.MissionStatus.MISSION_STATUS_IN_PROGRESS
MISSION_COMPLETED = mission_pb2.MissionStatus.MISSION_STATUS_COMPLETED
PROGRESS_IN_PROGRESS = mission_pb2.ProgressStatus.PROGRESS_STATUS_IN_PROGRESS
PROGRESS_COMPLETED = mission_pb2.ProgressStatus.PROGRESS_STATUS_COMPLETED

MOCK_NOW = '2021-09-25T12:00:00+0000'
TS_AFTER_NOW = timestamp_pb2.Timestamp()
# pylint: disable=no-member
TS_AFTER_NOW.FromDatetime(
    datetime.datetime.fromisoformat('2021-09-25T13:00:00+00:00'),
)

TS_BEFORE_NOW = timestamp_pb2.Timestamp()
# pylint: disable=no-member
TS_BEFORE_NOW.FromDatetime(
    datetime.datetime.fromisoformat('2021-09-25T11:00:00+00:00'),
)

TS_1_DAY_AFTER_NOW = timestamp_pb2.Timestamp()
# pylint: disable=no-member
TS_1_DAY_AFTER_NOW.FromDatetime(
    datetime.datetime.fromisoformat('2021-09-26T13:00:00+00:00'),
)

MISSIONS_NOTIFICATIONS_CLIENT_MESSAGES = {
    'cashback_levels.mission.notification.start.title': {
        'ru': [
            'Прокатитесь %(target)s раз в Комфорте',
            'Прокатитесь %(target)s раза в Комфорте',
            'Прокатитесь %(target)s раз в Комфорте',
        ],
    },
    'cashback_levels.mission.notification.finish.title': {
        'ru': ['Челлендж выполнен!'],
    },
    'cashback_levels.mission.notification.mission.title': {
        'ru': [
            'До награды осталась %(target)s поездка',
            'До награды осталось %(target)s поездки',
            'До награды осталось %(target)s поездок',
        ],
    },
    'cashback_levels.mission.notification.start.description': {
        'ru': ['Описание анонса цели'],
    },
    'cashback_levels.mission.notification.finish.description': {
        'ru': ['Описание карточки завершения цели'],
    },
    'cashback_levels.mission.notification.mission.description': {
        'ru': ['Описание карточки прогресса по цели'],
    },
    'cashback_levels.mission.notification.header.text': {
        'ru': ['Условия акции <img src="arrow_image_tag"></img>'],
    },
    'cashback_levels.mission.notification.progress.title': {
        'ru': [
            'Еще %(target)s поездка <img src="dot_image_tag"></img>',
            'Еще %(target)s поездки <img src="dot_image_tag"></img>',
            'Еще %(target)s поездок <img src="dot_image_tag"></img>',
        ],
    },
    'cashback_levels.mission.notification.progress.subtitle': {
        'ru': [
            '<img src="clock_image_tag"></img> %(days)s день до окончания',
            '<img src="clock_image_tag"></img> %(days)s дня до окончания',
            '<img src="clock_image_tag"></img> %(days)s дней до окончания',
        ],
    },
    'cashback_levels.mission.notification.reward.title': {'ru': ['Награда']},
    'cashback_levels.mission.notification.reward.subtitle': {
        'ru': ['Быллы придут в течение суток'],
    },
    'cashback_levels.mission.notification.reward.description': {
        'ru': [
            '<container meta_color="some_meta_color">'
            '<cashback_levels_reward_icon><img src="%(icon)s"></img></cashback_levels_reward_icon>'  # noqa: E501
            '<cashback_levels_reward_text> %(text)s</cashback_levels_reward_text>'  # noqa: E501
            '</container>',
        ],
    },
    'cashback_levels.mission.notification.buttons.action.title': {
        'ru': ['Я в деле'],
    },
    'cashback_levels.mission.notification.buttons.reject.title': {
        'ru': ['Отказаться'],
    },
    'cashback_levels.mission.notification.buttons.finish_action.title': {
        'ru': ['Как потратить баллы'],
    },
    'cashback_levels.mission.notification.buttons.confirm.title': {
        'ru': ['Понятно'],
    },
    'cashback_levels.mission.notification.buttons.mission_action.title': {
        'ru': ['В Комфорт'],
    },
}

CASHBACK_LEVELS_TARIFF_NAME_ORDER_MAPPING = {
    'econom': {
        'pretty_name_key': 'cashback_levels.mission.templates.econom_tariff',
        'order_number': 0,
        'vertical': 'taxi',
    },
    'business': {
        'pretty_name_key': 'cashback_levels.mission.templates.business_tariff',
        'order_number': 1,
        'vertical': 'taxi',
    },
    'comfortplus': {
        'pretty_name_key': (
            'cashback_levels.mission.templates.comportplus_tariff'
        ),
        'order_number': 2,
        'vertical': 'taxi',
    },
    'vip': {
        'pretty_name_key': 'cashback_levels.mission.templates.vip_tariff',
        'order_number': 3,
        'vertical': 'taxi',
    },
    'maybach': {
        'pretty_name_key': 'cashback_levels.mission.template.maybach_tariff',
        'order_number': 4,
        'vertical': 'ultimate',
    },
}

MISSION_TEMPLATES_CLIENT_MESSAGES = {
    'cashback_levels.mission.templates.rides_count_template': {
        'ru': ['%(value)s поездка', '%(value)s поездки', '%(value)s поездок'],
    },
    'cashback_levels.mission.templates.econom_tariff': {'ru': ['В Эконом']},
    'cashback_levels.mission.templates.business_tariff': {'ru': ['В Комфорт']},
    'cashback_levels.mission.templates.comportplus_tariff': {
        'ru': ['В Комфорт+'],
    },
    'cashback_levels.mission.templates.vip_tariff': {'ru': ['В Бизнес']},
    'cashback_levels.mission.template.maybach_tariff': {'ru': ['В Майбах']},
}
