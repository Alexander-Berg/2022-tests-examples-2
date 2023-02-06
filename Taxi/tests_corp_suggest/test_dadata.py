# pylint: disable=redefined-outer-name
import pytest

EMPTY_RESPONSE: dict = {'suggestions': []}
MOCK_RESPONSE = {
    'suggestions': [
        {
            'value': 'Рога и Копыта',
            'unrestricted_value': 'Рога и копыта',
            'data': {
                'hid': 'abc',
                'inn': '123',
                'kpp': '1234',
                'ogrn': '123',
                'ogrn_date': 1469998800000,
                'name': {
                    'latin': 'rogaikopita',
                    'full': 'рогаИкопыта',
                    'short': 'рогаИкопыта',
                    'full_with_opf': (
                        'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ '
                        'рогаИкопыта'
                    ),
                    'short_with_opf': 'ООО рогаИкопыта',
                },
                'okpo': '123',
                'okved': '123',
                'okved_type': '2014',
                'branch_type': 'MAIN',
                'address': {
                    'value': 'г Калуга, ул Вишневского, д 17, кв 55',
                    'unrestricted_value': (
                        '248007, Калужская обл, '
                        'г Калуга, ул Вишневского, д 17, кв 55'
                    ),
                    'data': {
                        'source': '',
                        'qc': '0',
                        'city': 'Калуга',
                        'city_with_type': 'г Калуга',
                        'street_with_type': 'ул Вишневского',
                        'house': '17',
                        'postal_code': '248007',
                    },
                },
                'management': None,
                'state': {
                    'actuality_date': 1469998800000,
                    'registration_date': 1469998800000,
                    'status': 'ACTIVE',
                    'liquidation_date': 1469999999999,
                },
                'type': 'LEGAL',
            },
        },
    ],
}
ERROR_RESPONSE = {
    'code': 'COUNTRY_IS_NOT_SUPPORTED',
    'message': 'Country kgz is not supported',
}


@pytest.mark.parametrize(
    'post_content, response_code, response_body',
    [
        pytest.param(
            {'query': 'inkram', 'country': 'rus'}, 200, EMPTY_RESPONSE,
        ),
        pytest.param(
            {'query': 'рога и копыта', 'country': 'rus'}, 200, MOCK_RESPONSE,
        ),
    ],
)
async def test_dadata_suggest(
        taxi_corp_suggest,
        mock_dadata_suggestions,
        post_content,
        response_code,
        response_body,
):
    if response_code == 200:
        mock_dadata_suggestions.data.suggest_response = response_body

    response = await taxi_corp_suggest.post(
        'corp-suggest/v1/dadata/suggest', json=post_content,
    )
    response_json = response.json()

    assert response.status == response_code, response_json
    assert response_json == response_body


async def test_dadata_errors(taxi_corp_suggest, mock_dadata_suggestions):
    mock_dadata_suggestions.data.dadata_error_code = 400

    response = await taxi_corp_suggest.post(
        'corp-suggest/v1/dadata/suggest',
        json={'country': 'rus', 'query': '123'},
    )
    response_json = response.json()

    assert response.status == 400, response_json
    assert response_json == {
        'code': 'DATA_SOURCE_ERROR',
        'message': 'Data source internal error',
    }
