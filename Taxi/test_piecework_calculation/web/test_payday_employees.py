import datetime
import decimal

import pytest

NOW = datetime.datetime(2020, 1, 1, 15, 40, 59)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'data,expected_status,expected_pg_result',
    [
        # Empty data
        ({}, 400, None),
        # Invalid data
        ({'loan_id': '123'}, 400, None),
        # All OK
        (
            {
                'loanId': '123e4567-e89b-12d3-a456-426614174000',
                'employeeId': '123e4567-e89b-12d3-a456-426614174000',
                'companyId': '123e4567-e89b-12d3-a456-426614174000',
                'dateTime': NOW.strftime('%d.%m.%Y %H:%M:%S'),
                'paidAt': NOW.strftime('%d.%m.%Y %H:%M:%S'),
                'period': NOW.strftime('%d.%m.%Y 00:00:00'),
                'amount': 1000.00,
            },
            200,
            {
                'amount': decimal.Decimal('1000'),
                'company_id': '123e4567-e89b-12d3-a456-426614174000',
                'date_time': datetime.datetime(2020, 1, 1, 12, 40, 59),
                'employee_id': '123e4567-e89b-12d3-a456-426614174000',
                'loan_id': '123e4567-e89b-12d3-a456-426614174000',
                'paid_at': datetime.datetime(2020, 1, 1, 12, 40, 59),
                'period': datetime.datetime(2019, 12, 31, 21, 0),
                'oebs_sent_status': 'new',
            },
        ),
    ],
)
async def test_payday_loan(
        web_context,
        web_app_client,
        data,
        expected_status,
        expected_pg_result,
        mock_uapi_keys,
):
    # pylint: disable=W0612
    @mock_uapi_keys('/v2/authorization')
    def handler(request):
        assert 'X-API-Key' in request.headers
        return {'key_id': 'some_key_id'}

    response = await web_app_client.post(
        '/v1/payday/loan', json=data, headers={'Authorization': 'TOKEN'},
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    async with web_context.pg.slave_pool.acquire() as conn:
        pg_results = await conn.fetch(
            'SELECT * FROM piecework.payday_employee_loan ',
        )

    assert pg_results
    pg_result = dict(pg_results[0])
    del pg_result['updated']
    del pg_result['created']
    assert pg_result == expected_pg_result
