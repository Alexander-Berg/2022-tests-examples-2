# pylint: disable=C0103
# pylint: disable=too-many-lines
# pylint: disable=redefined-outer-name
import copy
import http
import uuid

from aiohttp import web
import deepdiff
import pytest

from taxi.stq import async_worker_ng

from discounts_operation_calculations.stq import calc_segment_stats
from discounts_operation_calculations.stq import multidraft
from test_discounts_operation_calculations import conftest

MULTIDRAFTS_URL = 'test_url/multidraft/{multidraft_id}/?multi=true'
MULTIDRAFT_ID = 142
DATETIME_STR = '2020-10-01 15:54:32.123456'

CONTROL_SHARE = 10
TEST_SHARE = (100 - CONTROL_SHARE) / 100

SQL_FILES = ['fill_pg_segment_stats_all.sql', 'fill_pg_city_stats.sql']

CONFIGS = {
    'DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS': {
        'kt': {
            'name': 'algorithm1',
            'metric_name': 'Отобранные поездки',
            'second_metric_name': 'Цена дополнительного оффера',
            'algorithm_type': 'katusha',
            'max_absolute_value': 600,
            'max_value': 0.5,
            'min_value': 0.05,
            'discount_duration': 5,
            'disable_by_surge': 1.11,
            'payment_types': ['card', 'bitkoin'],
            'classes': ['uberx', 'econom', 'business'],
            'control_share': CONTROL_SHARE,
            'user_segment_path': 'yt_path',
        },
        'kt1': {
            'name': 'algorithm11',
            'metric_name': 'Отобранные поездки',
            'second_metric_name': 'Цена дополнительного оффера',
            'algorithm_type': 'katusha',
            'max_absolute_value': 600,
            'max_value': 0.5,
            'min_value': 0.05,
            'discount_duration': 5,
            'disable_by_surge': 1.11,
            'payment_types': ['card', 'bitkoin'],
            'classes': ['uberx', 'econom', 'business'],
            'control_share': CONTROL_SHARE,
            'user_segment_path': 'yt_path1',
        },
    },
    'DISCOUNTS_OPERATION_CALCULATIONS_COMMON_CONFIG': {
        'apply_for_airport_orders': True,
        'discount_class': 'katusha',
        'fallback_discount_class': 'katusha-flat',
        'discount_method': 'subvention-fix',
        'discount_target': 'tag_service',
        'point_a_is_enough': False,
        'round_digits': 2,
        'city_tz_mapping_path': 'пыщь',
        'ma_users_path': 'пыщь',
        'discounts_city_mapping_path': 'ололо',
    },
    'DISCOUNTS_OPERATION_CALCULATIONS_CITY_TZ_MAPPING': {
        'test_city': ['test_tz'],
    },
    'MULTIDRAFTS_URL': MULTIDRAFTS_URL,
    'DISCOUNTS_OPERATION_CALCULATIONS_STARTRACK_CONFIG': {
        '__default__': {
            'queue': 'TESTQUEUE',
            'tags': ['test'],
            'assignee': 'test_user',
            'followers': [],
        },
        'kt2': {'followers': ['test_user']},
    },
    'DISCOUNTS_OPERATION_CALCULATIONS_EXPERIMENTS_CONFIG': {
        'exp_hash_salt': 'abc',
        'partitions': [
            {'algo_name': 'kt', 'partition': [50, 100]},
            {'algo_name': 'kt1', 'partition': [0, 50]},
        ],
    },
    'DISCOUNTS_OPERATION_CALCULATIONS_PUSHES_CONFIG': {
        'discount_duration': {'__default__': 14},
        'push_discounts_close_lag': 2880,
    },
    'DISCOUNTS_OPERATION_CALCULATIONS_ELASTICITIES': (
        conftest.ELASTICITIES_DICT
    ),
    'DISCOUNTS_OPERATION_CALCULATIONS_SEGMENTS_MEAN_ELASTICITIES': (
        {
            '0': 0,
            '1': 1.1,
            '2': 2,
            '3': 2.9,
            'ma_active_Hconv': 0,
            'ma_active_Lconv': 1.6,
            'ma_active_Mconv': 0.8,
            'ma_notactive_Hconv': 0,
            'ma_notactive_Lconv': 1.9,
            'ma_notactive_Mconv': 0.9,
            'not_ma_active_Hconv': 0,
            'not_ma_active_Lconv': 0.75,
            'not_ma_active_Mconv': 0,
            'not_ma_notactive_Hconv': 0,
            'not_ma_notactive_Lconv': 0.65,
            'not_ma_notactive_Mconv': 0.8,
            'random': 0.8,
        }
    ),
}

