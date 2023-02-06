import pytest

from eats_integration_proxy.generated.web import (
    web_context as web_context_module,
)
from eats_integration_proxy.internal import entities


@pytest.mark.parametrize(
    'partner_infos',
    [
        {
            ('brand_id1', 'partner1'): entities.Partner(
                id=1,
                slug='partner1',
                brand_id='brand_id1',
                protocol='http',
                host='asdf.ru',
                port=80,
                login='login',
                password='password',
                token='token',
                dek='l9x7iaLRHDKTthxawStCzHfaEDlTnjTlZI4c3dojwZKJRWpXt'
                'xb5WKVmNSvXizTOp/n9KnfS/1e6F6sylrttcA==',
            ),
        },
    ],
)
@pytest.mark.pgsql('eats_integration_proxy', files=['initialize.sql'])
async def test_should_rewrite_data_in_cache(
        partner_infos, web_context: web_context_module.Context, pgsql,
):
    assert web_context.update_cache.storage == partner_infos
