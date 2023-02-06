# pylint: disable=import-error
import datetime

from geobus_tools import geobus  # noqa: F401 C5521
import pytest


NOW = datetime.datetime(2001, 9, 9, 1, 46, 39)


@pytest.mark.parametrize(
    'request_body, contractors',
    [
        (
            {
                'zone_id': 'moscow',
                'tariff_classes': ['econom'],
                'contractors': [
                    {'dbid_uuid': 'dbid_uuid0'},
                    {'dbid_uuid': 'dbid_uuid1'},
                ],
                'route': [[37.66, 55.73], [37.66, 55.71]],
                'calc_alternative_type': 'inner_combo',
                'user_id': 'deadb0d4',
            },
            [{'dbid_uuid': 'dbid_uuid0'}],
        ),
        (
            {
                'zone_id': 'moscow',
                'tariff_classes': ['comfort'],
                'contractors': [
                    {'dbid_uuid': 'dbid_uuid0'},
                    {'dbid_uuid': 'dbid_uuid1'},
                ],
                'route': [[37.66, 55.73], [37.66, 55.71]],
                'calc_alternative_type': 'inner_combo',
            },
            [],
        ),
        (
            {
                'zone_id': 'spb',
                'tariff_classes': ['econom'],
                'contractors': [{'dbid_uuid': 'dbid_uuid2'}],
                'route': [[37.66, 55.73], [37.66, 55.71]],
            },
            [{'dbid_uuid': 'dbid_uuid2'}],
        ),
        (
            {
                'zone_id': 'spb',
                'tariff_classes': ['comfort'],
                'contractors': [{'dbid_uuid': 'dbid_uuid2'}],
                'route': [[37.66, 55.73], [37.66, 55.71]],
            },
            [],
        ),
        (
            {
                'zone_id': 'moscow',
                'tariff_classes': ['econom'],
                'contractors': [
                    {'dbid_uuid': 'dbid_uuid3'},
                    {'dbid_uuid': 'dbid_uuid4'},
                ],
                'route': [[37.66, 55.73], [37.66, 55.71]],
                'calc_alternative_type': 'combo_check_1',
                'user_id': 'deadb0d4',
            },
            [{'dbid_uuid': 'dbid_uuid3'}],
        ),
    ],
)
@pytest.mark.pgsql(
    'combo_contractors',
    files=[
        'create_contractor_partitions.sql',
        'contractors.sql',
        'order_match_rule.sql',
    ],
)
@pytest.mark.config(ROUTER_SELECT=[{'routers': ['linear-fallback']}])
@pytest.mark.experiments3(filename='experiments3.json')
async def test_satisfy_combo_order(
        taxi_combo_contractors, mocked_time, request_body, contractors,
):
    mocked_time.set(NOW)
    await taxi_combo_contractors.invalidate_caches()

    response = await taxi_combo_contractors.post(
        '/satisfy_combo_order', json=request_body,
    )

    assert response.status_code == 200
    assert (
        sorted(response.json()['contractors'], key=lambda x: x['dbid_uuid'])
        == contractors
    )
