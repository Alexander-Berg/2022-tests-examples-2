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
        'solomon_metrics_reader_task': {
            'description': 'Some task',
            'enabled': True,
            'timeout': 60,
        },
    },
    MPA_HARVESTER_SOLOMON_METRICS_READER_SETTINGS={
        'cpu_usage': {
            'description': 'cpu usage',
            'enabled': True,
            'service_selector': {
                'project_name': 'taxi-infra',
                'service_name': 'client-events',
                'cluster_type': 'nanny',
            },
            'solomon_project_selector': {
                'abc': 'golovan',
                'text': '^yasm_%SERVICE%$',
            },
            'program': (
                '{project="%SOLOMON_PROJECT_ID%", '
                'hosts="*", ctype="stable|pre_stable", '
                'srv="%SERVICE%", prj="%PROJECT%", '
                'signal="portoinst-cpu_usage_cores_tmmv", }'
            ),
            'host': {'label': 'hosts'},
        },
    },
)
async def test_task(
        clownductor_mocks,
        mock_distlocks,
        mock_solomon,
        mock_solomon_sensors,
        yt_client,
        yt_apply,
):
    @mock_distlocks('/v1/locks/acquire/')
    async def _acquire_distlock():
        return {
            'status': 'free',
            'namespace': 'mpa-harvester',
            'name': 'solomon_metrics_reader_task',
        }

    @mock_solomon('/api/v2/projects')
    async def _get_projects(request):
        if request.query['page'] == '0':
            assert request.query == {
                '_usePagination': 'true',
                'filterByAbc': 'golovan',
                'page': '0',
                'pageSize': '10',
                'text': 'yasm_client-events',
            }
            return {
                'result': [
                    {
                        'id': 'yasm_client-events',
                        'name': 'client-events',
                        'description': '',
                        'owner': 'robot-yasm-golovan',
                        'onlyNewFormatWrites': False,
                        'onlyNewFormatReads': False,
                        'metricNameLabel': '',
                        'createdAt': '2021-02-10T17:35:29.788Z',
                        'updatedAt': '2021-02-10T17:35:29.788Z',
                        'createdBy': 'robot-yasm-golovan',
                        'updatedBy': 'robot-yasm-golovan',
                        'version': 1,
                    },
                ],
                'page': {
                    'pagesCount': 1,
                    'totalCount': 1,
                    'pageSize': 10,
                    'current': 0,
                },
            }
        # elif page > 0
        assert request.query == {
            '_usePagination': 'true',
            'filterByAbc': 'golovan',
            'page': '1',
            'pageSize': '10',
            'text': 'yasm_client-events',
        }
        return {
            'result': [],
            'page': {
                'pagesCount': 1,
                'totalCount': 1,
                'pageSize': 10,
                'current': 1,
            },
        }

    @mock_solomon_sensors('/api/v2/projects/yasm_client-events/sensors/data')
    async def _get_sensors(request):
        assert request.json == {
            'program': (
                '{project="yasm_client-events", hosts="*", '
                'ctype="stable|pre_stable", srv="client-events", '
                'prj="taxi-infra", signal="portoinst-cpu_usage_cores_tmmv", }'
            ),
            'from': '2020-01-01T14:58:50+03:00',
            'to': '2020-01-01T15:00:00+03:00',
            'version': 'GROUP_LINES_RETURN_VECTOR_2',
        }
        return {
            'vector': [
                {
                    'timeseries': {
                        'alias': '',
                        'kind': 'DGAUGE',
                        'type': 'DGAUGE',
                        'labels': {
                            'signal': 'portoinst-cpu_usage_cores_tmmv',
                            'hosts': (
                                'taxi-client-events-stable-4.'
                                + 'vla.yp-c.yandex.net'
                            ),
                        },
                        'timestamps': [
                            1650986040000,
                            1650986045000,
                            1650986050000,
                        ],
                        'values': [
                            2.8830979061002533,
                            2.896232638733151,
                            2.8877113765333586,
                        ],
                    },
                },
            ],
        }

    await run_cron.main(['mpa_harvester.crontasks.harvest', '-t', '0'])

    t_path = T_PATH_PREFIX + 'solomon_metrics'
    rows = list(yt_client.select_rows(f'* FROM [{t_path}]'))
    for row in rows:
        row.pop('$row_index', None)
        row.pop('$tablet_index', None)

    assert rows == [
        {
            'created': calendar.timegm(
                datetime.datetime(2020, 1, 1, 12, 0, 0, 0).utctimetuple(),
            ),
            'from': calendar.timegm(
                datetime.datetime(2020, 1, 1, 11, 58, 50, 0).utctimetuple(),
            ),
            'to': calendar.timegm(
                datetime.datetime(2020, 1, 1, 12, 0, 0, 0).utctimetuple(),
            ),
            'duration': 70000000,
            'metric': 'cpu_usage',
            'service_name': 'client-events',
            'yasm_project': 'yasm_client-events',
            'dc': None,
            'host': 'taxi-client-events-stable-4.vla.yp-c.yandex.net',
            'solomon_info': {
                'timeseries': {
                    'alias': '',
                    'type': 'DGAUGE',
                    'kind': 'DGAUGE',
                    'labels': {
                        'hosts': (
                            'taxi-client-events-stable-4.vla.yp-c.yandex.net'
                        ),
                        'signal': 'portoinst-cpu_usage_cores_tmmv',
                    },
                    'timestamps': [
                        1650986040000,
                        1650986045000,
                        1650986050000,
                    ],
                    'values': [
                        2.8830979061002533,
                        2.896232638733151,
                        2.8877113765333586,
                    ],
                },
            },
        },
    ]
