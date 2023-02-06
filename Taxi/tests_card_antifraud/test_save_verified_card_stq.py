import pytest


def select_device_cards(pgsql, user_uid, device_id):
    cursor = pgsql['card_antifraud'].cursor()
    cursor.execute(
        (
            f'SELECT * '
            f'FROM card_antifraud.verified_cards '
            f'WHERE yandex_uid = \'{user_uid}\''
            f'AND device_id = \'{device_id}\''
        ),
    )
    return list(cursor)


def select_device(pgsql, user_uid, device_id):
    cursor = pgsql['card_antifraud'].cursor()
    cursor.execute(
        (
            f'SELECT * '
            f'FROM card_antifraud.verified_devices '
            f'WHERE yandex_uid = \'{user_uid}\''
            f'AND device_id = \'{device_id}\''
        ),
    )
    return list(cursor)


@pytest.fixture(name='mock_cardstorage')
def _mock_cardstorage(mockserver):
    @mockserver.json_handler('/cardstorage/v1/payment_methods')
    def _mock_payment_methods(request):
        # TODO: move to static?
        sample_card_1 = {
            'valid': True,
            'permanent_card_id': 'permanent_card_id',
            'system': 'VISA',
            'billing_card_id': 'billing_card_id',
            'currency': 'rub',
            'region_id': '181',
            'expiration_year': 2050,
            'expiration_month': 6,
            'card_id': 'x-123456',
            'number': '111111***',
            'persistent_id': 'persistent_id',
            'possible_moneyless': False,
            'regions_checked': [],
            'owner': 'owner',
            'bound': True,
            'unverified': False,
            'from_db': False,
            'busy': False,
            'busy_with': [],
        }
        sample_card_2 = {
            'valid': True,
            'permanent_card_id': 'permanent_card_id',
            'system': 'VISA',
            'billing_card_id': 'billing_card_id',
            'currency': 'rub',
            'region_id': '181',
            'expiration_year': 2050,
            'expiration_month': 6,
            'card_id': 'x-234567',
            'number': '111111***',
            'persistent_id': 'persistent_id',
            'possible_moneyless': False,
            'regions_checked': [],
            'owner': 'owner',
            'bound': True,
            'unverified': False,
            'from_db': False,
            'busy': False,
            'busy_with': [],
        }
        return {'available_cards': [sample_card_1, sample_card_2]}


async def test_no_verified_cards_for_already_verified_device(
        stq_runner, mock_cardstorage, pgsql,
):
    task_id = '123'
    yandex_uid = '1234'
    device_id = 'verified_device_1'
    card_id = 'x-123456'

    args = [yandex_uid, card_id, device_id]

    await stq_runner.save_verified_card.call(task_id=task_id, args=args)

    pg_result = select_device_cards(pgsql, yandex_uid, device_id)
    assert not pg_result


async def test_verified_card_added_for_not_verified_device(
        stq_runner, mock_cardstorage, pgsql,
):
    task_id = '123'
    yandex_uid = '1234'
    device_id = 'not_verified_device'
    card_id = 'x-123456'

    args = [yandex_uid, card_id, device_id]

    await stq_runner.save_verified_card.call(task_id=task_id, args=args)

    pg_result = select_device_cards(pgsql, yandex_uid, device_id)
    assert len(pg_result) == 1
    assert card_id in pg_result[0]


async def test_device_becomes_verified(stq_runner, mock_cardstorage, pgsql):
    task_id = '123'
    yandex_uid = '2345'
    device_id = 'not_verified_device_1'
    card_id = 'x-123456'

    args = [yandex_uid, card_id, device_id]

    await stq_runner.save_verified_card.call(task_id=task_id, args=args)

    pg_result = select_device_cards(pgsql, yandex_uid, device_id)
    assert not pg_result

    pg_result = select_device(pgsql, yandex_uid, device_id)
    assert len(pg_result) == 1
    assert device_id in pg_result[0]
