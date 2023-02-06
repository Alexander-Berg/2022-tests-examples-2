# pylint: disable=len-as-condition
import datetime

import pytest


@pytest.fixture(autouse=True)
def mock_all(mockserver, load_binary, load_json):
    @mockserver.json_handler('/candidates/searchable')
    def _mock_candidates(request):
        return load_json('mock_candidates.json')

    @mockserver.handler('/driver-trackstory/v2/shorttracks')
    def _mock_trackstory(request):
        # use flatc if need
        # flatc -b --force-defaults schemas/fbs/driver-trackstory/handlers/shorttracks_extended_response.fbs  services/driver-map/testsuite/tests_driver_map/static/test_nearestdrivers_shorttracks_fbs/mock_trackstory_fbs.json # noqa: E501
        return mockserver.make_response(
            response=load_binary('mock_trackstory_fbs.bin'),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )


@pytest.mark.parametrize(
    'request_body,response_code',
    [
        ({}, 400),
        ({'point': [55, 35]}, 400),
        ({'point': [55, 35], 'classes': ['econom']}, 400),
        (
            {
                'point': [55, 35],
                'classes': ['econom'],
                'current_drivers': ['id1'],
            },
            200,
        ),
        (
            {
                'point': [55, 35],
                'classes': ['econom'],
                'current_drivers': ['id1'],
                'simplify': True,
            },
            200,
        ),
        (
            {'point': [55, 35], 'classes': ['econom'], 'current_drivers': []},
            200,
        ),
        ({'point': [55, 35], 'classes': [], 'current_drivers': []}, 400),
        ({'point': [0, 0], 'classes': ['econom'], 'current_drivers': []}, 400),
    ],
)
async def test_response_code(taxi_driver_map, request_body, response_code):
    response = await taxi_driver_map.post('nearestdrivers', json=request_body)
    assert response.status_code == response_code


async def test_response_code_404(taxi_driver_map, mockserver):
    @mockserver.json_handler('/candidates/searchable')
    def _mock_candidates(request):
        return mockserver.make_response(
            '{}', 404, content_type='application/json',
        )

    response = await taxi_driver_map.post(
        'nearestdrivers',
        {'point': [55, 35], 'classes': ['econom'], 'current_drivers': []},
    )
    assert response.status_code == 200
    assert response.json() == {'drivers': []}


