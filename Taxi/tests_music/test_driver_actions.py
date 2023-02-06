import pytest


DRIVER_AUTHORIZER_PARAMS = {'db': 'driver', 'session': 'driver_session1'}
DRIVER_UUID = 'id-2'

# add test schema for every test
# pylint: disable=invalid-name
pytestmark = [pytest.mark.pgsql('music', files=['music.sql'])]


@pytest.fixture(name='get_actions')
def _get_actions(taxi_music):
    async def _do(
            order_id, *, last_action_id=None, params=None, status_code=200,
    ):
        body = {'order_id': order_id}
        if last_action_id:
            body['last_action_id'] = last_action_id
        response = await taxi_music.post(
            'driver/music/getactions', json=body, params=params,
        )
        assert response.status_code == status_code
        return response

    return _do


@pytest.mark.config(TAXI_MUSIC_SERVICE_ENABLED=False)
async def test_service_disabled(get_actions, driver_authorizer):
    driver_authorizer.set_session('driver', 'driver_session1', DRIVER_UUID)
    await get_actions(
        'alias-id-2', params=DRIVER_AUTHORIZER_PARAMS, status_code=406,
    )


async def test_actions_switch_session(get_actions, driver_authorizer):
    driver_authorizer.set_session('driver', 'driver_session1', 'bad_uuid')
    response = await get_actions(
        'alias-id-2', params=DRIVER_AUTHORIZER_PARAMS, status_code=406,
    )
    assert response.json()['code'] == 'NotAcceptable'

    driver_authorizer.set_session('driver', 'driver_session1', DRIVER_UUID)
    response = await get_actions('alias-id-2', params=DRIVER_AUTHORIZER_PARAMS)
    content = response.json()
    assert len(content['actions']) == 4


@pytest.mark.driver_session(
    park_id='driver', session='driver_session1', uuid=DRIVER_UUID,
)
@pytest.mark.parametrize(
    'last_action_id, actions',
    [
        (None, ['play_music', 'pause', 'play', 'set_volume']),
        ('hex-id-2', ['play', 'set_volume']),
        ('hex-id-4', []),
    ],
)
async def test_actions_last_action(
        get_actions, driver_authorizer, last_action_id, actions,
):
    response = await get_actions(
        'alias-id-2',
        last_action_id=last_action_id,
        params=DRIVER_AUTHORIZER_PARAMS,
    )
    content = response.json()
    assert len(content['actions']) == len(actions)
    action_codes = [action['action_code'] for action in content['actions']]
    assert action_codes == actions


@pytest.mark.driver_session(
    park_id='driver', session='driver_session1', uuid=DRIVER_UUID,
)
@pytest.mark.parametrize(
    'expected_actions',
    [
        pytest.param(
            [], marks=pytest.mark.config(TAXI_MUSIC_RETURN_ALL_ACTIONS=False),
        ),
        pytest.param(
            ['play_music', 'pause', 'play', 'set_volume'],
            marks=pytest.mark.config(TAXI_MUSIC_RETURN_ALL_ACTIONS=True),
        ),
    ],
)
async def test_all_actions_on_config(
        get_actions, expected_actions, driver_authorizer,
):
    response = await get_actions(
        'alias-id-2',
        last_action_id='unknown-action-id',
        params=DRIVER_AUTHORIZER_PARAMS,
    )

    content = response.json()
    assert len(content['actions']) == len(expected_actions)
    given_actions = [action['action_code'] for action in content['actions']]
    assert given_actions == expected_actions
