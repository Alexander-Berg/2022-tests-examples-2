from aiohttp import web
import pytest


CALLS_HISTORY_URL = '/cc/v1/callcenter-stats/v2/calls/history'
CALLCENTER_STATS_DB_TIMEOUTS = {
    'admin_timeouts': {'network_timeout': 1200, 'statement_timeout': 1000},
    'calls_history': {'network_timeout': 1200, 'statement_timeout': 1000},
    'default': {'network_timeout': 1200, 'statement_timeout': 1000},
}


@pytest.mark.now('2019-09-03 11:00:00.00')
@pytest.mark.config(
    CALLCENTER_STATS_CALLS_LIST_LIMIT=100,
    CALLCENTER_STATS_DB_TIMEOUTS=CALLCENTER_STATS_DB_TIMEOUTS,
)
@pytest.mark.pgsql('callcenter_stats', files=['callcenter_calls_history.sql'])
@pytest.mark.parametrize(
    'request_body, expected_status, expected_data',
    (
        ('body_1.json', 200, 'expected_data_1.json'),
        ('body_2.json', 200, 'expected_data_2.json'),
        ('body_3.json', 400, '400-operator_not_in_db.json'),
        ('body_4.json', 200, 'empty_expected_data.json'),
        ('body_5.json', 400, '400-operator_no_agent_id.json'),
    ),
)
async def test_calls_history(
        taxi_callcenter_stats,
        request_body,
        load_json,
        mock_personal,
        expected_status,
        expected_data,
):
    response = await taxi_callcenter_stats.post(
        CALLS_HISTORY_URL, json=load_json(request_body),
    )
    assert response.status_code == expected_status
    assert response.json() == load_json(expected_data)


@pytest.mark.now('2019-09-03 11:00:00.00')
@pytest.mark.config(
    CALLCENTER_STATS_CALLS_LIST_LIMIT=1,
    CALLCENTER_STATS_DB_TIMEOUTS=CALLCENTER_STATS_DB_TIMEOUTS,
)
@pytest.mark.pgsql('callcenter_stats', files=['callcenter_calls_history.sql'])
async def test_calls_history_limit(
        taxi_callcenter_stats, load_json, mock_personal,
):
    response = await taxi_callcenter_stats.post(
        CALLS_HISTORY_URL, json=load_json('body_1.json'),
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['calls']) == 1
    assert data['calls'][0] == load_json('expected_data_1.json')['calls'][0]


@pytest.mark.now('2019-09-03 11:00:00.00')
@pytest.mark.config(
    CALLCENTER_STATS_CALLS_LIST_LIMIT=100,
    CALLCENTER_STATS_DB_TIMEOUTS=CALLCENTER_STATS_DB_TIMEOUTS,
)
@pytest.mark.pgsql('callcenter_stats', files=['callcenter_calls_history.sql'])
@pytest.mark.parametrize(
    'request_body, expected_data',
    (
        ('body_with_filter_1.json', 'expected_data_with_filter_1.json'),
        ('body_with_filter_2.json', 'expected_data_with_filter_2.json'),
        ('body_with_filter_3.json', 'expected_data_with_filter_3.json'),
        ('body_with_filter_4.json', 'expected_data_with_filter_4.json'),
        ('body_with_filter_5.json', 'expected_data_with_filter_5.json'),
        ('body_with_filter_6.json', 'expected_data_with_filter_6.json'),
        ('body_with_filter_7.json', 'expected_data_with_filter_7.json'),
        ('body_with_filter_9.json', 'expected_data_with_filter_9.json'),
        ('body_with_filter_10.json', 'expected_data_with_filter_10.json'),
        ('body_with_filter_11.json', 'expected_data_with_filter_11.json'),
    ),
)
async def test_calls_history_with_filter(
        taxi_callcenter_stats,
        request_body,
        load_json,
        mock_personal,
        expected_data,
):
    response = await taxi_callcenter_stats.post(
        CALLS_HISTORY_URL, json=load_json(request_body),
    )
    assert response.status_code == 200
    data = response.json()
    assert data == load_json(expected_data)


@pytest.mark.now('2019-09-03 11:00:00.00')
@pytest.mark.config(
    CALLCENTER_STATS_CALLS_LIST_LIMIT=100,
    CALLCENTER_STATS_DB_TIMEOUTS=CALLCENTER_STATS_DB_TIMEOUTS,
)
@pytest.mark.pgsql('callcenter_stats', files=['callcenter_calls_history.sql'])
@pytest.mark.parametrize(
    'allow_null_agent_id',
    (
        pytest.param(
            True,
            marks=pytest.mark.config(
                CALLCENTER_STATS_CALLS_HISTORY_ALLOW_NULL_AGENT_ID=True,
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                CALLCENTER_STATS_CALLS_HISTORY_ALLOW_NULL_AGENT_ID=False,
            ),
        ),
    ),
)
async def test_empty_login_filter(
        taxi_callcenter_stats,
        load_json,
        mock_personal,
        allow_null_agent_id,
        mockserver,
):
    response = await taxi_callcenter_stats.post(CALLS_HISTORY_URL, json={})
    assert response.status_code == 200
    data = response.json()
    assert data == load_json(
        'expected_empty_operator_filter_allow_null_agent_id.json'
        if allow_null_agent_id
        else 'expected_empty_operator_filter.json',
    )


