import datetime
from typing import Optional

import discounts_match  # pylint: disable=E0401
import pytest

from tests_eats_discounts import common


async def _check_discounts_replace(
        client,
        stq,
        pgsql,
        load_json,
        request_file_name: str,
        response_file_name: str,
        expected_status_code: int,
        stq_times_called: int,
        task_status: Optional[str],
        task_id: Optional[str] = None,
):
    task_id = task_id if task_id is not None else common.TASK_ID
    request = load_json(request_file_name)
    response = await client.post(
        '/v1/robot/discounts/replace',
        json=request,
        headers={
            'X-Ya-Service-Ticket': common.MOCK_SERVICE_TICKET,
            'X-Idempotency-Token': task_id,
        },
    )

    expected_response = load_json(response_file_name)
    assert response.status_code == expected_status_code, response.json()
    assert response.json() == expected_response
    assert (
        stq['eats_discounts_robot_discounts_replace'].times_called
        == stq_times_called
    )
    task = common.get_task(task_id, pgsql)
    keys = list(map(str, request['places']))
    if task_status is None:
        assert task is None
        for key in keys:
            assert common.get_unique_task(key, 'robot_replace', pgsql) is None
    else:
        assert task is not None and task['status'] == task_status
        for key in keys:
            assert (
                common.get_unique_task(key, 'robot_replace', pgsql) == task_id
            )


async def _robot_discounts_replace(
        stq_runner,
        pgsql,
        service_name: str,
        body: dict,
        task_id: str,
        expected_task_status: Optional[str],
        expected_task_message: Optional[str] = None,
):
    await stq_runner.eats_discounts_robot_discounts_replace.call(
        task_id=task_id, kwargs={'body': body, 'service_name': service_name},
    )
    task = common.get_task(task_id, pgsql)
    if expected_task_status is None:
        assert task is None
    else:
        assert task is not None
        assert task['status'] == expected_task_status
        assert task.get('message') == expected_task_message


@discounts_match.mark_now
async def test_robot_discounts_replace_ok(client, stq, pgsql, load_json):
    await _check_discounts_replace(
        client,
        stq,
        pgsql,
        load_json,
        'request.json',
        'response.json',
        200,
        1,
        'planned',
    )


