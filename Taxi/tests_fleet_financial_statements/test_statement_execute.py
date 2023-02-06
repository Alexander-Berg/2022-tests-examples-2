from tests_fleet_financial_statements.common import defaults
from tests_fleet_financial_statements.common import errors


async def test_default(statement_execute, pg_database):
    response = await statement_execute()
    assert response.status_code == 200, response.text

    with pg_database.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                stmt_revision,
                stmt_status,
                updated_at BETWEEN NOW() - '1 MINUTE'::INTERVAL
                               AND NOW() + '1 MINUTE'::INTERVAL,
                executed_at BETWEEN NOW() - '1 MINUTE'::INTERVAL
                                AND NOW() + '1 MINUTE'::INTERVAL,
                executed_by
            FROM
                fleet_financial_statements.finstmt
            WHERE
                park_id = %s
                AND stmt_ext_id = %s
        """,
            [defaults.PARK_ID, defaults.STMT_EXT_ID],
        )
        assert cursor.fetchone() == (3, 'executing', True, True, 'Y1000')


async def test_stq_call(statement_execute, stq_perform_client):
    response = await statement_execute()
    assert response.status_code == 200, response.text

    assert stq_perform_client.times_called == 1
    task = stq_perform_client.next_call()
    assert task['id'] == f'PARK-01/E/1'
    assert task['kwargs']['park_id'] == defaults.PARK_ID
    assert task['kwargs']['stmt_id'] == 1
    assert task['kwargs']['stmt_revision'] == 3
    assert not task['kwargs']['do_revert']


async def test_does_not_exists(statement_execute):
    response = await statement_execute(
        id='ffffffff-ffff-ffff-ffff-ffffffffffff',
    )
    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': errors.EC_DOES_NOT_EXIST,
        'message': errors.EM_DOES_NOT_EXIST,
    }


async def test_has_been_deleted(statement_execute):
    response = await statement_execute(
        id='00000000-0000-0000-0000-000000000002',
    )
    assert response.status_code == 410, response.text
    assert response.json() == {
        'code': errors.EC_HAS_BEEN_DELETED,
        'message': errors.EM_HAS_BEEN_DELETED,
    }


async def test_has_been_changed(statement_execute):
    response = await statement_execute(revision=1)
    assert response.status_code == 409, response.text
    assert response.json() == {
        'code': errors.EC_HAS_BEEN_CHANGED,
        'message': errors.EM_HAS_BEEN_CHANGED,
    }


async def test_wrong_state(statement_execute):
    response = await statement_execute(park_id='PARK-02')
    assert response.status_code == 409, response.text
    assert response.json() == {
        'code': errors.EC_WRONG_STATE,
        'message': errors.EM_WRONG_STATE,
    }
