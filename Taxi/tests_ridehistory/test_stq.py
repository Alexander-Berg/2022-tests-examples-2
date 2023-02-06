import datetime as dt

import pytest
import pytz


EXPECTED_UTC_TIME = dt.datetime(
    2017, 3, 7, 20, 47, 44, 747000, tzinfo=pytz.UTC,
)


@pytest.mark.parametrize(
    'kwargs, expected_user_index',
    [
        (
            {
                'order_created_at': {'$date': '2017-03-07T20:47:44.747Z'},
                'order_id': '777',
                'phone_id': {'$oid': '58bebe55b008e0bbfe5cc9d7'},
                'user_uid': '474241945',
                'payment_tech_type': 'coop_account',
                'payment_method_id': 'card-x777',
            },
            [
                [
                    '777',
                    '58bebe55b008e0bbfe5cc9d7',
                    '474241945',
                    EXPECTED_UTC_TIME,
                    EXPECTED_UTC_TIME,
                    False,
                    'coop_account',
                    'card-x777',
                ],
            ],
        ),
        (
            {
                'order_created_at': {'$date': '2017-03-07T20:47:44.747Z'},
                'order_id': '777',
                'phone_id': {'$oid': '58bebe55b008e0bbfe5cc9d7'},
                'user_uid': '474241945',
                'payment_tech_type': None,
                'payment_method_id': None,
            },
            [
                [
                    '777',
                    '58bebe55b008e0bbfe5cc9d7',
                    '474241945',
                    EXPECTED_UTC_TIME,
                    EXPECTED_UTC_TIME,
                    False,
                    None,
                    None,
                ],
            ],
        ),
        (
            {
                'order_created_at': {'$date': '2017-03-07T20:47:44.747Z'},
                'order_id': '777',
                'phone_id': {'$oid': '58bebe55b008e0bbfe5cc9d7'},
                'user_uid': '474241945',
            },
            [
                [
                    '777',
                    '58bebe55b008e0bbfe5cc9d7',
                    '474241945',
                    EXPECTED_UTC_TIME,
                    EXPECTED_UTC_TIME,
                    False,
                    None,
                    None,
                ],
            ],
        ),
        (
            {
                'order_created_at': {'$date': '2017-03-07T20:47:44.747Z'},
                'order_id': '777',
                'phone_id': {'$oid': '58bebe55b008e0bbfe5cc9d7'},
                'user_uid': '',
                'payment_tech_type': 'coop_account',
                'payment_method_id': 'card-x777',
            },
            [
                [
                    '777',
                    '58bebe55b008e0bbfe5cc9d7',
                    None,
                    EXPECTED_UTC_TIME,
                    EXPECTED_UTC_TIME,
                    False,
                    'coop_account',
                    'card-x777',
                ],
            ],
        ),
    ],
)
async def test_sample_task_with_args(
        stq_runner, get_user_index_rows, kwargs, expected_user_index,
):
    await stq_runner.ridehistory_fetch.call(
        task_id='sample_task', args=[], kwargs=kwargs, expect_fail=False,
    )

    assert get_user_index_rows() == expected_user_index


async def test_idempotency(stq_runner, get_user_index_rows):
    kwargs = {
        'order_created_at': {'$date': '2017-03-07T20:47:44.747Z'},
        'order_id': '777',
        'phone_id': {'$oid': '58bebe55b008e0bbfe5cc9d7'},
        'user_uid': '474241945',
    }

    await stq_runner.ridehistory_fetch.call(
        task_id='sample_task', args=[], kwargs=kwargs, expect_fail=False,
    )

    assert len(get_user_index_rows()) == 1

    await stq_runner.ridehistory_fetch.call(
        task_id='sample_task', args=[], kwargs=kwargs, expect_fail=False,
    )

    assert len(get_user_index_rows()) == 1


async def test_update(stq_runner, get_user_index_rows):
    kwargs = {
        'order_created_at': {'$date': '2017-03-07T20:47:44.747Z'},
        'order_id': '777',
        'phone_id': {'$oid': '58bebe55b008e0bbfe5cc9d7'},
        'user_uid': '474241945',
        'payment_tech_type': 'cash',
        'payment_method_id': None,
    }

    await stq_runner.ridehistory_fetch.call(
        task_id='sample_task', args=[], kwargs=kwargs, expect_fail=False,
    )

    assert get_user_index_rows() == [
        [
            '777',
            '58bebe55b008e0bbfe5cc9d7',
            '474241945',
            EXPECTED_UTC_TIME,
            EXPECTED_UTC_TIME,
            False,
            'cash',
            None,
        ],
    ]

    kwargs['payment_tech_type'] = 'card'
    kwargs['payment_method_id'] = 'card-666'

    await stq_runner.ridehistory_fetch.call(
        task_id='sample_task', args=[], kwargs=kwargs, expect_fail=False,
    )

    assert get_user_index_rows() == [
        [
            '777',
            '58bebe55b008e0bbfe5cc9d7',
            '474241945',
            EXPECTED_UTC_TIME,
            EXPECTED_UTC_TIME,
            False,
            'card',
            'card-666',
        ],
    ]
