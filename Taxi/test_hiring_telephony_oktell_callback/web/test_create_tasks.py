import pytest


@pytest.mark.parametrize(
    '_type, name, expected_status',
    [
        ('invalid', 'empty_list', 400),
        ('invalid', 'keys_1', 400),
        ('invalid', 'keys_2', 400),
        ('invalid', 'keys_3', 400),
        ('invalid', 'keys_4', 400),
        ('invalid', 'keys_5', 400),
        ('invalid', 'keys_6', 400),
        ('invalid', 'keys_7', 400),
        ('invalid', 'keys_8', 400),
        ('invalid', 'keys_9', 400),
        ('invalid', 'keys_10', 400),
        ('invalid', 'keys_11', 400),
        ('invalid', 'keys_12', 400),
        ('invalid', 'two_tasks_one_invalid', 400),
        ('invalid', 'two_tasks_equal_task_id', 200),
        ('valid', 'minimum', 200),
        ('valid', 'two_tasks', 200),
    ],
)
async def test_request(load_json, create_tasks, _type, name, expected_status):
    request = load_json('request_create_tasks.json')[_type][name]
    response = await create_tasks(request)
    assert response.status == expected_status
    if request['expected']:
        data = await response.json()
        assert data == request['expected']
