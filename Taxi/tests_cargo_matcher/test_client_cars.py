import pytest

CARGO_CARS = [
    {
        'carrying_capacity_kg': 10,
        'enabled': True,
        'height_cm': 50,
        'length_cm': 80,
        'max_loaders': 0,
        'taxi_class': 'courier',
        'width_cm': 50,
    },
    {
        'carrying_capacity_kg': 20,
        'enabled': True,
        'height_cm': 50,
        'length_cm': 100,
        'max_loaders': 0,
        'taxi_class': 'express',
        'width_cm': 60,
    },
    {
        'cargo_type': 'van',
        'cargo_type_limits_key': 'van',
        'enabled': True,
        'max_loaders': 2,
        'taxi_class': 'cargo',
    },
    {
        'cargo_type': 'lcv_m',
        'cargo_type_limits_key': 'lcv_m',
        'enabled': True,
        'max_loaders': 2,
        'taxi_class': 'cargo',
    },
    {
        'cargo_type': 'lcv_l',
        'cargo_type_limits_key': 'lcv_l',
        'enabled': True,
        'max_loaders': 2,
        'taxi_class': 'cargo',
    },
]

CARGO_LIMITS = {
    'lcv_l': {
        'carrying_capacity_max_kg': 6000,
        'carrying_capacity_min_kg': 1400,
        'height_max_cm': 250,
        'height_min_cm': 180,
        'length_max_cm': 601,
        'length_min_cm': 380,
        'width_max_cm': 250,
        'width_min_cm': 180,
    },
    'lcv_m': {
        'carrying_capacity_max_kg': 6000,
        'carrying_capacity_min_kg': 700,
        'height_max_cm': 230,
        'height_min_cm': 150,
        'length_max_cm': 520,
        'length_min_cm': 260,
        'width_max_cm': 230,
        'width_min_cm': 130,
    },
    'van': {
        'carrying_capacity_max_kg': 2001,
        'carrying_capacity_min_kg': 300,
        'height_max_cm': 201,
        'height_min_cm': 90,
        'length_max_cm': 290,
        'length_min_cm': 170,
        'width_max_cm': 201,
        'width_min_cm': 96,
    },
}


def _get_expected_result_cargocorp():
    return {
        'cars': [
            {
                'carrying_capacity_kg': 20,
                'height': 0.5,
                'length': 1.0,
                'tariff': {
                    'boarding': 20.0,
                    'name': 'express',
                    'per_km': 20.0,
                    'per_minute': 13.0,
                    'per_point': 100.0,
                    'requirements_fixed': 100.0,
                },
                'width': 0.6,
            },
            {
                'cargo_type': 'van',
                'carrying_capacity_kg': 300,
                'height': 2.01,
                'length': 2.9,
                'tariff': {
                    'boarding': 30.0,
                    'name': 'cargo',
                    'per_km': 20.0,
                    'per_minute': 13.0,
                    'per_point': 150.0,
                    'requirements_fixed': 50.0,
                },
                'width': 2.01,
            },
            {
                'cargo_type': 'lcv_m',
                'carrying_capacity_kg': 700,
                'height': 2.3,
                'length': 5.2,
                'tariff': {
                    'boarding': 30.0,
                    'name': 'cargo',
                    'per_km': 20.0,
                    'per_minute': 13.0,
                    'per_point': 0.0,
                    'requirements_fixed': 50.0,
                },
                'width': 2.3,
            },
            {
                'cargo_type': 'lcv_l',
                'carrying_capacity_kg': 1400,
                'height': 2.5,
                'length': 6.01,
                'tariff': {
                    'boarding': 60.0,
                    'name': 'cargo',
                    'per_km': 40.0,
                    'per_minute': 26.0,
                    'per_point': 200.0,
                    'requirements_fixed': 100.0,
                },
                'width': 2.5,
            },
        ],
    }


