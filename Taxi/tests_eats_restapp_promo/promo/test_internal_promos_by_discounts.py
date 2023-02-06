import pytest


DISCOUNT_PROMOS = {
    '11': {
        'promo_id': 301,
        'promo_type': 'one_plus_one',
        'promo_title': 'Два по цене одного',
    },
    '12': {
        'promo_id': 302,
        'promo_type': 'gift',
        'promo_title': 'Блюдо в подарок',
    },
    '13': {
        'promo_id': 303,
        'promo_type': 'discount',
        'promo_title': 'Скидка на меню или некоторые позиции',
    },
    '14': {
        'promo_id': 304,
        'promo_type': 'free_delivery',
        'promo_title': 'Бесплатная доставка',
    },
    '15': {
        'promo_id': 305,
        'promo_type': 'plus_happy_hours',
        'promo_title': 'Повышенный кешбэк в счастливые часы',
    },
    '16': {
        'promo_id': 306,
        'promo_type': 'plus_first_orders',
        'promo_title': 'Повышенный кешбэк для новичков',
    },
    '26': {
        'promo_id': 306,
        'promo_type': 'plus_first_orders',
        'promo_title': 'Повышенный кешбэк для новичков',
    },
}


def make_response(found_promos, unknown_discounts):
    response = {'found_promos': [], 'unknown_discounts': unknown_discounts}
    for discount_id in found_promos:
        data = DISCOUNT_PROMOS[discount_id].copy()
        data['discount_id'] = discount_id
        response['found_promos'].append(data)
    return response


@pytest.mark.parametrize(
    ['discount_ids', 'found_promos', 'unknown_discounts'],
    [
        pytest.param(
            ['100', '200'], [], ['100', '200'], id='unknown discounts only',
        ),
        pytest.param(['11'], ['11'], [], id='promo with single discount'),
        pytest.param(['26'], ['26'], [], id='promo with multiple discounts'),
        pytest.param(
            ['26', '16'],
            ['26', '16'],
            [],
            id='multiple discounts for same promo',
        ),
        pytest.param(
            ['11', '12', '15', '16', '13', '14'],
            ['11', '12', '15', '16', '13', '14'],
            [],
            id='multiple discounts',
        ),
        pytest.param(
            ['11', '100', '13', '200', '12'],
            ['11', '13', '12'],
            ['100', '200'],
            id='both known and unknown',
        ),
    ],
)
async def test_promos_internal_create_from_core(
        taxi_eats_restapp_promo, discount_ids, found_promos, unknown_discounts,
):
    response = await taxi_eats_restapp_promo.post(
        '/internal/eats-restapp-promo/v1/promos_by_discounts',
        json={'discount_ids': discount_ids},
    )
    assert response.status_code == 200
    assert response.json() == make_response(found_promos, unknown_discounts)
