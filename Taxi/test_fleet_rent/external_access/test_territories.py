from testsuite.utils import http

from fleet_rent.generated.web import web_context as context_module


async def test_fallback_access(
        web_context: context_module.Context,
        mock_territories,
        park_stub_factory,
):
    @mock_territories('/v1/countries/retrieve')
    async def _countries_retrieve(request: http.Request):
        assert request.json == {'_id': 'bel', 'projection': ['currency']}
        return {'_id': 'bel', 'currency': 'BYN'}

    territories_access = web_context.external_access.territories
    result = await territories_access.get_currency_by_country_id('bel')
    assert result == 'BYN'
