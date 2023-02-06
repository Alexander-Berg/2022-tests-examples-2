import pytest

DEFAULT_REQUEST_JSON = {'version': 2}


# TODO(umed): fix as part of https://st.yandex-team.ru/CARGODEV-10906
@pytest.mark.parametrize(
    'handle,json',
    [
        ('api/integration/v2/claims/accept', DEFAULT_REQUEST_JSON),
        # ('api/integration/v2/claims/cancel', DEFAULT_REQUEST_JSON),
        ('api/integration/v1/claims/edit', None),
    ],
)
@pytest.mark.parametrize(
    'locale,expected_response_msg',
    [
        ('en', 'Claim have changed, refresh the page'),
        ('ru', 'Заявка изменилась обновите страницу'),
    ],
)
async def test_b2b_error_localization(
        taxi_cargo_claims,
        pgsql,
        create_default_claim,
        get_default_request,
        get_default_headers,
        handle,
        json,
        stq,
        locale,
        expected_response_msg,
):
    cursor = pgsql['cargo_claims'].conn.cursor()
    cursor.execute(
        'UPDATE cargo_claims.claims SET taxi_order_id = \'taxi_order_id_1\'',
    )
    header_to_use = get_default_headers()
    header_to_use['Accept-language'] = locale
    json = get_default_request() if not json else json
    json['cancel_state'] = 'paid'
    response = await taxi_cargo_claims.post(
        '%s?claim_id=%s&version=2' % (handle, create_default_claim.claim_id),
        json=json,
        headers=header_to_use,
    )
    assert response.status_code == 409
    assert response.json()['message'] == expected_response_msg
