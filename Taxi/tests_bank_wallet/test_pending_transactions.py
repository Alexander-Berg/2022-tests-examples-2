import pytest

from tests_bank_wallet import common

PENDING_TOPUP = {
    'image': 'https://avatars.mdst.yandex.net/get-fintech/65575/income',
    'money': {'amount': '999', 'currency': 'RUB'},
    'status': {'code': 'HOLD', 'message': ''},
    'transaction_id': '4cd35924-8d69-4653-93a6-e4aa99afc5ea',
    'type': 'TOPUP',
}

TOPUP_LOCALIZATION = {
    'ru': {
        'additional_fields': [
            {
                'value': (
                    'Сумма пока не зачислена на счёт — сообщим, как только '
                    'это случится'
                ),
            },
        ],
        'description': 'с карты Visa ···· 5368',
        'name': 'Пополнение',
    },
    'en': {
        'additional_fields': [
            {
                'value': (
                    'The amount has not yet been credited to the account — '
                    'we will inform you as soon as this happens'
                ),
            },
        ],
        'description': 'from card Visa ···· 5368',
        'name': 'Top up',
    },
}

PENDING_TRANSFER = {
    'ru': {
        'image': 'tinkoff_url',
        'money': {'amount': '111', 'currency': 'RUB'},
        'status': {'code': 'HOLD', 'message': ''},
        'transaction_id': 'c8fe469a-3c83-4f7e-ad12-1417539a8b6a',
        'type': 'TRANSFER_OUT',
        'description': 'Перевод',
    },
    'en': {
        'image': 'tinkoff_url',
        'money': {'amount': '111', 'currency': 'RUB'},
        'status': {'code': 'HOLD', 'message': ''},
        'transaction_id': 'c8fe469a-3c83-4f7e-ad12-1417539a8b6a',
        'type': 'TRANSFER_OUT',
        'description': 'Transfer',
    },
}

TRANSFER_LOCALIZATION = {
    'ru': {
        'additional_fields': [
            {
                'value': (
                    'Сумма пока не зачислена на счёт — сообщим, как '
                    'только это случится'
                ),
            },
            {
                'name': 'Перевод по номеру телефона',
                'value': '+7 912 345-67-89',
            },
            {'name': 'Банк получателя', 'value': 'Тинькофф'},
            {'name': 'Статус', 'value': 'В обработке'},
        ],
        'name': 'Иван И.',
    },
    'en': {
        'additional_fields': [
            {
                'value': (
                    'The amount has not yet been credited to the account — '
                    'we will inform you as soon as this happens'
                ),
            },
            {'name': 'Transfer by phone number', 'value': '+7 912 345-67-89'},
            {'name': 'Receiver bank', 'value': 'Tinkoff'},
            {'name': 'Status', 'value': 'In processing'},
        ],
        'name': 'Иван И.',
    },
}


V1_HANDLE_PATH = '/v1/wallet/v1/get_pending_transactions'
V2_HANDLE_PATH = '/v1/wallet/v2/get_pending_transactions'


def _make_body(handle_path, limit=None, cursor=None):
    body = {}
    if cursor:
        body.update({'cursor': cursor})

    if handle_path == V1_HANDLE_PATH:
        if limit:
            body.update({'limit': limit})
        return body

    assert handle_path == V2_HANDLE_PATH
    limit = limit if limit else 200
    body.update({'agreement_id': 'public_agreement_id', 'limit': limit})
    return body


@pytest.mark.parametrize('handle_path', [V1_HANDLE_PATH, V2_HANDLE_PATH])
async def test_not_authorized(taxi_bank_wallet, handle_path):
    response = await taxi_bank_wallet.post(
        handle_path, json=_make_body(handle_path, 10),
    )
    assert response.status_code == 401


