import logging

import pytest

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    'classes_request, expected_classes',
    [
        pytest.param(
            {
                'identity': {'phone_id': '1a1a1a1a1a1a1a1a1a1a1a1a'},
                'client_id': 'client_id_1',
            },
            ['econom', 'vip'],
            id='with limit',
        ),
        pytest.param(
            {
                'identity': {'phone_id': '4a1a1a1a1a1a1a1a1a1a1a1a'},
                'client_id': 'client_id_3',
            },
            ['business', 'comfortplus', 'econom', 'start', 'vip'],
            id='without limit',
        ),
        pytest.param(
            {
                'identity': {'phone_id': 'b1a1a1a1a1a1a1a1a1a1a1a1'},
                'client_id': 'without_vat_id',
            },
            ['econom', 'comfort'],
            id='without vat',
        ),
    ],
)
@pytest.mark.config(
    CORP_WITHOUT_VAT_DEFAULT_CATEGORIES={'rus': ['econom', 'comfort']},
)
async def test_user_classes_available(
        web_app_client, patch, classes_request, expected_classes,
):
    @patch(
        'taxi_corp_integration_api.caches.tariff_settings_cache'
        '.Cache.get_tariff_names',
    )
    def tariff_names(*args, **kwargs):  # pylint: disable=W0612
        return {'econom', 'comfort', 'comfortplus', 'business', 'vip', 'start'}

    response = await web_app_client.post(
        'v1/user_classes_available', json=classes_request,
    )
    assert response.status == 200

    body = await response.json()
    assert body['classes_available'] == expected_classes
