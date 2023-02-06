import datetime

import discounts_match  # pylint: disable=E0401
import pytest

from tests_eats_discounts import common

HEADERS = {
    'X-Ya-Service-Ticket': common.MOCK_SERVICE_TICKET,
    'X-Idempotency-Token': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
}


@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.config(
    DISCOUNTS_MATCH_CLOSE_RULES_SETTINGS={
        '__default__': {'close_after_sec': 10},
    },
    EATS_DISCOUNTS_DISCOUNTS_CREATE_SETTINGS={'max_discounts': 5},
    EATS_DISCOUNTS_PARTNERS_DISCOUNTS_FIND_SETTINGS={'max_discounts': 6},
)
async def test_partners_discounts_finish_ok(
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
        'v1/partners/discounts/finish',
        json=load_json('request.json'),
        headers=HEADERS,
    )
    assert response.status_code == 200, response.content
    assert not response.content or response.content == b'{}'

    response = await client.post(
        '/v1/partners/discounts/find',
        json=load_json('partners_discounts_find_request.json'),
        headers=headers,
    )

    assert response.status_code == 200, response.json()
    common.compare_admin_responses(
        response.json(), load_json('partners_discounts_find_response.json'),
    )


async def test_partners_discounts_finish_fail(client, load_json):
    response = await client.post(
        'v1/partners/discounts/finish',
        json=load_json('request.json'),
        headers=HEADERS,
    )
    assert response.status_code == 400


async def test_partners_discounts_finish_idempotency(client, testpoint):
    @testpoint('idempotency_tp')
    async def idempotency_tp(data):
        pass

    request = {
        'discounts_data': [
            {'discount_id': '1', 'hierarchy_name': 'place_cashback'},
        ],
        'partner_user_id': 'another_partner_user_id',
    }
    headers = HEADERS
    response = await client.post(
        'v1/partners/discounts/finish', json=request, headers=headers,
    )
    assert response.status_code == 200, response.content
    assert not response.content or response.content == b'{}'
    assert idempotency_tp.times_called == 1

    response = await client.post(
        'v1/partners/discounts/finish', json=request, headers=headers,
    )
    assert response.status_code == 200, response.content
    assert not response.content or response.content == b'{}'
    assert idempotency_tp.times_called == 1