@pytest.mark.parametrize('handle_path', [V1_HANDLE_PATH, V2_HANDLE_PATH])
@pytest.mark.parametrize(
    'locale, title, topups_amount, topups_order, topups_start, topups_step, '
    'transfers_amount, transfers_order, transfers_start, transfers_step',
    [
        ['ru', None, 0, None, None, None, 0, None, None, None],
        ['en', None, 0, None, None, None, 0, None, None, None],
        ['ru', 'Перевод', 0, None, None, None, 1, None, 0, 1],
        ['en', 'Transfer', 0, None, None, None, 1, None, 0, 1],
        ['ru', 'Пополнение', 1, None, 0, 1, 0, None, None, None],
        ['en', 'Top Up', 1, None, 0, 1, 0, None, None, None],
        ['ru', 'Пополнение и перевод', 1, 'first', 0, 1, 1, 'last', 1, 1],
        ['en', 'Top Up And Transfer', 1, 'first', 0, 1, 1, 'last', 1, 1],
        ['ru', 'Пополнение и перевод', 1, 'last', 1, 1, 1, 'first', 0, 1],
        ['en', 'Top Up And Transfer', 1, 'last', 1, 1, 1, 'first', 0, 1],
        ['ru', 'Переводы', 0, None, None, None, 10, None, 0, 1],
        ['en', 'Transfers', 0, None, None, None, 10, None, 0, 1],
        ['ru', 'Пополнения', 10, None, 0, 1, 0, None, None, None],
        ['en', 'Top Ups', 10, None, 0, 1, 0, None, None, None],
        ['ru', 'Пополнение и переводы', 1, 'first', 0, 1, 10, 'last', 1, 1],
        ['en', 'Top Up And Transfers', 1, 'first', 0, 1, 10, 'last', 1, 1],
        ['ru', 'Пополнение и переводы', 1, 'last', 10, 1, 10, 'first', 0, 1],
        ['en', 'Top Up And Transfers', 1, 'last', 10, 1, 10, 'first', 0, 1],
        ['ru', 'Пополнения и перевод', 10, 'first', 0, 1, 1, 'last', 10, 1],
        ['en', 'Top Ups And Transfer', 10, 'first', 0, 1, 1, 'last', 10, 1],
        ['ru', 'Пополнения и перевод', 10, 'last', 1, 1, 1, 'first', 0, 1],
        ['en', 'Top Ups And Transfer', 10, 'last', 1, 1, 1, 'first', 0, 1],
        ['ru', 'Пополнения и переводы', 10, 'first', 0, 1, 10, 'last', 10, 1],
        ['en', 'Top Ups And Transfers', 10, 'first', 0, 1, 10, 'last', 10, 1],
        ['ru', 'Пополнения и переводы', 10, 'last', 10, 1, 10, 'first', 0, 1],
        ['en', 'Top Ups And Transfers', 10, 'last', 10, 1, 10, 'first', 0, 1],
    ],
)
async def test_ok(
        taxi_bank_wallet,
        bank_topup_mock,
        bank_core_faster_payments_mock,
        locale,
        title,
        topups_amount,
        topups_order,
        topups_start,
        topups_step,
        transfers_amount,
        transfers_order,
        transfers_start,
        transfers_step,
        handle_path,
):
    bank_topup_mock.set_amount(topups_amount)
    if topups_order:
        bank_topup_mock.set_order(topups_order)
    bank_core_faster_payments_mock.set_amount(transfers_amount)
    if transfers_order:
        bank_core_faster_payments_mock.set_order(transfers_order)
    headers = common.get_headers()
    headers['X-Request-Language'] = locale
    response = await taxi_bank_wallet.post(
        handle_path, json=_make_body(handle_path), headers=headers,
    )
    assert response.status_code == 200
    assert 'cursor' not in response.json()
    assert response.json().get('title', None) == title
    full = response.json()['transactions']
    assert len(full) == topups_amount + transfers_amount
    if topups_start:
        topups_stop = topups_start + topups_step * topups_amount
        for transaction in full[topups_start:topups_stop:topups_step]:
            for key in PENDING_TOPUP:
                assert transaction[key] == PENDING_TOPUP[key]
            for key in TOPUP_LOCALIZATION[locale]:
                assert transaction[key] == TOPUP_LOCALIZATION[locale][key]
    if transfers_start:
        transfers_stop = transfers_start + transfers_step * transfers_amount
        for transaction in full[transfers_start:transfers_stop:transfers_step]:
            for key in PENDING_TRANSFER[locale]:
                assert transaction[key] == PENDING_TRANSFER[locale][key]
            for key in TRANSFER_LOCALIZATION[locale]:
                assert transaction[key] == TRANSFER_LOCALIZATION[locale][key]

    for limit in range(1, len(full) + 1):
        paginated = []
        bank_topup_mock.set_amount(topups_amount)
        if topups_order:
            bank_topup_mock.set_order(topups_order)
        bank_core_faster_payments_mock.set_amount(transfers_amount)
        if transfers_order:
            bank_core_faster_payments_mock.set_order(transfers_order)
        response = await taxi_bank_wallet.post(
            handle_path,
            json=_make_body(handle_path, limit=limit),
            headers=headers,
        )
        assert response.json()['title'] == title
        paginated.extend(response.json()['transactions'])
        cursor = response.json().get('cursor', None)
        while cursor:
            bank_topup_mock.set_amount(topups_amount)
            if topups_order:
                bank_topup_mock.set_order(topups_order)
            bank_core_faster_payments_mock.set_amount(transfers_amount)
            if transfers_order:
                bank_core_faster_payments_mock.set_order(transfers_order)
            response = await taxi_bank_wallet.post(
                handle_path,
                json=_make_body(handle_path, cursor=cursor, limit=limit),
                headers=headers,
            )
            assert 'title' not in response.json()
            paginated.extend(response.json()['transactions'])
            cursor = response.json().get('cursor', None)
        assert paginated == full


