import pytest


URL = '/internal/umlaas-grocery-eta/v1/depot-eta'
DEPOT_ID = 123
CONSUMER = 'umlaas-grocery-eta/depot-eta'
TIMESTAMP = '2022-02-06T14:00:00+03:00'


def exp3_decorator(value):
    return pytest.mark.experiments3(
        name='grocery_eta',
        consumers=[CONSUMER],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        is_config=True,
        default_value=value,
    )


def exp3_without_external(ml_resource):
    return exp3_decorator(
        {
            'ml_model': {
                'ml_model_resource_name': ml_resource,
                'sources': {},
                'cooking_time': {'lower_bound': 6, 'upper_bound': 60},
                'delivery_time': {'upper_bound': 60},
                'total_time': {'upper_bound': 100500, 'window_width': 10},
            },
        },
    )


@pytest.mark.parametrize(
    'transport_type,expected_eta',
    [
        pytest.param(
            'pedestrian',
            360,
            marks=exp3_without_external(
                'grocery_eta_pedestrian_zone_resources_v2',
            ),
        ),
        pytest.param(
            'yandex_taxi',
            360,
            marks=exp3_without_external(
                'grocery_eta_yandex_taxi_zone_resources_v2',
            ),
        ),
    ],
)
async def test_depot_eta_ml_model_without_sources(
        taxi_umlaas_grocery_eta, grocery_depots, transport_type, expected_eta,
):
    grocery_depots.add_depot(DEPOT_ID)
    response = await taxi_umlaas_grocery_eta.post(
        URL,
        json={'depot_id': str(DEPOT_ID), 'transport_type': transport_type},
    )
    assert response.status == 200
    data = response.json()
    assert data['cooking_time'] == expected_eta


def exp3_all_sources(ml_resource):
    return exp3_decorator(
        {
            'ml_model': {
                'ml_model_resource_name': ml_resource,
                'sources': {
                    # depot-eta doesn't use routing, so not requesting
                    'depot_statistics_enabled': True,
                    'extra_depot_statistics_enabled': True,
                    'depot_state_enabled': True,
                    'shift_info_enabled': True,
                },
                'cooking_time': {'lower_bound': 6, 'upper_bound': 60},
                'delivery_time': {'upper_bound': 60},
                'total_time': {'upper_bound': 100500, 'window_width': 10},
            },
        },
    )


@pytest.mark.now(TIMESTAMP)
@pytest.mark.parametrize(
    'transport_type,expected_eta',
    [
        pytest.param(
            'pedestrian',
            360,
            marks=exp3_all_sources('grocery_eta_pedestrian_zone_resources_v2'),
        ),
        pytest.param(
            'yandex_taxi',
            360,
            marks=exp3_all_sources(
                'grocery_eta_yandex_taxi_zone_resources_v2',
            ),
        ),
    ],
)
async def test_depot_eta_ml_model_external_data(
        taxi_umlaas_grocery_eta,
        grocery_depots,
        testpoint,
        transport_type,
        expected_eta,
):
    @testpoint('depot-eta-ml-request')
    def depot_eta_ml_request(ml_request):
        pass

    grocery_depots.add_depot(DEPOT_ID)
    await taxi_umlaas_grocery_eta.enable_testpoints()
    response = await taxi_umlaas_grocery_eta.post(
        URL,
        json={'depot_id': str(DEPOT_ID), 'transport_type': transport_type},
    )
    assert response.status == 200
    data = response.json()
    assert data['cooking_time'] == expected_eta

    assert depot_eta_ml_request.times_called == 1

    ml_request = (await depot_eta_ml_request.wait_call())['ml_request']
    assert ml_request, 'error retrieving ML request'

    expected_request_keys = list(
        sorted(
            [
                'request_id',
                'predicting_at',
                'request_type',
                'user_info',
                'place_info',
                'courier_type',
            ]
            + ['depot_statistics', 'depot_state', 'shifts'],  # external data:
        ),
    )
    assert sorted(ml_request.keys()) == expected_request_keys
    for key in expected_request_keys:
        assert ml_request[key], key  # external source data is not empty

    assert len(ml_request['depot_statistics']) == 8
    depot_stats = ml_request['depot_statistics']['previous_halfhour']
    assert depot_stats['average_performer_speed'] == 12
    assert depot_stats['average_between_pickup_ms'] == 1290
    assert depot_stats['average_between_matched_ms'] == 1383
    assert depot_stats['average_assembling_ms'] == 4956
    assert depot_stats['average_between_assembling_ms'] == 3594
    assert depot_stats['average_time_ms'] == 8765
    assert depot_stats['average_cooking_time_ms'] == 100500


# TODO: upload log to YT test?
