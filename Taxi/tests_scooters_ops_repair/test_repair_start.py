import copy

import pytest

from tests_scooters_ops_repair import db_utils

HANDLER = '/scooters-ops-repair/v1/repair/start'

REPAIR_1 = {
    'repair_id': 'repair_id_1',
    'performer_id': 'performer_id_1',
    'depot_id': 'depot_id_1',
    'status': 'started',
    'vehicle_id': 'vehicle_id_1',
    'started_at': '2022-04-01T07:05:00+0000',
    'completed_at': None,
    'vehicle_info': {'mileage': 370.4},
    'jobs': [
        {
            'job_id': 'job_id_1',
            'status': 'completed',
            'type': 'type_1',
            'started_at': '2022-04-01T07:05:00+0000',
            'completed_at': '2022-04-01T07:15:00+0000',
        },
    ],
}


@pytest.mark.now('2022-04-01T07:05:00+00:00')
async def test_handler(taxi_scooters_ops_repair, pgsql, mockserver, load_json):
    @mockserver.json_handler('/scooters-misc/admin/v1/depots/list')
    def mock_depot_list(request):
        assert request.json == {'depot_id': 'depot_id_1'}
        return load_json('depot_list.json')

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def mock_car_details(request):
        assert request.args['car_id'] == 'vehicle_id_1'
        assert request.args['traits'] == 'ReportCars,ReportCarId'
        assert request.args['sensors'] == 'mileage'

        return load_json('car_details.json')

    response = await taxi_scooters_ops_repair.post(
        HANDLER,
        {
            'performer_id': 'performer_id_1',
            'vehicle_id': 'vehicle_id_1',
            'depot_id': 'depot_id_1',
        },
    )

    assert response.status == 200
    assert response.json() == {
        'jobs': [],
        'performer_id': 'performer_id_1',
        'depot_id': 'depot_id_1',
        'repair_id': db_utils.AnyValue(),
        'started_at': '2022-04-01T07:05:00+00:00',
        'status': 'started',
        'vehicle_id': 'vehicle_id_1',
        'vehicle_info': {'mileage': 370.39},
    }
    repair_id = response.json()['repair_id']

    assert mock_depot_list.times_called == 1
    assert mock_car_details.times_called == 1
    assert (
        db_utils.get_repairs(pgsql, ids=[repair_id], vehicle_info_params={})
        == [
            {
                'performer_id': 'performer_id_1',
                'depot_id': 'depot_id_1',
                'repair_id': repair_id,
                'status': 'started',
                'vehicle_id': 'vehicle_id_1',
                'started_at': db_utils.parse_timestring_aware(
                    '2022-04-01T07:05:00+0000',
                ),
                'completed_at': None,
                'vehicle_info': {'mileage': 370.39},
            },
        ]
    )


@pytest.mark.parametrize(
    ['car_detail_response', 'expected_mileage'],
    [
        pytest.param('car_details_without_telematics.json', 0.0),
        pytest.param('car_details_without_mileage_sensor.json', 0.0),
    ],
)
async def test_no_telematics(
        taxi_scooters_ops_repair,
        pgsql,
        mockserver,
        load_json,
        car_detail_response,
        expected_mileage,
):
    @mockserver.json_handler('/scooters-misc/admin/v1/depots/list')
    def _mock_depot_list(request):
        return load_json('depot_list.json')

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def _mock_car_details(request):
        return load_json(car_detail_response)

    response = await taxi_scooters_ops_repair.post(
        HANDLER,
        {
            'performer_id': 'performer_id_1',
            'vehicle_id': 'vehicle_id_1',
            'depot_id': 'depot_id_1',
        },
    )
    assert response.status == 200
    repair_id = response.json()['repair_id']

    assert db_utils.get_vehicle_info(pgsql, repair_ids=[repair_id]) == [
        {'repair_id': repair_id, 'mileage': expected_mileage},
    ]


