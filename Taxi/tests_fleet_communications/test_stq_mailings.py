import dateutil
import pytest


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_stq(mock_api, stq_runner, pg_dump):
    pg_initial = pg_dump()

    await stq_runner.fleet_communications_mailings.call(
        task_id='1', kwargs={'mailing_id': 'MAILING-01', 'park_id': 'PARK-01'},
    )

    assert mock_api['feeds']['/v1/create'].has_calls

    assert (
        mock_api['parks']['/driver-profiles/list'].next_call()['request'].json
        == {
            'fields': {'driver_profile': ['id']},
            'limit': 10000,
            'offset': 0,
            'query': {
                'park': {
                    'car': {'amenities': ['wifi'], 'categories': ['econom']},
                    'current_status': {'status': ['busy']},
                    'driver_profile': {
                        'affiliation_partner_sources': ['none'],
                        'work_rule_id': ['WORK_RULE-01'],
                        'work_status': ['working'],
                    },
                    'deptrans': {'statuses': ['permanent']},
                    'id': 'PARK-01',
                },
            },
            'sort_order': [
                {'direction': 'asc', 'field': 'driver_profile.created_date'},
            ],
        }
    )

    assert pg_dump() == {
        **pg_initial,
        'mailings': {
            **pg_initial['mailings'],
            'MAILING-01': (
                'PARK-01',
                'TEMPLATE-01',
                dateutil.parser.parse('2022-01-01T12:00:00+00:00'),
                '999',
                3,
                dateutil.parser.parse('2022-01-02T12:00:00+00:00'),
                False,
                None,
                None,
                'SENT',
                dateutil.parser.parse('2022-01-02T12:00:00+00:00'),
            ),
        },
    }


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_stq_drivers_already_exists(mock_api, stq_runner, pg_dump):
    pg_initial = pg_dump()

    await stq_runner.fleet_communications_mailings.call(
        task_id='1', kwargs={'mailing_id': 'MAILING-04', 'park_id': 'PARK-01'},
    )

    assert mock_api['parks']['/driver-profiles/list'].has_calls == 0

    assert mock_api['feeds']['/v1/create'].has_calls

    assert pg_dump() == {
        **pg_initial,
        'mailings': {
            **pg_initial['mailings'],
            'MAILING-04': (
                'PARK-01',
                'TEMPLATE-01',
                dateutil.parser.parse('2022-01-02T12:00:00+00:00'),
                '999',
                3,
                dateutil.parser.parse('2022-01-02T12:00:00+00:00'),
                False,
                None,
                None,
                'SENT',
                dateutil.parser.parse('2022-01-02T12:00:00+00:00'),
            ),
        },
        'mailing_contractors': {},
    }


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_stq_already_sent(mock_api, stq_runner, pg_dump):
    pg_initial = pg_dump()

    await stq_runner.fleet_communications_mailings.call(
        task_id='1', kwargs={'mailing_id': 'MAILING-02', 'park_id': 'PARK-01'},
    )

    assert mock_api['feeds']['/v1/create'].has_calls == 0

    assert mock_api['parks']['/driver-profiles/list'].has_calls == 0

    assert pg_dump() == {**pg_initial}


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_stq_has_been_deleted(mock_api, stq_runner, pg_dump):
    pg_initial = pg_dump()

    await stq_runner.fleet_communications_mailings.call(
        task_id='1', kwargs={'mailing_id': 'MAILING-03', 'park_id': 'PARK-01'},
    )

    assert mock_api['feeds']['/v1/create'].has_calls == 0

    assert mock_api['parks']['/driver-profiles/list'].has_calls == 0

    assert pg_dump() == {**pg_initial}
