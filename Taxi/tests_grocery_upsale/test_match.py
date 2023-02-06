import pytest


UPSALE_REQUEST = {
    'headers': {
        'X-YaTaxi-Session': 'taxi:taxi-user-id',
        'X-Yandex-UID': 'yandex-uid',
        'X-YaTaxi-User': 'eats_user_id=787898',
        'X-YaTaxi-PhoneId': 'phone_id',
    },
    'json': {
        'store_id': '0',
        'user_id': 787898,
        'product_ids': ['product1', 'product2'],
        'context': {
            'suggest_type': 'complement-items',
            'request_source': 'menu-page',
        },
    },
}

UPSALE_REQUEST_404 = {
    'headers': {
        'X-YaTaxi-Session': 'taxi:taxi-user-id',
        'X-Yandex-UID': 'yandex-uid',
        'X-YaTaxi-User': 'eats_user_id=787898',
        'X-YaTaxi-PhoneId': 'phone_id',
    },
    'json': {
        'store_id': '1234',
        'user_id': 787898,
        'product_ids': ['product1', 'product2'],
        'context': {
            'suggest_type': 'complement-items',
            'request_source': 'menu-page',
        },
    },
}

UPSALE_REQUEST_400 = {
    'headers': {
        'X-YaTaxi-Session': 'taxi:taxi-user-id',
        'X-Yandex-UID': 'yandex-uid',
        'X-YaTaxi-User': 'eats_user_id=787898',
        'X-YaTaxi-PhoneId': 'phone_id',
    },
    'json': {
        'store_id': '1234',
        'user_id': 787898,
        'product_ids': ['product1', 'product2'],
        'context': {
            'suggest_type': 'substitute-items',
            'request_source': 'cart-page',
        },
    },
}


@pytest.mark.now('2020-02-02T00:00:00+0300')
async def test_match_umlaas(taxi_grocery_upsale, umlaas_eats, grocery_depots):
    grocery_depots.add_depot(depot_test_id=1, legacy_depot_id='0')
    umlaas_eats.add_products(['foo', 'bar'])

    response = await taxi_grocery_upsale.post(
        '/internal/upsale/v1/match', **UPSALE_REQUEST,
    )
    assert response.status_code == 200

    assert response.json() == {
        'items': [{'product_id': 'foo'}, {'product_id': 'bar'}],
    }
    assert umlaas_eats.umlaas_called == 1


@pytest.mark.now('2020-02-02T00:00:00+0300')
async def test_match_umlaas_400(taxi_grocery_upsale, umlaas_eats):
    umlaas_eats.add_products(['foo', 'bar'])
    response = await taxi_grocery_upsale.post(
        '/internal/upsale/v1/match', **UPSALE_REQUEST_400,
    )
    assert response.status_code == 400

    assert umlaas_eats.umlaas_called == 0


@pytest.mark.now('2020-02-02T00:00:00+0300')
async def test_match_umlaas_404(taxi_grocery_upsale, umlaas_eats):
    umlaas_eats.add_products(['foo', 'bar'])
    response = await taxi_grocery_upsale.post(
        '/internal/upsale/v1/match', **UPSALE_REQUEST_404,
    )
    assert response.status_code == 404

    assert umlaas_eats.umlaas_called == 0


@pytest.mark.config(
    GROCERY_SUGGEST_COMPLEMENT_CANDIDATES_DEFAULT={
        '__default__': ['default1', 'default2'],
    },
)
@pytest.mark.now('2020-02-02T00:00:00+0300')
async def test_match_umlaas_500(
        taxi_grocery_upsale, umlaas_eats, grocery_depots,
):
    grocery_depots.add_depot(depot_test_id=1, legacy_depot_id='0')
    umlaas_eats.add_products(['foo', 'bar'])
    umlaas_eats.set_response_type(is_error=True)
    response = await taxi_grocery_upsale.post(
        '/internal/upsale/v1/match', **UPSALE_REQUEST,
    )
    assert response.json() == {
        'items': [{'product_id': 'default1'}, {'product_id': 'default2'}],
    }

    assert umlaas_eats.umlaas_called == 1
