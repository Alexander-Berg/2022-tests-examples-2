# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from crm_scheduler_plugins import *  # noqa: F403 F401


@pytest.fixture(name='crm_admin_get_list_mock')
def crm_admin_get_list_mock(mockserver):
    @mockserver.json_handler('/crm-admin/v1/campaigns/meta/list')
    def _mock_crm_admin(request):
        return {
            'campaigns': [
                {
                    'campaign_id': 123,
                    'groups': [
                        {
                            'group_id': 456,
                            'allowed_time_scope': {
                                'start_scope_time': '2021-12-14T10:00:00Z',
                                'end_scope_time': '2022-12-10T10:00:00Z',
                                'start_time_sec': 28800,
                                'stop_time_sec': 64800,
                            },
                        },
                    ],
                },
                {
                    'campaign_id': 987,
                    'groups': [
                        {
                            'group_id': 654,
                            'allowed_time_scope': {
                                'start_scope_time': '2021-10-01T12:00:00Z',
                                'end_scope_time': '2021-10-31T15:00:00Z',
                                'start_time_sec': 10 * 60 * 60,
                                'stop_time_sec': 18 * 60 * 60,
                            },
                        },
                    ],
                },
            ],
            'actual_ts': '2021-12-14T14:00:00Z',
        }
