import pytest


@pytest.mark.parametrize(
    'pg_case, provider_case, total_amount, expected_case',
    [
        ('existing_corp_method', 'corp', '1', 'available_for_corp_only'),
        (
            'existing_card_method',
            'corp+card',
            '10000',
            'available_with_overspending',
        ),
        (
            'existing_corp_method',
            'corp',
            '10000',
            'not_available_small_balance',
        ),
        (
            'existing_card_method',
            'corp_disabled',
            '1',
            'not_available_no_corp',
        ),
    ],
)
async def test_different_success_cases(
        taxi_eats_corp_orders_web,
        eats_user,
        yandex_uid,
        place_id,
        epma_payment_methods_provider,
        fill_db,
        load_json,
        pg_case,
        expected_case,
        provider_case,
        total_amount,
):
    epma_payment_methods_provider(provider_case)
    fill_db(f'{pg_case}.sql')
    response = await taxi_eats_corp_orders_web.post(
        '/v1/payment-method/get-verified',
        headers={
            'X-Eats-User': eats_user,
            'X-Yandex-UID': yandex_uid,
            'X-Remote-IP': '',
        },
        json={'place_id': place_id, 'total_amount': total_amount},
    )
    assert response.status == 200
    assert await response.json() == load_json('expected.json')[expected_case]


@pytest.mark.parametrize(
    'headers, status',
    [
        ({'X-Eats-User': f'user_id=1,personal_phone_id=1'}, 400),
        (
            {
                'X-Eats-User': f'user_id=1,personal_phone_id=1',
                'X-Remote-IP': '',
            },
            400,
        ),
        (
            {
                'X-Eats-User': f'user_id=1',
                'X-Yandex-UID': '1',
                'X-Remote-IP': '',
            },
            401,
        ),
        (
            {
                'X-Eats-User': f'personal_phone_id=1',
                'X-Yandex-UID': '1',
                'X-Remote-IP': '',
            },
            401,
        ),
    ],
)
async def test_invalid_headers(
        taxi_eats_corp_orders_web,
        eats_user,
        yandex_uid,
        place_id,
        check_payment_methods_db,
        load_json,
        headers,
        status,
):
    response = await taxi_eats_corp_orders_web.post(
        '/v1/payment-method/get-verified',
        headers=headers,
        json={'place_id': place_id, 'total_amount': '1'},
    )
    assert response.status == status
