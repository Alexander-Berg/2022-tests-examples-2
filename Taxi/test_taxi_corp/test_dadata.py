# pylint: disable=redefined-outer-name
import copy

import pytest

MOCK_RESPONSE: dict = {'suggestions': []}
ENABLED_FORK = {'is_active': True, 'cities': ['Москва', 'Екатеринбург']}
DISABLED_FORK = {'is_active': False, 'cities': ['Москва', 'Екатеринбург']}

SUGGEST_RESPONSE = {
    'suggestions': [
        {
            'data': {'finance': None, 'type': 'LEGAL'},
            'unrestricted_value': 'WITHOUT_VAT 1',
            'value': 'WITHOUT_VAT 1',
        },
        {
            'data': {'finance': None, 'type': 'INDIVIDUAL'},
            'unrestricted_value': 'WITHOUT_VAT 2',
            'value': 'WITHOUT_VAT 2',
        },
        {
            'data': {'finance': {'tax_system': None}, 'type': 'INDIVIDUAL'},
            'unrestricted_value': 'WITHOUT_VAT 3',
            'value': 'WITHOUT_VAT 3',
        },
        {
            'data': {'finance': {'tax_system': None}, 'type': 'LEGAL'},
            'unrestricted_value': 'WITH VAT 1',
            'value': 'WITH VAT 1',
        },
        {
            'data': {'finance': None, 'type': 'LEGAL'},
            'unrestricted_value': 'WITH VAT 2',
            'value': 'WITH VAT 2',
        },
    ],
}


@pytest.mark.parametrize(
    'passport_mock, post_content, response_code, response_body',
    [
        pytest.param(
            'trial',
            {'query': 'inkram', 'resource': 'party'},
            200,
            MOCK_RESPONSE,
        ),
        pytest.param(
            'trial',
            {'lol': 'kek'},
            400,
            {
                'errors': [
                    {
                        'text': (
                            'Additional properties are not allowed '
                            '(\'lol\' was unexpected)'
                        ),
                        'code': 'GENERAL',
                    },
                    {
                        'text': '\'query\' is a required property',
                        'code': 'GENERAL',
                    },
                    {
                        'text': '\'resource\' is a required property',
                        'code': 'GENERAL',
                    },
                ],
                'message': 'Invalid input',
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'fields': [
                        {
                            'message': (
                                'Additional properties are not allowed '
                                '(\'lol\' was unexpected)'
                            ),
                            'code': 'REQUEST_VALIDATION_ERROR',
                            'path': [],
                        },
                        {
                            'message': '\'query\' is a required property',
                            'code': 'REQUEST_VALIDATION_ERROR',
                            'path': [],
                        },
                        {
                            'message': '\'resource\' is a required property',
                            'code': 'REQUEST_VALIDATION_ERROR',
                            'path': [],
                        },
                    ],
                },
            },
        ),
        pytest.param(
            'fake',
            {'query': 'inkram', 'resource': 'party'},
            401,
            {
                'errors': [
                    {'code': 'GENERAL', 'text': 'Yandex UID not found'},
                ],
                'message': 'Yandex UID not found',
                'code': 'GENERAL',
            },
        ),
    ],
    indirect=['passport_mock'],
)
async def test_suggest_handler(
        taxi_corp_real_auth_client,
        patch,
        passport_mock,
        post_content,
        response_code,
        response_body,
):
    @patch('taxi.clients.dadata.DadataClient.suggest')
    async def _suggest(*args, **kwargs):
        return MOCK_RESPONSE

    response = await taxi_corp_real_auth_client.post(
        '/1.0/dadata/suggest', json=post_content,
    )
    response_json = await response.json()

    assert response.status == response_code, response_json
    assert response_json == response_body


