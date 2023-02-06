import uuid

import pytest

from tests_grocery_dispatch import configs
# pylint: disable=import-only-modules
from tests_grocery_dispatch.plugins.models import OrderInfo


DISPATCH_ID_0 = str(uuid.UUID('{00010203-2528-0202-0809-0a0b0c0d0e0f}'))
DISPATCH_ID_1 = str(uuid.UUID('{00010205-1106-0104-0805-0a0b0c0d0e0a}'))
DISPATCH_ID_2 = str(uuid.UUID('{00010207-0015-0908-0801-0a0b0c0d0e00}'))

DISPATCH_IDS = [DISPATCH_ID_0, DISPATCH_ID_1, DISPATCH_ID_2]

ORDER_ID_0 = '06e24e27fd584ee1a5ebec051d308e10-grocery'
ORDER_ID_1 = '06e24e27fd584ee1a5ebed051d308e10-grocery'
ORDER_ID_2 = '06e24e27fd584ee1a5ebef051d308e10-grocery'
ORDER_IDS = [ORDER_ID_0, ORDER_ID_1, ORDER_ID_2]

CLAIM_ID_0 = 'claim 0'
CLAIM_ID_1 = 'claim 1'
CLAIM_ID_2 = 'claim 2'

CLAIMS = [
    {
        'dispatch_id': DISPATCH_ID_0,
        'claim_id': CLAIM_ID_0,
        'claim_status': 'test 0',
        'claim_version': 101,
        'is_current_claim': True,
        'wave': 0,
    },
    {
        'dispatch_id': DISPATCH_ID_0,
        'claim_id': CLAIM_ID_1,
        'claim_status': 'test 1',
        'claim_version': 121,
        'is_current_claim': False,
        'wave': 1,
    },
    {
        'dispatch_id': DISPATCH_ID_1,
        'claim_id': CLAIM_ID_2,
        'claim_status': 'test 2',
        'claim_version': 333,
        'is_current_claim': True,
        'wave': 2,
    },
]

EXPECTED_RESPONSE = {
    'dispatches': [
        {
            'dispatch_id': DISPATCH_ID_0,
            'cargo_details': [
                {
                    'claim_id': CLAIM_ID_0,
                    'claim_status': 'test 0',
                    'is_current_claim': True,
                },
                {
                    'claim_id': CLAIM_ID_1,
                    'claim_status': 'test 1',
                    'is_current_claim': False,
                },
            ],
        },
        {
            'dispatch_id': DISPATCH_ID_1,
            'cargo_details': [
                {
                    'claim_id': CLAIM_ID_2,
                    'claim_status': 'test 2',
                    'is_current_claim': True,
                },
            ],
        },
        {'dispatch_id': DISPATCH_ID_2},
    ],
}

NOW = '2020-10-05T17:28:00+00:00'


@pytest.mark.now(NOW)
@configs.CARGO_DISPATCHES_THR_ONE_DAY
@pytest.mark.parametrize(
    'created_array, in_db',
    [
        (
            (
                '2020-10-05T16:28:00+00:00',  # новая, берем из бд
                '2020-10-05T10:28:00+00:00',  # новая, берем из бд
                '2020-10-05T15:28:00+00:00',
            ),  # не нашли в бд, не нашли в yt
            (True, True, False),
        ),
        (
            (
                '2020-10-03T16:28:00+00:00',  # старая, берем из бд и yt
                '2020-10-05T10:28:00+00:00',  # новая, берем из бд
                '2020-10-05T15:28:00+00:00',
            ),  # не нашли в бд, не нашли в yt
            (True, True, False),
        ),
        (
            (
                '2020-10-05T16:28:00+00:00',  # новая, берем из бд
                '2020-10-05T10:28:00+00:00',  # нет в бд, берем из yt
                '2020-10-05T15:28:00+00:00',
            ),  # не нашли в бд, не нашли в yt
            (True, False, False),
        ),
        (
            (
                '2020-10-03T16:28:00+00:00',  # старая, берем из бд и yt
                '2020-10-05T10:28:00+00:00',  # нет в бд, берем из yt
                '2020-10-05T15:28:00+00:00',
            ),  # не нашли в бд, не нашли в yt
            (True, False, False),
        ),
    ],
)
async def test_admin_info_not_empty_bd(
        taxi_grocery_dispatch,
        pgsql,
        created_array,
        in_db,
        grocery_cold_storage,
        cargo_pg,
        grocery_dispatch_pg,
):

    for claim in CLAIMS:
        cargo_pg.create_claim(**claim)

    grocery_cold_storage.set_cargo_dispatches_response(
        items=[
            {**claim, **{'item_id': claim['dispatch_id']}} for claim in CLAIMS
        ],
    )

    for dispatch_id, order_id, created, to_db in zip(
            DISPATCH_IDS, ORDER_IDS, created_array, in_db,
    ):
        if to_db:
            grocery_dispatch_pg.create_dispatch(
                dispatch_id=dispatch_id,
                order=OrderInfo(created=created, order_id=order_id),
            )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/admin/info', {'dispatches': DISPATCH_IDS},
    )

    assert response.status_code == 200
    assert response.json() == EXPECTED_RESPONSE