CREATE_MULTIDRAFT_RESPONSE = {
    'created_by': 'artem-mazanov',
    'created': '2021-10-28T14:04:33+0300',
    'updated': '2021-10-28T14:04:33+0300',
    'version': 1,
    'comments': [
        {
            'login': 'artem-mazanov',
            'comment': 'artem-mazanov прикрепил тикет TESTQUEUE-1',
        },
    ],
    'description': 'Выключение скидок в городе test_city',
    'tickets': ['TESTQUEUE-1'],
    'status': 'need_approval',
    'data': {},
}


@pytest.fixture
async def mock_other_services(
        expected_create_draft_request_path,
        patch,
        mock_ride_discounts,
        mock_taxi_approvals,
        mock_atlas_backend,
        mockserver,
        load_json,
):
    @mock_ride_discounts('/v1/admin/match-discounts/find-discounts')
    async def _find_discounts(request):
        return {
            'discounts_data': {
                'hierarchy_name': 'full_money_discounts',
                'discounts_info': [],
            },
        }

    @mockserver.json_handler('/startrek/issues')
    async def _create_ticket(*args, **kwargs):
        return {'key': 'TESTQUEUE-1'}

    @mock_taxi_approvals('/drafts/create/')
    async def _create_draft_handler(request):
        if expected_create_draft_request_path:
            expected_create_draft_request = load_json(
                expected_create_draft_request_path,
            )
            assert not deepdiff.DeepDiff(
                request.json,
                expected_create_draft_request,
                exclude_paths=['root[\'data\'][\'to_add\']'],
            )
        return {'id': 1, 'version': 1, 'status': 'waiting_check'}

    @mock_taxi_approvals('/drafts/attach/')
    async def _attach_draft_handler(request):
        return {'id': 1, 'version': 1}

    @mock_taxi_approvals('/drafts/1/')
    async def _get_draft_handler(request):
        return {'id': 1, 'version': 2, 'status': 'need_approval'}

    @mock_taxi_approvals('/multidrafts/create/')
    async def _create_multidraft_handler(request):
        if 'test_city' in request.json['description']:
            multidraft_id = MULTIDRAFT_ID
        else:
            raise RuntimeError('Unknown city!')
        _response = copy.deepcopy(CREATE_MULTIDRAFT_RESPONSE)
        _response['id'] = multidraft_id
        return _response

    @mock_atlas_backend('/api/classes')
    async def atlas_backend_handler_classes(request):  # pylint: disable=W0612
        return web.json_response(
            [{'ru': 'Эконом', 'en': 'econom'}, {'ru': 'uberX', 'en': 'uberx'}],
        )


