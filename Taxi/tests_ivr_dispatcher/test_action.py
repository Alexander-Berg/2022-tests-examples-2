import copy

import pytest

OCTONODE_ACTION_RESULT = {
    'type': 'initial',
    'status': 'ok',
    'caller_number': '+79009999999',
    'called_number': '80085',
    'brand': 'vezet',
    'call_guid': 'some guid',
    'origin_called_number': '+79001234567',
}

NEW_SESSION_ID = 'c642b150-759a-4679-b614-52c8d7bc485d'


async def test_unknown_worker(taxi_ivr_dispatcher):
    request = {'session_id': NEW_SESSION_ID, 'action': OCTONODE_ACTION_RESULT}

    response = await taxi_ivr_dispatcher.post('/action', json=request)

    assert response.status == 400


@pytest.mark.now('2020-07-20T15:15:00+0300')
async def test_presaved_worker(taxi_ivr_dispatcher):
    session_id = '23498776-4444-3333-2222-123456789012'

    request = {'session_id': session_id, 'action': OCTONODE_ACTION_RESULT}

    response = await taxi_ivr_dispatcher.post('/action', json=request)

    assert response.status == 200, response.text
    assert response.json() == {
        'params': {'start_recording': False},
        'type': 'answer',
    }


async def test_new_worker(taxi_ivr_dispatcher, mongodb):
    action = copy.deepcopy(OCTONODE_ACTION_RESULT)
    action['called_number'] = '77777'
    request = {'session_id': NEW_SESSION_ID, 'action': action}

    response = await taxi_ivr_dispatcher.post('/action', json=request)

    assert response.status == 200, response.text
    assert response.json() == {
        'params': {'start_recording': False},
        'type': 'answer',
    }

    db_session_doc = mongodb.ivr_disp_sessions.find_one(
        {'_id': NEW_SESSION_ID},
    )
    assert db_session_doc['worker_id'] == 'test_worker'