async def test_admin_info_empty_db(
        taxi_grocery_dispatch, grocery_cold_storage,
):
    grocery_cold_storage.set_cargo_dispatches_response(
        items=[
            {**claim, **{'item_id': claim['dispatch_id']}} for claim in CLAIMS
        ],
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/admin/info', {'dispatches': DISPATCH_IDS},
    )

    assert response.status_code == 200
    assert response.json() == EXPECTED_RESPONSE


async def test_admin_info_resp_is_sorted(
        taxi_grocery_dispatch,
        pgsql,
        grocery_cold_storage,
        cargo_pg,
        grocery_dispatch_pg,
):
    dispatch_id_0 = str(uuid.UUID('{00010203-2528-0202-0809-0a0b0c0d0e0f}'))

    claim_id_0 = 'claim 0'
    claim_id_1 = 'claim 1'
    claim_id_2 = 'claim 2'
    claim_id_3 = 'claim 3'

    claims = [
        {
            'dispatch_id': dispatch_id_0,
            'wave': 3,
            'claim_id': claim_id_3,
            'claim_status': 'test 3',
            'claim_version': 103,
            'is_current_claim': True,
        },
        {
            'dispatch_id': dispatch_id_0,
            'wave': 1,
            'claim_id': claim_id_1,
            'claim_status': 'test 1',
            'claim_version': 101,
            'is_current_claim': False,
        },
        {
            'dispatch_id': dispatch_id_0,
            'wave': 2,
            'claim_id': claim_id_2,
            'claim_status': 'test 2',
            'claim_version': 102,
            'is_current_claim': False,
        },
        {
            'dispatch_id': dispatch_id_0,
            'wave': 0,
            'claim_id': claim_id_0,
            'claim_status': 'test 0',
            'claim_version': 100,
            'is_current_claim': False,
        },
    ]

    for claim in claims:
        cargo_pg.create_claim(**claim)

    grocery_dispatch_pg.create_dispatch(
        dispatch_id=dispatch_id_0,
        order=OrderInfo(created=True, order_id=ORDER_ID_0),
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/admin/info', {'dispatches': [dispatch_id_0]},
    )

    # ожидается что ответ упорядочен по wave (от меньшего к большем)
    expected_response = {
        'dispatches': [
            {
                'dispatch_id': dispatch_id_0,
                'cargo_details': [
                    {
                        'claim_id': claim_id_0,
                        'claim_status': 'test 0',
                        'is_current_claim': False,
                    },
                    {
                        'claim_id': claim_id_1,
                        'claim_status': 'test 1',
                        'is_current_claim': False,
                    },
                    {
                        'claim_id': claim_id_2,
                        'claim_status': 'test 2',
                        'is_current_claim': False,
                    },
                    {
                        'claim_id': claim_id_3,
                        'claim_status': 'test 3',
                        'is_current_claim': True,
                    },
                ],
            },
        ],
    }

    assert response.status_code == 200
    assert response.json() == expected_response