@pytest.mark.parametrize(
    'expected_create_draft_request_path',
    ['expected_create_draft_request.json'],
)
@pytest.mark.now(DATETIME_STR)
@pytest.mark.pgsql('discounts_operation_calculations', files=SQL_FILES)
@pytest.mark.config(**CONFIGS)
async def test_flow_v2(
        expected_create_draft_request_path,
        calc_segment_stats_mock,
        pgsql,
        web_app_client,
        mock_other_services,
        patch,
        stq3_context,
):
    @patch('uuid.uuid4')
    def _uuid():
        return uuid.UUID(int=42, version=4)

    task_id = uuid.uuid4().hex

    response = await web_app_client.post(
        '/v2/statistics/calc_segment_stats',
        headers={'X-Yandex-Login': 'test_user'},
        json={
            'common_params': {
                'discounts_city': 'test_city',
                'companies': ['tuda-suda'],
                'payment_methods': ['card', 'bitkoin', 'cash'],
                'tariffs': ['econom', 'business'],
                'min_discount': 0,
                'max_discount': 30,
            },
            'custom_params': [
                {'algorithm_id': 'kt', 'max_surge': 1.31, 'with_push': False},
            ],
        },
    )
    assert response.status == 200
    content = await response.json()
    suggest_id = content['suggest_id']

    response = await web_app_client.get(
        f'/v2/suggests/{suggest_id}/detailed_info',
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'all_fixed_discounts': [],
        'calc_discounts_params': {
            'all_fixed_discounts': [
                {'algorithm_id': 'kt', 'fixed_discounts': []},
            ],
            'suggest_id': 1,
        },
        'calc_statistics_params': {
            'common_params': {
                'companies': ['tuda-suda'],
                'discounts_city': 'test_city',
                'max_discount': 30,
                'min_discount': 0,
                'tariffs': ['econom', 'business'],
                'payment_methods': ['card', 'bitkoin', 'cash'],
            },
            'custom_params': [
                {'algorithm_id': 'kt', 'max_surge': 1.31, 'with_push': False},
            ],
        },
        'segments': [],
        'status_info': {'status': 'CALC_SEGMENT_STATS'},
        'currency_info': {},
        'suggest_version': 2,
        'metric': 'extra_trips',
    }

    # Run task
    await calc_segment_stats.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=task_id, exec_tries=0, reschedule_counter=0, queue='',
        ),
    )

    # Check results after segments calculation
    response = await web_app_client.get(
        f'/v2/suggests/{suggest_id}/detailed_info',
    )

    assert response.status == 200
    content = await response.json()
    assert len(content['statistics']) == 3
    del content['statistics']  # this field tested in other place
    assert content == {
        'all_fixed_discounts': [
            {
                'algorithm_id': 'kt',
                'fixed_discounts': [
                    {'discount_value': 12, 'segment': 'random'},
                    {'discount_value': 0, 'segment': 'control'},
                ],
            },
        ],
        'calc_discounts_params': {
            'all_fixed_discounts': [
                {'algorithm_id': 'kt', 'fixed_discounts': []},
            ],
            'suggest_id': 1,
        },
        'calc_statistics_params': {
            'common_params': {
                'companies': ['tuda-suda'],
                'discounts_city': 'test_city',
                'max_discount': 30,
                'min_discount': 0,
                'tariffs': ['econom', 'business'],
                'payment_methods': ['card', 'bitkoin', 'cash'],
            },
            'custom_params': [
                {'algorithm_id': 'kt', 'max_surge': 1.31, 'with_push': False},
            ],
        },
        'segments': [
            {
                'algorithm_id': 'kt',
                'segment_names': [
                    'control',
                    'metrika_active_Hconv',
                    'metrika_active_Lconv',
                    'metrika_active_Mconv',
                    'metrika_notactive_Hconv',
                    'metrika_notactive_Lconv',
                    'metrika_notactive_Mconv',
                    'random',
                ],
            },
        ],
        'status_info': {'status': 'NOT_PUBLISHED'},
        'currency_info': {'currency_rate': 1.0},
        'suggest_version': 2,
        'metric': 'extra_trips',
    }

    # Calc discounts for suggest
    response = await web_app_client.post(
        '/v2/suggests/calc_discounts/',
        json={
            'max_absolute_value': 599,
            'suggest_id': suggest_id,
            'budget': 1000000,
            'all_fixed_discounts': [
                {
                    'algorithm_id': 'kt',
                    'fixed_discounts': [
                        {'discount_value': 0, 'segment': 'control'},
                    ],
                },
            ],
        },
    )

    assert response.status == 200
    content = await response.json()
    assert len(content['multidraft_params']['charts']) == 8

    # Publish suggest
    @patch('uuid.uuid4')
    def _uuid2():
        return uuid.UUID(int=142, version=4)

    task_id = uuid.uuid4().hex

    response = await web_app_client.post(
        '/v2/suggests/publish',
        headers={'X-Yandex-Login': 'test_user'},
        params={
            'suggest_id': suggest_id,
            'date_to': '2020-10-10T15:54:32.123456Z',
            'date_from': '2020-10-01T16:54:32Z',
        },
    )

    assert response.status == http.HTTPStatus.OK
    content = await response.json()
    assert content == {'task_id': task_id}

    # Run task
    await multidraft.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=task_id, exec_tries=0, reschedule_counter=0, queue='',
        ),
    )

    # Check result
    status_check = await web_app_client.get(
        f'/v1/multidraft/tasks/{task_id}/status/',
    )
    assert status_check.status == http.HTTPStatus.OK
    content = await status_check.json()
    assert content['status'] == 'COMPLETED'

    response = await web_app_client.get(
        f'/v1/multidraft/tasks/{task_id}/result/',
    )
    assert response.status == http.HTTPStatus.OK
    content = await response.json()
    assert content == {'multidraft': 'test_url/multidraft/142/?multi=true'}


