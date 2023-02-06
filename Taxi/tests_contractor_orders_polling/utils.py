HANDLER_URL = 'driver/v1/driver/polling/order'

HEADERS = {
    'X-Request-Application': 'taximeter',
    'X-Request-Platform': 'android',
    'X-Request-Application-Version': '9.07',
    'X-YaTaxi-Park-Id': '999',
    'X-YaTaxi-Driver-Profile-Id': '888',
    'Accept-Language': 'ru',
}

AIRPORT_QUEUE_PART = {
    'active': [
        {
            'airport_title': 'Курумоч',
            'current_place': '1 - 5',
            'queue_title': 'Заказы из аэропорта',
            'queues_infos': [
                {
                    'class_code': 2,
                    'current_place': '1 - 5',
                    'queue_exact_time': '1 ч',
                },
                {'class_code': 512, 'current_place': '1 - 5'},
            ],
            'region_name': 'samara_airport_waiting',
            'show_details_button': True,
            'show_navigation_button': False,
        },
    ],
    'dialog_events': [
        {'dialog': 'in_queue', 'from': 'near', 'to': 'in'},
        {'dialog': 'in_queue', 'to': 'in'},
    ],
    'dialog_state': 'in',
    'dialogs': [
        {
            'affirmative_button': 'Да',
            'name': 'busy',
            'negative_button': 'Отмена',
            'severity': 'info',
            'text': 'Если поставите статус «Занят». Вы уверены?',
            'title': 'Вы покинете очередь',
            'type': 'alert',
        },
        {
            'affirmative_button': 'Да',
            'name': 'change_tariff',
            'negative_button': 'Отмена',
            'severity': 'info',
            'text': 'Если поменяете тариф. Вы уверены?',
            'title': 'Вы покинете очередь',
            'type': 'alert',
        },
        {
            'name': 'in_queue',
            'severity': 'info',
            'text': 'Вы в очереди, ожидайте заказ.',
            'type': 'overlay_notification',
        },
    ],
    'near': [],
}
