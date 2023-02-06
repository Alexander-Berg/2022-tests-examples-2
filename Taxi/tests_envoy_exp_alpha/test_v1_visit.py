import pytest


def tpl(**kwargs):
    return tuple(kwargs.values())


async def test_success_dst_empty(taxi_envoy_exp_alpha):
    response = await taxi_envoy_exp_alpha.post(
        'v1/visit', json={'destinations': []},
    )
    assert response.status_code == 200
    assert response.json() == {'visited': ['alpha']}


@pytest.mark.parametrize(
    ['destination', 'result'],
    [
        tpl(dst='bravo', result=['alpha', 'bravo']),
        tpl(dst='delta', result=['alpha', 'delta']),
    ],
)
async def test_success_dst_nonempty(
        taxi_envoy_exp_alpha, mockserver, destination, result,
):
    @mockserver.json_handler(f'/envoy-exp-{destination}/v1/visit')
    async def _handler(request):
        return {'visited': request.json['visited'] + [destination]}

    response = await taxi_envoy_exp_alpha.post(
        'v1/visit', json={'destinations': [destination]},
    )
    assert _handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'visited': result}
