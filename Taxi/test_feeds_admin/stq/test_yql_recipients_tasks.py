import datetime
import typing

from aiohttp import web
# pylint: disable=redefined-outer-name
import pytest

from taxi.stq import async_worker_ng

from feeds_admin.stq import feeds_admin_send
from test_feeds_admin import const


NOW = datetime.datetime(3000, 1, 2, 4, 0)


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
<table>\n<tr><th>Id                      </th><th>Title  </th><th>Content                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   </th><th>Type  </th><th>Files  </th><th>Attributes                                                                                                                                                                  </th><th>Parameters  </th><th>ClusterType  </th><th>QueryType  </th><th>CreatedAt     </th><th>UpdatedAt     </th><th>Status   </th><th>WorkerId                          </th><th style="text-align: right;">  WorkerVersion</th><th style="text-align: right;">  WorkerPid</th><th>WorkerHost                      </th><th>ExternalQueryIds  </th></tr>\n<tr><td>5dc3206e095c4ea674695614</td><td>       </td><td>use hahn; \nPRAGMA yt.InferSchema = '1';\n\n--меняем параметры\n$banner_id = '5dc320448f19ce1841cbcee9'; --id рассылки в ленте\n\n--не меняем параметры\n$experiment_id ='TAXICRM-1974';\n$experiment_name = @@TAXICRM-1974_телемед@@;\n$experiment_type = 'promotion';\n$table = '//home/taxi-crm/drivers/segment/SEGMENT_TAXICRM-1974';\n\n\n--сегментация\n\n$segm = (\n        select db_id||'_'||driver_uuid as db_id__uuid\n             , unique_driver_id\n             , group_id \n\n        from $table\n        where wave_no = 1);\n\n\n\n--не меняем\n$today = cast(CurrentUtcDate() as string);\n$format = DateTime2::Format('%Y-%m-%d %H:%M:%S');\n$time = cast($format(CurrentUtcDatetime()) as string);\n$exper = 'home/taxi-crm/drivers/production/experiments/'||$today|| '_new'; --таблица для отчетности\n\n\nINSERT INTO $exper\nSELECT\n'FEED' as channel,\n$experiment_id as experiment_id,\n$experiment_name as experiment_name,\n$experiment_type as experiment_type,\nUnwrap(group_id) as group_id,\ndb_id__uuid as comm_obj_id, \nunique_driver_id as uniq_obj_id,\nJust($banner_id) as comm_ids,\nCAST(NULL as String) as text,\n$time as creation_time,\n$today  as creation_day,\nUnwrap(Yson::Serialize(Yson::FromString(''))) as properties\n\nFROM $segm \n;\nCOMMIT ;\n\n\nselect db_id__uuid\nfrom $segm\nwhere group_id = '1_test' and db_id__uuid != ''\n;</td><td>SQL   </td><td>[]     </td><td>{'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 YaBrowser/19.7.0.2015 Yowser/2.5 Safari/537.36'}</td><td>{}          </td><td>UNKNOWN      </td><td>SQL        </td><td>11-06 19:35:10</td><td>11-06 19:35:11</td><td>COMPLETED</td><td>b3217e9-bcfa8dab-6c5ad2c0-9dd69ca0</td><td style="text-align: right;">        5884539</td><td style="text-align: right;">     660104</td><td>yql-myt-prod01.search.yandex.net</td><td>[]                </td></tr>\n</table>
        ]"""  # noqa: E501 # pylint: disable=line-too-long

    def get_results(self):
        return _MockYqlResults(self._table)


class _MockDefaultYqlTable:
    def get_iterator(self):
        return self.rows

    column_names = ['db_id__uuid', 'param1', 'param2']
    rows = [
        ['db_id__uuid1', 'text1', 'param2'],
        ['db_id__uuid2', 'text2', None],
    ]


class _MockBigYqlTable:
    def get_iterator(self):
        return self.rows

    column_names = ['db_id__uuid', 'param1', 'param2']
    rows = [
        ['db_id__uuid', 'text', 'param'],
        ['db_id__uuid', 'text', 'param'],
        ['db_id__uuid', 'text', 'param'],
    ]


class _FeedsYqlTable:
    def get_iterator(self):
        return self.rows

    column_names = ['recipient_id', 'param1', 'param2']
    rows = [['channel1', 'text1', 'param2'], ['channel2', 'text2', None]]


class _MockOnlyDriversTable:
    def get_iterator(self):
        return self.rows

    column_names = ['db_id__uuid']
    rows = [['db_id__uuid']]


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_yql.sql'])
@pytest.mark.config(
    FEEDS_ADMIN_PUBLISH_TASK_SETTINGS={'retries': 5, 'batch_size': 2},
    FEEDS_SERVICES={
        'feeds-sample': {
            'description': 'test',
            'feed_count': 10,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
        },
    },
    FEEDS_ADMIN_SERVICES={
        '__default__': {
            'description': 'Параметры по умолчанию',
            'wave_sending': {
                'enabled': True,
                'delay_between_waves_sec': 600,
                'wave_size': 200000,
            },
        },
    },
)
@pytest.mark.parametrize(
    [
        'feed_id',
        'run_id',
        'should_fail',
        'has_more',
        'yql_table',
        'drivers',
        'filters',
    ],
    [
        (
            const.UUID_1,
            1,
            False,
            False,
            _MockDefaultYqlTable,
            [
                [
                    {
                        'driver': 'db_id__uuid1',
                        'text': 'foo is text1',
                        'title': 'bar is text1, param2',
                    },
                    {
                        'driver': 'db_id__uuid2',
                        'text': 'foo is text2',
                        'title': 'bar is text2, None',
                    },
                ],
            ],
            None,
        ),
        (
            const.UUID_2,
            2,
            False,
            False,
            _MockDefaultYqlTable,
            [
                [
                    {
                        'driver': 'db_id__uuid1',
                        'text': 'foo',
                        'title': 'bar',
                        'url': 'text1',
                        'teaser': 'text1',
                        'dsat_action': 'text1',
                    },
                    {
                        'driver': 'db_id__uuid2',
                        'text': 'foo',
                        'title': 'bar',
                        'url': 'text2',
                        'teaser': 'text2',
                        'dsat_action': 'text2',
                    },
                ],
            ],
            None,
        ),
        (
            const.UUID_1,
            1,
            False,
            True,
            _MockBigYqlTable,
            [
                [
                    {
                        'driver': 'db_id__uuid',
                        'text': 'foo is text',
                        'title': 'bar is text, param',
                    },
                    {
                        'driver': 'db_id__uuid',
                        'text': 'foo is text',
                        'title': 'bar is text, param',
                    },
                ],
                [
                    {
                        'driver': 'db_id__uuid',
                        'text': 'foo is text',
                        'title': 'bar is text, param',
                    },
                ],
            ],
            None,
        ),
        (
            const.UUID_4,
            4,
            True,
            False,
            None,
            [
                [
                    {
                        'driver': 'db_id__uuid',
                        'text': 'foo is text',
                        'title': 'bar is text, param',
                    },
                    {'driver': 'db_id__uuid'},
                ],
            ],
            None,
        ),
        (
            const.UUID_5,
            5,
            False,
            False,
            _MockOnlyDriversTable,
            None,
            {'drivers': ['db_id__uuid']},
        ),
        (
            const.UUID_6,
            6,
            False,
            False,
            _MockOnlyDriversTable,
            None,
            {'drivers': ['db_id__uuid']},
        ),
        (
            const.UUID_7,
            7,
            False,
            False,
            _FeedsYqlTable,
            None,
            [
                {
                    'channel': 'channel1',
                    'payload_params': {'param1': 'text1', 'param2': 'param2'},
                },
                {
                    'channel': 'channel2',
                    'payload_params': {'param1': 'text2', 'param2': 'None'},
                },
            ],
        ),
    ],
)
async def test_feed_admin_send_yql_task(
        stq_runner,
        stq3_context,
        patch,
        mock_driver_wall,
        mock_feeds,
        feed_id,
        run_id,
        should_fail,
        has_more,
        yql_table,
        drivers,
        filters,
):
    @mock_driver_wall('/internal/driver-wall/v1/add')
    async def handler(request):  # pylint: disable=W0612
        assert request.json['id'] == f'{feed_id}_{run_id}'
        assert yql_table != _FeedsYqlTable
        if drivers is not None:
            assert len(request.json['drivers']) == len(
                drivers[CallCounter.count],
            )
            for item in request.json['drivers']:
                assert item in drivers[CallCounter.count]
        assert request.json.get('filters') == filters

        CallCounter()
        return web.json_response({'id': request.json['id']})

    @mock_feeds('/v1/batch/create')
    async def handler_feeds(request):  # pylint: disable=W0612
        assert request.json['items'][0]['request_id'] == f'{feed_id}_{run_id}'
        assert yql_table == _FeedsYqlTable
        for item in request.json['items'][0].get('channels'):
            assert item in filters

        CallCounter()
        return web.json_response({'items': [], 'filtered': [], 'feed_ids': {}})

    @mock_driver_wall('/internal/driver-wall/v1/remove')
    async def handler_remove(request):  # pylint: disable=W0612
        assert should_fail
        return web.json_response({})

    @patch('taxi.util.dates.utcnow')
    def utcnow():  # pylint: disable=W0612
        return NOW

    @patch('feeds_admin.stq.feeds_admin_send._is_expired')
    def _is_expired(*args):  # pylint: disable=W0612
        return False

    @patch('yql.api.v1.client.YqlClient.query')
    def _query(*args, **kwargs):
        return _MockYqlRequestOperation(yql_table)

    @patch('feeds_admin.models.run_history.Run.mark_failed')
    def mark_failed(*args):  # pylint: disable=W0612
        assert should_fail

    CallCounter.count = 0
    task_info = async_worker_ng.TaskInfo(feed_id, 0, 0, queue='')
    await feeds_admin_send.task(stq3_context, task_info, feed_id)
    if drivers and not should_fail:
        assert CallCounter.count == len(drivers)


@pytest.mark.now('3000-12-01T3:00:00')
@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_run_recipients.sql'])
@pytest.mark.config(
    FEEDS_ADMIN_PUBLISH_TASK_SETTINGS={'retries': 5, 'batch_size': 5000},
    TVM_RULES=[{'dst': 'driver-wall', 'src': 'feeds-admin'}],
)
async def test_feed_yql_recipients_for_run(
        stq_runner, stq3_context, patch, mock_driver_wall,
):
    @mock_driver_wall('/internal/driver-wall/v1/add')
    async def handler(request):  # pylint: disable=W0612
        assert request.json['id'] == f'{const.UUID_2}_2'
        assert request.json['template']['text'] == 'foo'
        return web.json_response({'id': request.json['id']})

    @patch('feeds_admin.stq.feeds_admin_send._is_expired')
    def _is_expired(*args):  # pylint: disable=W0612
        return False

    @patch('yql.api.v1.client.YqlClient.query')
    def query(*args, **kwargs):  # pylint: disable=W0612
        return _MockYqlRequestOperation(_MockDefaultYqlTable)

    await stq_runner.feeds_admin_send.call(
        args=(const.UUID_2,), kwargs={'run_id': 2},
    )
