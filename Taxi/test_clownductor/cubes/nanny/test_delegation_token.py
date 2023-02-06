import pytest


@pytest.mark.parametrize(
    'use_cookies',
    [
        pytest.param(
            False,
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES={
                    'disable_cookies_delegation_token': True,
                },
            ),
            id='disable_cookies',
        ),
        pytest.param(True, id='with_cookies'),
    ],
)
async def test_delegation_token(
        nanny_mockserver,
        cookie_monster_mockserver,
        web_context,
        mockserver,
        use_cookies,
        get_cube,
):
    moster_handler = cookie_monster_mockserver()

    body = {
        'nanny_name': 'balancer_taxi_kitty_unstable',
        'secret_id': 'secret',
    }
    cube = get_cube('NannyGetDelegationToken', body)

    await cube.update()
    assert cube.success

    assert cube.data['payload'] == {'delegation_token': 'delegation_token_123'}
    assert nanny_mockserver.get_delegation_token.times_called == 1
    call = nanny_mockserver.get_delegation_token.next_call()
    if use_cookies:
        assert call.cookies
        assert moster_handler.times_called == 1
    else:
        assert not call.cookies
        assert not moster_handler.times_called
