import datetime
from typing import Optional

import discounts_match  # pylint: disable=E0401
import pytest

from tests_eats_discounts import common


async def _check_discounts_create(
        client,
        stq,
        pgsql,
        load_json,
        request_file_name: str,
        response_file_name: str,
        expected_status_code: int,
        stq_times_called: int,
        task_status: Optional[str],
):
    response = await client.post(
        '/v1/partners/discounts/create',
        json=load_json(request_file_name),
        headers={
            'X-Ya-Service-Ticket': common.MOCK_SERVICE_TICKET,
            'X-Idempotency-Token': common.TASK_ID,
        },
    )

    expected_response = load_json(response_file_name)
    assert response.status_code == expected_status_code, response.json()
    assert response.json() == expected_response
    assert (
        stq['eats_discounts_discounts_create'].times_called == stq_times_called
    )
    task = common.get_task(common.TASK_ID, pgsql)
    if task_status is None:
        assert task is None
    else:
        assert task is not None and task['status'] == task_status


TEST_DISCOUNTS_CREATE_OK = (
    pytest.param(
        'place_cashback_request.json', 'response.json', id='place_cashback',
    ),
    pytest.param(
        'retail_menu_discounts_request.json',
        'response.json',
        id='retail_menu_discounts',
    ),
    pytest.param(
        'yandex_cashback_request.json', 'response.json', id='yandex_cashback',
    ),
    pytest.param(
        'place_menu_cashback_request.json',
        'response.json',
        id='place_menu_cashback',
    ),
    pytest.param(
        'place_delivery_discounts_request.json',
        'response.json',
        id='place_delivery_discounts_request',
    ),
)


