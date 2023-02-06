import uuid

import pytest

from tests_bank_transfers import common
from tests_bank_transfers import db_helpers


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
        '/v1/transfers/v1/phone/get_suggested_banks',
        headers=headers,
        json=params,
    )
    assert response.status_code == 401


async def test_not_found(taxi_bank_transfers, bank_core_faster_payments_mock):
    params = {
        'transfer_id': 'e493fa8c-a742-4bfb-96e7-27126d0a9a15',
        'receiver_phone': common.RECEIVER_PHONE_1,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_suggested_banks',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 404


async def test_wrong_transfer_id_format(
        taxi_bank_transfers, bank_core_faster_payments_mock,
):
    params = {
        'transfer_id': 'e493fa8c',
        'receiver_phone': common.RECEIVER_PHONE_1,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_suggested_banks',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 400


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
        '/v1/transfers/v1/phone/get_suggested_banks',
        headers=headers,
        json=params,
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
        '/v1/transfers/v1/phone/get_suggested_banks',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 404


async def test_preferred_bank_not_in_cache(
        taxi_bank_transfers, bank_core_faster_payments_mock, pgsql,
):
    transfer_id = db_helpers.insert_transfer(pgsql)
    params = {
        'transfer_id': transfer_id,
        'receiver_phone': common.RECEIVER_PHONE_1,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_suggested_banks',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 200
    assert response.json() == {
        'banks': [
            {
                'bank_id': '100000000012',
                'description': common.PREFERRED,
                'image': (
                    'http://avatars.mdst.yandex.net/get-fintech/'
                    '65575/rosbank'
                ),
                'title': 'Росбанк',
            },
            {
                'bank_id': '100000000004',
                'description': common.SHORT_RECEIVER_NAME_1,
                'image': (
                    'http://avatars.mdst.yandex.net/get-fintech/'
                    '1401668/tinkoff'
                ),
                'title': 'Тинькофф',
            },
        ],
    }


async def test_preferred_bank_in_cache(
        taxi_bank_transfers, bank_core_faster_payments_mock, pgsql,
):
    transfer_id = db_helpers.insert_transfer(pgsql)
    params = {
        'transfer_id': transfer_id,
        'receiver_phone': common.RECEIVER_PHONE_2,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_suggested_banks',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 200
    assert response.json() == {
        'banks': [
            {
                'bank_id': '100000000012',
                'description': (
                    f'{common.SHORT_RECEIVER_NAME_2} \u2022 {common.PREFERRED}'
                ),
                'image': (
                    'http://avatars.mdst.yandex.net/get-fintech/'
                    '65575/rosbank'
                ),
                'title': 'Росбанк',
            },
            {
                'bank_id': '100000000004',
                'description': common.SHORT_RECEIVER_NAME_2,
                'image': (
                    'http://avatars.mdst.yandex.net/get-fintech/'
                    '1401668/tinkoff'
                ),
                'title': 'Тинькофф',
            },
        ],
    }


async def test_only_cached_banks(
        taxi_bank_transfers, bank_core_faster_payments_mock, pgsql,
):
    transfer_id = db_helpers.insert_transfer(pgsql)
    params = {
        'transfer_id': transfer_id,
        'receiver_phone': common.RECEIVER_PHONE_3,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_suggested_banks',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 200
    assert response.json() == {
        'banks': [
            {
                'bank_id': '100000000004',
                'description': common.SHORT_RECEIVER_NAME_3,
                'image': (
                    'http://avatars.mdst.yandex.net/get-fintech/'
                    '1401668/tinkoff'
                ),
                'title': 'Тинькофф',
            },
        ],
    }


async def test_only_preferred_bank(
        taxi_bank_transfers, bank_core_faster_payments_mock, pgsql,
):
    transfer_id = db_helpers.insert_transfer(
        pgsql, receiver_phone=common.RECEIVER_PHONE_00,
    )
    params = {
        'transfer_id': transfer_id,
        'receiver_phone': common.RECEIVER_PHONE_00,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_suggested_banks',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 200
    assert response.json() == {
        'banks': [
            {
                'bank_id': '100000000012',
                'description': common.PREFERRED,
                'image': (
                    'http://avatars.mdst.yandex.net/get-fintech/'
                    '65575/rosbank'
                ),
                'title': 'Росбанк',
            },
        ],
    }


async def test_no_banks(
        taxi_bank_transfers, bank_core_faster_payments_mock, pgsql,
):
    transfer_id = db_helpers.insert_transfer(
        pgsql, receiver_phone=common.RECEIVER_PHONE_01,
    )
    params = {
        'transfer_id': transfer_id,
        'receiver_phone': common.RECEIVER_PHONE_01,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_suggested_banks',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 200
    assert response.json() == {'banks': []}


async def test_cursor(
        taxi_bank_transfers, bank_core_faster_payments_mock, pgsql,
):
    page_size = 1
    transfer_id = db_helpers.insert_transfer(
        pgsql, receiver_phone=common.RECEIVER_PHONE_2,
    )
    params = {
        'transfer_id': transfer_id,
        'receiver_phone': common.RECEIVER_PHONE_2,
        'page_size': page_size,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_suggested_banks',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 200
    assert len(response.json()['banks']) == page_size
    assert response.json()['banks'][0] == {
        'bank_id': '100000000012',
        'description': (
            f'{common.SHORT_RECEIVER_NAME_2} \u2022 {common.PREFERRED}'
        ),
        'image': (
            'http://avatars.mdst.yandex.net/get-fintech/' '65575/rosbank'
        ),
        'title': 'Росбанк',
    }
    resp_cursor = response.json()['cursor']
    assert resp_cursor == 'eyJvZmZzZXQiOjEsInBhZ2Vfc2l6ZSI6MX0='
    params = {'transfer_id': transfer_id, 'cursor': resp_cursor}
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_suggested_banks',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 200
    assert len(response.json()['banks']) == page_size
    assert response.json() == {
        'banks': [
            {
                'bank_id': '100000000004',
                'description': common.SHORT_RECEIVER_NAME_2,
                'image': (
                    'http://avatars.mdst.yandex.net/get-fintech/'
                    '1401668/tinkoff'
                ),
                'title': 'Тинькофф',
            },
        ],
    }


async def test_cursor_en(
        taxi_bank_transfers, bank_core_faster_payments_mock, pgsql,
):
    page_size = 1
    transfer_id = db_helpers.insert_transfer(
        pgsql, receiver_phone=common.RECEIVER_PHONE_2,
    )
    headers = common.build_headers(language='en')
    params = {
        'transfer_id': transfer_id,
        'receiver_phone': common.RECEIVER_PHONE_2,
        'page_size': page_size,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_suggested_banks',
        headers=headers,
        json=params,
    )
    assert response.status_code == 200
    assert len(response.json()['banks']) == page_size
    assert response.json()['banks'][0] == {
        'bank_id': '100000000012',
        'description': (
            f'{common.SHORT_RECEIVER_NAME_2} \u2022 {common.PREFERRED_EN}'
        ),
        'image': (
            'http://avatars.mdst.yandex.net/get-fintech/' '65575/rosbank'
        ),
        'title': 'Rosbank',
    }
    resp_cursor = response.json()['cursor']
    assert resp_cursor == 'eyJvZmZzZXQiOjEsInBhZ2Vfc2l6ZSI6MX0='
    params = {'transfer_id': transfer_id, 'cursor': resp_cursor}
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_suggested_banks',
        headers=headers,
        json=params,
    )
    assert response.status_code == 200
    assert len(response.json()['banks']) == page_size
    assert response.json() == {
        'banks': [
            {
                'bank_id': '100000000004',
                'description': common.SHORT_RECEIVER_NAME_2,
                'image': (
                    'http://avatars.mdst.yandex.net/get-fintech/'
                    '1401668/tinkoff'
                ),
                'title': 'Tinkoff',
            },
        ],
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
        '/v1/transfers/v1/phone/get_suggested_banks',
        headers=common.build_headers(session_uuid=session_uuid),
        json=params,
    )
    assert response.status_code == 200
    banks = [
        {
            'bank_id': '100000000004',
            'description': common.SHORT_RECEIVER_NAME_3,
            'image': (
                'http://avatars.mdst.yandex.net/get-fintech/' '1401668/tinkoff'
            ),
            'title': 'Тинькофф',
        },
    ]
    if inner_transfers_enable:
        banks.insert(
            0,
            common.get_yandex_bank_description(
                description=common.SHORT_RECEIVER_NAME_3,
            ),
        )
    assert response.json() == {'banks': banks}


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
        '/v1/transfers/v1/phone/get_suggested_banks',
        headers=common.build_headers(session_uuid=session_uuid),
        json=params,
    )
    assert response.status_code == 200
    banks = [
        {
            'bank_id': '100000000012',
            'description': common.PREFERRED,
            'image': (
                'http://avatars.mdst.yandex.net/get-fintech/' '65575/rosbank'
            ),
            'title': 'Росбанк',
        },
        {
            'bank_id': '100000000004',
            'description': common.SHORT_RECEIVER_NAME_1,
            'image': (
                'http://avatars.mdst.yandex.net/get-fintech/' '1401668/tinkoff'
            ),
            'title': 'Тинькофф',
        },
    ]
    if inner_transfers_enable:
        banks.insert(
            0,
            common.get_yandex_bank_description(
                description=common.SHORT_RECEIVER_NAME_1,
            ),
        )
    assert response.json() == {'banks': banks}


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
async def test_yandex_bank_is_default_in_hist(
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
        'receiver_phone': common.RECEIVER_PHONE_YANDEX,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_suggested_banks',
        headers=common.build_headers(session_uuid=session_uuid),
        json=params,
    )
    assert response.status_code == 200
    banks = [
        {
            'bank_id': '100000000004',
            'description': common.get_receiver_short_name(
                common.RECEIVER_PHONE_YANDEX,
            ),
            'image': (
                'http://avatars.mdst.yandex.net/get-fintech/' '1401668/tinkoff'
            ),
            'title': 'Тинькофф',
        },
    ]
    if inner_transfers_enable:
        banks.insert(
            0,
            common.get_yandex_bank_description(
                description=f'{common.SHORT_RECEIVER_NAME_1} \u2022 {common.PREFERRED}',
            ),
        )
    assert response.json() == {'banks': banks}


@pytest.mark.parametrize(
    'receiver_phone',
    [
        common.RECEIVER_PHONE_00,
        common.RECEIVER_PHONE_1,
        common.RECEIVER_PHONE_2,
    ],
)
async def test_bd(
        taxi_bank_transfers,
        bank_core_faster_payments_mock,
        pgsql,
        receiver_phone,
):
    transfer_id = db_helpers.insert_transfer(
        pgsql, receiver_phone=receiver_phone,
    )
    params = {'transfer_id': transfer_id, 'receiver_phone': receiver_phone}
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_suggested_banks',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 200
    transfer = db_helpers.select_transfer(pgsql, transfer_id)
    assert transfer.receiver_name == common.get_receiver_name(receiver_phone)
    assert transfer.receiver_phone == receiver_phone


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
async def test_yandex_bank_is_default_no_in_hist(
        taxi_bank_transfers,
        bank_core_faster_payments_mock,
        pgsql,
        session_uuid,
        inner_transfers_enable,
):
    transfer_id = db_helpers.insert_transfer(
        pgsql, receiver_phone=common.RECEIVER_PHONE_YANDEX,
    )
    params = {
        'transfer_id': transfer_id,
        'receiver_phone': common.RECEIVER_PHONE_YANDEX,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_suggested_banks',
        headers=common.build_headers(session_uuid=session_uuid),
        json=params,
    )
    assert response.status_code == 200
    banks = [
        {
            'bank_id': '100000000004',
            'description': common.get_receiver_short_name(
                common.RECEIVER_PHONE_YANDEX,
            ),
            'image': (
                'http://avatars.mdst.yandex.net/get-fintech/' '1401668/tinkoff'
            ),
            'title': 'Тинькофф',
        },
    ]
    if inner_transfers_enable:
        banks.insert(
            0,
            common.get_yandex_bank_description(description=common.PREFERRED),
        )
    assert response.json() == {'banks': banks}


# TODO delete next test after outgoing transfers became available without FPS
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
async def test_no_fps(
        taxi_bank_transfers,
        bank_core_faster_payments_mock,
        pgsql,
        session_uuid,
        inner_transfers_enable,
):
    bank_core_faster_payments_mock.add_yandex_to_bank_hist()
    transfer_id = db_helpers.insert_transfer(
        pgsql,
        receiver_phone=common.RECEIVER_PHONE_3,
        buid=common.TEST_YANDEX_UID,
    )
    params = {
        'transfer_id': transfer_id,
        'receiver_phone': common.RECEIVER_PHONE_3,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_suggested_banks',
        headers=common.build_headers(
            session_uuid=session_uuid, buid=common.TEST_YANDEX_UID,
        ),
        json=params,
    )
    assert response.status_code == 200
    banks = []

    if inner_transfers_enable:
        banks.insert(
            0,
            common.get_yandex_bank_description(
                description=common.SHORT_RECEIVER_NAME_3,
            ),
        )
    assert response.json() == {'banks': banks}


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
        '/v1/transfers/v1/phone/get_suggested_banks',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 200
    banks = [
        {
            'bank_id': '100000000004',
            'description': common.get_receiver_short_name(receiver_phone),
            'image': (
                'http://avatars.mdst.yandex.net/get-fintech/' '1401668/tinkoff'
            ),
            'title': 'Тинькофф',
        },
    ]
    assert response.json() == {'banks': banks}


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
        '/v1/transfers/v1/phone/get_suggested_banks',
        headers=common.build_headers(buid=str(uuid.uuid4())),
        json=params,
    )
    assert response.status_code == 404
