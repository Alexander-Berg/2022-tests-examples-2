# pylint: disable=no-value-for-parameter
import datetime

import pytest

from taxi_corp import stq_tasks


@pytest.mark.parametrize(
    'user_id, phone_id, client_id, status_updated, expected_result',
    [
        (
            'user_id_1',
            None,
            None,
            datetime.datetime(2018, 1, 31, 23, 15, 16),
            {
                '2018-02': {'spent_with_vat': 1500000},
                '2018-03': {'spent_with_vat': 0},
            },
        ),
        (
            None,
            'phone_id_1',
            'client_id_1',
            datetime.datetime(2018, 3, 15, 23, 15, 16),
            {
                '2018-02': {'spent_with_vat': 0},
                '2018-03': {'spent_with_vat': 2000000},
            },
        ),
        (
            'user_id_not_stat',
            None,
            None,
            datetime.datetime(2019, 4, 15, 23, 15, 16),
            {'2019-04': {'spent_with_vat': 0}},
        ),
    ],
)
async def test_refund(
        taxi_corp_app_stq,
        patch,
        db,
        load_json,
        user_id,
        phone_id,
        client_id,
        status_updated,
        expected_result,
):
    await stq_tasks.refund(
        taxi_corp_app_stq, user_id, phone_id, client_id, status_updated,
    )

    if user_id is not None:
        corp_user = await db.corp_users.find_one({'_id': user_id})
    else:
        corp_user = await db.corp_users.find_one(
            {'phone_id': phone_id, 'client_id': client_id},
        )

    assert corp_user.get('stat') == expected_result
