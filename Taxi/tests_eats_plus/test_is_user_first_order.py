import pytest

from tests_eats_plus import conftest

DEFAULT_HEADERS = {
    'X-Request-Language': 'ru',
    'content-type': 'application/json',
}


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.parametrize('has_user_id_in_auth_context', [True, False])
@pytest.mark.experiments3(
    filename='exp3_eats_plus_place_cashback_presentation.json',
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
async def test_getting_user_id_from_auth_context(
        taxi_eats_plus,
        passport_blackbox,
        eats_order_stats,
        plus_wallet,
        eats_eaters,
        has_user_id_in_auth_context,
):
    eats_order_stats()
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 123321})
    headers = DEFAULT_HEADERS.copy()
    if has_user_id_in_auth_context:
        headers['X-Eats-User'] = 'personal_phone_id=111,user_id=222'
    response = await taxi_eats_plus.post(
        # handle itself doesn't matter,
        # just need something to call IsUserFirstOrder(..)
        'internal/eats-plus/v1/presentation/cashback/place',
        json={'yandex_uid': 'user-uid', 'place_id': 1},
        headers=headers,
    )

    assert response.status_code == 200
    assert eats_eaters.times_called != has_user_id_in_auth_context
