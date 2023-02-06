KEYSET = 'grocery_performer_communications'
DEPOT_ID_LEGACY = '12345'
ORDER_ID = '451ae655d0a84c7c98a195f6e295bcb3-grocery'
SHORT_ORDER_ID = '210619-566-7598'
REGION_ID = 123
TIMEZONE = 'Europe/Moscow'
DEPOT_SHORT_ADDRESS = 'Кооперативная, 2'
TASK_ID = 'TASK_UNIQUE_ID'

ORDER = {
    'order_id': ORDER_ID,
    'short_order_id': SHORT_ORDER_ID,
    'depot_id': DEPOT_ID_LEGACY,
    'zone_type': 'pedestrian',
    'created': '2021-06-22T12:00:00+0300',
    'max_eta': 3600,
    'user_locale': 'ru',
    'personal_phone_id': '507f191e810c19729de860ea',
    'items': [
        {
            'item_id': 'item_id_1',
            'title': 'Молоко',
            'price': '40.99',
            'currency': 'RUB',
            'quantity': '1',
        },
        {
            'item_id': 'item_id_2',
            'title': 'Хлеб',
            'price': '30.11',
            'currency': 'RUB',
            'quantity': '2',
        },
    ],
}

PARK_ID = '05941f975c604bcebc1933864bd18f41'
PROFILE_ID = '4bc5f30599b940368403830a932c2f3d'

# (park_id)_(driver_id) or (dbid_uuid)
PERFORMER_ID = f'{PARK_ID}_{PROFILE_ID}'

PERFORMER_NAME = 'Петр Петров'
REPORT_TYPE = 'weekly'

REPORT = {
    'currency': 'NIS',
    'employer_name': 'Self-employed',
    'depot_id': DEPOT_ID_LEGACY,
    'period_start': '2021-07-15T00:00:00+03:00',
    'period_end': '2021-07-22T00:00:00+03:00',
    'tips': '25.11',
    'total_income': '295.42',
    'slot_count': 10,
    'order_count': 24,
    'duration_total': '7.5',
    'weekdays': {
        'duration': '6',
        'duration_income': '100.31',
        'orders': 17,
        'orders_income': '120.01',
    },
    'weekends': {
        'duration': '1.5',
        'duration_income': '20',
        'orders': 7,
        'orders_income': '60.21',
    },
    'adjustment': '-30.22',
}

REPORT_EXTRA = {
    'currency': 'NIS',
    'employer_name': 'Self-employed',
    'depot_id': DEPOT_ID_LEGACY,
    'period_start': '2021-07-15T00:00:00+03:00',
    'period_end': '2021-07-22T00:00:00+03:00',
    'tips': '25.11',
    'total_income': '295.42',
    'slot_count': 10,
    'order_count': 24,
    'duration_total': '7.5',
    'adjustment': '+30.22',
    'extra_argument': 'extra field value',
    'unused_argument': 'unused argument value',
}
