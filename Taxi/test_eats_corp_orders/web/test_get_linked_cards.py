import pytest


# todo: test with disabled:
#  - that it not returns
#  - new method makes enabled
#  - unlink works
@pytest.mark.parametrize(
    'pg_case, expected_case, provider_case',
    [
        ('existing_card_method', 'existing_card_and_corp_method', 'corp'),
        (
            'existing_card_method',
            'existing_card_no_corp_method',
            'corp_disabled',
        ),
        (
            'existing_card_method',
            'existing_card_no_corp_method',
            'corp_not_exists',
        ),
        ('existing_corp_method', 'existing_corp_method', 'corp'),
        ('existing_corp_method', 'no_available_methods', 'corp_disabled'),
        ('existing_corp_method', 'no_available_methods', 'corp_not_exists'),
    ],
)
async def test_different_success_cases(
        taxi_eats_corp_orders_web,
        eats_user,
        yandex_uid,
        check_payment_methods_db,
        payment_methods_provider,
        fill_db,
        load_json,
        pg_case,
        expected_case,
        provider_case,
):
    payment_methods_provider(provider_case)
    fill_db(f'{pg_case}.sql')
    response = await taxi_eats_corp_orders_web.get(
        '/v1/payment-method/get-linked',
        headers={'X-Eats-User': eats_user, 'X-Yandex-UID': yandex_uid},
    )
    assert response.status == 200
    assert await response.json() == load_json('expected.json')[expected_case]


@pytest.mark.parametrize(
    'headers, status',
    [
        ({'X-Eats-User': f'user_id=1,personal_phone_id=1'}, 400),
        ({'X-Eats-User': f'user_id=1', 'X-Yandex-UID': '1'}, 401),
        ({'X-Eats-User': f'personal_phone_id=1', 'X-Yandex-UID': '1'}, 401),
    ],
)
async def test_invalid_headers(
        taxi_eats_corp_orders_web,
        eats_user,
        yandex_uid,
        check_payment_methods_db,
        load_json,
        headers,
        status,
):
    response = await taxi_eats_corp_orders_web.get(
        '/v1/payment-method/get-linked', headers=headers,
    )
    assert response.status == status
