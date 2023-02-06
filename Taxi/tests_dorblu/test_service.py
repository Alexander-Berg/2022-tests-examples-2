# flake8: noqa
# pylint: disable=import-error,wildcard-import
from dorblu_plugins.generated_tests import *


async def test_group_rules_get(taxi_dorblu):
    response = await taxi_dorblu.get(
        'v1/rules/group/get?group=test_service_rtc',
    )
    assert response.status_code == 200
    assert response.json() == {
        'group': 'test_service_rtc',
        'group_type': 'rtc',
        'from_file': 'taxi/nanny.taxi_dorblu_testing',
        'project': 'taxi',
        'rules': [
            {
                'Options': {'CustomHttp': [431, [405, 407]]},
                'filter': {'type': 'Dummy'},
                'name': 'TOTAL',
                'rule_id': 2,
            },
        ],
    }


async def test_group_list(taxi_dorblu):
    response = await taxi_dorblu.get('/v1/rules/group/list_cached')
    assert response.status_code == 200
    known_groups = [
        'test_service_rtc',
        'test_service_conductor',
        'test_service2_conductor',
        'test_service2_rtc',
        'test_service_tcp_err_rtc',
    ]
    # only check issubset not equality, because
    assert set(known_groups).issubset(set(response.json()))


async def test_group_hosts_get(taxi_dorblu):
    response = await taxi_dorblu.get(
        '/v1/hosts/group/get?group=test_service_rtc',
    )
    assert response.status_code == 200
    assert response.json() == [{'hostname': 'localhost', 'dc': 'test_dc'}]
