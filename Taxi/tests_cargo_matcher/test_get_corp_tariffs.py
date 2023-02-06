import pytest


@pytest.mark.parametrize(
    'point, point_exists, expected_result',
    [
        ([37.1, 55.1], True, ['cargo', 'cargocorp', 'express']),
        ([100, 100], False, []),
    ],
)
async def test_simple_get_tariffs(
        taxi_cargo_matcher,
        mockserver,
        load_json,
        point,
        point_exists,
        expected_result,
):
    @mockserver.json_handler('/corp-tariffs/v1/client_tariff/current')
    def _dummy_tariffs(request):
        return {
            'tariff': {
                'id': '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_1',
                'home_zone': 'moscow',
                'categories': load_json('categories_with_cargocorp.json'),
            },
            'disable_surge': False,
            'disable_paid_supply_price': False,
            'disable_fixed_price': True,
            'client_tariff_plan': {
                'tariff_plan_series_id': 'tariff_plan_id_123',
                'date_from': '2020-01-22T15:30:00+00:00',
                'date_to': '2021-01-22T15:30:00+00:00',
            },
        }

    response = await taxi_cargo_matcher.post(
        '/v1/client-tariffs',
        json={'corp_client_id': 'c' * 32, 'point_a': point},
    )

    if point_exists:
        assert _dummy_tariffs.times_called == 1

    assert response.status_code == 200
    assert sorted(response.json()['tariffs']) == expected_result
