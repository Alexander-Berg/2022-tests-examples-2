import pytest

from testsuite.utils import matching


async def test_validation_passed(load_json, validate):
    events = load_json('processing_events.json')
    result = await validate(events)
    assert result == {'operation_id': matching.AnyString()}


async def test_validation_failed(load_json, validate):
    events = load_json('processing_events.json')[-1:]
    result = await validate(events)
    long_long_message = result['fail_reason']['message']
    assert result == {
        'operation_id': matching.AnyString(),
        'fail_reason': {
            'code': 'race_condition',
            'message': long_long_message,
            'details': {},
        },
    }


@pytest.fixture(name='validate')
def _validate(taxi_cargo_finance):
    url = '/internal/cargo-finance/flow/performer/fines/func/validate-fine-update'  # noqa: E501

    async def _wrapper(events):
        response = await taxi_cargo_finance.post(
            url,
            params={'taxi_alias_id': 'alias_id_1'},
            json={'events': events},
        )
        assert response.status_code == 200
        return response.json()

    return _wrapper
