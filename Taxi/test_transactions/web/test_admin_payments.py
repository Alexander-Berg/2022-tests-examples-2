import urllib

import pytest


CONFIGS = dict(
    TVM_RULES=[{'dst': 'yb-trust-payments', 'src': 'transactions'}],
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)


@pytest.fixture
def payments_mocks(mockserver, load_json):
    """Put your mocks here"""
    response_cache = load_json('db_admin_payments.json')

    @mockserver.handler('/trust-payments/v2/payment_status/', prefix=True)
    def _get_payment(request):
        parsed = urllib.parse.urlparse(request.path_qs)
        path_split = parsed.path.split('/')
        purchase_token = path_split[path_split.index('payment_status') + 1]
        query = urllib.parse.parse_qs(parsed.query)
        assert 'show_processing_info' in query
        assert query['show_processing_info'] == ['1']
        if purchase_token in response_cache:
            response_data = response_cache[purchase_token]
            return mockserver.make_response(status=200, json=response_data)
        return mockserver.make_response(status=500, json={})


@pytest.mark.config(**CONFIGS)
@pytest.mark.usefixtures('payments_mocks')
async def test_payments_existing(web_app_client):
    response = await web_app_client.get(
        'admin/payments/65020fbb46d0182c45621518bd34a07f',
    )
    assert response.status == 200
    content = await response.json()
    expected_content = {
        'processing_info': {
            'terminal_id': 990001,
            'processing_cc': 'yamoney_h2h_emulator',
        },
    }
    assert content == expected_content


@pytest.mark.config(**CONFIGS)
@pytest.mark.usefixtures('payments_mocks')
async def test_payments_nonexisting(web_app_client):
    response = await web_app_client.get(
        'admin/payments/65020fbb46d0182c45621518bd34a07k',
    )
    assert response.status == 500


@pytest.mark.config(**CONFIGS)
async def test_payments_format_error(web_app_client, mockserver):
    @mockserver.handler('/trust-payments/v2/payment_status/', prefix=True)
    def _get_payment(request):
        return mockserver.make_response(status=200, json={})

    response = await web_app_client.get(
        'admin/payments/65020fbb46d0182c45621518bd34a07d',
    )
    assert response.status == 500
