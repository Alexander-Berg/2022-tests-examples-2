CARS = [
    {
        'location': {'lat': 45.01254, 'lon': 39.05333},
        'model_id': 'ninebot_max_plus',
        'id': 'fde7fa72-00c7-df2a-577d-364291726950',
        'number': '1234',
        'telematics': {
            'fuel_distance': 31.54466133,
            'fuel_level': 64,
            'remaining_time': 9000,
        },
    },
]

AREAS = [
    {
        'geometry': {
            'coordinates': [
                [
                    [37.31, 55.61],
                    [37.24, 55.62],
                    [37.21, 55.58],
                    [37.31, 55.61],
                ],
            ],
            'type': 'Polygon',
        },
        'id': 'scooters__polygon__135',
        'revision': '123',
        'tags': [],
    },
    {
        'geometry': {
            'coordinates': [
                [
                    [37.451, 55.851],
                    [37.452, 55.851],
                    [37.452, 55.852],
                    [37.452, 55.851],
                ],
            ],
            'type': 'Polygon',
        },
        'id': 'scooters__polygon__456',
        'revision': '12',
        'tags': [],
    },
]

DEFAULT_HEADERS = {
    'X-Yandex-UID': '4060779350',
    'X-Ya-User-Ticket': 'user-ticket',
    'X-YaTaxi-UserId': 'user-id',
    'X-YaTaxi-User': 'personal_phone_id=123345',
    'X-YaTaxi-Pass-Flags': 'portal,neophonish,ya-plus,cashback-plus',
    'X-Ya-Phone-Verified': '+78005553535',
    'DeviceId': 'DEVICE_ID',
}

CARD_PAYMENT_METHOD = {'account_id': 'card', 'card': 'x123'}

DEFAULT_PAYLOAD = {'payment_methods': [CARD_PAYMENT_METHOD]}