@pytest.mark.now('2022-04-01T07:05:00+00:00')
async def test_retry(taxi_scooters_ops_repair, pgsql, mockserver, load_json):
    @mockserver.json_handler('/scooters-misc/admin/v1/depots/list')
    def mock_depot_list(request):
        return load_json('depot_list.json')

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def mock_car_details(request):
        return load_json('car_details.json')

    response1 = await taxi_scooters_ops_repair.post(
        HANDLER,
        {
            'performer_id': 'performer_id_1',
            'vehicle_id': 'vehicle_id_1',
            'depot_id': 'depot_id_1',
        },
    )
    assert response1.status == 200
    assert response1.json() == {
        'jobs': [],
        'performer_id': 'performer_id_1',
        'repair_id': db_utils.AnyValue(),
        'depot_id': 'depot_id_1',
        'started_at': '2022-04-01T07:05:00+00:00',
        'status': 'started',
        'vehicle_id': 'vehicle_id_1',
        'vehicle_info': {'mileage': 370.39},
    }
    assert mock_depot_list.times_called == 1
    assert mock_car_details.times_called == 1
    repair_id = response1.json()['repair_id']

    response2 = await taxi_scooters_ops_repair.post(
        HANDLER,
        {
            'performer_id': 'performer_id_1',
            'vehicle_id': 'vehicle_id_1',
            'depot_id': 'depot_id_1',
        },
    )
    assert response2.status == 200
    assert response2.json() == {
        'jobs': [],
        'performer_id': 'performer_id_1',
        'repair_id': repair_id,
        'depot_id': 'depot_id_1',
        'started_at': '2022-04-01T07:05:00+00:00',
        'status': 'started',
        'vehicle_id': 'vehicle_id_1',
        'vehicle_info': {'mileage': 370.39},
    }
    assert mock_depot_list.times_called == 1
    assert mock_car_details.times_called == 1


@pytest.mark.parametrize(
    ['depot_list_response', 'car_detail_response', 'expected_message'],
    [
        pytest.param(
            'depot_list.json',
            'car_details_empty.json',
            'unknown vehicle_id:vehicle_id_1',
        ),
        pytest.param(
            'depot_list_empty.json',
            'car_details.json',
            'unknown depot_id:depot_id_1',
        ),
    ],
)
async def test_bad_request__scooter_depot_not_exists(
        taxi_scooters_ops_repair,
        mockserver,
        load_json,
        depot_list_response,
        car_detail_response,
        expected_message,
):
    @mockserver.json_handler('/scooters-misc/admin/v1/depots/list')
    def _mock_depot_list(request):
        return load_json(depot_list_response)

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def _mock_car_details(request):
        return load_json(car_detail_response)

    response = await taxi_scooters_ops_repair.post(
        HANDLER,
        {
            'performer_id': 'performer_id_1',
            'vehicle_id': 'vehicle_id_1',
            'depot_id': 'depot_id_1',
        },
    )

    assert response.status == 400
    assert response.json() == {
        'code': 'bad_request',
        'message': expected_message,
    }


@pytest.mark.parametrize(
    ['body', 'expected_message'],
    [
        pytest.param(
            {
                'performer_id': 'performer_id_1',
                'vehicle_id': 'vehicle_id_2',
                'depot_id': 'depot_id_1',
            },
            'performer already has active repairs',
        ),
        pytest.param(
            {
                'performer_id': 'performer_id_2',
                'vehicle_id': 'vehicle_id_1',
                'depot_id': 'depot_id_1',
            },
            'vehicle already has active repairs',
        ),
    ],
)
async def test_bad_request__existing_repair(
        pgsql,
        taxi_scooters_ops_repair,
        mockserver,
        load_json,
        body,
        expected_message,
):

    db_utils.add_repair(pgsql, copy.deepcopy(REPAIR_1))

    @mockserver.json_handler('/scooters-misc/admin/v1/depots/list')
    def _mock_depot_list(request):
        return load_json('depot_list.json')

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def _mock_car_details(request):
        return load_json('car_details.json')

    response = await taxi_scooters_ops_repair.post(HANDLER, body)

    assert response.status == 400
    assert response.json() == {
        'code': 'bad_request',
        'message': expected_message,
    }