@pytest.mark.parametrize(
    'expected_create_draft_request_path',
    ['expected_create_draft_request_ab.json'],
)
@pytest.mark.now(DATETIME_STR)
@pytest.mark.pgsql('discounts_operation_calculations', files=SQL_FILES)
@pytest.mark.config(**CONFIGS)
async def test_flow_v2_ab(
        expected_create_draft_request_path,
        calc_segment_stats_mock,
        pgsql,
        web_app_client,
        mock_other_services,
        patch,
        stq3_context,
):
    @patch('uuid.uuid4')
    def _uuid():
        return uuid.UUID(int=42, version=4)

    task_id = uuid.uuid4().hex

    response = await web_app_client.post(
        '/v2/statistics/calc_segment_stats',
        headers={'X-Yandex-Login': 'test_user'},
        json={
            'common_params': {
                'discounts_city': 'test_city',
                'companies': ['tuda-suda'],
                'tariffs': ['econom', 'business'],
                'payment_methods': ['card', 'bitkoin', 'cash'],
                'min_discount': 0,
                'max_discount': 30,
            },
            'custom_params': [
                {'algorithm_id': 'kt', 'max_surge': 1.31, 'with_push': False},
                {
                    'algorithm_id': 'kt1',
                    'max_surge': 1.32,
                    'with_push': True,
                    'fallback_discount': 6,
                },
            ],
        },
    )
    assert response.status == 200
    content = await response.json()
    suggest_id = content['suggest_id']

    response = await web_app_client.get(
        f'/v2/suggests/{suggest_id}/detailed_info',
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'all_fixed_discounts': [],
        'calc_discounts_params': {
            'all_fixed_discounts': [
                {'algorithm_id': 'kt', 'fixed_discounts': []},
                {'algorithm_id': 'kt1', 'fixed_discounts': []},
            ],
            'suggest_id': 1,
        },
        'calc_statistics_params': {
            'common_params': {
                'companies': ['tuda-suda'],
                'discounts_city': 'test_city',
                'max_discount': 30,
                'min_discount': 0,
                'tariffs': ['econom', 'business'],
                'payment_methods': ['card', 'bitkoin', 'cash'],
            },
            'custom_params': [
                {'algorithm_id': 'kt', 'max_surge': 1.31, 'with_push': False},
                {
                    'algorithm_id': 'kt1',
                    'max_surge': 1.32,
                    'with_push': True,
                    'fallback_discount': 6,
                },
            ],
        },
        'segments': [],
        'status_info': {'status': 'CALC_SEGMENT_STATS'},
        'currency_info': {},
        'suggest_version': 2,
        'metric': 'extra_trips',
    }

    # Run task
    await calc_segment_stats.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=task_id, exec_tries=0, reschedule_counter=0, queue='',
        ),
    )

    # Check results after segments calculation
    response = await web_app_client.get(
        f'/v2/suggests/{suggest_id}/detailed_info',
    )

    assert response.status == 200
    content = await response.json()
    assert len(content['statistics']) == 6
    del content['statistics']  # this field tested in test_restrieve_statistics
    assert content == {
        'all_fixed_discounts': [
            {
                'algorithm_id': 'kt',
                'fixed_discounts': [
                    {'discount_value': 12, 'segment': 'random'},
                    {'discount_value': 0, 'segment': 'control'},
                ],
            },
            {
                'algorithm_id': 'kt1',
                'fixed_discounts': [
                    {'discount_value': 12, 'segment': 'random'},
                    {'discount_value': 0, 'segment': 'control'},
                ],
            },
        ],
        'calc_discounts_params': {
            'all_fixed_discounts': [
                {'algorithm_id': 'kt', 'fixed_discounts': []},
                {'algorithm_id': 'kt1', 'fixed_discounts': []},
            ],
            'suggest_id': 1,
        },
        'calc_statistics_params': {
            'common_params': {
                'companies': ['tuda-suda'],
                'discounts_city': 'test_city',
                'max_discount': 30,
                'min_discount': 0,
                'tariffs': ['econom', 'business'],
                'payment_methods': ['card', 'bitkoin', 'cash'],
            },
            'custom_params': [
                {'algorithm_id': 'kt', 'max_surge': 1.31, 'with_push': False},
                {
                    'algorithm_id': 'kt1',
                    'max_surge': 1.32,
                    'with_push': True,
                    'fallback_discount': 6,
                },
            ],
        },
        'segments': [
            {
                'algorithm_id': 'kt',
                'segment_names': [
                    'control',
                    'metrika_active_Hconv',
                    'metrika_active_Lconv',
                    'metrika_active_Mconv',
                    'metrika_notactive_Hconv',
                    'metrika_notactive_Lconv',
                    'metrika_notactive_Mconv',
                    'random',
                ],
            },
            {
                'algorithm_id': 'kt1',
                'segment_names': [
                    'control',
                    'metrika_active_Hconv',
                    'metrika_active_Lconv',
                    'metrika_active_Mconv',
                    'metrika_notactive_Hconv',
                    'metrika_notactive_Lconv',
                    'metrika_notactive_Mconv',
                    'random',
                ],
            },
        ],
        'status_info': {'status': 'NOT_PUBLISHED'},
        'currency_info': {'currency_rate': 1.0},
        'suggest_version': 2,
        'metric': 'extra_trips',
    }

    # Calc discounts for suggest
    response = await web_app_client.post(
        '/v2/suggests/calc_discounts/',
        json={
            'max_absolute_value': 599,
            'suggest_id': suggest_id,
            'budget': 1000000,
            'all_fixed_discounts': [
                {
                    'algorithm_id': 'kt',
                    'fixed_discounts': [
                        {'discount_value': 0, 'segment': 'control'},
                    ],
                },
            ],
        },
    )

    assert response.status == 200
    content = await response.json()

    assert len(content['multidraft_params']['charts']) == 8

    # Publish suggest
    @patch('uuid.uuid4')
    def _uuid2():
        return uuid.UUID(int=142, version=4)

    task_id = uuid.uuid4().hex

    response = await web_app_client.post(
        '/v2/suggests/publish',
        headers={'X-Yandex-Login': 'test_user'},
        params={
            'suggest_id': suggest_id,
            'date_to': '2020-10-10T15:54:32.123456Z',
            'date_from': '2020-10-01T16:54:32Z',
        },
    )

    assert response.status == http.HTTPStatus.OK
    content = await response.json()
    assert content == {'task_id': task_id}

    # Run task
    await multidraft.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=task_id, exec_tries=0, reschedule_counter=0, queue='',
        ),
    )

    # Check result
    status_check = await web_app_client.get(
        f'/v1/multidraft/tasks/{task_id}/status/',
    )
    assert status_check.status == http.HTTPStatus.OK
    content = await status_check.json()
    assert content['status'] == 'COMPLETED'

    response = await web_app_client.get(
        f'/v1/multidraft/tasks/{task_id}/result/',
    )
    assert response.status == http.HTTPStatus.OK
    content = await response.json()
    assert content == {'multidraft': 'test_url/multidraft/142/?multi=true'}

    # check logger_data
    get_segment_stats_hist_query = """SELECT
            algorithm_id,
            segment,
            price_from,
            discount,
            price_to,
            trips,
            extra_trips,
            gmv,
            new_gmv,
            discount,
            city,
            metric,
            weekly_budget,
            is_uploaded_to_yt,
            date_from,
            date_to,
            actions
         FROM discounts_operation_calculations.segment_stats_all_hist
         order by algorithm_id, segment, price_from, discount"""
    cursor = pgsql['discounts_operation_calculations'].cursor()
    cursor.execute(get_segment_stats_hist_query)
    segment_stats_hist = list(cursor)
    cursor.close()

    assert len(segment_stats_hist) == 88
    assert segment_stats_hist[0:3] == [
        (
            'kt',
            'control',
            pytest.approx(50),
            pytest.approx(0.0),
            pytest.approx(75),
            pytest.approx(1099.0),
            pytest.approx(0.0),
            pytest.approx(359975.0),
            pytest.approx(1799875.0),
            pytest.approx(0.0),
            'test_city',
            pytest.approx(0.0),
            pytest.approx(0.0),
            False,
            '2020-10-01T16:54:32.000000Z',
            '2020-10-10T15:54:32.123456Z',
            [],
        ),
        (
            'kt',
            'control',
            pytest.approx(100),
            pytest.approx(0.0),
            pytest.approx(125),
            pytest.approx(3257.5),
            pytest.approx(0.0),
            pytest.approx(2227482.5),
            pytest.approx(11137412.5),
            pytest.approx(0.0),
            'test_city',
            pytest.approx(0.0),
            pytest.approx(0.0),
            False,
            '2020-10-01T16:54:32.000000Z',
            '2020-10-10T15:54:32.123456Z',
            [],
        ),
        (
            'kt',
            'control',
            pytest.approx(150),
            pytest.approx(0.0),
            pytest.approx(175),
            pytest.approx(2321.5),
            pytest.approx(0.0),
            pytest.approx(4214647.5),
            pytest.approx(21073237.5),
            pytest.approx(0.0),
            'test_city',
            pytest.approx(0.0),
            pytest.approx(0.0),
            False,
            '2020-10-01T16:54:32.000000Z',
            '2020-10-10T15:54:32.123456Z',
            [],
        ),
    ]


