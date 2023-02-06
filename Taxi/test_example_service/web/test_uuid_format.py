import pytest

from . import common


@pytest.mark.parametrize(
    'params',
    [
        common.Params(
            {'uuid': '5a1795f67d384d268dd1694ffa3e2456'},
            200,
            {'uuid': '5a1795f67d384d268dd1694ffa3e2456', 'version': 4},
        ),
        common.Params(
            {'uuid': 'f1936e327e1f11eaad85acde48001122'},
            200,
            {'uuid': 'f1936e327e1f11eaad85acde48001122', 'version': 1},
        ),
        common.Params(
            {'uuid': '5a1795f67d384d268dd1694ffa3e6'},
            400,
            common.make_request_error(
                'Invalid value for uuid: failed to parse uuid.UUID from '
                '\'5a1795f67d384d268dd1694ffa3e6\'',
            ),
        ),
    ],
)
async def test_dates(web_app_client, params):
    response = await web_app_client.get('/uuid-echo', params=params.request)
    assert response.status == params.status
    assert await response.json() == params.response
