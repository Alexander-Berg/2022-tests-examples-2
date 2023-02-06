OPERATOR_IDS = {
    'operator_1': '111',
    'operator_2': '222',
    'operator_no_calls': 'no_calls_id',
}
OPERATOR_CALLCENTERS = {
    'operator_1': 'volgograd_cc',
    'operator_2': 'krasnodar_cc',
    'operator_no_calls': 'volgograd_cc',
}
PHONE_TO_PHONE_ID_MAPPING = {
    '+79872676410': 'abonent_phone_id',
    '+79999999999': 'phone_id_1_extra',
    '+79991111111': 'phone_id_1',
    '+79992222222': 'phone_id_2',
    '+79993333333': 'phone_id_3',
}
DEFAULT_LOOKUP_RULES = (
    {'talk_duration': {'from': 60, 'to': 300}},
    {'talk_duration': {'from': 300, 'to': 900}},
    {'talk_duration': {'from': 900}},
)
OTHER_LOOKUP_RULES = (
    {'talk_duration': {'from': 40, 'to': 120}},
    {'talk_duration': {'from': 120, 'to': 240}},
    {'talk_duration': {'from': 240}},
)
DEFAULT_QA_TICKET_FIELDS = {
    'full_name': {'name': 'imaOperatora', 'description': 'Имя оператора'},
    'callcenter_id': {'name': 'components', 'description': 'Колл-центр'},
    'login': {'name': 'login', 'description': 'Логин'},
    'call_time': {'name': 'RecTime', 'description': 'Время звонка'},
    'call_date': {'name': 'RecDate', 'description': 'Дата звонка'},
    'talk_duration': {
        'name': 'DialogTime',
        'description': 'Время в разговоре',
    },
    'abonent_phone_number': {
        'name': 'PhoneNumberOktell',
        'description': 'Номер абонента',
    },
    'called_number': {'name': 'nomerLinii', 'description': 'Номер линии'},
    'city': {'name': 'gorod', 'description': 'Город'},
    'queue': {'name': 'imaOceredi', 'description': 'Имя очереди'},
    'recording_url': {'name': 'RecURL', 'description': 'Ссылка на диалог'},
    'order_created': {
        'name': 'zakazOformlen',
        'description': 'Заказ оформлен',
    },
    'order_url': {
        'name': 'ssylkaNaZakaz1',
        'description': 'Ссылка на заказ 1',
    },
    'order_url_2': {
        'name': 'ssylkaNaZakaz2',
        'description': 'Ссылка на заказ 2',
    },
    'order_url_3': {
        'name': 'ssylkaNaZakaz3',
        'description': 'Ссылка на заказ 3',
    },
    'order_url_4': {
        'name': 'ssylkaNaZakaz4',
        'description': 'Ссылка на заказ 4',
    },
    'order_url_5': {
        'name': 'ssylkaNaZakaz5',
        'description': 'Ссылка на заказ 5',
    },
    'ml_rating': {'name': 'mlRating', 'description': 'Рейтинг ML'},
    'ticket_type': 'prosluskaIOcenka',
    'support_direction': 'test_direction',
}
EMPTY_QA_TICKET_FIELDS: dict = {
    'full_name': {},
    'callcenter_id': {},
    'login': {},
    'call_time': {},
    'call_date': {},
    'talk_duration': {},
    'abonent_phone_number': {},
    'called_number': {},
    'city': {},
    'queue': {},
    'recording_url': {},
    'order_created': {},
    'order_url': {},
}
CC_PHONE_INFO_MAP = {
    '__default__': {
        'application': 'call_center',
        'city_name': 'Неизвестен',
        'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
    },
    '+74959999999': {
        'application': 'call_center',
        'city_name': 'Москва',
        'geo_zone_coords': {'lon': 37.622504, 'lat': 55.753215},
    },
    '+74958888888': {
        'application': 'call_center',
        'city_name': 'Набережные Челны',
        'geo_zone_coords': {'lon': 52.406384, 'lat': 55.740776},
    },
    '+74957777777': {
        'application': 'call_center',
        'city_name': 'Нижневартовск',
        'geo_zone_coords': {'lon': 76.558902, 'lat': 60.938545},
    },
}
ORDER_BY_CALL_LINK_ID = {
    '__default__': set(),
    'id1/hash': {'order+id+1'},
    'id3/hash': {'order=id_3'},
    'id4/hash': {'order=id_4'},
    'id5/hash': {'order=id=5'},
    'id6/hash': {'order=id_6'},
    'id7/hash': {'order=id_7'},
    'id8/hash': {'order=id_8'},
    'id9/hash': {'order=id_9'},
    'id10/hash': {'order=id_10'},
    'id11/hash': {'order=id_11'},
    'id12/hash': {'order=id_12', 'order=id-12', 'order=id+12'},
    'id13/hash': {'order=id_13'},
    'id16/hash': {
        'order=id_16',
        'order=id-16',
        'order=id+16',
        'order=id/16',
        'order=id=16',
    },
    'id17/hash': {'order=id_17'},
    'id18/hash': {'order=id_18'},
    'id19/hash': {'order=id_19'},
    'id20/hash': {'order=id_20'},
    'id22/hash': {'order=id_22'},
}
