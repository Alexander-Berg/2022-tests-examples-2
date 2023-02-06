import datetime
import json
from typing import Union

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
    EATS_DISCOUNTS_PARTNERS_DISCOUNTS_FIND_SETTINGS={'max_discounts': 3},
    EATS_DISCOUNTS_MINIMUM_TIME_TO_VALIDATE=360,
    EATS_DISCOUNTS_PARTNERS_DISCOUNTS_MODIFY_SETTINGS={'modify_time_sec': 420},
)
@pytest.mark.parametrize(
    'request_file_name, find_discounts_response_file_name',
    (
        pytest.param(
            'modify_with_finish_request.json',
            'partners_discounts_find_with_finish_response.json',
            id='with_finish',
        ),
        pytest.param(
            'modify_auto_finish_request.json',
            'partners_discounts_find_auto_finish_response.json',
            id='auto_finish',
        ),
    ),
)
async def test_partners_discounts_modify_ok(
        client,
        pgsql,
        stq_runner,
        load_json,
        mocked_time,
        headers,
        request_file_name: str,
        find_discounts_response_file_name: str,
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

    modify_start_time = datetime.datetime(2020, 1, 1, 12, 0, 2)
    mocked_time.set(modify_start_time)

    response = await client.post(
        'v1/partners/discounts/modify',
        json=load_json(request_file_name),
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
        response.json(), load_json(find_discounts_response_file_name),
    )


@pytest.mark.parametrize(
    'request_file_name, response_file_name, expected_status_code',
    (
        pytest.param(
            'active_period_request.json',
            'active_period_response.json',
            400,
            id='active_period_present',
        ),
        pytest.param(
            'not_found_request.json',
            'not_found_response.json',
            404,
            id='not_found',
        ),
    ),
)
async def test_partners_discounts_modify_fail(
        client,
        load_json,
        headers,
        request_file_name: str,
        response_file_name: str,
        expected_status_code: int,
):
    response = await client.post(
        'v1/partners/discounts/modify',
        json=load_json(request_file_name),
        headers=HEADERS,
    )
    assert response.status_code == expected_status_code, response.json()
    assert response.json() == load_json(response_file_name)


@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.config(
    EATS_DISCOUNTS_MINIMUM_TIME_TO_VALIDATE=360,
    EATS_DISCOUNTS_PARTNERS_DISCOUNTS_MODIFY_SETTINGS={'modify_time_sec': 420},
)
async def test_partners_discounts_modify_idempotency(
        client, pgsql, stq_runner, load_json, mocked_time, testpoint,
):
    @testpoint('idempotency_tp')
    async def idempotency_tp(data):
        pass

    now = mocked_time.now()

    common.plan_task(common.TASK_ID, pgsql, now)
    await common.partners_discounts_create(
        stq_runner,
        pgsql,
        load_json('discounts_create_body.json'),
        common.TASK_ID,
        'finished',
    )

    request = load_json('modify_auto_finish_request.json')
    response = await client.post(
        'v1/partners/discounts/modify', json=request, headers=HEADERS,
    )
    assert response.status_code == 200, response.content
    assert not response.content or response.content == b'{}'
    assert idempotency_tp.times_called == 1

    response = await client.post(
        'v1/partners/discounts/modify', json=request, headers=HEADERS,
    )
    assert response.status_code == 200, response.content
    assert not response.content or response.content == b'{}'
    assert idempotency_tp.times_called == 1


@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.config(
    DISCOUNTS_MATCH_CLOSE_RULES_SETTINGS={
        '__default__': {'close_after_sec': 10},
    },
    EATS_DISCOUNTS_PARTNERS_DISCOUNTS_FIND_SETTINGS={'max_discounts': 3},
    EATS_DISCOUNTS_MINIMUM_TIME_TO_VALIDATE=360,
    EATS_DISCOUNTS_PARTNERS_DISCOUNTS_MODIFY_SETTINGS={'modify_time_sec': 420},
)
@pytest.mark.parametrize(
    'billing_get_response, modify_limit, status_or_response',
    (
        pytest.param(
            'billing_limits_first_response.json',
            {
                'currency': 'RUB',
                'closing_threshold': 10,
                'value': '700.0',
                'tickets': ['NEWDISCOUNTS-1'],
            },
            200,
            id='ok',
        ),
        pytest.param(
            'billing_limits_second_response.json',
            {
                'currency': 'RUB',
                'closing_threshold': 10,
                'value': '700.0',
                'tickets': ['NEWDISCOUNTS-1'],
            },
            'Limit changed, but id is not changed.',
            id='identical_reference',
        ),
        pytest.param(
            'billing_limits_first_response.json',
            {
                'currency': 'RUB',
                'closing_threshold': 10,
                'value': '800.0',
                'tickets': ['NEWDISCOUNTS-1'],
            },
            'Changing parameters for limit is forbidden.',
            id='change_value',
        ),
        pytest.param(
            'billing_limits_first_response.json',
            {
                'currency': 'USD',
                'closing_threshold': 10,
                'value': '700.0',
                'tickets': ['NEWDISCOUNTS-1'],
            },
            'Changing currency for limit is forbidden.',
            id='change_currency',
        ),
        pytest.param(
            'billing_limits_first_response.json',
            {'currency': 'USD', 'closing_threshold': 10, 'value': '700.0'},
            'You need to fill in at least one ticket for the limit.',
            id='without_tickets',
        ),
    ),
)
async def test_partners_discounts_modify_limit(
        client,
        mockserver,
        pgsql,
        stq_runner,
        load_json,
        mocked_time,
        headers,
        billing_get_response: str,
        modify_limit: dict,
        status_or_response: Union[int, dict],
):
    first_call_billing_create = True

    @mockserver.json_handler('/billing-limits/v1/create')
    def _billing_create_handler(request):
        nonlocal first_call_billing_create
        expected_request, response = (
            (
                'billing_limits_create_first_request.json',
                'billing_limits_first_response.json',
            )
            if first_call_billing_create
            else (
                'billing_limits_create_second_request.json',
                'billing_limits_second_response.json',
            )
        )
        first_call_billing_create = False
        billing_create_request = json.loads(request.get_data())
        assert billing_create_request == load_json(expected_request)
        return load_json(response)

    @mockserver.json_handler('/billing-limits/v1/get')
    def _billing_get_handler(request):
        billing_create_request = json.loads(request.get_data())
        assert billing_create_request == load_json(
            'billing_limits_get_request.json',
        )
        return load_json(billing_get_response)

    now = mocked_time.now()

    common.plan_task(common.TASK_ID, pgsql, now)
    await common.partners_discounts_create(
        stq_runner,
        pgsql,
        load_json('discounts_create_body_with_limit.json'),
        common.TASK_ID,
        'finished',
    )

    modify_start_time = datetime.datetime(2020, 1, 1, 12, 0, 2)
    mocked_time.set(modify_start_time)

    modify_request_json = load_json('modify_auto_finish_request.json')
    modify_request_json['new_discount_data']['discount_data']['data'][
        'discount'
    ]['limit'] = modify_limit
    response = await client.post(
        'v1/partners/discounts/modify',
        json=modify_request_json,
        headers=HEADERS,
    )
    if response.status_code != 200 and status_or_response != 200:
        assert json.loads(response.content)['message'] == status_or_response
        return
    assert response.status_code == 200, response.content
    assert not response.content or response.content == b'{}'

    response = await client.post(
        '/v1/partners/discounts/find',
        json=load_json('partners_discounts_find_with_limit_request.json'),
        headers=headers,
    )

    assert response.status_code == 200, response.json()
    common.compare_admin_responses(
        response.json(),
        load_json('partners_discounts_find_with_limit_response.json'),
    )
