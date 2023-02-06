import pytest


def _create_request(interval_info):
    return {
        'zone_name': 'moscow',
        'zonal_tariff_description': _create_zonal_tariff_response(
            interval_info,
        ),
    }


def _create_zonal_tariff_response(interval_info):
    return {
        'currency_rules': {
            'code': 'RUB',
            'sign': '₽',
            'template': '$VALUE$ $SIGN$$CURRENCY$',
            'text': 'руб.',
        },
        'layout': 'default',
        'max_tariffs': _create_max_tariffs(interval_info),
        'paid_cancel_enabled': True,
    }


def _create_max_tariffs(interval_info):
    max_tariffs = []
    for name, prices in interval_info.items():
        max_tariffs.append(
            {
                'class': name,
                'id': name,
                'intervals': _create_intervals(prices),
                'name': name,
                'service_levels': [1],
            },
        )
    return max_tariffs


def _create_intervals(prices):
    return [
        {
            'category_type': 'application',
            'name': 'bar',
            'price_groups': [
                {'id': 'free_route', 'name': 'baz', 'prices': prices},
            ],
            'schedule': {'1': [{'end': '23:59', 'start': '00:00'}]},
            'title': 'foo',
        },
    ]


async def test_non_config_tariff_without_update(
        taxi_cargo_tariffs, mockserver,
):
    json = _create_request(
        interval_info={
            'foo': [
                {
                    'id': 'free_waiting',
                    'name': 'Бесплатное ожидание',
                    'price': '3 мин',
                    'visual_group': 'main',
                },
            ],
        },
    )
    response = await taxi_cargo_tariffs.post(
        'internal/cargo-tariffs/v1/update-zonal-tariffs', json=json,
    )
    assert response.status_code == 200
    assert not response.json()['is_updated']
    assert (
        response.json()['zonal_tariff_description']
        == json['zonal_tariff_description']
    )


@pytest.mark.config(
    CARGO_TARIFFS_FREE_WAITING={
        'moscow': {
            'express': {
                'source': {
                    'free_waiting_time': 120,
                    'free_waiting_time_with_door_to_door': 180,
                },
            },
        },
    },
)
@pytest.mark.translations(
    cargo={
        'cargo_tariffs_minutes': {'ru': 'мин'},
        'cargo_tariffs_seconds': {'ru': 'сек'},
        'cargo_tariffs_free_waiting_without_d2d_source_point': {
            'ru': 'Бесплатное время в точке А без от двери до двери',
        },
    },
)
async def test_happy_path(taxi_cargo_tariffs, mockserver):
    json = _create_request(
        interval_info={
            'express': [
                {
                    'id': 'free_waiting',
                    'name': 'Бесплатное ожидание',
                    'price': '3 мин',
                    'visual_group': 'main',
                },
            ],
        },
    )
    response = await taxi_cargo_tariffs.post(
        'internal/cargo-tariffs/v1/update-zonal-tariffs', json=json,
    )
    json_result = _create_zonal_tariff_response(
        interval_info={
            'express': [
                {
                    'id': 'free_waiting',
                    'name': 'Бесплатное ожидание',
                    'price': '3 мин',
                    'visual_group': 'main',
                },
                {
                    'id': 'free_waiting_without_d2d_source_point',
                    'name': 'Бесплатное время в точке А без от двери до двери',
                    'price': '2 мин',
                    'visual_group': 'main',
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json()['is_updated']
    assert response.json()['zonal_tariff_description'] == json_result


@pytest.mark.config(
    CARGO_TARIFFS_FREE_WAITING={
        'moscow': {
            'express': {
                'source': {
                    'free_waiting_time': 120,
                    'free_waiting_time_with_door_to_door': 180,
                },
            },
        },
    },
)
async def test_tariff_not_translated_without_update(
        taxi_cargo_tariffs, mockserver,
):
    json = _create_request(
        interval_info={
            'express': [
                {
                    'id': 'free_waiting',
                    'name': 'Бесплатное ожидание',
                    'price': '3 мин',
                    'visual_group': 'main',
                },
            ],
        },
    )
    response = await taxi_cargo_tariffs.post(
        'internal/cargo-tariffs/v1/update-zonal-tariffs', json=json,
    )
    assert response.status_code == 200
    assert not response.json()['is_updated']
    assert (
        response.json()['zonal_tariff_description']
        == json['zonal_tariff_description']
    )
