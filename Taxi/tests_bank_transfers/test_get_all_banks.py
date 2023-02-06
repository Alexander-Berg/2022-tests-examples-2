import uuid

import pytest

from tests_bank_transfers import common
from tests_bank_transfers import db_helpers

YANDEX_BANK_DESCRIPTION = {
    'bank_id': '100000000150',
    'title': 'Яндекс Банк',
    'image': 'https://avatars.mdst.yandex.net/get-fintech/1401668/ya-bank.png',
}


def get_all_banks(
        has_default=False,
        has_yandex=False,
        yandex_is_default=False,
        default_pos=-3,
):
    all_banks = [
        {
            'bank_id': '100000000111',
            'title': 'Сбербанк',
            'image': (
                'http://avatars.mdst.yandex.net/get-fintech/1401668/sberbank'
            ),
        },
        {
            'bank_id': '100000000004',
            'title': 'Тинькофф',
            'image': (
                'http://avatars.mdst.yandex.net/get-fintech/1401668/tinkoff'
            ),
        },
        {
            'bank_id': '100000000008',
            'title': 'Альфа-Банк',
            'image': (
                'http://avatars.mdst.yandex.net/get-fintech/1401668/alfabank'
            ),
        },
        {
            'bank_id': '100000000005',
            'title': 'ВТБ Банк',
            'image': 'http://avatars.mdst.yandex.net/get-fintech/1401668/vtb',
        },
        {
            'bank_id': '100000000007',
            'title': 'Райффайзенбанк',
            'image': (
                'http://avatars.mdst.yandex.net/get-fintech/65575/raiffeisen'
            ),
        },
        {
            'bank_id': '100000000015',
            'title': 'Банк ФК Открытие',
            'image': (
                'http://avatars.mdst.yandex.net/get-fintech/1401668/'
                'otkritie-bank'
            ),
        },
        {
            'bank_id': '100000000001',
            'title': 'Газпромбанк',
            'image': (
                'http://avatars.mdst.yandex.net/get-fintech/65575/gazprombank'
            ),
        },
        {
            'bank_id': '100000000011',
            'title': 'РНКБ БАНК',
            'image': 'http://avatars.mdst.yandex.net/get-fintech/65575/rncb',
        },
        {
            'bank_id': '100000000016',
            'title': 'Почта Банк',
            'image': (
                'http://avatars.mdst.yandex.net/get-fintech/1401668/pochtabank'
            ),
        },
        {
            'bank_id': '100000000009',
            'title': 'QIWI Кошелек',
            'image': 'http://avatars.mdst.yandex.net/get-fintech/1401668/qiwi',
        },
        {'bank_id': '100000000191', 'title': 'Банк Казани'},
        {
            'bank_id': '100000000014',
            'title': 'Банк Русский Стандарт',
            'image': (
                'http://avatars.mdst.yandex.net/get-fintech/65575/rsb-logo'
            ),
        },
        {'bank_id': '110000000207', 'title': 'Дойче банк'},
        {
            'bank_id': '100000000012',  # default_bank
            'title': 'Росбанк',
            'image': (
                'http://avatars.mdst.yandex.net/get-fintech/65575/rosbank'
            ),
        },
        {'bank_id': '100000000190', 'title': 'РОСКОСМОСБАНК'},
        {
            'bank_id': '100000000065',
            'title': 'Точка',
            'image': 'http://avatars.mdst.yandex.net/get-fintech/65575/tochka',
        },
    ]

    if yandex_is_default:
        all_banks.insert(
            0,
            common.get_yandex_bank_description(description=common.PREFERRED),
        )
        return all_banks
    if has_default:
        default = all_banks[default_pos]
        default['description'] = common.PREFERRED
        del all_banks[default_pos]
        all_banks.insert(0, default)
    if has_yandex:
        all_banks.insert(0, common.get_yandex_bank_description())
    return all_banks


