import aiohttp
import pytest

from taxi import config
from taxi.clients import dadata


@pytest.fixture(name='test_dada_client')
async def dada_client(loop, db, simple_secdist):
    session = aiohttp.ClientSession(loop=loop)
    yield dadata.DadataClient(
        config=config.Config(db), session=session, apikey='MOCK_KEY',
    )
    await session.close()


async def test_dadata(test_dada_client, patch_aiohttp_session, response_mock):
    response_example = {
        'suggestions': [
            {
                'value': 'ООО \'УК ЛОСОСИНА\'',
                'unrestricted_value': 'ООО \'УК ЛОСОСИНА\'',
                'data': {
                    'kpp': '270401001',
                    'capital': None,
                    'management': {
                        'name': 'Муркин Владимир Владимирович',
                        'post': 'ГЕНЕРАЛЬНЫЙ ДИРЕКТОР',
                        'disqualified': None,
                    },
                    'founders': None,
                    'managers': None,
                    'branch_type': 'MAIN',
                    'branch_count': 0,
                    'source': None,
                    'qc': None,
                    'hid': '07678111a25e0c56f5af8c01a4d16cd1944da24130e1f3f',
                    'type': 'ILLEGAL',
                    'state': {
                        'status': 'ACTIVE',
                        'actuality_date': 1577836800000,
                        'registration_date': 1401753600000,
                        'liquidation_date': None,
                    },
                    'opf': {
                        'type': '2014',
                        'code': '12300',
                        'full': 'Общество с неограниченной ответственностью',
                        'short': 'ООО',
                    },
                    'name': {
                        'full_with_opf': 'УПРАВЛЯЮЩАЯ КОМПАНИЯ ЛОСОСИНА',
                        'short_with_opf': 'ООО \'УК ЛОСОСИНА\'',
                        'latin': None,
                        'full': 'УПРАВЛЯЮЩАЯ КОМПАНИЯ ЛОСОСИНА',
                        'short': 'УК ЛОСОСИНА',
                    },
                    'inn': '0004023400',
                    'ogrn': '1142709000664',
                    'okpo': None,
                    'okved': '68.32.1',
                    'okveds': None,
                    'authorities': None,
                    'documents': None,
                    'licenses': None,
                    'finance': {
                        'tax_system': None,
                        'income': None,
                        'expense': None,
                        'debt': None,
                        'penalty': None,
                    },
                },
            },
        ],
    }

    @patch_aiohttp_session(
        'https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/party',
        'POST',
    )
    def _dadata_api(method, url, headers, json, **kwargs):
        assert method == 'post'
        assert (
            'suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/party' in url
        )
        assert headers.get('Authorization') == 'Token MOCK_KEY'
        assert json
        return response_mock(json=response_example, status=200)

    response = await test_dada_client.suggest(query='лососи', resource='party')
    assert response == response_example
    assert _dadata_api.calls


@pytest.mark.parametrize('response_code', [400, 500])
async def test_dadata_errors(
        test_dada_client, patch_aiohttp_session, response_mock, response_code,
):
    @patch_aiohttp_session(
        'https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/party',
        'POST',
    )
    def _dadata_api(method, url, headers, json, **kwargs):
        return response_mock(status=response_code)

    if response_code == 500:
        with pytest.raises(dadata.InternalServerError):
            await test_dada_client.suggest(query='лососи', resource='party')
    else:
        with pytest.raises(dadata.BadRequestError):
            await test_dada_client.suggest(query='лососи', resource='park')
