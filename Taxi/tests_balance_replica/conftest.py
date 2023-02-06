# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from balance_replica_plugins import *  # noqa: F403 F401


@pytest.fixture(name='get_personal_accounts')
def _get_personal_accounts(pgsql):
    def _wrapper():
        cursor = pgsql['balance-replica'].cursor()
        cursor.execute(
            'SELECT id, version, contract_id, external_id, service_code '
            'FROM personal_accounts.personal_account '
            'ORDER BY id, version',
        )
        result = [
            {
                'id': row[0],
                'version': row[1],
                'contract_id': row[2],
                'external_id': row[3],
                'service_code': row[4],
            }
            for row in cursor
        ]
        return result

    return _wrapper


@pytest.fixture(name='get_banks')
def _get_banks(pgsql):
    def _wrapper():
        cursor = pgsql['balance-replica'].cursor()
        cursor.execute(
            'SELECT accounts, bik, city, cor_acc, cor_acc_type, '
            'hidden, id, info, name, swift, update_dt '
            'FROM banks.bank '
            'ORDER BY id',
        )
        result = [
            {
                'accounts': row[0],
                'bik': row[1],
                'city': row[2],
                'cor_acc': row[3],
                'cor_acc_type': row[4],
                'hidden': row[5],
                'id': row[6],
                'info': row[7],
                'name': row[8],
                'swift': row[9],
                'update_dt': row[10],
            }
            for row in cursor
        ]
        return result

    return _wrapper