@pytest.mark.parametrize(
    'headers',
    [
        ({}),
        (
            {
                'X-YaBank-SessionUUID': common.TEST_SESSION_UUID,
                'X-Yandex-UID': common.TEST_YANDEX_UID,
                'X-YaBank-PhoneID': common.TEST_PHONE_ID,
                'X-Request-Language': common.TEST_LOCALE,
            }
        ),
    ],
)
async def test_not_authorized(taxi_bank_transfers, headers):
    params = {
        'transfer_id': 'e493fa8c-a742-4bfb-96e7-27126d0a9a15',
        'receiver_phone': common.RECEIVER_PHONE_1,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/faster/get_all_banks', headers=headers, json=params,
    )
    assert response.status_code == 401


async def test_wrong_transfer_id_format(
        taxi_bank_transfers, bank_core_faster_payments_mock,
):
    params = {
        'transfer_id': 'e493fa8c',
        'receiver_phone': common.RECEIVER_PHONE_1,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/faster/get_all_banks',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 400


async def test_no_receiver_phone_for_c2c(taxi_bank_transfers, pgsql):
    transfer_id = db_helpers.insert_transfer(
        pgsql, transfer_type='C2C', receiver_phone=None,
    )
    params = {'transfer_id': transfer_id}
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/faster/get_all_banks',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 400


async def test_no_receiver_phone_for_me2me(taxi_bank_transfers, pgsql):
    transfer_id = db_helpers.insert_transfer(
        pgsql, transfer_type='ME2ME', receiver_phone=None,
    )
    params = {'transfer_id': transfer_id}
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/faster/get_all_banks',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 200
    assert response.json() == {'banks': common.BANKS_WITH_M2M}


async def test_not_found(taxi_bank_transfers, bank_core_faster_payments_mock):
    params = {
        'transfer_id': 'e493fa8c-a742-4bfb-96e7-27126d0a9a15',
        'receiver_phone': common.RECEIVER_PHONE_1,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/faster/get_all_banks',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 404


async def test_buid_not_found(
        taxi_bank_transfers, bank_core_faster_payments_mock, pgsql,
):
    transfer_id = db_helpers.insert_transfer(pgsql)
    headers = common.build_headers(buid='e493fa8c-a742-4bfb-96e7-27126d0a9a15')
    params = {
        'transfer_id': transfer_id,
        'receiver_phone': common.RECEIVER_PHONE_1,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/faster/get_all_banks', headers=headers, json=params,
    )
    assert response.status_code == 404


async def test_wrong_transfer_status(
        taxi_bank_transfers, bank_core_faster_payments_mock, pgsql,
):
    transfer_id = db_helpers.insert_transfer(pgsql, status='SUCCESS')
    params = {
        'transfer_id': transfer_id,
        'receiver_phone': common.RECEIVER_PHONE_1,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/faster/get_all_banks',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 404


@pytest.mark.parametrize('transfer_type', ['C2C', 'ME2ME'])
async def test_ok_no_preferred(
        taxi_bank_transfers,
        bank_core_faster_payments_mock,
        pgsql,
        transfer_type,
):
    transfer_id = db_helpers.insert_transfer(
        pgsql,
        receiver_phone=common.RECEIVER_PHONE_01,
        transfer_type=transfer_type,
    )
    params = {'transfer_id': transfer_id}
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/faster/get_all_banks',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 200
    if transfer_type == 'ME2ME':
        assert response.json() == {'banks': common.BANKS_WITH_M2M}
        assert (
            bank_core_faster_payments_mock.get_default_bank_handler.times_called
            == 0
        )
    else:
        assert response.json() == {'banks': get_all_banks()}
        assert (
            bank_core_faster_payments_mock.get_default_bank_handler.times_called
            == 1
        )


@pytest.mark.parametrize('transfer_type', ['C2C', 'ME2ME'])
async def test_ok_preferred(
        taxi_bank_transfers,
        bank_core_faster_payments_mock,
        pgsql,
        transfer_type,
):
    transfer_id = db_helpers.insert_transfer(
        pgsql, transfer_type=transfer_type,
    )
    params = {'transfer_id': transfer_id}
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/faster/get_all_banks',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 200
    all_banks = get_all_banks(has_default=True)
    all_banks[0]['description'] = common.PREFERRED
    if transfer_type == 'ME2ME':
        assert response.json() == {'banks': common.BANKS_WITH_M2M}
    else:
        assert response.json() == {'banks': all_banks}


async def test_ok_preferred_cursor(
        taxi_bank_transfers, bank_core_faster_payments_mock, pgsql,
):
    transfer_id = db_helpers.insert_transfer(pgsql)
    page_size = 8
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/faster/get_all_banks',
        headers=common.build_headers(),
        json={'transfer_id': transfer_id, 'page_size': page_size},
    )
    assert response.status_code == 200
    all_banks = get_all_banks(has_default=True)
    all_banks[0]['description'] = common.PREFERRED
    assert response.json()['banks'] == all_banks[:page_size]
    cursor = response.json()['cursor']
    assert cursor == 'eyJvZmZzZXQiOjgsInBhZ2Vfc2l6ZSI6OH0='
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/faster/get_all_banks',
        headers=common.build_headers(),
        json={'transfer_id': transfer_id, 'cursor': cursor},
    )
    assert response.json()['banks'] == all_banks[page_size : page_size * 2]


async def test_bad_cursor(
        taxi_bank_transfers, bank_core_faster_payments_mock, pgsql,
):
    transfer_id = db_helpers.insert_transfer(pgsql)
    cursor = 'bad_cursor'
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/faster/get_all_banks',
        headers=common.build_headers(),
        json={'transfer_id': transfer_id, 'cursor': cursor},
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'session_uuid, inner_transfers_enable',
    [
        ('f7c31972-25d4-4977-905f-42ecf4a357f5', True),
        ('f7c31972-25d4-4977-905f-42ecf4a357f6', False),
    ],
)
@pytest.mark.experiments3(
    filename='bank_transfer_inner_transfers_feature_experiments.json',
)
async def test_yandex_bank_in_hist_no_default(
        taxi_bank_transfers,
        bank_core_faster_payments_mock,
        pgsql,
        session_uuid,
        inner_transfers_enable,
):
    bank_core_faster_payments_mock.add_yandex_to_bank_hist()
    transfer_id = db_helpers.insert_transfer(
        pgsql, receiver_phone=common.RECEIVER_PHONE_3,
    )
    params = {
        'transfer_id': transfer_id,
        'receiver_phone': common.RECEIVER_PHONE_3,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/faster/get_all_banks',
        headers=common.build_headers(session_uuid=session_uuid),
        json=params,
    )
    assert response.status_code == 200
    assert response.json() == {
        'banks': get_all_banks(has_yandex=inner_transfers_enable),
    }


