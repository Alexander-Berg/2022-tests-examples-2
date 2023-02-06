import dateutil
import pytest

NOW = '2020-01-01T20:00:00+03:00'


@pytest.mark.now(NOW)
async def test_stq_ok(stq_runner, mock_api, pg_dump):
    pg_initial = pg_dump()
    await stq_runner.contractor_instant_payouts_set_all_contractors_rule.call(
        task_id='1',
        kwargs={
            'park_id': 'PARK-01',
            'rule_id': '00000000-0000-0000-0000-000000000001',
            'operation_uid': '777',
            'created_at': '2020-02-01T00:00:00+03:00',
        },
    )
    del pg_initial['park_operation']['PARK-01']
    assert pg_dump() == {
        **pg_initial,
        'rule_target': {
            **pg_initial['rule_target'],
            201: (
                1,
                999,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
                777,
                dateutil.parser.parse('2020-02-01T00:00:00+03:00'),
                'PARK-01',
                '00000000-0000-0000-0000-000000000001',
                'CONTRACTOR-02',
                False,
            ),
            328: (
                0,
                777,
                dateutil.parser.parse('2020-02-01T00:00:00+03:00'),
                777,
                dateutil.parser.parse('2020-02-01T00:00:00+03:00'),
                'PARK-01',
                '00000000-0000-0000-0000-000000000001',
                'CONTRACTOR-04',
                False,
            ),
            437: (
                0,
                777,
                dateutil.parser.parse('2020-02-01T00:00:00+03:00'),
                777,
                dateutil.parser.parse('2020-02-01T00:00:00+03:00'),
                'PARK-01',
                '00000000-0000-0000-0000-000000000001',
                'CONTRACTOR-05',
                False,
            ),
        },
        'rule_target_change_log': {
            **pg_initial['rule_target_change_log'],
            (201, 1): (
                777,
                dateutil.parser.parse('2020-02-01T00:00:00+03:00'),
                True,
                False,
            ),
            (328, 0): (
                777,
                dateutil.parser.parse('2020-02-01T00:00:00+03:00'),
                None,
                False,
            ),
            (437, 0): (
                777,
                dateutil.parser.parse('2020-02-01T00:00:00+03:00'),
                None,
                False,
            ),
        },
    }
