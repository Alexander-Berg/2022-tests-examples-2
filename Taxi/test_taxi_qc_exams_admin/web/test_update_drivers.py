from aiohttp import web
import pytest

from taxi import discovery

HEADERS = {'Content-Type': 'application/json'}


@pytest.mark.config(
    QC_EXAMS_ADMIN_UPDATE_DRIVERS_IGNORE_FIELDS=['city', 'country'],
)
@pytest.mark.parametrize('scenario', ['modified', 'unmodified', 'new'])
async def test_update_drivers(
        web_app_client,
        mock_quality_control_py3,
        patch_aiohttp_session,
        response_mock,
        scenario,
):
    @patch_aiohttp_session(discovery.find_service('taximeter_xservice').url)
    def patch_update_drivers(method, urql, json, **kwargs):
        old_data = dict(park_id='park', driver_id='driver')
        if scenario != 'new':
            old_data['car_id'] = 'old_car'

        new_data = dict(
            park_id='park',
            driver_id='driver',
            car_id='car',
            modified_date='2019-01-18T14:30:00Z',
        )
        assert json == dict(items=[dict(old_data=old_data, new_data=new_data)])
        return response_mock(
            json=dict(processed=[dict(park_id='park', driver_id='driver')]),
        )

    @mock_quality_control_py3('/api/v1/data/bulk_retrieve')
    def mock_bulk_retrieve(request):
        assert request.json == dict(items=['park_driver'])
        assert request.query == dict(type='driver')

        if scenario == 'new':
            return web.json_response(dict(items=[]))

        old_car = 'old_car' if scenario == 'modified' else 'car'
        return web.json_response(
            dict(
                items=[
                    dict(
                        id='park_driver',
                        type='driver',
                        data=dict(
                            park_id='park',
                            car_id=old_car,
                            city='Москва',
                            country='rus',
                        ),
                        modified='2019-04-20T12:00:00Z',
                    ),
                ],
            ),
        )

    @mock_quality_control_py3('/api/v1/data/list')
    def mock_data_list(request):
        assert request.method.lower() == 'post'
        assert request.query == dict(type='driver')

        return web.json_response({})

    @mock_quality_control_py3('/api/v1/state/bulk_retrieve')
    def mock_state_bulk_retrieve(request):
        assert request.method.lower() == 'post'
        return web.json_response(
            dict(
                items=[
                    dict(id=x, type=request.query['type'], exams=[])
                    for x in request.json['items']
                ],
            ),
        )

    data = dict(items=[dict(park_id='park', driver_id='driver')])
    response = await web_app_client.post(
        'v1/update/drivers', json=data, headers=HEADERS,
    )

    assert response.status == 200
    response_data = await response.json()

    items = response_data.pop(
        'unmodified' if scenario == 'unmodified' else 'modified', [],
    )

    assert response_data == dict()
    assert items == [dict(park_id='park', driver_id='driver')]

    if scenario == 'unmodified':
        assert not patch_update_drivers.calls
        assert mock_state_bulk_retrieve.times_called == 0
    else:
        assert patch_update_drivers.calls
        assert mock_state_bulk_retrieve.times_called == 1

    assert mock_bulk_retrieve.times_called == 1
    calls = []
    while mock_data_list.has_calls:
        calls.append(mock_data_list.next_call())

    if scenario == 'unmodified':
        assert not calls
        return

    if scenario == 'new':
        assert calls[0]['request'].json == [
            dict(type='driver', id='park_driver', data=dict(park_id='park')),
        ]
        calls = calls[1:]

    assert len(calls) == 1
    assert calls[0]['request'].json == [
        dict(
            type='driver',
            id='park_driver',
            data=dict(
                park_id='park', car_id='car', city='Москва', country='rus',
            ),
        ),
    ]


