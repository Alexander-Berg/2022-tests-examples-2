# pylint: disable=W0212
from unittest import mock

import pytest

from generated.models import tinkoff_secured as tinkoff_models
from taxi.clients_wrappers import tinkoff_secured


@pytest.fixture(autouse=True)
def tinkoff_service(mockserver_ssl):
    @mockserver_ssl.json_handler(
        r'/tinkoff-secured/api/v1/card/(?P<cid>\d+)/limits', regex=True,
    )
    # pylint: disable=W0612
    def get_card_limits(request, cid):
        cid = int(cid)
        return tinkoff_models.Limits(
            ucid=cid,
            spend_limit=tinkoff_models.LimitDescriptor(
                limit_period='IRREGULAR', limit_value=100, limit_remain=0,
            ),
            cash_limit=tinkoff_models.LimitDescriptor(
                limit_period='IRREGULAR', limit_value=0, limit_remain=0,
            ),
        ).serialize()


@pytest.mark.skip(reason='failing test, service out of exploitation')
@pytest.mark.config(
    SSL_CLIENT_CERTIFICATE_TINKOFF={
        'keyfile': 'TINKOFF_KEYFILE_CONTENT',
        'certfile': 'TINKOFF_CERTFILE_CONTENT',
    },
)
async def test_ssl_certs_retrieval_from_secdist(web_context):
    client = tinkoff_secured.TinkoffSecuredClient(web_context, {}, False)

    with mock.patch.object(
            client,
            '_load_secret_tmp_file',
            wraps=client._load_secret_tmp_file,
    ) as mocked:
        await client.get_limits(100500)
        mocked.assert_called()


@pytest.mark.skip(reason='failing test, service out of exploitation')
@pytest.mark.config(SSL_CLIENT_CERTIFICATE_TINKOFF={})
async def test_ssl_certs_not_configured(web_context):
    client = tinkoff_secured.TinkoffSecuredClient(web_context, {}, False)

    with mock.patch.object(
            client,
            '_load_secret_tmp_file',
            wraps=client._load_secret_tmp_file,
    ) as mocked:
        await client.get_limits(100500)
        mocked.assert_not_called()


@pytest.mark.skip(reason='failing test, service out of exploitation')
@pytest.mark.config(
    SSL_CLIENT_CERTIFICATE_TINKOFF={
        'keyfile': 'TINKOFF_KEYFILE_CONTENT',
        'certfile': 'KEY_NOT_EXISTS',
    },
)
async def test_ssl_certs_misconfigured(web_context):
    client = tinkoff_secured.TinkoffSecuredClient(web_context, {}, False)

    with mock.patch.object(
            client,
            '_load_secret_tmp_file',
            wraps=client._load_secret_tmp_file,
    ):
        await client.get_limits(100500)
