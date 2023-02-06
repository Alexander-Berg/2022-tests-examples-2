import pytest


def tpl(**kwargs):
    return tuple(kwargs.values())


@pytest.mark.parametrize(
    ['visited', 'result'],
    [
        tpl(visited=[], result=['charlie']),
        tpl(visited=['bravo'], result=['bravo', 'charlie']),
    ],
)
async def test_success(taxi_envoy_exp_charlie, visited, result):
    response = await taxi_envoy_exp_charlie.post(
        'v1/visit', json={'visited': visited},
    )
    assert response.status_code == 200
    assert response.json() == {'visited': result}
