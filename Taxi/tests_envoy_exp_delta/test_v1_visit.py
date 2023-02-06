import pytest


def tpl(**kwargs):
    return tuple(kwargs.values())


@pytest.mark.parametrize(
    ['visited', 'result'],
    [
        tpl(visited=[], result=['delta']),
        tpl(visited=['bravo'], result=['bravo', 'delta']),
    ],
)
async def test_success(taxi_envoy_exp_delta, visited, result):
    response = await taxi_envoy_exp_delta.post(
        'v1/visit', json={'visited': visited},
    )
    assert response.status_code == 200
    assert response.json() == {'visited': result}
