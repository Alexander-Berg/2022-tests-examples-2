import pytest


@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_CITY_TZ_MAPPING={
        'Санкт-Петербург': ['spb'],
        'Нижний Тагил': ['nizhnytagil'],
        'Москва': ['moscow'],
        'Саратов': ['saratov'],
        'Пенза': ['penza'],
    },
)
@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_suggests_to_publish.sql'],
)
async def test_get_active_discounts_statistics(web_app_client):
    response = await web_app_client.get(
        '/v1/suggests/active_discounts_statistics',
    )

    assert response.status == 200
    content = await response.json()

    assert content == {
        'active_discounts_total_count': 2,
        'cities_with_discount_total_count': 2,
        'cities_without_discount_total_count': 3,
        'active_discounts_counts': [
            {'discounts_city': 'Санкт-Петербург', 'count': 0},
            {'discounts_city': 'Нижний Тагил', 'count': 1},
            {'discounts_city': 'Москва', 'count': 1},
            {'discounts_city': 'Саратов', 'count': 0},
            {'discounts_city': 'Пенза', 'count': 0},
        ],
    }
