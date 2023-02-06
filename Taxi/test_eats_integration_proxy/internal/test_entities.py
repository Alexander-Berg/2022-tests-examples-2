import pytest

from eats_integration_proxy.internal import entities


@pytest.mark.parametrize(
    ('protocol', 'host', 'port', 'path', 'actual_url'),
    [
        ['https', 'example', None, '/', 'https://example/'],
        ['http', None, None, None, 'http://'],
        ['https', 'example', None, None, 'https://example'],
        ['https', 'example', None, '/test_path', 'https://example/test_path'],
        [None, 'example', None, '/', 'example/'],
        [None, 'example', 43, '/', 'example:43/'],
        ['http', 'example', 43, '/', 'http://example:43/'],
        ['http', 'example', 43, '/test_path', 'http://example:43/test_path'],
        [None, '$mockserver', 43, '/test_path', '$mockserver/test_path'],
        ['https', '$mockserver', None, None, '$mockserver'],
        ['https', '$mockserver', None, '/test_path', '$mockserver/test_path'],
    ],
)
async def test_partner_full_qualified_url(
        protocol, host, port, path, actual_url,
):
    partner = entities.Partner(
        brand_id='',
        slug='',
        protocol=protocol,
        host=host,
        port=port,
        login=None,
        password=None,
        token=None,
    )

    assert partner.full_qualified_url(path) == actual_url
