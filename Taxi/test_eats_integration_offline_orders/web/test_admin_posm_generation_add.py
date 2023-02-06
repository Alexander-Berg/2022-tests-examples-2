import http

import psycopg2.extras
import pytest

from testsuite.utils import callinfo


DEFAULT_TOKEN = {'idempotency_token': 'new-idempotency-token'}


@pytest.mark.parametrize(
    ('params', 'request_body', 'expected_code', 'stq_called'),
    (
        pytest.param(
            {'place_id': 'place_id__1', **DEFAULT_TOKEN},
            {'template_ids': [1, 2]},
            http.HTTPStatus.OK,
            True,
            id='OK-global-templates',
        ),
        pytest.param(
            {'place_id': 'place_id__4', **DEFAULT_TOKEN},
            {'template_ids': [4]},
            http.HTTPStatus.OK,
            True,
            id='OK-restaurant-template',
        ),
        pytest.param(
            {'place_id': 'not-found', **DEFAULT_TOKEN},
            {'template_ids': [1, 2]},
            http.HTTPStatus.NOT_FOUND,
            False,
            id='place_not_found',
        ),
        pytest.param(
            {'place_id': 'place_id__1', **DEFAULT_TOKEN},
            {'template_ids': [100500]},
            http.HTTPStatus.NOT_FOUND,
            False,
            id='template_not_found',
        ),
        pytest.param(
            {'place_id': 'place_id__1', **DEFAULT_TOKEN},
            {'template_ids': [1, 100500]},
            http.HTTPStatus.NOT_FOUND,
            False,
            id='one_template_not_found',
        ),
        pytest.param(
            {'place_id': 'place_id__1', **DEFAULT_TOKEN},
            {'template_ids': [4]},
            http.HTTPStatus.NOT_FOUND,
            False,
            id='template_not_belong',
        ),
        pytest.param(
            {
                'place_id': 'place_id__1',
                'idempotency_token': 'unique-idempotency-token-1',
            },
            {'template_ids': [1]},
            http.HTTPStatus.CONFLICT,
            False,
            id='non-idempotency',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=[
        'restaurants.sql',
        'tables.sql',
        'posm_templates.sql',
        'restaurants_posm_templates.sql',
        'posm_generations.sql',
        'posm_generations_templates.sql',
    ],
)
async def test_admin_posm_generation_add(
        taxi_eats_integration_offline_orders_web,
        stq,
        pgsql,
        params,
        request_body,
        expected_code,
        stq_called,
):
    cursor = pgsql['eats_integration_offline_orders'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    cursor.execute('select max(id) from posm_generations')
    old_max_id = cursor.fetchone()

    response = await taxi_eats_integration_offline_orders_web.post(
        '/admin/v1/posm/generation',
        params=params,
        json=request_body,
        headers={'X-Yandex-Login': 'username'},
    )
    body = await response.json()
    assert response.status == expected_code

    cursor.execute('select max(id) from posm_generations')
    new_max_id = cursor.fetchone()
    try:
        stq_info = stq.ei_offline_orders_generate_posm.next_call()
    except callinfo.CallQueueEmptyError:
        assert not stq_called
        assert new_max_id == old_max_id
        return
    assert old_max_id != new_max_id
    assert stq_called
    assert stq_info['id'] == str(body['generation_id'])