@pytest.mark.parametrize(
    'scenario',
    [
        'db_missed',
        'bulk_failed',
        'parks_failed',
        'state_bulk_failed',
        'update_failed',
        'update_status',
        'data_failed',
    ],
)
async def test_update_drivers_error(
        web_app_client,
        mock_quality_control_py3,
        mock_fleet_parks,
        patch_aiohttp_session,
        response_mock,
        scenario,
):
    @patch_aiohttp_session(discovery.find_service('taximeter_xservice').url)
    def patch_update_drivers(method, url, json, **kwargs):
        old_data = dict(park_id='park', driver_id='driver', car_id='old')
        new_data = dict(
            park_id='park',
            driver_id='driver',
            car_id='car',
            modified_date='2019-01-18T14:30:00Z',
            city='Москва',
            country='rus',
        )
        assert json == dict(items=[dict(old_data=old_data, new_data=new_data)])

        if scenario == 'update_status':
            return response_mock(status=500)
        if scenario == 'update_failed':
            return response_mock(
                json=dict(failed=[dict(park_id='park', driver_id='driver')]),
            )
        return response_mock(
            json=dict(processed=[dict(park_id='park', driver_id='driver')]),
        )

    @mock_fleet_parks('/v1/parks/list')
    def mock_parks_list(request):
        if scenario == 'parks_failed':
            return web.json_response(status=500)
        ids = request.json['query']['park']['ids']
        return web.json_response(
            dict(
                parks=[
                    dict(
                        id=x,
                        login=x + '_login',
                        name=x,
                        is_active=True,
                        city_id='Москва',
                        locale='ru',
                        is_billing_enabled=False,
                        is_franchising_enabled=False,
                        demo_mode=False,
                        country_id='rus',
                        geodata={'lat': 0, 'lon': 0, 'zoom': 0},
                    )
                    for x in ids
                ],
            ),
        )

    @mock_quality_control_py3('/api/v1/data/bulk_retrieve')
    def mock_bulk_retrieve(request):
        assert request.json == dict(items=['park_driver'])
        assert request.query == dict(type='driver')

        if scenario == 'bulk_failed':
            return web.json_response(status=500)
        return web.json_response(
            dict(
                items=[
                    dict(
                        id='park_driver',
                        type='driver',
                        data=dict(park_id='park', car_id='old'),
                        modified='2019-04-20T12:00:00Z',
                    ),
                ],
            ),
        )

    @mock_quality_control_py3('/api/v1/data/list')
    def mock_data_list(request):
        assert request.method.lower() == 'post'
        assert request.query == dict(type='driver')

        if scenario == 'data_failed':
            return web.json_response(status=500)
        return web.json_response(dict())

    @mock_quality_control_py3('/api/v1/state/bulk_retrieve')
    def mock_state_bulk_retrieve(request):
        assert request.method.lower() == 'post'
        if scenario == 'state_bulk_failed':
            return web.json_response(status=500)
        return web.json_response(
            dict(
                items=[
                    dict(id=x, type=request.query['type'], exams=[])
                    for x in request.json['items']
                ],
            ),
        )

    driver_id = 'driver' if scenario != 'db_missed' else 'missed_driver'
    data = dict(items=[dict(park_id='park', driver_id=driver_id)])
    response = await web_app_client.post(
        'v1/update/drivers', json=data, headers=HEADERS,
    )

    assert response.status == 200
    response_data = await response.json()

    items = response_data.pop('failed', [])

    assert response_data == dict()
    assert items == [dict(park_id='park', driver_id=driver_id)]

    if scenario in ['db_missed', 'bulk_failed', 'parks_failed']:
        assert not patch_update_drivers.calls
    else:
        assert len(patch_update_drivers.calls) == 1

    if scenario == 'db_missed':
        assert (
            mock_bulk_retrieve.times_called == 0
            and mock_parks_list.times_called == 0
            and mock_state_bulk_retrieve.times_called == 0
            and mock_data_list.times_called == 0
        )
    elif scenario in ['bulk_failed']:
        assert (
            mock_bulk_retrieve.times_called == 3
            and mock_parks_list.times_called == 1
            and mock_state_bulk_retrieve.times_called == 0
            and mock_data_list.times_called == 0
        )
    elif scenario in ['parks_failed']:
        assert (
            mock_bulk_retrieve.times_called == 1
            and mock_parks_list.times_called == 3
            and mock_state_bulk_retrieve.times_called == 0
            and mock_data_list.times_called == 0
        )
    elif scenario in ['state_bulk_failed']:
        assert (
            mock_bulk_retrieve.times_called == 1
            and mock_parks_list.times_called == 1
            and mock_state_bulk_retrieve.times_called == 3
            and mock_data_list.times_called == 0
        )
    elif scenario in ['update_failed', 'update_status']:
        assert (
            mock_bulk_retrieve.times_called == 1
            and mock_parks_list.times_called == 1
            and mock_state_bulk_retrieve.times_called == 1
            and mock_data_list.times_called == 0
        )
    else:
        assert (
            mock_bulk_retrieve.times_called == 1
            and mock_parks_list.times_called == 1
            and mock_state_bulk_retrieve.times_called == 1
            and mock_data_list.times_called == 3
        )


