import dateutil
import pytest

NOW = '2020-01-01T12:00:00+00:00'


@pytest.mark.now(NOW)
@pytest.mark.config(
    FLEET_ANTIFRAUD_PARK_CHECK={
        'is_enabled': True,
        'expiring_interval': 86400,
        'billing_fetching_overlap': 3600,
    },
)
async def test_stq(stq_runner, mock_api, pg_dump):
    pg_initial = pg_dump()

    await stq_runner.fleet_antifraud_transaction_check.call(
        task_id='1',
        kwargs={
            'park_id': 'PARK-01',
            'contractor_profile_id': 'CONTRACTOR-01',
            'transactions': [
                {
                    'entry_id': 4,
                    'account': {
                        'agreement_id': 'agreement/tip',
                        'sub_account': 'tip/card',
                        'currency': 'RUB',
                    },
                    'amount': '200.0000',
                    'event_at': '2020-01-01T00:00:00+00:00',
                    'details': {'alias_id': 'ORDER-04'},
                },
            ],
        },
    )

    assert pg_dump() == {
        **pg_initial,
        'park_check_suspicious': {
            **pg_initial['park_check_suspicious'],
            ('PARK-01', 'CONTRACTOR-01', 'ORDER-04', '4'): (
                'tips',
                100,
                None,
                dateutil.parser.parse('2020-01-01T00:00:00+00:00'),
                dateutil.parser.parse('2020-01-02T00:00:00+00:00'),
                200,
                None,
                None,
                2,
                dateutil.parser.parse('2020-01-02T00:00:00+00:00'),
            ),
        },
    }