async def test_nearest(taxi_driver_map, load_json):
    request = load_json('request1.json')
    answer = load_json('answer1.json')
    headers = {'X-Yandex-UID': '1234', 'X-YaTaxi-UserId': 'testsuite'}
    response = await taxi_driver_map.post(
        'nearestdrivers', json=request, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == answer

    request['current_drivers'].append(answer['drivers'][1]['id'])
    request['current_drivers'].append(answer['drivers'][2]['id'])
    new_answer = {}
    new_answer['drivers'] = []
    new_answer['drivers'].append(answer['drivers'][1])
    new_answer['drivers'].append(answer['drivers'][2])
    new_answer['drivers'].append(answer['drivers'][0])

    response = await taxi_driver_map.post(
        'nearestdrivers', json=request, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == new_answer


@pytest.mark.config(SHOW_MAX_ALLOWED_CLASS=True)
@pytest.mark.experiments3(
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='display_classes_experiment',
    consumers=['driver-map/nearestdrivers'],
    clauses=[],
    default_value={'econom': ['cargo']},
)
async def test_display_classes_experiment(
        taxi_driver_map, load_json, mockserver,
):
    request = load_json('request1.json')
    answer = load_json('answer1.json')
    headers = {'X-Yandex-UID': '1234', 'X-YaTaxi-UserId': 'testsuite'}

    @mockserver.json_handler('/candidates/searchable')
    def _mock_candidates(request):
        assert request.json['allowed_classes'] == ['cargo', 'econom']
        return load_json('mock_candidates.json')

    response = await taxi_driver_map.post(
        'nearestdrivers', json=request, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == answer


@pytest.mark.config(NEAREST_DRIVERS_REPLACE_DISPLAY_CLASSES=['econom'])
async def test_replace_display_classes(taxi_driver_map, load_json):
    request = load_json('request1.json')
    headers = {'X-Yandex-UID': '1234', 'X-YaTaxi-UserId': 'testsuite'}

    response = await taxi_driver_map.post(
        'nearestdrivers', json=request, headers=headers,
    )
    assert response.status_code == 200
    for driver in response.json()['drivers']:
        assert driver['display_tariff'] == 'econom', driver['id']


@pytest.mark.parametrize(
    'expected_static, expected_non_static',
    [
        pytest.param(
            ['2509cddd17575dcba28707624b515074'],
            ['f6160fb7cb83b7a1aa5f39a4c73d4540'],
            marks=[
                pytest.mark.config(TAXIROUTE_STATIC_ICON_CLASSES=['business']),
            ],
            id='static_icon_business',
        ),
        pytest.param(
            [],
            [
                '2509cddd17575dcba28707624b515074',
                'f6160fb7cb83b7a1aa5f39a4c73d4540',
            ],
            marks=[pytest.mark.config(TAXIROUTE_STATIC_ICON_CLASSES=[])],
            id='static_icon_none',
        ),
    ],
)
async def test_static_icon_classes(
        taxi_driver_map, load_json, expected_static, expected_non_static,
):
    request = load_json('request1.json')
    response = await taxi_driver_map.post('nearestdrivers', json=request)
    assert response.status_code == 200
    response_json = response.json()
    for driver in response_json['drivers']:
        directions = [x['direction'] for x in driver['positions']]
        if driver['id'] in expected_static:
            assert all(d == 0 for d in directions), driver['id']
        elif driver['id'] in expected_non_static:
            assert any(d != 0 for d in directions), driver['id']


# Generated via `tvmknife unittest service -s 444 -d 111`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUIvAMQbw:WPKzP90'
    '8f_Y5-7PxLhkZEx1cC5i4kdTYbv4eO1h_0tDX1d1u'
    'P8Og7N_Nl1RWyGsl_Dwk3ceh581YfoyCy0iJfW-Iv'
    'zRFi8cm4R8B8bQRq-Cuu15W1z0IGwp0Gg58UNeJ8f'
    'Go-kdaqCB2RpPcthDoqA-a9Sk-Qy_Cih0jW02ueII'
)

# Generated via `tvmknife unittest service -s 111 -d 111`
DRIVER_MAP_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgQIbxBv:HnWBiEb0q'
    'TecqNtfSO2O8gdh0MrHRl-bPGm47DFcjRqnK6l7Dp'
    '85VtHrO0lair9AUnsbAqQ6OLdaM7sp4qVG43A_1Kz'
    'c6GeO7X6LWWeQGKIMQVOPQyVBMcfvf1SQcx-YmGnp'
    'U6CsLiWR3YOSc6cPn1Sq7XXCiMVH1sCuMNov_zQ'
)


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[
        {'src': 'mock', 'dst': 'driver-map'},
        {'src': 'driver-map', 'dst': 'candidates'},
    ],
)
@pytest.mark.tvm2_ticket(
    {444: MOCK_SERVICE_TICKET, 111: DRIVER_MAP_SERVICE_TICKET},
)
async def test_tvm(taxi_driver_map, load_json):
    response = await taxi_driver_map.post(
        'nearestdrivers',
        json=load_json('request1.json'),
        headers={'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET},
    )
    assert response.status_code == 200
    assert response.json() == load_json('answer1.json')
    response = await taxi_driver_map.post(
        'nearestdrivers', json=load_json('request1.json'),
    )
    assert response.status_code == 401


@pytest.mark.config(NEAREST_DRIVERS_USE_SPORADIC_ID=True)
async def test_hash_driver(taxi_driver_map, load_json, mocked_time):
    request = load_json('request1.json')

    mocked_time.set(datetime.datetime(2019, 1, 1, 10, 00, 00))
    response = await taxi_driver_map.post('nearestdrivers', json=request)
    assert response.status_code == 200
    json = response.json()

    mocked_time.set(datetime.datetime(2019, 1, 1, 10, 3, 1))
    await taxi_driver_map.tests_control(invalidate_caches=False)
    response = await taxi_driver_map.post('nearestdrivers', json=request)
    assert response.status_code == 200
    matching_drivers = [
        index
        for (index, driver) in enumerate(response.json()['drivers'])
        if json['drivers'][index]['id'] == driver['id']
    ]
    assert 0 < len(matching_drivers) < 3

    mocked_time.set(datetime.datetime(2019, 1, 1, 10, 10, 1))
    await taxi_driver_map.tests_control(invalidate_caches=False)
    response = await taxi_driver_map.post('nearestdrivers', json=request)
    assert response.status_code == 200
    matching_drivers = [
        index
        for (index, driver) in enumerate(response.json()['drivers'])
        if json['drivers'][index]['id'] == driver['id']
    ]
    assert not matching_drivers


async def test_fallback_candidates(
        taxi_driver_map, statistics, mockserver, load_json,
):
    @mockserver.json_handler('/candidates/searchable')
    def _mock_candidates(request):
        return mockserver.make_response('', status=500)

    statistics.fallbacks = ['driver-map.candidates']
    await taxi_driver_map.invalidate_caches()

    request = load_json('request1.json')
    async with statistics.capture(taxi_driver_map) as capture:
        response = await taxi_driver_map.post('nearestdrivers', json=request)

    assert response.status_code == 200
    assert capture.statistics['driver-map.candidates.error'] == 1
    assert 'driver-map.candidates.success' not in capture.statistics


async def test_fallback_trackstory(
        taxi_driver_map, statistics, mockserver, load_json,
):
    @mockserver.json_handler('/candidates/searchable')
    def _mock_candidates(request):
        return load_json('mock_candidates.json')

    @mockserver.handler('/driver-trackstory/v2/shorttracks')
    def _mock_trackstory(request):
        return mockserver.make_response('', status=500)

    statistics.fallbacks = ['driver-map.trackstory']
    await taxi_driver_map.invalidate_caches()

    request = load_json('request1.json')
    async with statistics.capture(taxi_driver_map) as capture:
        response = await taxi_driver_map.post('nearestdrivers', json=request)

    assert response.status_code == 200
    assert capture.statistics['driver-map.trackstory.error'] == 1
    assert capture.statistics['driver-map.candidates.success'] == 1
    assert 'driver-map.trackstory.success' not in capture.statistics
    assert 'driver-map.candidates.error' not in capture.statistics


async def test_statistics_update_candidates(
        taxi_driver_map, statistics, mockserver, load_json,
):
    @mockserver.json_handler('/candidates/searchable')
    def _mock_candidates(request):
        return mockserver.make_response('', status=500)

    request = load_json('request1.json')
    async with statistics.capture(taxi_driver_map) as capture:
        response = await taxi_driver_map.post('nearestdrivers', json=request)

    assert response.status_code == 500
    assert capture.statistics['driver-map.candidates.error'] == 1


async def test_statistics_update_trackstory(
        taxi_driver_map, statistics, mockserver, load_json,
):
    @mockserver.json_handler('/candidates/searchable')
    def _mock_candidates(request):
        return load_json('mock_candidates.json')

    @mockserver.handler('/driver-trackstory/v2/shorttracks')
    def _mock_trackstory(request):
        return mockserver.make_response('', status=500)

    request = load_json('request1.json')
    async with statistics.capture(taxi_driver_map) as capture:
        response = await taxi_driver_map.post('nearestdrivers', json=request)

    assert response.status_code == 500
    assert capture.statistics['driver-map.trackstory.error'] == 1