@pytest.mark.config(
    QC_EXAMS_ADMIN_UPDATE_DRIVERS_HANDLER_SETTINGS=dict(
        limits=dict(max_request_items=0),
    ),
)
async def test_update_drivers_limit(
        web_app_client, patch_aiohttp_session, response_mock,
):
    @patch_aiohttp_session(discovery.find_service('taximeter_xservice').url)
    def patch_update_drivers(method, url, json, **kwargs):
        return response_mock(json=dict())

    @patch_aiohttp_session(discovery.find_service('quality_control').url)
    def patch_data(method, url, params, json, **kwargs):
        return response_mock(json=dict())

    data = dict(items=[dict(park_id='park', driver_id='driver')])
    response = await web_app_client.post(
        'v1/update/drivers', json=data, headers=HEADERS,
    )

    assert response.status == 200
    response_data = await response.json()

    items = response_data.pop('failed', [])

    assert response_data == dict()
    assert items == [dict(park_id='park', driver_id='driver')]

    assert not patch_update_drivers.calls
    assert not patch_data.calls


@pytest.mark.config(
    QC_EXAMS_ADMIN_UPDATE_DRIVERS_HANDLER_SETTINGS=dict(
        throttlers=dict(
            bulk_retrieve=dict(size=3, sleep=0),
            qc_post_data=dict(size=1, sleep=0),
            countries=dict(size=2, sleep=0),
            update=dict(size=2, sleep=0),
            state_bulk_retrieve=dict(size=5, sleep=0),
        ),
    ),
)
async def test_throttlers(
        web_app_client,
        mock_quality_control_py3,
        patch_aiohttp_session,
        response_mock,
):
    @patch_aiohttp_session(discovery.find_service('taximeter_xservice').url)
    def patch_update_drivers(method, url, json, **kwargs):
        return response_mock(
            json=dict(
                processed=[
                    dict(
                        park_id=x['new_data']['park_id'],
                        driver_id=x['new_data']['driver_id'],
                    )
                    for x in json['items']
                ],
            ),
        )

    @mock_quality_control_py3('/api/v1/data/bulk_retrieve')
    def mock_bulk_retrieve(request):
        return web.json_response(dict(items=[]))

    @mock_quality_control_py3('/api/v1/data/list')
    def mock_data_list(request):
        return web.json_response({})

    @mock_quality_control_py3('/api/v1/state/bulk_retrieve')
    def mock_state_bulk_retrieve(request):
        assert request.method.lower() == 'post'
        return web.json_response(
            dict(
                items=[
                    dict(id=x, type=request.query['type'], exams=[])
                    for x in request.json['items']
                ],
            ),
        )

    data = dict(
        items=[dict(park_id='park', driver_id=f'driver{x}') for x in range(5)],
    )
    response = await web_app_client.post(
        'v1/update/drivers', json=data, headers=HEADERS,
    )

    assert response.status == 200
    response_data = await response.json()

    items = response_data.pop('modified')
    assert response_data == dict()
    assert len(items) == 5

    assert len(patch_update_drivers.calls) == 3

    assert mock_bulk_retrieve.times_called == 2
    assert mock_state_bulk_retrieve.times_called == 1
    assert mock_data_list.times_called == 10  # twice per each value


