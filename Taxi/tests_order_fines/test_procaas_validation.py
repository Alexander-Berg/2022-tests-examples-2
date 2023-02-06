import pytest


async def test_validation_passed(load_json, validate):
    events = load_json('processing_events.json')
    result = await validate(events)
    assert result == {
        'operation_id': events[-1]['payload']['data']['operation_id'],
        'current_decision': events[1]['payload']['data']['decision'],
        'new_decision': events[-1]['payload']['data']['decision'],
    }


async def test_validation_failed(load_json, validate):
    events = load_json('processing_events.json')[-1:]
    result = await validate(events)
    long_long_message = result['fail_reason']['message']
    assert result == {
        'operation_id': events[-1]['payload']['data']['operation_id'],
        'current_decision': {'has_fine': False},
        'fail_reason': {
            'code': 'race_condition',
            'message': long_long_message,
            'details': {},
        },
    }


@pytest.fixture(name='validate')
def _validate(taxi_order_fines, order_proc):
    async def _wrapper(events):
        response = await taxi_order_fines.post(
            '/procaas/fines/validate-update-request',
            params={'item_id': order_proc['_id']},
            json={'events': events},
        )
        assert response.status_code == 200
        return response.json()

    return _wrapper
