import pytest


def _dict_ordered(obj):
    result = obj
    if isinstance(obj, dict):
        result = sorted(
            (key, _dict_ordered(value)) for key, value in obj.items()
        )
    if isinstance(obj, list):
        result = sorted(_dict_ordered(x) for x in obj)

    return result


def _prepare_response(response: dict) -> dict:
    response['tasks_status'].sort(key=lambda x: x['task_id'])
    return _dict_ordered(response)


@pytest.mark.config(
    EATS_DISCOUNTS_DISCOUNTS_GET_TASKS_STATUS_SETTINGS={'max_tasks': 8},
)
@pytest.mark.pgsql('eats_discounts', files=['init_tasks.sql'])
async def test_partners_discounts_get_tasks_status_ok(
        client, headers, load_json,
):
    response = await client.post(
        '/v1/partners/discounts/get-tasks-status/',
        json=load_json('request.json'),
        headers=headers,
    )

    expected_response = load_json('response_ok.json')
    assert response.status_code == 200, expected_response
    assert _prepare_response(response.json()) == _prepare_response(
        expected_response,
    )


@pytest.mark.config(
    EATS_DISCOUNTS_DISCOUNTS_GET_TASKS_STATUS_SETTINGS={'max_tasks': 4},
)
@pytest.mark.pgsql('eats_discounts', files=['init_tasks.sql'])
@pytest.mark.parametrize(
    ['request_filename', 'response_filename', 'expected_code'],
    [
        pytest.param(
            'request.json',
            'response_fail_bad_request.json',
            400,
            id='bad request fail',
        ),
        pytest.param(
            'request_fail_not_found.json',
            'response_fail_not_found.json',
            404,
            id='not found fail',
        ),
    ],
)
async def test_partners_discounts_get_tasks_status_fail(
        client,
        headers,
        load_json,
        request_filename,
        response_filename,
        expected_code,
):
    response = await client.post(
        '/v1/partners/discounts/get-tasks-status/',
        json=load_json(request_filename),
        headers=headers,
    )

    expected_response = load_json(response_filename)
    assert response.status_code == expected_code, expected_response
    assert response.json() == expected_response
