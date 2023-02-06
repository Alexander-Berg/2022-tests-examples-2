import pytest


@pytest.mark.parametrize(
    'body, status',
    [
        ({'old-style': '--abc--'}, 200),
        ({'old-style': 'abc--'}, 200),
        ({'old-style': 'abc'}, 200),
        ({'old-style': 'ab'}, 400),
        ({'anchored': 'abc'}, 200),
        ({'anchored': '--abc--'}, 400),
        ({'anchored': 'abc--'}, 400),
    ],
)
async def test(web_app_client, body, status):
    resp = await web_app_client.post('/patterns', json=body)
    assert resp.status == status
