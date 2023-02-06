import json

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from driver_fix_plugins import *  # noqa: F403 F401
import pytest

from tests_driver_fix import common

BUG_PROFILES_DEFAULT_VALUE = {
    'classes': ['econom', 'business'],
    'dbid': '7ad36bc7560449998acbe2c57a75c293',
    'position': [0.0, 0.0],
    'uuid': 'c5673ab7870c45b3adc42fec699a252c',
}


async def test_protocol_bug(taxi_driver_fix, mockserver):
    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        return {'drivers': [BUG_PROFILES_DEFAULT_VALUE]}

    @mockserver.json_handler('/protocol/3.0/nearestzone')
    def _protocol(request):
        assert request.get_data() != b'{"point":['
        return {'nearest_zone': {}}

    response = await taxi_driver_fix.post(
        '/v1/view/offer',
        json={'driver_profile_id': 'uuid', 'park_id': 'dbid'},
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )

    assert response.status_code == 200


@pytest.fixture
def service_client_default_headers():
    return {'Accept-Language': 'en'}


@pytest.fixture
def taxi_dms_mock(mockserver):
    @mockserver.json_handler('/driver-mode-subscription/v1/mode/info')
    def _driver_mode_subscription_mode_info(request):
        assert request.args['driver_profile_id'] == 'uuid'
        assert request.args['park_id'] == 'dbid'
        return {
            'mode': {
                'name': 'driver_fix_mode',
                'started_at': '2019-05-01T08:00:00+0300',
                'features': [
                    {
                        'name': 'driver_fix',
                        'settings': {
                            'rule_id': 'subvention_rule_id',
                            'shift_close_time': '00:00:00+03:00',
                        },
                    },
                    {'name': 'tags'},
                ],
            },
        }


@pytest.fixture
def taxi_vbd_mock(mockserver):
    @mockserver.json_handler('/billing_subventions/v1/virtual_by_driver')
    async def _get_by_driver(request):
        assert json.loads(request.get_data()) == {
            'driver': {'db_id': 'dbid', 'uuid': 'uuid'},
            'types': ['driver_fix'],
        }
        return mockserver.make_response('not found error', 404)


def pytest_collection_modifyitems(config, items):
    for item in items:
        item.add_marker(pytest.mark.geoareas(filename='geoareas.json'))
        item.add_marker(pytest.mark.tariffs(filename='tariffs.json'))