@discounts_match.mark_now
async def test_robot_discounts_replace_task_ok(client, stq, pgsql, load_json):
    await _check_discounts_replace(
        client,
        stq,
        pgsql,
        load_json,
        'request.json',
        'response.json',
        200,
        1,
        'planned',
    )
    await _check_discounts_replace(
        client,
        stq,
        pgsql,
        load_json,
        'replace_request.json',
        'replace_response.json',
        200,
        2,
        'planned',
        'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    )


@pytest.mark.config(
    EATS_DISCOUNTS_ROBOT_DISCOUNTS_REPLACE_SETTINGS={'max_discounts': 2},
)
@discounts_match.mark_now
async def test_robot_discounts_replace_fail_validation(
        client, stq, pgsql, load_json,
):
    await _check_discounts_replace(
        client,
        stq,
        pgsql,
        load_json,
        'too_many_discounts_request.json',
        'too_many_discounts_response.json',
        400,
        0,
        None,
    )


@discounts_match.mark_now
async def test_robot_discounts_replace_planned_twice(
        client, mocked_time, stq, pgsql, testpoint, load_json,
):
    request_file_name = 'request.json'
    response_file_name = 'response.json'

    call_count = 0
    old_planned_task = None

    @testpoint('planned_before_call_tp')
    async def planned_before_call_tp(data):
        nonlocal request_file_name
        nonlocal response_file_name
        nonlocal call_count
        nonlocal old_planned_task
        call_count += 1
        if call_count == 1:
            now = mocked_time.now()
            now += datetime.timedelta(seconds=1)
            mocked_time.set(now)
            assert (
                stq['eats_discounts_robot_discounts_replace'].times_called == 0
            )
            old_planned_task = common.get_task(common.TASK_ID, pgsql)
            assert old_planned_task['status'] == 'planned'

            await _check_discounts_replace(
                client,
                stq,
                pgsql,
                load_json,
                request_file_name,
                response_file_name,
                200,
                1,
                'planned',
            )
        elif call_count == 2:
            assert (
                stq['eats_discounts_robot_discounts_replace'].times_called == 0
            )
            task = common.get_task(common.TASK_ID, pgsql)
            assert task.pop('modified_at') != old_planned_task.pop(
                'modified_at',
            )
            assert task == old_planned_task

    await _check_discounts_replace(
        client,
        stq,
        pgsql,
        load_json,
        request_file_name,
        response_file_name,
        200,
        2,
        'planned',
    )
    assert planned_before_call_tp.times_called == 2


@pytest.mark.parametrize(
    'status',
    (
        pytest.param('started', id='started'),
        pytest.param('failed', id='failed'),
        pytest.param('finished', id='finished'),
        pytest.param('interrupted', id='interrupted'),
    ),
)
@discounts_match.mark_now
async def test_robot_discounts_replace_plan_started_fail(
        client, mocked_time, stq, pgsql, testpoint, load_json, status: str,
):
    request_file_name = 'request.json'
    response_file_name = 'response.json'

    @testpoint('planned_before_call_tp')
    async def planned_before_call_tp(data):
        nonlocal request_file_name
        nonlocal response_file_name
        now = mocked_time.now()
        now += datetime.timedelta(seconds=1)
        mocked_time.set(now)
        assert stq['eats_discounts_robot_discounts_replace'].times_called == 0
        task = common.get_task(common.TASK_ID, pgsql)
        assert task['status'] == 'planned'
        common.set_task_status(common.TASK_ID, status, pgsql)
        await _check_discounts_replace(
            client,
            stq,
            pgsql,
            load_json,
            request_file_name,
            response_file_name,
            200,
            0,
            status,
        )

    await _check_discounts_replace(
        client,
        stq,
        pgsql,
        load_json,
        request_file_name,
        response_file_name,
        200,
        1,
        status,
    )
    assert planned_before_call_tp.times_called == 1


@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
async def test_robot_discounts_replace_queue_ok(
        stq_runner, pgsql, mocked_time, load_json,
):
    request_file_name = 'request.json'
    common.plan_task(common.TASK_ID, pgsql, mocked_time.now())
    common.add_unique_task(common.TASK_ID, '1', 'robot_replace', pgsql)
    await _robot_discounts_replace(
        stq_runner,
        pgsql,
        'service_name',
        load_json(request_file_name),
        common.TASK_ID,
        'finished',
    )

    task = common.get_task(common.TASK_ID, pgsql)
    assert task is not None

    task_result = task.get('task_result')
    assert task_result is not None

    replace_discounts = task_result['replace_discounts']

    assert 'closed_discount_ids' not in replace_discounts

    create_discounts = replace_discounts['create_discounts']

    inserted_discount_ids = create_discounts['inserted_discount_ids']
    assert len(inserted_discount_ids) == 1

    assert 'affected_discount_ids' not in create_discounts


@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
async def test_robot_discounts_replace_queue_interrupted_ok(
        stq_runner, pgsql, mocked_time, load_json,
):
    request_file_name = 'request.json'
    task_id = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
    common.plan_task(common.TASK_ID, pgsql, mocked_time.now())
    common.plan_task(task_id, pgsql, mocked_time.now())
    common.add_unique_task(task_id, '1', 'robot_replace', pgsql)
    await _robot_discounts_replace(
        stq_runner,
        pgsql,
        'service_name',
        load_json(request_file_name),
        common.TASK_ID,
        'interrupted',
    )


@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
async def test_robot_discounts_replace_queue_partially_interrupted_ok(
        stq_runner, pgsql, mocked_time, load_json,
):
    request_file_name = 'partially_interrupted_request.json'
    task_id = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
    common.plan_task(common.TASK_ID, pgsql, mocked_time.now())
    common.plan_task(task_id, pgsql, mocked_time.now())
    common.add_unique_task(task_id, '1', 'robot_replace', pgsql)
    common.add_unique_task(common.TASK_ID, '2', 'robot_replace', pgsql)
    await _robot_discounts_replace(
        stq_runner,
        pgsql,
        'service_name',
        load_json(request_file_name),
        common.TASK_ID,
        'finished',
    )

    task = common.get_task(common.TASK_ID, pgsql)
    assert task is not None

    task_result = task.get('task_result')
    assert task_result is not None

    replace_discounts = task_result['replace_discounts']

    assert 'closed_discount_ids' not in replace_discounts

    create_discounts = replace_discounts['create_discounts']

    inserted_discount_ids = create_discounts['inserted_discount_ids']
    assert len(inserted_discount_ids) == 1

    assert 'affected_discount_ids' not in create_discounts


@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@pytest.mark.config(
    EATS_DISCOUNTS_PARTNERS_DISCOUNTS_FIND_SETTINGS={'max_discounts': 3},
)
@pytest.mark.config(
    EATS_DISCOUNTS_ROBOT_DISCOUNTS_REPLACE_SETTINGS={
        'max_discounts': 2,
        'replace_time_delta_sec': 17,
    },
)
@discounts_match.mark_now
async def test_robot_discounts_replace_queue_with_closing_ok(
        client, stq_runner, pgsql, mocked_time, load_json, headers,
):
    request = load_json('request.json')
    common.plan_task(common.TASK_ID, pgsql, mocked_time.now())
    common.add_unique_task(common.TASK_ID, '1', 'robot_replace', pgsql)
    await _robot_discounts_replace(
        stq_runner, pgsql, 'service_name', request, common.TASK_ID, 'finished',
    )

    response = await client.post(
        '/v1/partners/discounts/find',
        json=load_json('partners_discounts_find_request.json'),
        headers=headers,
    )

    assert response.status_code == 200, response.json()
    common.compare_admin_responses(
        response.json(), load_json('partners_discounts_find_response_1.json'),
    )

    now = mocked_time.now()
    now += datetime.timedelta(days=1)
    mocked_time.set(now)

    task_id = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
    common.plan_task(task_id, pgsql, mocked_time.now())
    common.add_unique_task(task_id, '1', 'robot_replace', pgsql)
    await _robot_discounts_replace(
        stq_runner, pgsql, 'service_name', request, task_id, 'finished',
    )

    response = await client.post(
        '/v1/partners/discounts/find',
        json=load_json('partners_discounts_find_request.json'),
        headers=headers,
    )

    assert response.status_code == 200, response.json()
    common.compare_admin_responses(
        response.json(), load_json('partners_discounts_find_response_2.json'),
    )

    task = common.get_task(task_id, pgsql)
    assert task is not None

    task_result = task.get('task_result')
    assert task_result is not None

    replace_discounts = task_result['replace_discounts']

    assert len(replace_discounts['closed_discount_ids']) == 1

    create_discounts = replace_discounts['create_discounts']

    inserted_discount_ids = create_discounts['inserted_discount_ids']
    assert len(inserted_discount_ids) == 1

    assert 'affected_discount_ids' not in create_discounts


@pytest.mark.config(
    EATS_DISCOUNTS_ROBOT_DISCOUNTS_REPLACE_SETTINGS={'max_discounts': 2},
)
@discounts_match.mark_now
async def test_robot_discounts_replace_queue_fail_validation(
        client, stq_runner, pgsql, mocked_time, load_json,
):
    common.plan_task(common.TASK_ID, pgsql, mocked_time.now())
    common.add_unique_task(common.TASK_ID, '1', 'robot_replace', pgsql)
    await _robot_discounts_replace(
        stq_runner,
        pgsql,
        'service_name',
        load_json('too_many_discounts_request.json'),
        common.TASK_ID,
        'failed',
        'error',
    )


async def test_robot_discounts_repalce_queue_fail_parse(
        client, stq_runner, pgsql, mocked_time,
):
    common.plan_task(common.TASK_ID, pgsql, mocked_time.now())
    common.add_unique_task(common.TASK_ID, '1', 'robot_replace', pgsql)
    await _robot_discounts_replace(
        stq_runner,
        pgsql,
        'service_name',
        {},
        common.TASK_ID,
        'failed',
        'parse_error',
    )


@pytest.mark.config(
    EATS_DISCOUNTS_ROBOT_DISCOUNTS_REPLACE_SETTINGS={'max_discounts': 2},
)
@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_robot_discounts_replace_queue_fail_self_intersection(
        client, stq_runner, pgsql, mocked_time, load_json,
):
    common.plan_task(common.TASK_ID, pgsql, mocked_time.now())
    common.add_unique_task(common.TASK_ID, '1', 'robot_replace', pgsql)
    await _robot_discounts_replace(
        stq_runner,
        pgsql,
        'service_name',
        load_json('self_intersecting_request.json'),
        common.TASK_ID,
        'failed',
        'self_intersection_error',
    )


@pytest.mark.parametrize(
    'error_type',
    (
        pytest.param('discounts_lib_error'),
        pytest.param('discounts_match_lib_error'),
    ),
)
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
async def test_robot_discounts_replace_queue_fail(
        stq_runner, testpoint, pgsql, mocked_time, load_json, error_type: str,
):
    @testpoint('queue_error_tp')
    def queue_error_tp(data):
        return {error_type: True}

    common.plan_task(common.TASK_ID, pgsql, mocked_time.now())
    common.add_unique_task(common.TASK_ID, '1', 'robot_replace', pgsql)
    await _robot_discounts_replace(
        stq_runner,
        pgsql,
        'service_name',
        load_json('request.json'),
        common.TASK_ID,
        'failed',
        'error',
    )
    assert queue_error_tp.times_called == 1


@pytest.mark.parametrize(
    'status',
    (
        pytest.param('failed', id='failed'),
        pytest.param('finished', id='finished'),
        pytest.param('interrupted', id='interrupted'),
    ),
)
@discounts_match.mark_now
async def test_robot_discounts_replace_queue_start_started_fail(
        stq_runner, pgsql, mocked_time, load_json, status: str,
):
    common.plan_task(common.TASK_ID, pgsql, mocked_time.now())
    common.add_unique_task(common.TASK_ID, '1', 'robot_replace', pgsql)
    common.set_task_status(common.TASK_ID, status, pgsql)
    old_task = common.get_task(common.TASK_ID, pgsql)
    now = mocked_time.now()
    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)

    await _robot_discounts_replace(
        stq_runner,
        pgsql,
        'service_name',
        load_json('request.json'),
        common.TASK_ID,
        status,
    )
    assert common.get_task(common.TASK_ID, pgsql) == old_task


