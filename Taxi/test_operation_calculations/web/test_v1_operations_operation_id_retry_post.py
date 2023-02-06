import http
import logging

import pytest


@pytest.mark.parametrize(
    'operation_id, expected_status, expected_content',
    (
        pytest.param(
            'c76ba14187e0ffd7b8360e9c50ee3cd8',
            http.HTTPStatus.OK,
            {
                'created_at': '2020-01-01T12:00:00+03:00',
                'created_by': 'robot',
                'id': 'c76ba14187e0ffd7b8360e9c50ee3cd8',
                'params': {
                    'commission': 10,
                    'end_date': '2021-01-01',
                    'maxtrips': 10,
                    'price_increase': 1.5,
                    'start_date': '2020-01-01',
                    'tariff_zone': 'moscow',
                    'tariffs': ['econom'],
                    'type': 'nmfg-subventions',
                    'sub_nobrand': 211837,
                    'sub_brand': 170317,
                    'a1': 5,
                    'a2': 0,
                    'm': 20,
                    'hours': [1],
                    'week_days': ['mon'],
                    'subvenion_end_date': '2021-01-01',
                    'subvenion_start_date': '2020-01-01',
                },
                'status': 'CREATED',
                'updated_at': '2020-01-02T04:00:00+03:00',
                'updated_by': 'test_robot',
            },
            id='ok',
        ),
        pytest.param(
            'invalid_id',
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'OPERATION_NOT_FOUND',
                'message': 'Operation with id="invalid_id" not found',
            },
            id='not_found',
        ),
        pytest.param(
            '85a626b31928fd33896877208148d982',
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'CANNOT_RETRY',
                'message': (
                    'Cannot retry operation. '
                    'Need status: FAILED,STARTED. '
                    'Operation status: CREATED.'
                ),
            },
            id='invalid_status',
        ),
    ),
)
@pytest.mark.now('2020-01-02T01:00:00+00:00')
@pytest.mark.pgsql('operation_calculations', files=['pg_operations.sql'])
async def test_v1_operations_operation_id_retry_post(
        web_app_client,
        operation_id,
        expected_status,
        expected_content,
        caplog,
):
    caplog.set_level(logging.INFO, logger='taxi.opentracing.reporter')

    response = await web_app_client.post(
        f'/v1/operations/{operation_id}/retry/',
        headers={'X-Yandex-Login': 'test_robot'},
    )
    assert response.status == expected_status, await response.text()
    assert await response.json() == expected_content

    if expected_status == http.HTTPStatus.OK:
        message = f'Operation with id="{operation_id}" retried.'
        assert message in caplog.messages
