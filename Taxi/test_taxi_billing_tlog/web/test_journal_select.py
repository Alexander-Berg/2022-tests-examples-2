# pylint: disable=redefined-outer-name
import pytest


@pytest.fixture
def url():
    return '/v1/journal/select'


async def test_empty_db(web_app_client, url):
    response = await web_app_client.post(url, json={})
    assert response.status == 200
    data = await response.json()
    assert data == {'entries': []}


_EXPECTED = [
    {
        'amount': '1.6800',
        'currency': 'EUR',
        'product': 'park_b2b_trip_payment',
        'is_payable': True,
        'service_id': 651,
    },
    {
        'amount': '3.1415',
        'currency': 'USD',
        'product': 'park_b2b_trip_payment',
        'is_payable': True,
        'service_id': 651,
        'tariff_class': 'cargo',
    },
]


@pytest.mark.pgsql('billing_tlog@0', files=('journal.sql',))
@pytest.mark.parametrize(
    'query,expected',
    (
        ({}, {'entries': _EXPECTED}),
        ({'product': 'park_b2b_trip_payment'}, {'entries': _EXPECTED}),
        ({'product': 'client_b2b_trip_payment'}, {'entries': []}),
    ),
)
async def test_select_filtered(web_app_client, url, query, expected):
    response = await web_app_client.post(url, json=query)
    assert response.status == 200
    data = await response.json()
    assert data == expected
