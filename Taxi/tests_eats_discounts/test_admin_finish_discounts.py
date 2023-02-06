import datetime

import discounts_match  # pylint: disable=E0401
import pytest

from tests_eats_discounts import common


def _prepare_check_response(response: dict) -> dict:
    response['lock_ids'].sort(key=lambda lock: lock['id'])
    return response


@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.config(
    DISCOUNTS_MATCH_CLOSE_RULES_SETTINGS={
        '__default__': {'close_after_sec': 10},
    },
    EATS_DISCOUNTS_DISCOUNTS_CREATE_SETTINGS={'max_discounts': 5},
    EATS_DISCOUNTS_ADMIN_MATCH_DISCOUNTS_SETTINGS={'max_discounts': 6},
)
async def test_admin_finish_discounts_ok(
        client, pgsql, stq_runner, load_json, mocked_time, headers,
):
    now = mocked_time.now()

    common.plan_task(common.TASK_ID, pgsql, now)
    await common.partners_discounts_create(
        stq_runner,
        pgsql,
        load_json('discounts_create_body.json'),
        common.TASK_ID,
        'finished',
    )

    finish_start_time = datetime.datetime(2020, 1, 1, 12, 0, 2)
    mocked_time.set(finish_start_time)

    response = await client.post(
        'v1/admin/finish-discounts',
        json=load_json('request.json'),
        headers=common.get_draft_headers(),
    )
    assert response.status_code == 200, response.content
    assert not response.content or response.content == b'{}'

    response = await client.post(
        '/v1/admin/match-discounts',
        json=load_json('admin_match_discounts_request.json'),
        headers=headers,
    )

    assert response.status_code == 200, response.json()
    common.compare_admin_responses(
        response.json(), load_json('admin_match_discounts_response.json'),
    )


async def test_admin_finish_discounts_fail(client, load_json):
    response = await client.post(
        'v1/admin/finish-discounts',
        json=load_json('request.json'),
        headers=common.get_draft_headers(),
    )
    assert response.status_code == 400


@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.config(
    DISCOUNTS_MATCH_CLOSE_RULES_SETTINGS={
        '__default__': {'close_after_sec': 10},
    },
    EATS_DISCOUNTS_DISCOUNTS_CREATE_SETTINGS={'max_discounts': 5},
    EATS_DISCOUNTS_ADMIN_MATCH_DISCOUNTS_SETTINGS={'max_discounts': 6},
)
async def test_admin_finish_discounts_check_ok(
        client, pgsql, stq_runner, load_json, mocked_time, headers,
):
    now = mocked_time.now()

    common.plan_task(common.TASK_ID, pgsql, now)
    await common.partners_discounts_create(
        stq_runner,
        pgsql,
        load_json('discounts_create_body.json'),
        common.TASK_ID,
        'finished',
    )

    finish_start_time = datetime.datetime(2020, 1, 1, 12, 0, 2)
    mocked_time.set(finish_start_time)

    response = await client.post(
        'v1/admin/finish-discounts/check',
        json=load_json('request.json'),
        headers=headers,
    )
    assert response.status_code == 200, response.json()
    assert _prepare_check_response(response.json()) == _prepare_check_response(
        load_json('response.json'),
    )

    response = await client.post(
        '/v1/admin/match-discounts',
        json=load_json('admin_match_discounts_request.json'),
        headers=headers,
    )

    assert response.status_code == 200, response.json()
    common.compare_admin_responses(
        response.json(), load_json('admin_match_discounts_response.json'),
    )


async def test_admin_finish_discounts_check_fail(client, load_json):
    response = await client.post(
        'v1/admin/finish-discounts/check',
        json=load_json('request.json'),
        headers=common.get_draft_headers(),
    )
    assert response.status_code == 400


async def test_admin_finish_discounts_idempotency(client, testpoint):
    @testpoint('idempotency_tp')
    async def idempotency_tp(data):
        pass

    request = {
        'discounts_data': [
            {'discount_id': '1', 'hierarchy_name': 'place_cashback'},
        ],
    }
    response = await client.post(
        'v1/admin/finish-discounts',
        json=request,
        headers=common.get_draft_headers(),
    )
    assert response.status_code == 200, response.content
    assert not response.content or response.content == b'{}'
    assert idempotency_tp.times_called == 1

    response = await client.post(
        'v1/admin/finish-discounts',
        json=request,
        headers=common.get_draft_headers(),
    )
    assert response.status_code == 200, response.content
    assert not response.content or response.content == b'{}'
    assert idempotency_tp.times_called == 1


async def test_admin_finish_discounts_check_idempotency(client, testpoint):
    @testpoint('idempotency_tp')
    async def idempotency_tp(data):
        pass

    request = {
        'discounts_data': [
            {'discount_id': '1', 'hierarchy_name': 'place_cashback'},
        ],
    }
    expected_response = {'data': request, 'lock_ids': []}

    response = await client.post(
        'v1/admin/finish-discounts/check',
        json=request,
        headers=common.get_headers(),
    )
    assert response.status_code == 200, response.json()
    assert response.json() == expected_response
    assert idempotency_tp.times_called == 1

    response = await client.post(
        'v1/admin/finish-discounts/check',
        json=request,
        headers=common.get_headers(),
    )
    assert response.status_code == 200, response.json()
    assert response.json() == expected_response
    assert idempotency_tp.times_called == 1


@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.config(
    DISCOUNTS_MATCH_CLOSE_RULES_SETTINGS={
        '__default__': {'close_after_sec': 10},
    },
    EATS_DISCOUNTS_DISCOUNTS_CREATE_SETTINGS={'max_discounts': 5},
    EATS_DISCOUNTS_ADMIN_MATCH_DISCOUNTS_SETTINGS={'max_discounts': 6},
    EATS_DISCOUNTS_FUNDED_HIERARCHIES=['place_cashback'],
)
async def test_admin_finish_discounts_funded_hierarchies(
        client, pgsql, stq_runner, load_json, mocked_time, headers,
):
    now = mocked_time.now()

    common.plan_task(common.TASK_ID, pgsql, now)
    await common.partners_discounts_create(
        stq_runner,
        pgsql,
        load_json('discounts_create_body.json'),
        common.TASK_ID,
        'finished',
    )
    finish_start_time = datetime.datetime(2020, 1, 1, 12, 0, 2)
    mocked_time.set(finish_start_time)

    response = await client.post(
        'v1/admin/finish-discounts/check',
        json=load_json('request.json'),
        headers=headers,
    )
    assert response.status_code == 200, response.json()
    assert _prepare_check_response(response.json()) == _prepare_check_response(
        load_json('response.json'),
    )

    response = await client.post(
        '/v1/admin/match-discounts',
        json=load_json('admin_match_discounts_request.json'),
        headers=headers,
    )

    assert response.status_code == 200, response.json()
    common.compare_admin_responses(
        response.json(), load_json('admin_match_discounts_response.json'),
    )
