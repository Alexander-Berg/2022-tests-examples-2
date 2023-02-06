import pytest

from processing_antifraud import const


# pylint: disable=invalid-name
def mark_check_card_settings_experiment(
        enabled: bool = True, zone: str = 'moscow',
):
    return pytest.mark.client_experiments3(
        consumer=const.PROCESSING_ANTIFRAUD_CONSUMER,
        experiment_name=const.EXPERIMENTS3_CHECK_CARD_SETTINGS,
        args=[
            {'name': 'zone', 'type': 'string', 'value': zone},
            {
                'name': 'phone_id',
                'type': 'string',
                'value': '58247911c0d947f1eef0b1bb',
            },
            {'name': 'yandex_uid', 'type': 'string', 'value': '123456'},
        ],
        value={'enabled': enabled},
    )


# pylint: disable=invalid-name
def mark_move_to_cash_settings_experiment(reason: str):
    return pytest.mark.client_experiments3(
        consumer=const.PROCESSING_ANTIFRAUD_CONSUMER,
        experiment_name=const.EXPERIMENTS3_MOVE_TO_CASH_SETTINGS,
        args=[
            {
                'name': 'phone_id',
                'type': 'string',
                'value': '58247911c0d947f1eef0b1bb',
            },
            {'name': 'yandex_uid', 'type': 'string', 'value': '123456'},
        ],
        value={'reason': reason, 'need_cvn': False},
    )
