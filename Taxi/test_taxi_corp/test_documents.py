# pylint: disable=redefined-outer-name

import datetime

import pytest

NOW = datetime.date.fromisoformat('2021-04-10')
CORP_YADOC_ACT_SLUGS = {'rus': {'language': 'ru', 'slug': 'campaign-slug'}}

CONTRACT_ID = '951088/20'

CLIENT_RESPONSE = {'name': 'The Boring Company', 'country': 'rus'}
CONTRACTS_RESPONSE = {
    'contracts': [{'contract_id': 7800, 'external_id': CONTRACT_ID}],
}
MANAGERS_RESPONSE = {
    'managers': [
        {
            'contracts': [
                {
                    'contract_id': CONTRACT_ID,
                    'services': ['drive', 'taxi', 'cargo', 'eats2'],
                },
            ],
            'manager': {
                'name': 'Анастасия Чернова',
                'phone': '+7 499 705 5555',
                'mobile_phone': '',
                'extension': '67461',
                'email': 'anvchernova@ybs.yandex.ru',
                'tier': 'SMB',
            },
        },
    ],
}


@pytest.fixture
def mock_yadoc(mockserver):

    documents = [
        {
            'doc_type': 'ACT',
            'doc_date': '2021-01-15',
            'doc_id': 100,
            'doc_number': 'N1',
            'reversed_flag': False,
            'edo_enabled_flag': False,
            'delivery_statuses': [
                {'channel': 'EMAIL', 'sent_date': '2021-10-27T10:53:47.286Z'},
            ],
        },
        {
            'doc_type': 'ACT',
            'doc_date': '2021-01-15',
            'doc_id': 200,
            'doc_number': 'N2',
            'reversed_flag': False,
            'edo_enabled_flag': False,
            'delivery_statuses': [
                {'channel': 'EMAIL', 'sent_date': '2021-10-27T10:53:47.286Z'},
            ],
        },
        {
            'doc_type': 'ACT',
            'doc_date': '2021-02-15',
            'doc_id': 300,
            'doc_number': 'N3',
            'reversed_flag': False,
            'edo_enabled_flag': False,
            'delivery_statuses': [
                {'channel': 'EMAIL', 'sent_date': '2021-10-27T10:53:47.286Z'},
            ],
        },
        {
            'doc_type': 'ACT',
            'doc_date': '2021-01-15',
            'doc_id': 400,
            'doc_number': 'N4',
            'reversed_flag': False,
            'edo_enabled_flag': True,
            'delivery_statuses': [
                {'channel': 'EMAIL', 'sent_date': '2021-10-27T10:53:47.286Z'},
            ],
        },
        {
            'doc_type': 'ACT',
            'doc_date': '2021-01-15',
            'doc_id': 500,
            'doc_number': 'N5',
            'reversed_flag': False,
            'edo_enabled_flag': False,
            'delivery_statuses': [
                {'channel': 'string', 'sent_date': '2021-10-27T10:53:47.286Z'},
            ],
        },
        {
            'doc_type': 'ACT',
            'doc_date': '2018-04-15',
            'doc_id': 600,
            'doc_number': 'N6',
            'reversed_flag': False,
            'edo_enabled_flag': False,
            'delivery_statuses': [
                {'channel': 'EMAIL', 'sent_date': '2021-10-27T10:53:47.286Z'},
            ],
        },
        {
            'doc_type': 'ACT',
            'doc_date': '2018-03-15',
            'doc_id': 700,
            'doc_number': 'N7',
            'reversed_flag': False,
            'edo_enabled_flag': False,
            'delivery_statuses': [
                {'channel': 'EMAIL', 'sent_date': '2021-10-27T10:53:47.286Z'},
            ],
        },
        {
            'doc_type': 'ACT',
            'doc_date': '2021-01-15',
            'doc_id': 800,
            'doc_number': 'N8',
            'reversed_flag': False,
            'edo_enabled_flag': False,
            'delivery_statuses': None,
        },
        {
            'doc_type': 'ACT',
            'doc_date': '2021-02-15',
            'doc_id': 900,
            'doc_number': 'N9',
            'reversed_flag': False,
            'edo_enabled_flag': True,
            'delivery_statuses': None,
        },
        {
            'doc_type': 'ACT',
            'doc_date': '2021-03-10',
            'doc_id': 1000,
            'doc_number': 'N10',
            'reversed_flag': False,
            'edo_enabled_flag': True,
            'delivery_statuses': None,
        },
    ]

    class MockYadoc:
        @staticmethod
        @mockserver.json_handler('/yadoc/v1/documents')
        def get_documents(request):

            contract_id = request.json['contract_id']
            date_from = request.json['date_from']
            date_to = request.json['date_to']

            docs = []
            for doc in documents:
                doc_date = doc['doc_date']
                if date_from <= doc_date <= date_to:
                    docs.append(doc)

            contract = {'documents': docs}
            if docs:
                contract.update(
                    {
                        'date_from': date_from,
                        'date_to': date_to,
                        'party_id': '111',
                        'contract_id': contract_id,
                    },
                )
            response = {'content': [{'contracts': [contract]}]}
            return mockserver.make_response(json=response, status=200)

        @staticmethod
        @mockserver.json_handler('/yadoc/documents/{doc_id}/download')
        def download_document(request):
            return mockserver.make_response(json={}, status=200)

    return MockYadoc()


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    ['passport_mock', 'include_edo_doc_by_date'],
    [
        pytest.param('client1', False, id='common_path'),
        pytest.param(
            'client1',
            False,
            marks=pytest.mark.config(
                CORP_YADOC_EDO_ACT_DATES={'2021-03': '2021-04-15'},
            ),
            id='except-edo-doc-by-date',
        ),
        pytest.param(
            'client1',
            True,
            marks=pytest.mark.config(
                CORP_YADOC_EDO_ACT_DATES={'2021-03': '2021-04-05'},
            ),
            id='include-edo-doc-by-less-date',
        ),
        pytest.param(
            'client1',
            True,
            marks=pytest.mark.config(
                CORP_YADOC_EDO_ACT_DATES={'2021-03': '2021-04-10'},
            ),
            id='include-edo-doc-by-equal-date',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_get_documents(
        taxi_corp_real_auth_client,
        passport_mock,
        mock_yadoc,
        mock_corp_clients,
        include_edo_doc_by_date,
):
    mock_corp_clients.data.get_contracts_response = CONTRACTS_RESPONSE

    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/documents', params={'contract_id': 7800},
    )
    response_json = await response.json()
    assert response.status == 200, response_json

    expected_response = {
        'documents': [
            {'doc_date': '2021-01-15', 'doc_id': 100, 'doc_number': 'N1'},
            {'doc_date': '2021-01-15', 'doc_id': 200, 'doc_number': 'N2'},
            {'doc_date': '2021-02-15', 'doc_id': 300, 'doc_number': 'N3'},
            {'doc_date': '2021-01-15', 'doc_id': 400, 'doc_number': 'N4'},
            {'doc_date': '2018-04-15', 'doc_id': 600, 'doc_number': 'N6'},
            {'doc_date': '2021-02-15', 'doc_id': 900, 'doc_number': 'N9'},
        ],
    }
    if include_edo_doc_by_date:
        expected_response['documents'].append(
            {'doc_date': '2021-03-10', 'doc_id': 1000, 'doc_number': 'N10'},
        )
    assert response_json == expected_response

    assert mock_yadoc.get_documents.times_called == 1
    request = mock_yadoc.get_documents.next_call()['request'].json
    assert request == {
        'date_from': '2018-04-10',
        'date_to': '2021-04-10',
        'contract_id': ['7800'],
        'doc_type': ['ACT'],
        'exclude_reversed': True,
    }


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    ['passport_mock', 'email', 'contract_id', 'external_id', 'documents'],
    [
        pytest.param(
            'client1',
            'client1@yandex.ru',
            7800,
            CONTRACT_ID,
            [
                {'doc_date': '2021-01-15', 'doc_number': 'N2', 'doc_id': 200},
                {'doc_date': '2021-02-15', 'doc_number': 'N3', 'doc_id': 300},
            ],
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(CORP_YADOC_ACT_SLUGS=CORP_YADOC_ACT_SLUGS)
async def test_send_documents(
        patch,
        taxi_corp_real_auth_client,
        passport_mock,
        email,
        contract_id,
        external_id,
        documents,
        mock_corp_clients,
        mock_yadoc,
):
    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    mock_corp_clients.data.get_client_response = CLIENT_RESPONSE
    mock_corp_clients.data.get_contracts_response = CONTRACTS_RESPONSE
    mock_corp_clients.data.sf_managers_response = MANAGERS_RESPONSE

    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/client1/send_documents',
        params={'contract_id': 7800},
        json={'email': email, 'documents': documents},
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {}

    stq_calls = _put.calls
    assert len(stq_calls) == len(documents)
    for call in stq_calls:
        kwargs = call['kwargs']['kwargs']
        assert kwargs['email'] == email
        assert kwargs['external_id'] == external_id
        assert kwargs['country_settings'] == CORP_YADOC_ACT_SLUGS['rus']
        assert kwargs['client_name'] == CLIENT_RESPONSE['name']
        assert kwargs['manager'] == MANAGERS_RESPONSE['managers'][0]['manager']
        assert kwargs['document'] in documents
