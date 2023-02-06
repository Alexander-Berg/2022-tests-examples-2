import pytest

from tests_eats_coupons import conftest

PATH = '/internal/coupon_finish'

PHONE_ID = '0123456789ab0123456789cf'

DEFAULT_REQUEST = {
    'order_id': 'r_order_id',
    'yandex_uid': 'r_yandex_uid',
    'success': False,
    'coupon_id': 'r_coupon_id',
    'application_name': 'iphone',
    'personal_phone_id': PHONE_ID,
}


async def test_request_parsing(taxi_eats_coupons, mockserver):
    @mockserver.json_handler('/coupons/internal/coupon_finish')
    def _mock_coupons(request):
        assert request.json == {
            'service': 'eats',
            'order_id': format_order_id(DEFAULT_REQUEST['order_id']),
            'yandex_uid': DEFAULT_REQUEST['yandex_uid'],
            'success': DEFAULT_REQUEST['success'],
            'coupon_id': DEFAULT_REQUEST['coupon_id'],
            'application_name': DEFAULT_REQUEST['application_name'],
            'personal_phone_id': DEFAULT_REQUEST['personal_phone_id'],
        }
        return {}

    expected_status_code = 200
    response = await taxi_eats_coupons.post(PATH, DEFAULT_REQUEST)
    assert response.status_code == expected_status_code


def format_order_id(order_id):
    return 'eats:{' + order_id + '}'


@pytest.mark.parametrize('taxi_coupons_response', [400, 500])
async def test_response_proxy(
        taxi_eats_coupons,
        mockserver,
        mock_coupons_response_proxy,
        response_context,
        taxi_coupons_response,
):
    response_context.set_params(
        conftest.ResponseParams(code=taxi_coupons_response),
    )

    response = await taxi_eats_coupons.post(
        PATH, json=DEFAULT_REQUEST, headers=conftest.HEADERS,
    )
    assert response.status_code == taxi_coupons_response
