import pytest

TRANSACTION_PRODUCTS = [
    {
        'category_id': 'scoring',
        'products': [
            {
                'product': 'partner_scoring',
                'product_details': 'partner_scoring',
            },
        ],
    },
    {
        'category_id': 'recurring_payments',
        'products': [
            {'product': 'TRANSFER_PAYMENT'},
            {'product': 'YA_TRANSFER'},
        ],
    },
]

DETAILS_LINKS = [
    {
        'category_ids': ['recurring_payments'],
        'link': '/regular-charges/{id}/parks/{park_id}/edit/',
        'tanker': {
            'key': 'link_regular_charges_text',
            'keyset': 'opteum_page_report_payouts',
        },
    },
    {
        'link': '/scoring/{id}/',
        'tanker': {
            'key': 'link_scoring_text',
            'keyset': 'opteum_page_report_payouts',
        },
    },
]

URL = '/api/v1/reports/payouts/details/links'

HEADERS = {
    'Accept-Language': 'ru',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'abacaba',
    'X-Yandex-UID': '123',
    'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
    'X-Real-IP': '127.0.0.1',
}


@pytest.mark.config(
    OPTEUM_REPORT_PAYOUTS_TRANSACTION_PRODUCTS=TRANSACTION_PRODUCTS,
    OPTEUM_REPORT_PAYOUTS_DETAILS_LINKS=DETAILS_LINKS,
)
@pytest.mark.translations(
    opteum_page_report_payouts={
        'link_regular_charges_text': {'ru': 'Списание №'},
    },
)
async def test_success(web_app_client):

    response = await web_app_client.post(URL, headers=HEADERS)

    assert response.status == 200

    data = await response.json()
    assert data == {
        'links': [
            {
                'link': '/regular-charges/{id}/parks/{park_id}/edit/',
                'transaction_type': 'recurring_payments',
                'title': 'Списание №',
            },
        ],
    }
