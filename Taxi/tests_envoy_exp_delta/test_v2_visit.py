import pytest


def tpl(**kwargs):
    return tuple(kwargs.values())


@pytest.mark.parametrize(
    ['dest', 'info'],
    [
        tpl(dest=[], info=[{'key': 'service', 'value': 'delta'}]),
        tpl(
            dest=['bravo'],
            info=[
                {'key': 'service', 'value': 'delta'},
                {'key': 'error', 'value': '"dest" have to be empty'},
            ],
        ),
    ],
)
async def test_success(taxi_envoy_exp_delta, dest, info):
    response = await taxi_envoy_exp_delta.post('v2/visit', json={'dest': dest})
    assert response.status_code == 200
    assert response.json() == {'info': info}
