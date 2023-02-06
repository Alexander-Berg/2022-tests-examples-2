import pytest


def tpl(**kwargs):
    return tuple(kwargs.values())


@pytest.mark.parametrize(
    ['dest', 'info'],
    [
        tpl(dest=[], info=[{'key': 'service', 'value': 'charlie'}]),
        tpl(
            dest=['bravo'],
            info=[
                {'key': 'service', 'value': 'charlie'},
                {'key': 'error', 'value': '"dest" have to be empty'},
            ],
        ),
    ],
)
async def test_success(taxi_envoy_exp_charlie, dest, info):
    response = await taxi_envoy_exp_charlie.post(
        'v2/visit', json={'dest': dest},
    )
    assert response.status_code == 200
    assert response.json() == {'info': info}
