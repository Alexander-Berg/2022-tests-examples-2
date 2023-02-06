import pytest


TRANSLATIONS = pytest.mark.translations(
    client_messages={
        'scooters.screens.shortcuts.qr_scan.title': {'ru': 'Сканировать'},
        'scooters.screens.shortcuts.qr_scan.subtitle': {
            'ru': 'QR-код на руле самоката',
        },
        'scooters.screens.shortcuts.support.title': {'ru': 'Поддержка'},
        'scooters.claim.scooter_point_title': {
            'ru': 'Аккумулятор для самоката №%(number)s',
        },
        'scooters.claim.scooter_point_comment': {'ru': 'Самокат №%(number)s'},
        'scooters.claim.depot_point_title': {
            'ru': 'Возврат аккумуляторов в лавку',
        },
        'scooters.claim.depot_point_comment': {
            'ru': 'Возврат аккумуляторов в лавку',
        },
        'scooters.claim.deadflow_comment': {'ru': 'Заказ на воскрешение'},
    },
)