@pytest.mark.parametrize(
    'session_uuid, inner_transfers_enable',
    [
        ('f7c31972-25d4-4977-905f-42ecf4a357f5', True),
        ('f7c31972-25d4-4977-905f-42ecf4a357f6', False),
    ],
)
@pytest.mark.experiments3(
    filename='bank_transfer_inner_transfers_feature_experiments.json',
)
async def test_yandex_bank_in_hist_default(
        taxi_bank_transfers,
        bank_core_faster_payments_mock,
        pgsql,
        session_uuid,
        inner_transfers_enable,
):
    bank_core_faster_payments_mock.add_yandex_to_bank_hist()
    transfer_id = db_helpers.insert_transfer(
        pgsql, receiver_phone=common.RECEIVER_PHONE_1,
    )
    params = {
        'transfer_id': transfer_id,
        'receiver_phone': common.RECEIVER_PHONE_1,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/faster/get_all_banks',
        headers=common.build_headers(session_uuid=session_uuid),
        json=params,
    )
    assert response.status_code == 200
    assert response.json() == {
        'banks': get_all_banks(
            has_yandex=inner_transfers_enable, has_default=True,
        ),
    }


@pytest.mark.parametrize(
    'session_uuid, inner_transfers_enable',
    [
        ('f7c31972-25d4-4977-905f-42ecf4a357f5', True),
        ('f7c31972-25d4-4977-905f-42ecf4a357f6', False),
    ],
)
@pytest.mark.experiments3(
    filename='bank_transfer_inner_transfers_feature_experiments.json',
)
async def test_yandex_bank_is_default(
        taxi_bank_transfers,
        bank_core_faster_payments_mock,
        pgsql,
        session_uuid,
        inner_transfers_enable,
):
    bank_core_faster_payments_mock.add_yandex_to_bank_hist()
    transfer_id = db_helpers.insert_transfer(
        pgsql, receiver_phone=common.RECEIVER_PHONE_YANDEX,
    )
    params = {
        'transfer_id': transfer_id,
        'receiver_phone': common.RECEIVER_PHONE_1,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/faster/get_all_banks',
        headers=common.build_headers(session_uuid=session_uuid),
        json=params,
    )
    assert response.status_code == 200
    assert response.json() == {
        'banks': get_all_banks(yandex_is_default=inner_transfers_enable),
    }


