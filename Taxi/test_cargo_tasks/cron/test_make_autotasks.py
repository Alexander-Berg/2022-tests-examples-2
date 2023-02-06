# pylint: disable=redefined-outer-name
import datetime
import typing

import pytest

from cargo_tasks.generated.cron import run_cron


TODAY = datetime.datetime.now().day
CURRENT_HOUR = datetime.datetime.now().hour
ANOTHER_DAY = (datetime.datetime.now() - datetime.timedelta(days=10)).day
TASKS_CONFIG = {
    'enabled': True,
    'tasks': [
        {
            'alias': 'example_task',
            'launch_time': {
                'days_to_launch': [ANOTHER_DAY],
                'hours_to_launch': [],
                'should_reschedule_from_weekend': True,
            },
            'yql_link': (
                'https://yql.yandex-team.ru/Operations/should_not_be_launched'
            ),
            'enabled': True,
            'activity_defaults': {
                'text': 'some_text',
                'responsible_user_id': 133730035,
                'task_type_id': 1,
            },
        },
        {
            'alias': 'example_task',
            'launch_time': {
                'days_to_launch': [TODAY],
                'hours_to_launch': [9, 12, 18, CURRENT_HOUR],
                'should_reschedule_from_weekend': True,
            },
            'yql_link': 'https://yql.yandex-team.ru/Operations/Ylj7wAVK8O09M1YQmGCYyXRpfHKFUQxvrDgsd9IhV-g=',  # noqa: E501 # pylint: disable=line-too-long
            'enabled': True,
            'activity_defaults': {
                'text': 'some_text',
                'responsible_user_id': 133730035,
                'task_type_id': 1,
            },
        },
    ],
}
EXPECTED_REQUEST = {
    'tasks': [
        {
            'text': 'text1',
            'complete_till': 1649998784,
            'entity_id': 1,
            'entity_type': 'leads',
            'task_type_id': 1,
            'responsible_user_id': 133730035,
            'is_completed': True,
        },
        {
            'text': 'text2',
            'complete_till': 1649998784,
            'entity_id': 1,
            'entity_type': 'leads',
            'task_type_id': 1,
            'responsible_user_id': 133730035,
            'is_completed': False,
        },
    ],
}


class CallCounter:
    count = 0

    def __new__(cls):
        cls.count += 1


class _MockYqlResults:
    class result:  # pylint: disable=C0103
        status_code = 200
        text = 'OK'

    errors: typing.List[str] = []
    _table = None

    def __init__(self, table):
        self._table = table

    def __iter__(self):
        return iter([self._table()])


class _MockYqlRequestOperation:
    _table = None

    def __init__(self, table):
        self._table = table

    def run(self):
        return _MockYqlRequestOperation(_MockDefaultYqlTable)

    @property
    def special(self):
        return """[
<table>\n<tr><th>Id                      </th><th>Title  </th><th>Content                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   </th><th>Type  </th><th>Files  </th><th>Attributes                                                                                                                                                                  </th><th>Parameters  </th><th>ClusterType  </th><th>QueryType  </th><th>CreatedAt     </th><th>UpdatedAt     </th><th>Status   </th><th>WorkerId                          </th><th style="text-align: right;">  WorkerVersion</th><th style="text-align: right;">  WorkerPid</th><th>WorkerHost                      </th><th>ExternalQueryIds  </th></tr>\n<tr><td>5dc3206e095c4ea674695614</td><td>       </td><td>use hahn;\nSELECT\n1 as lead_id,\n'sql text' as text,\ncast(CurrentUtcDatetime() as Uint32) as complete_till,\n1 as task_type_id;</td><td>SQL   </td><td>[]     </td><td>{'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 YaBrowser/19.7.0.2015 Yowser/2.5 Safari/537.36'}</td><td>{}          </td><td>UNKNOWN      </td><td>SQL        </td><td>11-06 19:35:10</td><td>11-06 19:35:11</td><td>COMPLETED</td><td>b3217e9-bcfa8dab-6c5ad2c0-9dd69ca0</td><td style="text-align: right;">        5884539</td><td style="text-align: right;">     660104</td><td>yql-myt-prod01.search.yandex.net</td><td>[]                </td></tr>\n</table>
        ]"""  # noqa: E501 # pylint: disable=line-too-long

    @property
    def web_url(self):
        return 'mocked_web_url'

    @property
    def share_url(self):
        return 'mocked_share_url'

    @property
    def status(self):
        return 'COMPLETED'

    @property
    def operation_id(self):
        return 'operation_id'

    def get_results(self):
        return _MockYqlResults(self._table)


class _MockDefaultYqlTable:
    def get_iterator(self):
        return self.rows

    column_names = [
        'lead_id',
        'text',
        'complete_till',
        'task_type_id',
        'is_completed',
    ]
    rows = [
        [1, 'text1', 1649998784, 1, True],
        [1, 'text2', 1649998784, 1, False],
    ]


@pytest.fixture
def patch_yql(patch, load_json, mockserver):
    # pylint: disable=unused-variable
    @patch('yql.api.v1.client.YqlClient.query')
    def patch_yql_query(*args, **kwargs):
        return _MockYqlRequestOperation(_MockDefaultYqlTable)

    # pylint: disable=unused-variable
    @patch('yql.client.operation.YqlSqlOperationRequest')
    def patch_operation_request(*args, **kwargs):
        return _MockYqlRequestOperation(_MockDefaultYqlTable)

    # pylint: disable=unused-variable
    @patch('yql.client.operation.YqlOperationStatusRequest')
    def patch_status_request(*args, **kwargs):
        return _MockYqlRequestOperation(_MockDefaultYqlTable)

    @patch('yql.api.v1.client.YqlClient.query')
    def _query(*args, **kwargs):
        return _MockYqlRequestOperation(_MockDefaultYqlTable)


@pytest.mark.config(CARGO_TASKS_AMOCRM_AUTOTASKS=TASKS_CONFIG)
async def test_make_autotasks(
        mockserver, yt_apply, yt_client, patch_yql, load_json,
):
    @mockserver.json_handler(
        '/cargo-sf/internal/cargo-sf/amocrm/internal-requests/create-task-free',  # noqa: E501 # pylint: disable=line-too-long
    )
    def _mock_create_task(request):
        assert request.json == EXPECTED_REQUEST
        return {}

    await run_cron.main(['cargo_tasks.crontasks.make_autotasks', '-t', '0'])

    assert _mock_create_task.times_called == 1
