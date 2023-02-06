import calendar
import datetime
import logging

import pytest

# pylint: disable=redefined-outer-name
from mpa_harvester.generated.cron import run_cron

logger = logging.getLogger(__name__)

T_PATH_PREFIX = '//home/unittests/unittests/features/mpa-harvester/raw/'


@pytest.mark.now('2020-01-01T12:00:00+0000')
@pytest.mark.config(
    MPA_HARVESTER_TASKS={
        'miscroservices_info_reader_task': {
            'description': 'Some task',
            'enabled': True,
            'timeout': 60,
        },
    },
)
async def test_task(clownductor_mocks, mock_distlocks, yt_client, yt_apply):
    @mock_distlocks('/v1/locks/acquire/')
    async def _acquire_distlock():
        return {
            'status': 'free',
            'namespace': 'mpa-harvester',
            'name': 'get_services_task',
        }

    await run_cron.main(['mpa_harvester.crontasks.harvest', '-t', '0'])

    t_path = T_PATH_PREFIX + 'services'
    rows = list(yt_client.select_rows(f'* FROM [{t_path}]'))
    for row in rows:
        row.pop('$row_index', None)
        row.pop('$tablet_index', None)

    assert (
        sorted(
            rows, key=lambda item: item['clownductor_info']['service']['id'],
        )
        == [
            {
                'created': calendar.timegm(
                    datetime.datetime(2020, 1, 1, 12, 0, 0, 0).utctimetuple(),
                ),
                'name': 'service',
                'service_id': 1,
                'project_id': 2,
                'clownductor_info': {
                    'project': {
                        'id': 2,
                        'name': 'taxi-infra',
                        'namespace_id': 1,
                        'owners': {
                            'groups': ['group-2'],
                            'logins': ['admin-2'],
                        },
                    },
                    'service': {
                        'id': 1,
                        'project_name': 'taxi-infra',
                        'project_id': 2,
                        'name': 'service',
                        'cluster_type': 'nanny',
                        'abc_service': 'serviceabc',
                    },
                },
            },
            {
                'created': calendar.timegm(
                    datetime.datetime(2020, 1, 1, 12, 0, 0, 0).utctimetuple(),
                ),
                'name': 'client-events',
                'service_id': 2,
                'project_id': 2,
                'clownductor_info': {
                    'project': {
                        'id': 2,
                        'name': 'taxi-infra',
                        'namespace_id': 1,
                        'owners': {
                            'groups': ['group-2'],
                            'logins': ['admin-2'],
                        },
                    },
                    'service': {
                        'id': 2,
                        'project_name': 'taxi-infra',
                        'project_id': 2,
                        'name': 'client-events',
                        'cluster_type': 'nanny',
                        'abc_service': 'client_events',
                    },
                },
            },
        ]
    )
