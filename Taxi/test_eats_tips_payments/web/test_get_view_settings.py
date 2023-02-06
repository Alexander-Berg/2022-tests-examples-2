# pylint: disable=invalid-name
import pytest

from test_eats_tips_payments import conftest


def _format_request_param(*, recipient_id=None, place_id=None):
    return dict(
        filter(
            lambda item: item[1] is not None,
            {'recipient_id': recipient_id, 'place_id': place_id}.items(),
        ),
    )


@pytest.mark.config(
    EATS_TIPS_PAYMENTS_CUSTOM_THEME_OPTIONS={
        '000030': {
            'name': 'shoko',
            'promo_image_url': 'test_promo_image_url',
            'promo_url': 'test_promo_url',
        },
    },
)
@pytest.mark.parametrize(
    'request_params, expected_status, expected_result,',
    [
        pytest.param(
            _format_request_param(recipient_id=conftest.PARTNER_ID_1),
            200,
            {
                'show_place_name': False,
                'place_name': '',
                'place_photo': '',
                'theme': 'light',
            },
            id='success',
        ),
        pytest.param(
            _format_request_param(
                recipient_id=conftest.PARTNER_ID_1,
                place_id=conftest.PLACE_ID_1,
            ),
            200,
            {
                'show_place_name': True,
                'place_name': 'кафе',
                'place_photo': 'photo2',
                'theme': 'custom',
                'theme_options': {
                    'name': 'shoko',
                    'promo_image_url': 'test_promo_image_url',
                    'promo_url': 'test_promo_url',
                },
                'type': 'restaurant',
            },
            id='with custom theme',
        ),
        pytest.param(
            _format_request_param(
                recipient_id=conftest.PARTNER_ID_1,
                place_id=conftest.PLACE_ID_2,
            ),
            200,
            {
                'show_place_name': True,
                'place_name': 'кафе',
                'place_photo': 'photo2',
                'theme': 'dark',
                'type': 'restaurant',
            },
            id='standard theme',
        ),
    ],
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-payments/brand-settings',
    config_name='eats_tips_payments_brand_settings',
    args=[{'name': 'brand_slug', 'type': 'string', 'value': 'shoko'}],
    value={
        'commission_percent': 5,
        'commission_should_be_compensated': True,
        'theme_name': 'shoko',
        'promo_url': 'test_promo_url',
        'promo_image_url': 'test_promo_image_url',
    },
)
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
async def test_get_view_settings(
        web_app,
        web_app_client,
        mock_eats_tips_partners_for_settings,
        # params:
        request_params,
        expected_status,
        expected_result,
):
    response = await web_app_client.get(
        '/v1/payments/view-settings', params=request_params,
    )
    assert response.status == expected_status, request_params
    content = await response.json()
    assert content == expected_result
