import pytest

from tests_driver_mode_index import utils

BILLING_DRIVER_MODE_SETTINGS_CONFIG = {
    'driver_fix': [
        {
            'start': '2019-12-17T00:00:00+03:00',
            'value': {
                'additional_profile_tags': ['df_tag1', 'df_tag2'],
                'commission_enabled': False,
                'promocode_compensation_enabled': False,
            },
        },
        {
            'start': '2025-12-17T00:00:00+03:00',
            'value': {
                'additional_profile_tags': [
                    'tag_from_future1',
                    'tag_from_future2',
                ],
                'commission_enabled': False,
                'promocode_compensation_enabled': False,
            },
        },
    ],
    'orders': [
        {
            'start': '2019-04-01T00:00:00+03:00',
            'value': {
                'additional_profile_tags': [
                    'actual_order_tag1',
                    'actual_order_tag2',
                ],
                'commission_enabled': True,
                'promocode_compensation_enabled': True,
            },
        },
        {
            'start': '2019-03-01T00:00:00+03:00',
            'value': {
                'additional_profile_tags': ['order_tag1', 'order_tag2'],
                'commission_enabled': True,
                'promocode_compensation_enabled': True,
            },
        },
    ],
    'uberdriver_v2': [
        {
            'start': '2019-12-12T00:00:00+03:00',
            'value': {
                'additional_profile_tags': ['udv2_tag1', 'udv2_tag2'],
                'commission_enabled': True,
                'promocode_compensation_enabled': True,
            },
        },
    ],
    'uberdriver_v3': [
        {
            'start': '2019-12-12T00:00:00+03:00',
            'value': {
                'additional_profile_tags': ['udv3_tag1', 'udv3_tag2'],
                'commission_enabled': True,
                'promocode_compensation_enabled': True,
            },
        },
    ],
}


@pytest.mark.now('2020-01-07T12:00:00+0300')
@pytest.mark.config()
@pytest.mark.config(
    DRIVER_MODE_INDEX_CONFIG=utils.get_config(billing_sync_enabled=False),
    BILLING_DRIVER_MODE_SETTINGS=BILLING_DRIVER_MODE_SETTINGS_CONFIG,
)
@pytest.mark.pgsql('driver_mode_index', files=['init_db.sql'])
@pytest.mark.parametrize(
    'park_id, driver_profile_id, expected_result',
    [
        pytest.param(
            'dbid_not_subscribed',
            'uuid_not_subscribed',
            {'actual_order_tag1', 'actual_order_tag2'},
            id='check for not subscribed user',
        ),
        pytest.param(
            'dbid1',
            'uuid1',
            {'actual_order_tag1', 'actual_order_tag2'},
            id='check latest rules in configs from db',
        ),
        pytest.param(
            'dbid2',
            'uuid2',
            {'df_tag1', 'df_tag2'},
            id='simple check driver fix tags from db',
        ),
        pytest.param(
            'dbid3',
            'uuid3',
            {'udv3_tag1', 'udv3_tag2'},
            id='simple check uberdriver tags from db',
        ),
        pytest.param(
            'dbid4',
            'uuid4',
            {'df_tag1', 'df_tag2'},
            id='secret mode driver from db',
        ),
    ],
)
async def test_driver_virtual_tags(
        taxi_driver_mode_index,
        park_id,
        driver_profile_id,
        expected_result,
        mockserver,
        pgsql,
        mocked_time,
):
    request = {
        'driver_info': {
            'park_id': park_id,
            'driver_profile_id': driver_profile_id,
        },
    }
    response = await taxi_driver_mode_index.post(
        'v1/driver/virtual_tags', json=request,
    )
    assert response.status_code == 200
    assert set(response.json()['virtual_tags']) == expected_result