def _get_expected_result_cargo():
    return {
        'cars': [
            {
                'carrying_capacity_kg': 20,
                'height': 0.5,
                'length': 1.0,
                'tariff': {
                    'boarding': 20.0,
                    'name': 'express',
                    'per_km': 20.0,
                    'per_minute': 13.0,
                    'per_point': 100.0,
                    'requirements_fixed': 100.0,
                },
                'width': 0.6,
            },
            {
                'cargo_type': 'van',
                'carrying_capacity_kg': 300,
                'height': 2.01,
                'length': 2.9,
                'tariff': {
                    'boarding': 20.0,
                    'name': 'cargo',
                    'per_km': 13.0,
                    'per_minute': 13.0,
                    'per_point': 100.0,
                    'requirements_fixed': 0.0,
                },
                'width': 2.01,
            },
            {
                'cargo_type': 'lcv_m',
                'carrying_capacity_kg': 700,
                'height': 2.3,
                'length': 5.2,
                'tariff': {
                    'boarding': 20.0,
                    'name': 'cargo',
                    'per_km': 13.0,
                    'per_minute': 13.0,
                    'per_point': 100.0,
                    'requirements_fixed': 0.0,
                },
                'width': 2.3,
            },
            {
                'cargo_type': 'lcv_l',
                'carrying_capacity_kg': 1400,
                'height': 2.5,
                'length': 6.01,
                'tariff': {
                    'boarding': 20.0,
                    'name': 'cargo',
                    'per_km': 13.0,
                    'per_minute': 13.0,
                    'per_point': 100.0,
                    'requirements_fixed': 0.0,
                },
                'width': 2.5,
            },
        ],
    }


@pytest.fixture(name='mock_corp_tariffs_with_cargo_corp')
def _mock_corp_tariffs_with_cargo_corp(mockserver, load_json):
    @mockserver.json_handler('/corp-tariffs/v1/client_tariff/current')
    def _tariffs(request):
        return {
            'tariff': {
                'id': '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_1',
                'home_zone': 'moscow',
                'categories': load_json('categories_with_cargocorp.json'),
            },
            'disable_paid_supply_price': False,
            'disable_fixed_price': True,
            'client_tariff_plan': {
                'tariff_plan_series_id': 'tariff_plan_id_123',
                'date_from': '2020-01-22T15:30:00+00:00',
                'date_to': '2021-01-22T15:30:00+00:00',
            },
        }

    return _tariffs


@pytest.fixture(name='v1_client_cars')
def _v1_client_cars(taxi_cargo_matcher):
    async def call():
        response = await taxi_cargo_matcher.post(
            '/v1/client-cars',
            json={
                'corp_client_id': 'corp_client_id_12312312312312312',
                'point_a': [37.1, 55.1],
            },
        )
        return response

    return call


@pytest.mark.config(
    CARGO_MATCHER_CARS=CARGO_CARS, CARGO_TYPE_LIMITS=CARGO_LIMITS,
)
async def test_client_cars(
        mock_corp_tariffs_with_cargo_corp,
        exp3_cargo_add_fake_middle_point,
        v1_client_cars,
        conf_exp3_cargocorp_autoreplacement,
):
    await conf_exp3_cargocorp_autoreplacement(is_enabled=True)
    response = await v1_client_cars()
    assert response.status_code == 200
    assert response.json() == _get_expected_result_cargocorp()


@pytest.mark.config(
    CARGO_MATCHER_CARS=CARGO_CARS, CARGO_TYPE_LIMITS=CARGO_LIMITS,
)
async def test_client_cars_no_cargocorp_replacement(
        mock_corp_tariffs_with_cargo_corp,
        exp3_cargo_add_fake_middle_point,
        v1_client_cars,
        conf_exp3_cargocorp_autoreplacement,
):
    await conf_exp3_cargocorp_autoreplacement(is_enabled=False)
    response = await v1_client_cars()
    assert response.status_code == 200
    assert response.json() == _get_expected_result_cargo()
