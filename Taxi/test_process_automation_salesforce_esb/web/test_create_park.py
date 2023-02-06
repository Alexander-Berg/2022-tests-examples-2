import json

import pytest


@pytest.fixture
def create_park_mock(request, patch):
    @patch('taxi.clients.admin.AdminApiClient.create_park')
    async def _create_park(*args, **kwargs):
        return {'id': '123', 'apikey': 'afkdjfdf2213'}


@pytest.fixture
async def mock_secdist(simple_secdist):
    simple_secdist['settings_override'][
        'PARTNER_CONTRACTS_ADMIN_TOKEN'
    ] = 'abc'
    return simple_secdist


@pytest.mark.servicetest
@pytest.mark.usefixtures('create_park_mock')
async def test_create_park(
        web_app_client, mock_secdist,  # pylint: disable=redefined-outer-name
):
    data = {
        'pay_donations_without_offer': False,
        'coupon': True,
        'automate_marketing_payments': False,
        'enable_grade_for_sticker': False,
        'balance_threshold': -5000,
        'city': 'Москва',
        'enable_branding_sticker': False,
        'creditcard': True,
        'phone_pd_id': '',
        'marketing_agreement': True,
        'type': 'taxipark',
        'enable_branding_lightbox': False,
        'additional_compensation_by_card': 0,
        'enable_branding_co_branding': False,
        'additional_compensation_by_cash': 0,
        'phone': '+7951879',
        'host': (
            'https://taximeter-xservice.taxi.tst.yandex.net/xservice/yandex'
        ),
        'takes_urgent': True,
        'enable_grade_for_full_branding': False,
        'name': 'testevgen',
        'billing_client_id': '188700938',
        'enable_grade_for_lightbox': False,
        'franchise_zones': [],
    }
    response = await web_app_client.post(
        '/v1/admin/park/create', data=json.dumps(data),
    )

    assert response.status == 200
    content = await response.text()
    assert content == '{"id": "123", "apikey": "afkdjfdf2213"}'