@pytest.mark.parametrize(
    'request_file_name, response_file_name', TEST_DISCOUNTS_CREATE_OK,
)
@discounts_match.mark_now
async def test_partners_discounts_create_ok(
        client,
        stq,
        pgsql,
        load_json,
        request_file_name: str,
        response_file_name: str,
):
    await _check_discounts_create(
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


TEST_DISCOUNTS_CREATE_FAIL_VALIDATION = (
    pytest.param(
        'too_many_discounts_request.json',
        'too_many_discounts_response.json',
        id='too_many_discounts',
    ),
    pytest.param(
        'place_cashback_no_place_request.json',
        'no_place_response.json',
        id='place_cashback_no_place',
    ),
    pytest.param(
        'yandex_cashback_no_place_request.json',
        'no_place_response.json',
        id='yandex_cashback_no_place',
    ),
    pytest.param(
        'place_menu_cashback_no_place_request.json',
        'no_place_response.json',
        id='place_menu_cashback_no_place',
    ),
    pytest.param(
        'place_delivery_discounts_no_place_request.json',
        'no_place_response.json',
        id='place_delivery_no_place',
    ),
    pytest.param(
        'place_menu_cashback_no_product_request.json',
        'no_product_response.json',
        id='place_menu_cashback_no_product',
    ),
    pytest.param(
        'retail_menu_discounts_no_place_request.json',
        'no_place_response.json',
        id='retail_menu_discounts_no_place',
    ),
    pytest.param(
        'retail_menu_discounts_no_product_request.json',
        'no_product_response.json',
        id='retail_menu_discounts_no_product',
    ),
)


@pytest.mark.parametrize(
    'request_file_name, response_file_name',
    TEST_DISCOUNTS_CREATE_FAIL_VALIDATION,
)
@pytest.mark.config(
    EATS_DISCOUNTS_DISCOUNTS_CREATE_SETTINGS={'max_discounts': 2},
)
@discounts_match.mark_now
async def test_partners_discounts_create_fail_validation(
        client,
        stq,
        pgsql,
        load_json,
        request_file_name: str,
        response_file_name: str,
):
    await _check_discounts_create(
        client,
        stq,
        pgsql,
        load_json,
        request_file_name,
        response_file_name,
        400,
        0,
        None,
    )


@discounts_match.mark_now
async def test_partners_discounts_create_planned_twice(
        client, mocked_time, stq, pgsql, testpoint, load_json,
):
    request_file_name = 'place_cashback_request.json'
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
            assert stq['eats_discounts_discounts_create'].times_called == 0
            old_planned_task = common.get_task(common.TASK_ID, pgsql)
            assert old_planned_task['status'] == 'planned'

            await _check_discounts_create(
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
            assert stq['eats_discounts_discounts_create'].times_called == 0
            task = common.get_task(common.TASK_ID, pgsql)
            assert task.pop('modified_at') != old_planned_task.pop(
                'modified_at',
            )
            assert task == old_planned_task

    await _check_discounts_create(
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
async def test_partners_discounts_create_plan_started_fail(
        client, mocked_time, stq, pgsql, testpoint, load_json, status: str,
):
    request_file_name = 'place_cashback_request.json'
    response_file_name = 'response.json'

    @testpoint('planned_before_call_tp')
    async def planned_before_call_tp(data):
        nonlocal request_file_name
        nonlocal response_file_name
        now = mocked_time.now()
        now += datetime.timedelta(seconds=1)
        mocked_time.set(now)
        assert stq['eats_discounts_discounts_create'].times_called == 0
        task = common.get_task(common.TASK_ID, pgsql)
        assert task['status'] == 'planned'
        common.set_task_status(common.TASK_ID, status, pgsql)
        await _check_discounts_create(
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

    await _check_discounts_create(
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


TEST_DISCOUNTS_CREATE_QUEUE_OK = (
    pytest.param('place_cashback_request.json', id='place_cashback'),
    pytest.param(
        'retail_menu_discounts_request.json', id='retail_menu_discounts',
    ),
    pytest.param('yandex_cashback_request.json', id='yandex_cashback'),
    pytest.param('place_menu_cashback_request.json', id='place_menu_cashback'),
)


@pytest.mark.parametrize(['request_file_name'], TEST_DISCOUNTS_CREATE_QUEUE_OK)
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
async def test_partners_discounts_create_queue_ok(
        stq_runner, pgsql, mocked_time, load_json, request_file_name: str,
):
    common.plan_task(common.TASK_ID, pgsql, mocked_time.now())
    await common.partners_discounts_create(
        stq_runner,
        pgsql,
        load_json(request_file_name),
        common.TASK_ID,
        'finished',
    )

    task = common.get_task(common.TASK_ID, pgsql)
    assert task is not None

    task_result = task.get('task_result')
    assert task_result is not None

    create_discounts = task_result.get('create_discounts')
    assert create_discounts is not None

    inserted_discount_ids = create_discounts.get('inserted_discount_ids')
    assert inserted_discount_ids is not None

    assert len(inserted_discount_ids) == 1

    affected_discount_ids = create_discounts.get('affected_discount_ids')
    if affected_discount_ids is not None:
        assert len(affected_discount_ids) >= 1


TEST_DISCOUNTS_CREATE_QUEUE_FAIL_VALIDATION = (
    pytest.param('too_many_discounts_request.json', id='too_many_discounts'),
    pytest.param(
        'place_cashback_no_place_request.json', id='place_cashback_no_place',
    ),
    pytest.param(
        'yandex_cashback_no_place_request.json', id='yandex_cashback_no_place',
    ),
    pytest.param(
        'place_menu_cashback_no_place_request.json',
        id='place_menu_cashback_no_place',
    ),
    pytest.param(
        'place_menu_cashback_no_product_request.json',
        id='place_menu_cashback_no_product',
    ),
    pytest.param(
        'retail_menu_discounts_no_place_request.json',
        id='retail_menu_discounts_no_place',
    ),
    pytest.param(
        'retail_menu_discounts_no_product_request.json',
        id='retail_menu_discounts_no_product',
    ),
    pytest.param(
        'place_delivery_discounts_no_place_request.json',
        id='place_delivery_discounts_no_place',
    ),
)


@pytest.mark.parametrize(
    'request_file_name', TEST_DISCOUNTS_CREATE_QUEUE_FAIL_VALIDATION,
)
@pytest.mark.config(
    EATS_DISCOUNTS_DISCOUNTS_CREATE_SETTINGS={'max_discounts': 2},
)
@discounts_match.mark_now
async def test_partners_discounts_create_queue_fail_validation(
        client,
        stq_runner,
        pgsql,
        mocked_time,
        load_json,
        request_file_name: str,
):
    common.plan_task(common.TASK_ID, pgsql, mocked_time.now())
    await common.partners_discounts_create(
        stq_runner,
        pgsql,
        load_json(request_file_name),
        common.TASK_ID,
        'failed',
        'error',
    )


async def test_partners_discounts_create_queue_fail_parse(
        client, stq_runner, pgsql, mocked_time,
):
    common.plan_task(common.TASK_ID, pgsql, mocked_time.now())
    await common.partners_discounts_create(
        stq_runner,
        pgsql,
        {'partner_user_id': 'some_partner_user_id'},
        common.TASK_ID,
        'failed',
        'parse_error',
    )


@pytest.mark.config(
    EATS_DISCOUNTS_DISCOUNTS_CREATE_SETTINGS={'max_discounts': 2},
)
@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_partners_discounts_create_queue_fail_self_intersection(
        client, stq_runner, pgsql, mocked_time, load_json,
):
    common.plan_task(common.TASK_ID, pgsql, mocked_time.now())
    await common.partners_discounts_create(
        stq_runner,
        pgsql,
        load_json('self_intersecting_request.json'),
        common.TASK_ID,
        'failed',
        'self_intersection_error',
    )


@pytest.mark.config(
    EATS_DISCOUNTS_DISCOUNTS_CREATE_SETTINGS={'max_discounts': 2},
)
@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_partners_discounts_create_queue_fail_intersection(
        client, stq_runner, pgsql, mocked_time, load_json,
):
    common.plan_task(common.TASK_ID, pgsql, mocked_time.now())
    await common.partners_discounts_create(
        stq_runner,
        pgsql,
        load_json('intersecting_request.json'),
        common.TASK_ID,
        'finished',
    )

    task_id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaab'
    common.plan_task(task_id, pgsql, mocked_time.now())
    await common.partners_discounts_create(
        stq_runner,
        pgsql,
        load_json('intersecting_request.json'),
        task_id,
        'failed',
        'intersection_error',
    )

    task = common.get_task(task_id, pgsql)
    assert task is not None

    task_result = task.get('task_result')
    assert task_result is not None

    create_discounts = task_result.get('create_discounts')
    assert create_discounts is not None

    affected_discount_ids = create_discounts.get('affected_discount_ids')
    assert affected_discount_ids is not None
    assert len(affected_discount_ids) == 1


@pytest.mark.parametrize(
    'error_type',
    (
        pytest.param('discounts_lib_error'),
        pytest.param('discounts_match_lib_error'),
    ),
)
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
async def test_partners_discounts_create_queue_fail(
        stq_runner, testpoint, pgsql, mocked_time, load_json, error_type: str,
):
    @testpoint('queue_error_tp')
    def queue_error_tp(data):
        return {error_type: True}

    common.plan_task(common.TASK_ID, pgsql, mocked_time.now())
    await common.partners_discounts_create(
        stq_runner,
        pgsql,
        load_json('place_cashback_request.json'),
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
async def test_partners_discounts_create_queue_start_started_fail(
        stq_runner, pgsql, mocked_time, load_json, status: str,
):
    common.plan_task(common.TASK_ID, pgsql, mocked_time.now())
    common.set_task_status(common.TASK_ID, status, pgsql)
    old_task = common.get_task(common.TASK_ID, pgsql)
    now = mocked_time.now()
    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)

    await common.partners_discounts_create(
        stq_runner,
        pgsql,
        load_json('place_cashback_request.json'),
        common.TASK_ID,
        status,
    )
    assert common.get_task(common.TASK_ID, pgsql) == old_task


@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
async def test_partners_discounts_create_queue_start_twice(
        stq_runner, testpoint, pgsql, mocked_time, load_json,
):
    request_file_name = 'place_cashback_request.json'
    called = False
    body = load_json(request_file_name)

    @testpoint('queue_tp')
    async def queue_tp(data):
        nonlocal body
        nonlocal called
        if not called:
            called = True
            await common.partners_discounts_create(
                stq_runner, pgsql, body, common.TASK_ID, 'finished',
            )

    @testpoint('queue_error_tp')
    def queue_error_tp(data):
        pass

    common.plan_task(common.TASK_ID, pgsql, mocked_time.now())
    await common.partners_discounts_create(
        stq_runner, pgsql, body, common.TASK_ID, 'finished',
    )
    assert queue_tp.times_called == 2
    assert queue_error_tp.times_called == 1


@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
async def test_partners_discounts_create_queue_start_missing(
        stq_runner, testpoint, pgsql, mocked_time, load_json,
):
    @testpoint('queue_tp')
    async def queue_tp(data):
        pass

    @testpoint('queue_error_tp')
    def queue_error_tp(data):
        pass

    await common.partners_discounts_create(
        stq_runner,
        pgsql,
        load_json('place_cashback_request.json'),
        common.TASK_ID,
        None,
    )
    assert queue_tp.times_called == 1
    assert queue_error_tp.times_called == 0