@pytest.mark.now('2019-09-03 11:00:00.00')
@pytest.mark.pgsql('callcenter_stats', files=['callcenter_calls_history.sql'])
@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'metaqueues': ['help_cc'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
        'corp': {
            'metaqueues': ['corp_cc'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
        'god': {
            'metaqueues': ['help_cc', 'corp_cc'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
    },
)
@pytest.mark.parametrize(
    ['request_body', 'expected_status_code', 'expected_call_ids'],
    (
        pytest.param(
            {},
            200,
            [
                'id1',
                'id2',
                'id3',
                'id4',
                'id5',
                'id6',
                'id7',
                'id8',
                'id9',
                'id10',
                'id11',
            ],
            id='no project',
        ),
        pytest.param(
            {'project': 'god'},
            200,
            [
                'id1',
                'id2',
                'id3',
                'id4',
                'id5',
                'id6',
                'id7',
                'id8',
                'id9',
                'id10',
                'id11',
            ],
            id='god-mode project',
        ),
        pytest.param(
            {'project': 'corp'},
            200,
            ['id1', 'id2', 'id3', 'id10', 'id11'],
            id='corp project',
        ),
        pytest.param(
            {'project': 'disp'}, 500, None, id='non-existent project',
        ),
        pytest.param(
            {'metaqueue_filter': ['corp_cc', 'help_cc'], 'project': 'corp'},
            409,
            [],
            id='metaqueue not found in project',
        ),
    ),
)
async def test_project_filtering(
        taxi_callcenter_stats,
        mock_personal,
        request_body,
        expected_status_code,
        expected_call_ids,
):
    response = await taxi_callcenter_stats.post(
        CALLS_HISTORY_URL, json=request_body,
    )
    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        data = response.json()
        call_ids = {call['call_id'] for call in data['calls']}
        assert call_ids == set(expected_call_ids)


@pytest.mark.now('2019-09-03 11:00:00.00')
@pytest.mark.pgsql('callcenter_stats', files=['callcenter_calls_history.sql'])
@pytest.mark.config(
    CALLCENTER_STATS_CALLS_LIST_LIMIT=100,
    CALLCENTER_STATS_DB_TIMEOUTS=CALLCENTER_STATS_DB_TIMEOUTS,
)
@pytest.mark.parametrize(
    ['request_body', 'expected_call_ids'],
    (
        pytest.param(
            {'abonent_phone_number': 'abc89991111111abc'},
            ['id3', 'id5', 'id7', 'id8', 'id9', 'id10', 'id11'],
        ),
    ),
)
async def test_innormalize_abonent_phone(
        taxi_callcenter_stats, mockserver, request_body, expected_call_ids,
):
    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve', prefix=True)
    def _phones_bulk_retrieve(request):
        return web.Response(
            body='{"items":[{"id": "phone_id_1", "value": "+79991111111"}, '
            '{"id": "phone_id_1_extra", "value": "+79999999999"}, '
            '{"id": "phone_id_2", "value": "+79992222222"}, '
            '{"id": "phone_id_3", "value": "+79993333333"}, '
            '{"id": "phone_id_4", "value": "+79994444444"}]}',
        )

    @mockserver.json_handler('/personal/v1/phones/find')
    def phones_find(request):
        json_body = request.json
        phone = json_body['value']
        assert phone == '+79991111111'
        phone_id = 'phone_id_1'
        body = '{"id": "%s", "value": "%s"}' % (phone_id, phone)
        return web.Response(body=body)

    response = await taxi_callcenter_stats.post(
        CALLS_HISTORY_URL, json=request_body,
    )
    assert response.status_code == 200
    data = response.json()
    call_ids = {call['call_id'] for call in data['calls']}
    assert call_ids == set(expected_call_ids)
    assert phones_find.times_called


@pytest.mark.now('2019-09-03 11:00:00.00')
@pytest.mark.pgsql('callcenter_stats', files=['callcenter_calls_history.sql'])
@pytest.mark.config(
    CALLCENTER_STATS_CALLS_LIST_LIMIT=100,
    CALLCENTER_STATS_DB_TIMEOUTS=CALLCENTER_STATS_DB_TIMEOUTS,
)
@pytest.mark.parametrize(
    ['request_body', 'expected_call_ids'],
    (pytest.param({'abonent_phone_number': 'phone_id_2'}, {'id1'}),),
)
async def test_find_for_abonent_phone_id(
        taxi_callcenter_stats, mockserver, request_body, expected_call_ids,
):
    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve', prefix=True)
    def _phones_bulk_retrieve(request):
        return web.Response(
            body='{"items":[{"id": "phone_id_1", "value": "+79991111111"}, '
            '{"id": "phone_id_1_extra", "value": "+79999999999"}, '
            '{"id": "phone_id_2", "value": "+79992222222"}, '
            '{"id": "phone_id_3", "value": "+79993333333"}, '
            '{"id": "phone_id_4", "value": "+79994444444"}]}',
        )

    @mockserver.json_handler('/personal/v1/phones/find')
    def phones_find(request):
        return web.Response(status=404)

    response = await taxi_callcenter_stats.post(
        CALLS_HISTORY_URL, json=request_body,
    )
    assert response.status_code == 200
    data = response.json()
    call_ids = {call['call_id'] for call in data['calls']}
    assert call_ids == set(expected_call_ids)
    assert phones_find.times_called
