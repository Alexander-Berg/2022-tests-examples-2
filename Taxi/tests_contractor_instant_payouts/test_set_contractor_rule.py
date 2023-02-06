import dateutil
import pytest


NOW = '2020-01-01T20:00:00+03:00'


@pytest.mark.now(NOW)
async def test_success__set(set_contractor_rule, mock_api, pg_dump):
    pg_initial = pg_dump()

    response = await set_contractor_rule(
        park_id='PARK-01',
        contractor_id='CONTRACTOR-05',
        rule_id='00000000-0000-0000-0000-000000000001',
    )
    assert response.status_code == 204, response.text

    assert pg_dump() == {
        **pg_initial,
        'operation': {
            **pg_initial['operation'],
            1: (
                dateutil.parser.parse(NOW),
                dateutil.parser.parse(NOW),
                'set_contractor_rule',
                'park',
                None,
                None,
                None,
                None,
            ),
        },
        'rule_target': {
            **pg_initial['rule_target'],
            1: (
                0,
                1,
                dateutil.parser.parse(NOW),
                1,
                dateutil.parser.parse(NOW),
                'PARK-01',
                '00000000-0000-0000-0000-000000000001',
                'CONTRACTOR-05',
                False,
            ),
        },
        'rule_target_change_log': {
            **pg_initial['rule_target_change_log'],
            (1, 0): (1, dateutil.parser.parse(NOW), None, False),
        },
    }


@pytest.mark.now(NOW)
async def test_success__reset(set_contractor_rule, mock_api, pg_dump):
    pg_initial = pg_dump()

    response = await set_contractor_rule(
        park_id='PARK-01',
        contractor_id='CONTRACTOR-01',
        rule_id='00000000-0000-0000-0000-000000000002',
    )
    assert response.status_code == 204, response.text

    assert pg_dump() == {
        **pg_initial,
        'operation': {
            **pg_initial['operation'],
            1: (
                dateutil.parser.parse(NOW),
                dateutil.parser.parse(NOW),
                'set_contractor_rule',
                'park',
                None,
                None,
                None,
                None,
            ),
        },
        'rule_target': {
            **pg_initial['rule_target'],
            101: (
                1,
                999,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
                1,
                dateutil.parser.parse(NOW),
                'PARK-01',
                '00000000-0000-0000-0000-000000000001',
                'CONTRACTOR-01',
                True,
            ),
            102: (
                1,
                999,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
                1,
                dateutil.parser.parse(NOW),
                'PARK-01',
                '00000000-0000-0000-0000-000000000002',
                'CONTRACTOR-01',
                False,
            ),
        },
        'rule_target_change_log': {
            **pg_initial['rule_target_change_log'],
            (101, 1): (1, dateutil.parser.parse(NOW), False, True),
            (102, 1): (1, dateutil.parser.parse(NOW), True, False),
        },
    }


@pytest.mark.now(NOW)
async def test_set_contractor_rule__unset(
        set_contractor_rule, mock_api, pg_dump,
):
    pg_initial = pg_dump()

    response = await set_contractor_rule(
        park_id='PARK-01', contractor_id='CONTRACTOR-01', rule_id=None,
    )
    assert response.status_code == 204, response.text

    assert pg_dump() == {
        **pg_initial,
        'operation': {
            **pg_initial['operation'],
            1: (
                dateutil.parser.parse(NOW),
                dateutil.parser.parse(NOW),
                'set_contractor_rule',
                'park',
                None,
                None,
                None,
                None,
            ),
        },
        'rule_target': {
            **pg_initial['rule_target'],
            101: (
                1,
                999,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
                1,
                dateutil.parser.parse(NOW),
                'PARK-01',
                '00000000-0000-0000-0000-000000000001',
                'CONTRACTOR-01',
                True,
            ),
        },
        'rule_target_change_log': {
            **pg_initial['rule_target_change_log'],
            (101, 1): (1, dateutil.parser.parse(NOW), False, True),
        },
    }


@pytest.mark.now(NOW)
async def test_idempotency(set_contractor_rule, mock_api, pg_dump):
    pg_initial = pg_dump()

    response = await set_contractor_rule(
        park_id='PARK-01',
        contractor_id='CONTRACTOR-01',
        rule_id='00000000-0000-0000-0000-000000000001',
    )
    assert response.status_code == 204, response.text

    assert pg_dump() == pg_initial, 'Nothing was expected to change'
