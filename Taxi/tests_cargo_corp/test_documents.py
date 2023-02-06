import pytest

from tests_cargo_corp import utils

CONTRACTS_RESPONSE = {
    'contracts': [
        {
            'contract_id': 0,
            'external_id': '101/0',
            'payment_type': 'postpaid',
            'is_offer': False,
            'currency': 'RUB',
            'services': ['cargo'],
        },
    ],
}

SHOWN_MONTHS_AMOUNT = 1
DATETIME_STRING = '2021-05-31T19:00:00+00:00'


@pytest.fixture(name='get_translation')
def _get_translation(load_json):
    translations = load_json('localizations/corp.json')

    def wrapper(message_key):
        for item in translations:
            if item['_id'] == message_key:
                return item['values'][0]['value']
        return None

    return wrapper


@pytest.mark.now(DATETIME_STRING)
@pytest.mark.config(CARGO_CORP_DOCS_MONTHS_AMOUNT=SHOWN_MONTHS_AMOUNT)
async def test_documents_list(
        taxi_cargo_corp,
        mockserver,
        get_taxi_corp_contracts,
        get_translation,
        load_json,
):
    yadoc_response = load_json('yadoc_responses.json')['list_response']

    @mockserver.json_handler('/yadoc/public/api/v1/documents')
    def _yadoc_handler(request):
        assert request.json['doc_type'] == ['ACT']
        assert request.json['exclude_reversed']
        assert request.json['date_to'] == '2021-04-30'
        assert request.json['date_from'] == '2021-04-01'

        return mockserver.make_response(status=200, json=yadoc_response)

    get_taxi_corp_contracts.set_response(200, CONTRACTS_RESPONSE)

    response = await taxi_cargo_corp.get(
        '/internal/cargo-corp/v1/client/documents/list',
        headers={'X-B2B-Client-Id': utils.CORP_CLIENT_ID},
    )

    assert response.status_code == 200
    response_json = response.json()

    assert response_json == {
        'months': [
            {
                'year': 2021,
                'month_name': get_translation('month.12'),
                'month': '2021-12',
                'amount': 241.1,
            },
            {
                'year': 2021,
                'month_name': get_translation('month.05'),
                'month': '2021-05',
            },
        ],
    }


async def test_documents_urls(
        taxi_cargo_corp, mockserver, get_taxi_corp_contracts, load_json,
):
    yadoc_response = load_json('yadoc_responses.json')['urls_response']

    @mockserver.json_handler('/yadoc/public/api/v1/documents')
    def _list_handler(request):
        assert request.json['doc_type'] == ['ACT', 'INV', 'AGENT_REP']
        assert request.json['date_from'] == '2021-12-01'
        assert request.json['date_to'] == '2021-12-31'

        return mockserver.make_response(status=200, json=yadoc_response)

    @mockserver.json_handler(
        r'/yadoc/public/api/documents/(?P<doc_id>\d+)/url', regex=True,
    )
    def _download_handler(request, doc_id):
        return mockserver.make_response(
            status=200,
            json={
                'url': f'/some/url/to/doc/{doc_id}',
                'expires_at': DATETIME_STRING,
            },
        )

    get_taxi_corp_contracts.set_response(200, CONTRACTS_RESPONSE)

    response = await taxi_cargo_corp.get(
        '/internal/cargo-corp/v1/client/documents/urls',
        headers={'X-B2B-Client-Id': utils.CORP_CLIENT_ID},
        params={'month': '2021-12'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'urls': [
            {
                'url': '/some/url/to/doc/0',
                'expires_at': DATETIME_STRING,
                'doc_name': 'Акт - 1',
                'doc_date': '2021-12-02',
            },
            {
                'url': '/some/url/to/doc/1',
                'expires_at': DATETIME_STRING,
                'doc_name': 'Акт - 2',
                'doc_date': '2021-12-10',
            },
            {
                'url': '/some/url/to/doc/2',
                'expires_at': DATETIME_STRING,
                'doc_name': 'Акт - 3',
                'doc_date': '2021-11-02',
            },
            {
                'url': '/some/url/to/doc/3',
                'expires_at': DATETIME_STRING,
                'doc_name': 'Счет-фактура - 1',
                'doc_date': '2021-12-02',
            },
            {
                'url': '/some/url/to/doc/4',
                'expires_at': DATETIME_STRING,
                'doc_name': 'Отчет агента - 1',
                'doc_date': '2021-12-02',
            },
        ],
    }