@pytest.mark.config(
    QC_EXAMS_ADMIN_UPDATE_DRIVERS_IGNORE_FIELDS=['car_id', 'city', 'country'],
)
async def test_ignored_fields(web_app_client, mock_quality_control_py3):
    @mock_quality_control_py3('/api/v1/data/bulk_retrieve')
    def mock_bulk_retrieve(request):
        assert request.json == dict(items=['park_driver'])
        assert request.query == dict(type='driver')

        return web.json_response(
            dict(
                items=[
                    dict(
                        id='park_driver',
                        type='driver',
                        data=dict(park_id='park', car_id='old_car'),
                        modified='2019-04-20T12:00:00Z',
                    ),
                ],
            ),
        )

    @mock_quality_control_py3('/api/v1/data/list')
    def mock_data_list(request):
        assert request.method.lower() == 'post'
        assert request.query == dict(type='driver')

        return web.json_response({})

    data = dict(items=[dict(park_id='park', driver_id='driver')])
    response = await web_app_client.post(
        'v1/update/drivers', json=data, headers=HEADERS,
    )

    assert response.status == 200
    response_data = await response.json()

    items = response_data.pop('modified')
    assert response_data == dict()
    assert items == [dict(park_id='park', driver_id='driver')]

    assert mock_bulk_retrieve.times_called == 1
    assert mock_data_list.times_called == 1

    assert mock_data_list.next_call()['request'].json == [
        dict(
            type='driver',
            id='park_driver',
            data=dict(
                park_id='park', car_id='car', city='Москва', country='rus',
            ),
        ),
    ]


TEST_QC_UPDATE_CALLS_NUMBER = 0


@pytest.mark.config(
    QC_EXAMS_ADMIN_UPDATE_DRIVERS_IGNORE_FIELDS=['city', 'country'],
)
async def test_qc_update_once(web_app_client, mock_quality_control_py3):
    @mock_quality_control_py3('/api/v1/data/bulk_retrieve')
    def mock_bulk_retrieve(request):
        assert request.json == dict(items=['park_driver'])
        assert request.query == dict(type='driver')
        global TEST_QC_UPDATE_CALLS_NUMBER  # pylint: disable=W0603

        if TEST_QC_UPDATE_CALLS_NUMBER:
            response_body = dict(
                items=[
                    dict(
                        id='park_driver',
                        type='driver',
                        data=dict(
                            park_id='park',
                            car_id='car',
                            city='Москва',
                            country='rus',
                        ),
                        modified='2019-04-20T12:00:00Z',
                    ),
                ],
            )
        else:
            TEST_QC_UPDATE_CALLS_NUMBER = 1
            response_body = dict(
                items=[
                    dict(
                        id='park_driver',
                        type='driver',
                        data=dict(park_id='park', car_id='car'),
                        modified='2019-04-20T12:00:00Z',
                    ),
                ],
            )

        return web.json_response(response_body)

    @mock_quality_control_py3('/api/v1/data/list')
    def mock_data_list(request):
        assert request.method.lower() == 'post'
        assert request.query == dict(type='driver')

        return web.json_response({})

    data = dict(items=[dict(park_id='park', driver_id='driver')])
    response = await web_app_client.post(
        'v1/update/drivers', json=data, headers=HEADERS,
    )

    assert response.status == 200
    response_data = await response.json()

    items = response_data.pop('modified')
    assert response_data == dict()
    assert items == [dict(park_id='park', driver_id='driver')]

    assert mock_bulk_retrieve.times_called == 1
    assert mock_data_list.times_called == 1

    assert mock_data_list.next_call()['request'].json == [
        dict(
            type='driver',
            id='park_driver',
            data=dict(
                park_id='park', car_id='car', city='Москва', country='rus',
            ),
        ),
    ]

    data = dict(items=[dict(park_id='park', driver_id='driver')])
    response = await web_app_client.post(
        'v1/update/drivers', json=data, headers=HEADERS,
    )

    global TEST_QC_UPDATE_CALLS_NUMBER  # pylint: disable=W0603
    assert TEST_QC_UPDATE_CALLS_NUMBER == 1

    assert response.status == 200
    response_data = await response.json()
    items = response_data.pop('unmodified')
    assert response_data == dict()
    assert items == [dict(park_id='park', driver_id='driver')]

    assert mock_bulk_retrieve.times_called == 2
    assert mock_data_list.times_called == 0
