import pytest


@pytest.mark.parametrize(
    'previous_action,action',
    [('standing', 'walking'), ('walking', 'running'), ('running', 'standing')],
)
async def test_sample_v1_action(taxi_userver_sample, previous_action, action):
    # Do a request to `userver-sample` handle `/sample/v1/action`.
    json = {'id': 'to_' + action, 'action': previous_action}
    response = await taxi_userver_sample.put('sample/v1/action', json=json)
    assert response.status_code == 200

    json['action'] = action
    response = await taxi_userver_sample.put('sample/v1/action', json=json)
    assert response.json() == {'previous_action': previous_action}