@pytest.mark.parametrize('handle_path', [V1_HANDLE_PATH, V2_HANDLE_PATH])
@pytest.mark.parametrize(
    'locale, title, topups_amount, topups_indices, transfers_amount, '
    'transfers_indices',
    [
        ['ru', 'Пополнения и переводы', 4, [0, 2, 4, 6], 4, [1, 3, 5, 7]],
        ['en', 'Top Ups And Transfers', 4, [0, 2, 4, 6], 4, [1, 3, 5, 7]],
        ['ru', 'Пополнения и переводы', 2, [0, 2], 6, [1, 3, 4, 5, 6, 7]],
        ['en', 'Top Ups And Transfers', 2, [0, 2], 6, [1, 3, 4, 5, 6, 7]],
        ['ru', 'Пополнения и переводы', 6, [0, 2, 4, 5, 6, 7], 2, [1, 3]],
        ['en', 'Top Ups And Transfers', 6, [0, 2, 4, 5, 6, 7], 2, [1, 3]],
    ],
)
async def test_mixed(
        taxi_bank_wallet,
        bank_topup_mock,
        bank_core_faster_payments_mock,
        locale,
        title,
        topups_amount,
        topups_indices,
        transfers_amount,
        transfers_indices,
        handle_path,
):
    bank_topup_mock.set_amount(topups_amount)
    bank_topup_mock.set_order('mixed')
    bank_core_faster_payments_mock.set_amount(transfers_amount)
    bank_core_faster_payments_mock.set_order('mixed')
    headers = common.get_headers()
    headers['X-Request-Language'] = locale
    response = await taxi_bank_wallet.post(
        handle_path, json=_make_body(handle_path), headers=headers,
    )
    assert response.status_code == 200
    assert 'cursor' not in response.json()
    assert response.json()['title'] == title
    full = response.json()['transactions']
    assert len(full) == topups_amount + transfers_amount
    for i in topups_indices:
        transaction = full[i]
        for key in PENDING_TOPUP:
            assert transaction[key] == PENDING_TOPUP[key]
        for key in TOPUP_LOCALIZATION[locale]:
            assert transaction[key] == TOPUP_LOCALIZATION[locale][key]
    for i in transfers_indices:
        transaction = full[i]
        for key in PENDING_TRANSFER[locale]:
            assert transaction[key] == PENDING_TRANSFER[locale][key]
        for key in TRANSFER_LOCALIZATION[locale]:
            assert transaction[key] == TRANSFER_LOCALIZATION[locale][key]

    for limit in range(1, len(full) + 1):
        paginated = []
        bank_topup_mock.set_amount(topups_amount)
        bank_topup_mock.set_order('mixed')
        bank_core_faster_payments_mock.set_amount(transfers_amount)
        bank_core_faster_payments_mock.set_order('mixed')
        response = await taxi_bank_wallet.post(
            handle_path,
            json=_make_body(handle_path, limit=limit),
            headers=headers,
        )
        assert response.json()['title'] == title
        paginated.extend(response.json()['transactions'])
        cursor = response.json().get('cursor', None)
        while cursor:
            bank_topup_mock.set_amount(topups_amount)
            bank_topup_mock.set_order('mixed')
            bank_core_faster_payments_mock.set_amount(transfers_amount)
            bank_core_faster_payments_mock.set_order('mixed')
            response = await taxi_bank_wallet.post(
                handle_path,
                json=_make_body(handle_path, cursor=cursor, limit=limit),
                headers=headers,
            )
            assert 'title' not in response.json()
            paginated.extend(response.json()['transactions'])
            cursor = response.json().get('cursor', None)
        assert paginated == full


@pytest.mark.parametrize('handle_path', [V1_HANDLE_PATH, V2_HANDLE_PATH])
@pytest.mark.parametrize(
    'title, error_in',
    [
        [None, 'both'],
        ['Пополнения', 'transfers'],
        ['Переводы', 'topups'],
        ['Пополнения и переводы', 'no'],
    ],
)
async def test_runtime_errors_in_ftc(
        taxi_bank_wallet,
        bank_topup_mock,
        bank_core_faster_payments_mock,
        title,
        error_in,
        handle_path,
):
    transactions_count = 20
    if error_in in ['both', 'topups']:
        bank_topup_mock.set_http_status_code(500)
        transactions_count -= 10
    if error_in in ['both', 'transfers']:
        bank_core_faster_payments_mock.set_http_status_code(500)
        transactions_count -= 10
    bank_topup_mock.set_amount(10)
    bank_core_faster_payments_mock.set_amount(10)
    headers = common.get_headers()

    response = await taxi_bank_wallet.post(
        handle_path, json=_make_body(handle_path), headers=headers,
    )
    assert response.status_code == 200
    assert 'cursor' not in response.json()
    assert response.json().get('title', None) == title
    full = response.json()['transactions']

    assert len(full) == transactions_count
