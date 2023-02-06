import discounts_match  # pylint: disable=E0401
import pytest

from tests_eats_discounts import common


async def _init_data(stq_runner, pgsql, load_json, now):
    common.plan_task(common.TASK_ID, pgsql, now)
    task_id_2 = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
    common.plan_task(task_id_2, pgsql, now)
    await common.partners_discounts_create(
        stq_runner,
        pgsql,
        load_json('discounts_create_body_1.json'),
        common.TASK_ID,
        'finished',
    )
    await common.partners_discounts_create(
        stq_runner,
        pgsql,
        load_json('discounts_create_body_2.json'),
        task_id_2,
        'finished',
    )


async def _check_find_discounts(
        client, headers, request: dict, expected_response: dict,
):
    response = await client.post(
        '/v1/partners/discounts/find', json=request, headers=headers,
    )

    assert response.status_code == 200, response.json()
    common.compare_admin_responses(response.json(), expected_response)


@pytest.mark.config(
    EATS_DISCOUNTS_DISCOUNTS_CREATE_SETTINGS={'max_discounts': 2},
    EATS_DISCOUNTS_PARTNERS_DISCOUNTS_FIND_SETTINGS={'max_discounts': 100},
)
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
async def test_partners_discounts_find_ok(
        client, load_json, stq_runner, pgsql, mocked_time, headers,
):
    await _init_data(stq_runner, pgsql, load_json, mocked_time.now())
    await _check_find_discounts(
        client, headers, load_json('request.json'), load_json('response.json'),
    )


@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.config(
    EATS_DISCOUNTS_DISCOUNTS_CREATE_SETTINGS={'max_discounts': 2},
    EATS_DISCOUNTS_PARTNERS_DISCOUNTS_FIND_SETTINGS={'max_discounts': 2},
)
async def test_partners_discounts_find_pagination(
        client, load_json, stq_runner, pgsql, mocked_time, headers,
):
    await _init_data(stq_runner, pgsql, load_json, mocked_time.now())

    await _check_find_discounts(
        client,
        headers,
        load_json('request_1.json'),
        load_json('response_1.json'),
    )
    await _check_find_discounts(
        client,
        headers,
        load_json('request_2.json'),
        load_json('response_2.json'),
    )
    await _check_find_discounts(
        client,
        headers,
        load_json('request_3.json'),
        load_json('response_3.json'),
    )


async def test_partners_discounts_find_fail(client, headers):
    response = await client.post(
        '/v1/partners/discounts/find',
        json={
            'conditions': [{'condition_name': 'place', 'values': ['']}],
            'hierarchy_names': ['place_cashback'],
        },
        headers=headers,
    )

    assert response.status_code == 400, response.json()
    assert response.json() == {
        'code': 'Validation error',
        'message': (
            'Exception in AnyOtherConditionsVectorFromGenerated for '
            '\'place\' : Wrong type!'
        ),
    }
