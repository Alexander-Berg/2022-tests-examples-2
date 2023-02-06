from typing import Optional

import pytest

from rida.utils import suggested_price
from rida.utils import zone_settings
from test_rida import experiments_utils
from test_rida import helpers


@pytest.mark.parametrize(
    ['price_format', 'expected_precision'],
    [
        pytest.param('1000', -3),
        pytest.param('100', -2),
        pytest.param('10', -1),
        pytest.param('1', 0),
        pytest.param('0.1', 1),
        pytest.param('0.01', 2),
    ],
)
def test_price_format_to_precision(price_format: str, expected_precision: int):
    prec = zone_settings._price_format_to_precision(  # pylint: disable=W0212
        price_format,
    )
    assert prec == expected_precision


@pytest.mark.parametrize(
    ['price', 'price_precision', 'expected_price'],
    [
        pytest.param(123789.12345, -2, '123800'),
        pytest.param(123789.12345, -1, '123790'),
        pytest.param(123789.12345, 0, '123789'),
        pytest.param(123789.12345, 1, '123789.1'),
        pytest.param(123789.12345, 2, '123789.12'),
    ],
)
def test_round_price(price: int, price_precision: int, expected_price: str):
    result_price = suggested_price.round_price(
        price=price, price_precision=price_precision,
    )
    assert result_price == expected_price


def get_auth_headers(user_id: int, accept_language: str):
    token = helpers.get_auth_headers(user_id)
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept-Language': accept_language,
    }
    return headers


@pytest.mark.parametrize(
    [
        'country_id',
        'zone_id',
        'distance',
        'duration',
        'expected_suggested_price',
        'accept_language',
    ],
    [
        # errors
        pytest.param(None, 0, 1, 1, None, 'ru', id='missing_country_id'),
        pytest.param(1, 0, None, 1, None, 'en', id='missing_distance'),
        pytest.param(1, 0, 1, None, None, 'de', id='missing_duration'),
        pytest.param(1, 0, 1, 1, None, 'ru', id='unknown_country'),
        # caclulate by country settings:
        # 2*(600/60) + 3*(10000/1000) + 119 = 20 + 30 + 119 = 169 ≈ 200
        pytest.param(12, None, 10000, 600, '200', 'en', id='no_zone'),
        pytest.param(12, 0, 10000, 600, '200', 'de', id='default_zone'),
        pytest.param(12, 0, 10000, 600, '200', 'ru', id='unknown_zone'),
        pytest.param(12, 2, 10000, 600, '200', 'en', id='unknown_city'),
        # country min offer: 125 ≈ 100
        pytest.param(12, 0, 1, 1, '100', 'de', id='country_min_offer'),
        # zone fix price: 356 ≈ 400
        pytest.param(12, 3, 10000, 600, '400', 'ru', id='fix_price'),
        # calculate by matched zone settings:
        # 5*(1800/60) + 7*(10000/1000) + 21 = 150 + 70 + 31 = 251 ≈ 300
        pytest.param(12, 1, 10000, 1800, '300', 'en', id='matched_zone'),
        # zone min offer: 240 ≈ 200
        pytest.param(12, 1, 1, 1, '200', 'de', id='zone_min_offer'),
    ],
)
@pytest.mark.parametrize('request_body_as_query', [True, False])
@pytest.mark.parametrize('send_jwt_auth', [True, False])
async def test_get_suggested_price_different_locales(
        web_app_client,
        country_id: Optional[int],
        zone_id: Optional[int],
        distance: Optional[int],
        duration: Optional[int],
        expected_suggested_price: Optional[str],
        request_body_as_query: bool,
        send_jwt_auth: bool,
        accept_language: str,
):
    request_params = {}
    if send_jwt_auth:
        request_params['headers'] = get_auth_headers(
            user_id=1234, accept_language=accept_language,
        )
    request_body = {
        'country_id': country_id,
        'zone_id': zone_id,
        'distance': distance,
        'duration': duration,
    }
    request_body = {k: v for k, v in request_body.items() if v is not None}
    if request_body_as_query:
        request_params['data'] = request_body
    else:
        request_params['json'] = request_body
    response = await web_app_client.post(
        '/v1/getSuggestedPrice', **request_params,
    )
    assert response.status == 200
    response_json = await response.json()
    if expected_suggested_price is None:
        assert response_json == {'status': 'OK'}
    else:
        assert response_json == {
            'status': 'OK',
            'data': {'suggestedPrice': expected_suggested_price},
        }


@pytest.mark.parametrize(
    ['expected_override_price'],
    [
        pytest.param(
            '200',
            marks=experiments_utils.get_price_overrides_marks(
                time_coefficient=20,
            ),
            id='time_coefficient',
        ),
        pytest.param(
            '300',
            marks=experiments_utils.get_price_overrides_marks(
                distance_coefficient=3,
            ),
            id='distance_coefficient',
        ),
        pytest.param(
            '1400',
            marks=experiments_utils.get_price_overrides_marks(
                suggest_price_constant=1377,
            ),
            id='suggest_price_constant',
        ),
        pytest.param(
            '1500',
            marks=experiments_utils.get_price_overrides_marks(
                min_offer_amount=1477,
            ),
            id='min_offer_amount',
        ),
    ],
)
@pytest.mark.parametrize('send_jwt_auth', [True, False])
async def test_price_overrides(
        web_app_client,
        send_jwt_auth: bool,
        expected_override_price: Optional[str],
):
    request_params = {
        'json': {
            'country_id': 12,
            'zone_id': 1,
            'distance': 100000,
            'duration': 600,
        },
    }
    if send_jwt_auth:
        request_params['headers'] = helpers.get_auth_headers(user_id=1234)
    response = await web_app_client.post(
        '/v1/getSuggestedPrice', **request_params,
    )
    assert response.status == 200
    response_json = await response.json()

    expected_suggested_price = '800'  # default for this zone & values
    is_expected_override = all([send_jwt_auth, expected_override_price])
    if is_expected_override:
        expected_suggested_price = str(expected_override_price)
    assert response_json == {
        'status': 'OK',
        'data': {'suggestedPrice': expected_suggested_price},
    }
