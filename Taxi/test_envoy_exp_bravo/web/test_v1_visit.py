import pytest


def tpl(**kwargs):
    return tuple(kwargs.values())


@pytest.mark.parametrize(
    ['visited', 'result'],
    [
        tpl(visited=[], result=['bravo']),
        tpl(visited=['alpha'], result=['alpha', 'bravo']),
    ],
)
async def test_success_dst_empty(taxi_envoy_exp_bravo_web, visited, result):
    response = await taxi_envoy_exp_bravo_web.post(
        '/v1/visit', json={'destinations': [], 'visited': visited},
    )
    assert response.status == 200

    content = await response.json()
    assert content == {'visited': result}


@pytest.mark.parametrize(
    ['destination', 'visited', 'result'],
    [
        tpl(dst='charlie', vis=[], res=['bravo', 'charlie']),
        tpl(dst='charlie', vis=['alpha'], res=['alpha', 'bravo', 'charlie']),
        tpl(dst='delta', vis=[], res=['bravo', 'delta']),
        tpl(dst='delta', vis=['alpha'], res=['alpha', 'bravo', 'delta']),
    ],
)
async def test_success_dst_nonempty(
        taxi_envoy_exp_bravo_web, mockserver, destination, visited, result,
):
    @mockserver.json_handler(f'/envoy-exp-{destination}/v1/visit')
    async def _handler(request):
        return {'visited': request.json['visited'] + [destination]}

    response = await taxi_envoy_exp_bravo_web.post(
        '/v1/visit', json={'destinations': [destination], 'visited': visited},
    )
    assert _handler.times_called == 1
    assert response.status == 200

    content = await response.json()
    assert content == {'visited': result}