@pytest.mark.parametrize(
    'expected_create_draft_request_path',
    ['expected_create_draft_request.json'],
)
@pytest.mark.now(DATETIME_STR)
@pytest.mark.pgsql('discounts_operation_calculations', files=SQL_FILES)
@pytest.mark.config(**CONFIGS)
async def test_flow_v2_with_returns(
        expected_create_draft_request_path,
        calc_segment_stats_mock,
        pgsql,
        web_app_client,
        mock_other_services,
        patch,
        stq3_context,
):
    @patch('uuid.uuid4')
    def _uuid():
        return uuid.UUID(int=42, version=4)

    task_id = uuid.uuid4().hex

    response = await web_app_client.post(
        '/v2/statistics/calc_segment_stats',
        headers={'X-Yandex-Login': 'test_user'},
        json={
            'common_params': {
                'discounts_city': 'test_city',
                'companies': ['tuda-suda'],
                'payment_methods': ['card', 'bitkoin', 'cash'],
                'tariffs': ['econom', 'business'],
                'min_discount': 6,
                'max_discount': 30,
            },
            'custom_params': [
                {'algorithm_id': 'kt', 'max_surge': 1.31, 'with_push': False},
            ],
        },
    )
    assert response.status == 200
    content = await response.json()
    suggest_id = content['suggest_id']

    # Run task
    await calc_segment_stats.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=task_id, exec_tries=0, reschedule_counter=0, queue='',
        ),
    )

    # Check results after segments calculation
    response = await web_app_client.get(
        f'/v2/suggests/{suggest_id}/detailed_info',
    )

    assert response.status == 200
    content = await response.json()
    assert len(content['statistics']) == 3
    del content['statistics']  # this field tested in test_retrieve_statistics
    assert content == {
        'all_fixed_discounts': [
            {
                'algorithm_id': 'kt',
                'fixed_discounts': [
                    {'discount_value': 12, 'segment': 'random'},
                    {'discount_value': 0, 'segment': 'control'},
                ],
            },
        ],
        'calc_discounts_params': {
            'all_fixed_discounts': [
                {'algorithm_id': 'kt', 'fixed_discounts': []},
            ],
            'suggest_id': 1,
        },
        'calc_statistics_params': {
            'common_params': {
                'companies': ['tuda-suda'],
                'discounts_city': 'test_city',
                'max_discount': 30,
                'min_discount': 6,
                'tariffs': ['econom', 'business'],
                'payment_methods': ['card', 'bitkoin', 'cash'],
            },
            'custom_params': [
                {'algorithm_id': 'kt', 'max_surge': 1.31, 'with_push': False},
            ],
        },
        'segments': [
            {
                'algorithm_id': 'kt',
                'segment_names': [
                    'control',
                    'metrika_active_Hconv',
                    'metrika_active_Lconv',
                    'metrika_active_Mconv',
                    'metrika_notactive_Hconv',
                    'metrika_notactive_Lconv',
                    'metrika_notactive_Mconv',
                    'random',
                ],
            },
        ],
        'status_info': {'status': 'NOT_PUBLISHED'},
        'currency_info': {'currency_rate': 1.0},
        'suggest_version': 2,
        'metric': 'extra_trips',
    }

    # Recalc budget statistics
    response = await web_app_client.post(
        '/v2/statistics/calc_budget_statistics',
        json={
            'suggest_id': suggest_id,
            'all_fixed_discounts': [
                {
                    'algorithm_id': 'kt',
                    'fixed_discounts': [
                        {'discount_value': 0, 'segment': 'control'},
                        {'discount_value': 9, 'segment': 'random'},
                    ],
                },
            ],
        },
    )

    assert response.status == 200
    content = await response.json()
    assert len(content['charts']) == 3

    # Check changed fixed_discounts
    response = await web_app_client.get(
        f'/v2/suggests/{suggest_id}/detailed_info',
    )

    assert response.status == 200
    content = await response.json()
    assert content['all_fixed_discounts'] == [
        {
            'algorithm_id': 'kt',
            'fixed_discounts': [
                {'discount_value': 0, 'segment': 'control'},
                {'discount_value': 9, 'segment': 'random'},
            ],
        },
    ]

    # Calc discounts for suggest
    response = await web_app_client.post(
        '/v2/suggests/v2/calc_discounts/',
        json={
            'max_absolute_value': 599,
            'suggest_id': suggest_id,
            'budget': 50000000,
        },
    )

    assert response.status == 200
    content = await response.json()

    assert len(content['multidraft_params']['charts']) == 3

    # Recalc discounts for suggest
    response = await web_app_client.post(
        '/v2/suggests/v2/calc_discounts/',
        json={
            'max_absolute_value': 599,
            'suggest_id': suggest_id,
            'budget': 500000000,
        },
    )
    assert response.status == 200
    prev_content = content
    content = await response.json()

    # result should be changed
    assert content != prev_content

    # Recalc budget statistics again
    response = await web_app_client.post(
        '/v2/statistics/calc_budget_statistics',
        json={
            'suggest_id': suggest_id,
            'all_fixed_discounts': [
                {
                    'algorithm_id': 'kt',
                    'fixed_discounts': [
                        {'discount_value': 0, 'segment': 'control'},
                        {'discount_value': 12, 'segment': 'random'},
                    ],
                },
            ],
        },
    )

    assert response.status == 200
    content = await response.json()
    assert len(content['charts']) == 3

    # Check that all next calculations was erased
    response = await web_app_client.get(
        f'/v2/suggests/{suggest_id}/detailed_info',
    )

    assert response.status == 200
    content = await response.json()

    assert len(content['statistics']) == 3
    del content['statistics']  # this field already checked

    assert content == {
        'calc_statistics_params': {
            'common_params': {
                'discounts_city': 'test_city',
                'companies': ['tuda-suda'],
                'tariffs': ['econom', 'business'],
                'min_discount': 6,
                'max_discount': 30,
                'payment_methods': ['card', 'bitkoin', 'cash'],
            },
            'custom_params': [
                {'algorithm_id': 'kt', 'max_surge': 1.31, 'with_push': False},
            ],
        },
        'status_info': {'status': 'NOT_PUBLISHED'},
        'suggest_version': 2,
        'segments': [
            {
                'algorithm_id': 'kt',
                'segment_names': [
                    'control',
                    'metrika_active_Hconv',
                    'metrika_active_Lconv',
                    'metrika_active_Mconv',
                    'metrika_notactive_Hconv',
                    'metrika_notactive_Lconv',
                    'metrika_notactive_Mconv',
                    'random',
                ],
            },
        ],
        'calc_discounts_params': {
            'suggest_id': 1,
            'all_fixed_discounts': [
                {'algorithm_id': 'kt', 'fixed_discounts': []},
            ],
        },
        'all_fixed_discounts': [
            {
                'algorithm_id': 'kt',
                'fixed_discounts': [
                    {'segment': 'control', 'discount_value': 0},
                    {'segment': 'random', 'discount_value': 12},
                ],
            },
        ],
        'currency_info': {'currency_rate': 1.0},
        'metric': 'extra_trips',
    }

    # Calc discounts for suggest
    response = await web_app_client.post(
        '/v2/suggests/v2/calc_discounts/',
        json={
            'max_absolute_value': 599,
            'suggest_id': suggest_id,
            'budget': 50000000,
        },
    )

    assert response.status == 200
    content = await response.json()

    assert len(content['multidraft_params']['charts']) == 3

    # Check final detailed info
    response = await web_app_client.get(
        f'/v2/suggests/{suggest_id}/detailed_info',
    )

    assert response.status == 200