@pytest.mark.parametrize(
    'session_uuid, inner_transfers_enable',
    [
        ('f7c31972-25d4-4977-905f-42ecf4a357f5', True),
        ('f7c31972-25d4-4977-905f-42ecf4a357f6', False),
    ],
)
@pytest.mark.experiments3(
    filename='bank_transfer_inner_transfers_feature_experiments.json',
)
async def test_default_bank_in_top(
        taxi_bank_transfers,
        bank_core_faster_payments_mock,
        pgsql,
        session_uuid,
        inner_transfers_enable,
):
    bank_core_faster_payments_mock.add_yandex_to_bank_hist()
    transfer_id = db_helpers.insert_transfer(
        pgsql, receiver_phone=common.RECEIVER_PHONE_SBER,
    )
    params = {
        'transfer_id': transfer_id,
        'receiver_phone': common.RECEIVER_PHONE_SBER,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/faster/get_all_banks',
        headers=common.build_headers(session_uuid=session_uuid),
        json=params,
    )
    assert response.status_code == 200
    assert response.json() == {
        'banks': get_all_banks(
            has_default=True, has_yandex=inner_transfers_enable, default_pos=0,
        ),
    }


@pytest.mark.parametrize(
    'receiver_phone', [common.RECEIVER_PHONE_YANDEX, common.RECEIVER_PHONE_3],
)
@pytest.mark.experiments3(
    filename='bank_transfer_inner_transfers_feature_experiments.json',
)
async def test_no_yandex_in_self_transfers(
        taxi_bank_transfers,
        bank_core_faster_payments_mock,
        bank_userinfo_mock,
        pgsql,
        receiver_phone,
):
    bank_core_faster_payments_mock.add_yandex_to_bank_hist()
    bank_userinfo_mock.set_phone_number(receiver_phone)

    transfer_id = db_helpers.insert_transfer(
        pgsql, receiver_phone=receiver_phone,
    )
    params = {'transfer_id': transfer_id, 'receiver_phone': receiver_phone}
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/faster/get_all_banks',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 200
    assert response.json() == {'banks': get_all_banks(has_yandex=False)}


async def test_security(taxi_bank_transfers, pgsql):
    transfer_id = db_helpers.insert_transfer(
        pgsql,
        receiver_phone=common.RECEIVER_PHONE_1,
        buid=common.TEST_BANK_UID,
    )

    # different buids in transfer and request
    params = {
        'transfer_id': transfer_id,
        'receiver_phone': common.RECEIVER_PHONE_1,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/faster/get_all_banks',
        headers=common.build_headers(buid=str(uuid.uuid4())),
        json=params,
    )
    assert response.status_code == 404