@pytest.mark.parametrize(
    'passport_mock', [pytest.param('trial')], indirect=['passport_mock'],
)
async def test_suggest(taxi_corp_real_auth_client, patch, passport_mock):
    @patch('taxi.clients.dadata.DadataClient.suggest')
    async def _suggest(*args, **kwargs):
        return SUGGEST_RESPONSE

    response = await taxi_corp_real_auth_client.post(
        '/1.0/dadata/suggest', json={'query': 'WITH', 'resource': 'party'},
    )
    response_json = await response.json()

    assert response.status == 200, response_json
    assert response_json == SUGGEST_RESPONSE


@pytest.mark.parametrize(
    ('passport_mock', 'inn', 'dadata_response'),
    [
        pytest.param(
            'trial',
            'WITHOUT_VAT 1',
            {
                'suggestions': [
                    {
                        'data': {
                            'finance': {'tax_system': 'USN'},
                            'type': 'LEGAL',
                        },
                        'unrestricted_value': 'WITHOUT_VAT 1',
                        'value': 'WITHOUT_VAT 1',
                    },
                ],
            },
            marks=pytest.mark.config(
                CORP_WITHOUT_VAT_FORK_CITIES=ENABLED_FORK,
            ),
        ),
        pytest.param(
            'trial',
            'WITHOUT_VAT 2',
            {
                'suggestions': [
                    {
                        'data': {'finance': None, 'type': 'INDIVIDUAL'},
                        'unrestricted_value': 'WITHOUT_VAT 2',
                        'value': 'WITHOUT_VAT 2',
                    },
                ],
            },
            marks=pytest.mark.config(
                CORP_WITHOUT_VAT_FORK_CITIES=ENABLED_FORK,
            ),
        ),
        pytest.param(
            'trial',
            'WITH_VAT',
            {
                'suggestions': [
                    {
                        'data': {
                            'finance': {'tax_system': None},
                            'type': 'LEGAL',
                        },
                        'unrestricted_value': 'WITH_VAT',
                        'value': 'WITH_VAT',
                    },
                ],
            },
            marks=pytest.mark.config(
                CORP_WITHOUT_VAT_FORK_CITIES=ENABLED_FORK,
            ),
        ),
        pytest.param(
            'trial2',
            'CITY_DISABLED_WITHOUT_VAT',
            {
                'suggestions': [
                    {
                        'data': {
                            'finance': {'tax_system': None},
                            'type': 'LEGAL',
                        },
                        'unrestricted_value': 'CITY_DISABLED_WITHOUT_VAT',
                        'value': 'CITY_DISABLED_WITHOUT_VAT',
                    },
                ],
            },
            marks=pytest.mark.config(
                CORP_WITHOUT_VAT_FORK_CITIES=ENABLED_FORK,
            ),
        ),
        pytest.param(
            'trial2',
            'WITHOUT_VAT_CONFIG_DISABLED',
            {
                'suggestions': [
                    {
                        'data': {'finance': None, 'type': 'INDIVIDUAL'},
                        'unrestricted_value': 'WITHOUT_VAT_CONFIG_DISABLED',
                        'value': 'WITHOUT_VAT_CONFIG_DISABLED',
                    },
                ],
            },
            marks=pytest.mark.config(
                CORP_WITHOUT_VAT_FORK_CITIES=DISABLED_FORK,
            ),
        ),
    ],
    indirect=['passport_mock'],
)
async def test_find_by_id(
        taxi_corp_real_auth_client, patch, passport_mock, inn, dadata_response,
):
    @patch('taxi.clients.dadata.DadataClient.find_by_id')
    async def _find_by_id(*args, **kwargs):
        return dadata_response

    response = await taxi_corp_real_auth_client.post(
        '/1.0/dadata/find_by_id', json={'query': inn, 'resource': 'party'},
    )
    response_json = await response.json()

    assert response.status == 200, response_json
    expected_response = copy.deepcopy(dadata_response)
    for x in expected_response['suggestions']:
        x['is_without_vat_allowed'] = x['value'].startswith('WITHOUT_VAT')
    assert response_json == expected_response
