import pytest

from tests_fleet_payouts.utils import pg
from tests_fleet_payouts.utils import xcmp


EXPECTED_BALANCES = {
    ('balance_id_3', 'clid_3', 'contract_id_3'): {
        'balance_id': 'balance_id_3',
        'date': xcmp.Date('2020-03-23T14:00:00+03:00'),
        'clid': 'clid_3',
        'bcid': 'bcid_3',
        'contract_id': 'contract_id_3',
        'contract_type': 'contract_type_3',
        'contract_alias': 'contract_alias_3',
        'contract_limit': xcmp.Decimal('0.0'),
        'amount': xcmp.Decimal(100.0),
        'currency': 'RUB',
        'request_flag': 'Y',
        'org_id': 'org_id_3',
        'reject_code': None,
        'reject_reason': None,
    },
    ('balance_id_3', 'clid_3_1', 'contract_id_3_1'): {
        'balance_id': 'balance_id_3',
        'date': xcmp.Date('2020-03-23T14:00:00+03:00'),
        'clid': 'clid_3_1',
        'bcid': 'bcid_3_1',
        'contract_id': 'contract_id_3_1',
        'contract_type': 'contract_type_3_1',
        'contract_alias': 'contract_alias_3_1',
        'contract_limit': xcmp.Decimal('0.0'),
        'amount': xcmp.Decimal(100.0),
        'currency': 'RUB',
        'request_flag': 'Y',
        'org_id': 'org_id_3_1',
        'reject_code': None,
        'reject_reason': None,
    },
    ('balance_id_4', 'clid_4', 'contract_id_4'): {
        'balance_id': 'balance_id_4',
        'date': xcmp.Date('2020-03-24T14:00:00+03:00'),
        'clid': 'clid_4',
        'bcid': 'bcid_4',
        'contract_id': 'contract_id_4',
        'contract_type': 'contract_type_4',
        'contract_alias': 'contract_alias_4',
        'contract_limit': xcmp.Decimal(0.0),
        'amount': xcmp.Decimal(100.0),
        'currency': 'RUB',
        'request_flag': 'Y',
        'org_id': 'org_id_4',
        'reject_code': None,
        'reject_reason': None,
    },
}


@pytest.mark.pgsql('fleet_payouts', files=['balances.sql'])
async def test_expire_balances(taxi_fleet_payouts, pgsql):
    await taxi_fleet_payouts.run_task('periodic-balance-cleanup')

    balances = pg.dump_balances(pgsql)
    assert len(balances) == 3
    assert EXPECTED_BALANCES == balances
