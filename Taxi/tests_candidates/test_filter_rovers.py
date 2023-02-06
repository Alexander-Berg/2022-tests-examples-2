import pytest

_DEFAULT_ROUTER_SELECT = [
    {'routers': ['yamaps']},
    {'ids': ['moscow'], 'routers': ['linear-fallback']},
]


@pytest.fixture(autouse=True)
def mock_retrieve_by_contractor_id(mockserver):
    @mockserver.json_handler(
        '/contractor-transport/v1/transport-active/retrieve-by-contractor-id',
    )
    def _mock_retrieve_by_contractor_id(request):
        return {
            'contractors_transport': [
                {
                    'contractor_id': 'dbid0_uuid1',
                    'is_deleted': False,
                    'revision': '1234567_2',
                    'transport_active': {'type': 'rover'},
                },
            ],
        }


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT, EXTRA_EXAMS_BY_ZONE={},
)
@pytest.mark.parametrize(
    'logistic, expected_drivers',
    [
        (None, []),
        ({'include_rovers': False}, []),
        ({'include_rovers': True}, ['dbid0_uuid1']),
    ],
)
async def test_include_rovers(
        taxi_candidates,
        driver_positions,
        logistic: dict,
        expected_drivers: list,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid1_uuid2', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.630971, 55.743789]},
        ],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 10,
        'point': [37.630971, 55.743789],
    }
    if logistic:
        request_body['logistic'] = logistic

    response = await taxi_candidates.post('order-search', json=request_body)
    assert response.status_code == 200, response.text

    candidates = response.json()['candidates']
    candidates_list = [candidate['id'] for candidate in candidates]
    assert candidates_list == expected_drivers


@pytest.fixture(autouse=True)
def eats_shifts_journal(mockserver):
    @mockserver.json_handler(
        '/eats-performer-shifts/internal/eats-performer-shifts/v1/courier-shift-states/updates',  # noqa: E501
    )
    def _eats_shifts_journal(request):
        if not request.args['cursor']:
            return {
                'data': {
                    'shifts': [
                        {
                            'courier_id': 'dbid0_uuid1',
                            'eats_courier_id': '10',
                            'shift_id': '19950',
                            'zone_id': '6341',
                            'zone_group_id': None,
                            'meta_group_id': '67890',
                            'status': 'in_progress',
                            'started_at': '2020-07-28T08:47:00Z',
                            'closes_at': '2020-07-28T09:07:12Z',
                            'paused_at': None,
                            'unpauses_at': None,
                            'updated_ts': '2020-07-28T09:07:12Z',
                            'is_high_priority': True,
                        },
                    ],
                    'cursor': '1',
                },
            }
        return {'data': {'shifts': [], 'cursor': '1'}}


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT, EXTRA_EXAMS_BY_ZONE={},
)
@pytest.mark.now('2020-07-28T08:48:00+00:00')
async def test_delivery_include_rovers(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid1_uuid2', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.630971, 55.743789]},
        ],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 10,
        'point': [37.630971, 55.743789],
        'order': {'request': {'delivery': {'include_rovers': True}}},
    }

    response = await taxi_candidates.post('order-search', json=request_body)
    assert response.status_code == 200, response.text

    candidates = response.json()['candidates']
    candidates_list = [candidate['id'] for candidate in candidates]
    assert candidates_list == ['dbid0_uuid1']
