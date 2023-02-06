import pytest


async def test_history_empty_params(taxi_parks_activation):
    response = await taxi_parks_activation.get(
        'v1/parks/activation/history', params={},
    )
    assert response.status_code == 200
    assert response.json() == {
        'parks_activation_history': [
            {
                'timestamp': '1970-01-15T03:56:08.000',
                'revision': 1,
                'park_id': 'park1',
                'field_name': 'field1',
                'value_before': 'val1',
                'value_after': 'val2',
            },
            {
                'timestamp': '1970-01-15T03:58:08.000',
                'revision': 2,
                'park_id': 'park1',
                'field_name': 'field1',
                'value_before': 'val2',
                'value_after': 'val1',
            },
            {
                'timestamp': '1970-01-15T03:58:08.001',
                'revision': 3,
                'park_id': 'park2',
                'field_name': 'deactivated',
                'value_after': 'true',
                'additional_data': {'reason': 'low balance', 'threshold': 1.0},
            },
            {
                'timestamp': '1970-01-15T03:58:09.001',
                'revision': 4,
                'park_id': 'park1',
                'field_name': 'deactivated',
                'value_after': 'true',
                'additional_data': {'reason': 'no active contracts'},
            },
            {
                'timestamp': '1970-01-15T03:58:10.001',
                'revision': 5,
                'park_id': 'park2',
                'field_name': 'deactivated',
                'value_after': 'false',
            },
        ],
    }


async def test_history_filter_park(taxi_parks_activation):
    response = await taxi_parks_activation.get(
        'v1/parks/activation/history', params={'park_id': 'park2'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'parks_activation_history': [
            {
                'timestamp': '1970-01-15T03:58:08.001',
                'revision': 3,
                'park_id': 'park2',
                'field_name': 'deactivated',
                'value_after': 'true',
                'additional_data': {'reason': 'low balance', 'threshold': 1.0},
            },
            {
                'timestamp': '1970-01-15T03:58:10.001',
                'revision': 5,
                'park_id': 'park2',
                'field_name': 'deactivated',
                'value_after': 'false',
            },
        ],
    }


async def test_history_filter_time(taxi_parks_activation):
    response = await taxi_parks_activation.get(
        'v1/parks/activation/history',
        params={
            'time_from': '1970-01-15T03:58:08.000',
            'time_to': '1970-01-15T03:58:09.001',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'parks_activation_history': [
            {
                'timestamp': '1970-01-15T03:58:08.000',
                'revision': 2,
                'park_id': 'park1',
                'field_name': 'field1',
                'value_before': 'val2',
                'value_after': 'val1',
            },
            {
                'timestamp': '1970-01-15T03:58:08.001',
                'revision': 3,
                'park_id': 'park2',
                'field_name': 'deactivated',
                'value_after': 'true',
                'additional_data': {'reason': 'low balance', 'threshold': 1.0},
            },
            {
                'timestamp': '1970-01-15T03:58:09.001',
                'revision': 4,
                'park_id': 'park1',
                'field_name': 'deactivated',
                'value_after': 'true',
                'additional_data': {'reason': 'no active contracts'},
            },
        ],
    }


async def test_history_offset_limit(taxi_parks_activation):
    response = await taxi_parks_activation.get(
        'v1/parks/activation/history', params={'offset': 1, 'limit': 2},
    )
    assert response.status_code == 200
    assert response.json() == {
        'parks_activation_history': [
            {
                'timestamp': '1970-01-15T03:58:08.000',
                'revision': 2,
                'park_id': 'park1',
                'field_name': 'field1',
                'value_before': 'val2',
                'value_after': 'val1',
            },
            {
                'timestamp': '1970-01-15T03:58:08.001',
                'revision': 3,
                'park_id': 'park2',
                'field_name': 'deactivated',
                'value_after': 'true',
                'additional_data': {'reason': 'low balance', 'threshold': 1.0},
            },
        ],
    }


async def test_history_park_offset_limit(taxi_parks_activation):
    response = await taxi_parks_activation.get(
        'v1/parks/activation/history',
        params={'park_id': 'park1', 'offset': 1, 'limit': 1},
    )
    assert response.status_code == 200
    assert response.json() == {
        'parks_activation_history': [
            {
                'timestamp': '1970-01-15T03:58:08.000',
                'revision': 2,
                'park_id': 'park1',
                'field_name': 'field1',
                'value_before': 'val2',
                'value_after': 'val1',
            },
        ],
    }


@pytest.mark.config(
    PARKS_ACTIVATION_UPDATES_HANDLER={
        'max_answer_count': 1000,
        'get_park_updates_db_timeout_ms': 250,
    },
    PARKS_ACTIVATION_HISTORY_HANDLER={
        'max_answer_count': 1,
        'get_park_history_db_timeout_ms': 250,
    },
)
async def test_history_park_offset_limit_config(taxi_parks_activation):
    response = await taxi_parks_activation.get(
        'v1/parks/activation/history',
        params={'park_id': 'park1', 'offset': 1},
    )
    assert response.status_code == 200
    assert response.json() == {
        'parks_activation_history': [
            {
                'timestamp': '1970-01-15T03:58:08.000',
                'revision': 2,
                'park_id': 'park1',
                'field_name': 'field1',
                'value_before': 'val2',
                'value_after': 'val1',
            },
        ],
    }