@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
async def test_robot_discounts_replace_queue_start_twice(
        stq_runner, testpoint, pgsql, mocked_time, load_json,
):
    request_file_name = 'request.json'
    called = False
    body = load_json(request_file_name)

    @testpoint('queue_tp')
    async def queue_tp(data):
        nonlocal body
        nonlocal called
        if not called:
            called = True
            await _robot_discounts_replace(
                stq_runner,
                pgsql,
                'service_name',
                body,
                common.TASK_ID,
                'finished',
            )

    @testpoint('queue_error_tp')
    def queue_error_tp(data):
        pass

    common.plan_task(common.TASK_ID, pgsql, mocked_time.now())
    common.add_unique_task(common.TASK_ID, '1', 'robot_replace', pgsql)
    await _robot_discounts_replace(
        stq_runner, pgsql, 'service_name', body, common.TASK_ID, 'finished',
    )
    assert queue_tp.times_called == 2
    assert queue_error_tp.times_called == 1


@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
async def test_robot_discounts_replace_queue_start_missing(
        stq_runner, testpoint, pgsql, mocked_time, load_json,
):
    @testpoint('queue_tp')
    async def queue_tp(data):
        pass

    @testpoint('queue_error_tp')
    def queue_error_tp(data):
        pass

    await _robot_discounts_replace(
        stq_runner,
        pgsql,
        'service_name',
        load_json('request.json'),
        common.TASK_ID,
        None,
    )
    assert queue_tp.times_called == 1
    assert queue_error_tp.times_called == 0
