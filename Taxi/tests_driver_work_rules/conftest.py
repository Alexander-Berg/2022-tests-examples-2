# pylint: disable=wildcard-import, unused-wildcard-import, import-error, C0411
from driver_work_rules_plugins import *  # noqa: F403 F401
import pytest

from tests_driver_work_rules import defaults


@pytest.fixture(name='mock_dispatcher_access_control', autouse=True)
def _mock_dispatcher_access_control(mockserver):
    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    def _get_users_list(request):
        return {
            'users': [
                {
                    'park_id': defaults.PARK_ID,
                    'passport_uid': '1',
                    'yandex_uid': '1',
                    'group_id': defaults.GROUP_ID,
                    'group_name': defaults.GROUP_NAME,
                    'email': defaults.EMAIL,
                    'is_enabled': True,
                    'is_confirmed': False,
                    'is_superuser': False,
                    'is_usage_consent_accepted': False,
                    'id': 'user1',
                },
            ],
        }


@pytest.fixture(autouse=True)
def fleet_synchronizer(mockserver):
    @mockserver.json_handler(
        '/fleet-synchronizer/fleet-synchronizer/v1/sync/park/property',
    )
    def _mock_sync_handler(request):
        return {}
