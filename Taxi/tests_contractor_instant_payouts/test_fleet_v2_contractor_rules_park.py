import dateutil
import pytest

NOW = '2020-01-01T20:00:00+03:00'


@pytest.mark.now(NOW)
async def test_set_contractor_rules_by_park_id_ok(fleet_v2, stq, pgsql):
    response = await fleet_v2.set_all_contractors_rule(
        park_id='PARK-01',
        json={'rule_id': '00000000-0000-0000-0000-000000000001'},
    )
    assert response.status_code == 204, response.text
    with pgsql['contractor_instant_payouts'].cursor() as cursor:
        cursor.execute(
            """
            SELECT
                uid,
                started_at,
                created_at,
                name,
                initiator,
                user_id,
                user_provider
            FROM
                contractor_instant_payouts.operation
            """,
        )
        assert cursor.fetchall() == [
            (
                999,
                dateutil.parser.parse('2015-01-01T00:00:00+03:00'),
                dateutil.parser.parse('2015-01-01T00:00:00+03:00'),
                'testsuite',
                'platform',
                None,
                None,
            ),
            (
                1,
                dateutil.parser.parse(NOW),
                dateutil.parser.parse(NOW),
                'set_all_contractors_rule',
                'park',
                1000,
                'yandex',
            ),
        ]
        cursor.execute(
            """
            SELECT
                park_id,
                operation_id,
                created_at
            FROM
                contractor_instant_payouts.park_operation
            """,
        )
        assert cursor.fetchall() == [
            ('PARK-01', 1, dateutil.parser.parse(NOW)),
        ]
        stq_cip = stq.contractor_instant_payouts_set_all_contractors_rule
        assert stq_cip.times_called == 1
        task = stq_cip.next_call()
        print(task)
        assert task['kwargs']['park_id'] == 'PARK-01'
        assert (
            task['kwargs']['rule_id'] == '00000000-0000-0000-0000-000000000001'
        )
        assert task['kwargs']['operation_uid'] == '1'
        assert task['kwargs']['created_at'] == '2020-01-01T17:00:00+00:00'


@pytest.mark.now(NOW)
async def test_set_contractor_rules_by_park_id_no_rule(fleet_v2, stq, pgsql):
    response = await fleet_v2.set_all_contractors_rule(
        park_id='PARK-01',
        json={'rule_id': '10101010-1010-1010-1010-101010101010'},
    )
    assert response.status_code == 400


@pytest.mark.now(NOW)
async def test_set_contractor_rules_by_park_id_conflict(fleet_v2, stq, pgsql):
    with pgsql['contractor_instant_payouts'].cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO
                contractor_instant_payouts.park_operation (
                    park_id,
                    operation_id,
                    created_at
                )
            VALUES (
                'PARK-01',
                123,
                '2020-01-01T19:59:00+00:00'
            )
            """,
        )
    response = await fleet_v2.set_all_contractors_rule(
        park_id='PARK-01',
        json={'rule_id': '00000000-0000-0000-0000-000000000001'},
    )
    assert response.status_code == 409


@pytest.mark.now(NOW)
async def test_set_contractor_rules_by_park_id_idempotency(
        fleet_v2, stq, pgsql,
):
    with pgsql['contractor_instant_payouts'].cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO
                contractor_instant_payouts.park_operation (
                    park_id,
                    operation_id,
                    created_at,
                    idempotency_token
                )
            VALUES (
                'PARK-01',
                123,
                '2020-01-01T19:59:00+00:00',
                'token'
            )
            """,
        )
    response = await fleet_v2.set_all_contractors_rule(
        park_id='PARK-01',
        idempotency_token='token',
        json={'rule_id': '00000000-0000-0000-0000-000000000001'},
    )
    assert response.status_code == 204, response.text
