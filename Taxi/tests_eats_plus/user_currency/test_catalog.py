import pytest

DEFAULT_HEADERS = {
    'X-Request-Language': 'ru',
    'X-YaTaxi-User': 'personal_phone_id=111,eats_user_id=222',
    'X-YaTaxi-Session': 'taxi:333',
    'X-Yandex-Uid': '3456723',
    'X-YaTaxi-Bound-Uids': '',
    'X-YaTaxi-Pass-Flags': 'portal',
    'content-type': 'application/json',
}


@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 1,
            'revision_id': 1,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'location': {'geo_point': [37.525496503606774, 55.75568074159372]},
            'country': {
                'id': 1,
                'code': 'abc',
                'name': 'USSR',
                'currency': {'sign': '$', 'code': 'BYN'},
            },
            'region': {
                'id': 123,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
            'categories': [{'id': 1, 'name': 'some_name'}],
            'business': 'store',
            'type': 'native',
        },
    ],
)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.config(
    EATS_PLUS_DEFAULT_CURRENCY={
        'enabled': False,
        'fallback': False,
        'currency': 'RUB',
    },
)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
async def test_cashback_places_list_currency(
        taxi_eats_plus, passport_blackbox, eats_order_stats, mockserver,
):
    eats_order_stats()
    passport_blackbox()

    @mockserver.json_handler('plus-wallet/v1/balances')
    def _plus_balance(request):
        assert request.query.get('currencies') == 'BYN'
        return {
            'balances': [
                {
                    'wallet_id': 'wallet_2',
                    'balance': f'{100}',
                    'currency': 'BYN',
                },
            ],
        }

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/presentation/cashback/places-list',
        json={'yandex_uid': 'user-uid', 'place_ids': [1]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {'cashback': []}
