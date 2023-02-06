import datetime


import pytest


from . import utils


# pylint: disable=too-many-arguments
@pytest.mark.parametrize(
    'json_request,expected_code,expected_account,expected_log',
    [
        (
            {
                'unique_driver_id': '000000000000000000000001',
                'status': 'silver',
                'reason': ' unioned',
            },
            200,
            [
                (
                    '000000000000000000000001',
                    datetime.datetime(2019, 4, 30, 21, 0),
                    'silver',
                    '{}',
                    True,
                ),
            ],
            [
                ('silver', '000000000000000000000001', 'unioned', 0),
                ('silver', '000000000000000000000001', 'recount', 133),
                ('gold', '000000000000000000000001', 'recount', 233),
                ('newbie', '000000000000000000000001', 'registration', 0),
            ],
        ),
        (
            {
                'unique_driver_id': '000000000000000000000002',
                'status': 'gold',
                'reason': ' unioned',
            },
            200,
            [
                (
                    '000000000000000000000002',
                    datetime.datetime(2019, 4, 30, 21, 0),
                    'gold',
                    '{}',
                    True,
                ),
            ],
            [('gold', '000000000000000000000002', 'unioned', 0)],
        ),
        (
            {
                'unique_driver_id': '000000000000000000000002',
                'status': 'bad_status',
                'reason': ' unioned',
            },
            400,
            None,
            None,
        ),
    ],
)
@pytest.mark.pgsql(
    'loyalty', files=['loyalty_accounts.sql', 'status_logs.sql'],
)
@pytest.mark.now('2019-04-01T06:35:00+0500')
async def test_admin_driver_status_set(
        taxi_loyalty,
        tags,
        pgsql,
        json_request,
        expected_code,
        expected_account,
        expected_log,
):
    tags.set_append_tag(json_request['status'])

    response = await taxi_loyalty.post(
        'admin/loyalty/v1/status/set', json=json_request,
    )

    assert response.status_code == expected_code
    if response.status_code == 200:
        unique_driver_id = json_request['unique_driver_id']
        account = utils.select_account(pgsql, unique_driver_id)
        assert account == expected_account
        log = utils.select_log(pgsql, unique_driver_id)
        assert log == expected_log
