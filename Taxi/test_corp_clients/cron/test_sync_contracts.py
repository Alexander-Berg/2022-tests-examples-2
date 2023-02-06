# pylint: disable=redefined-outer-name
import pytest

from taxi.clients import billing_v2

from corp_clients.generated.cron import run_cron

CORP_COUNTRIES_SUPPORTED = {
    'rus': {'currency': 'RUB', 'deactivate_threshold': '156.8'},
}


@pytest.fixture
def get_client_contracts_mock(patch, load_json):
    @patch('taxi.clients.billing_v2.BalanceClient.get_client_contracts')
    async def _get_client_contracts(client_id, **kwargs):
        assert client_id is not None
        json_file = 'get_client_contracts_response.json'
        return load_json(json_file).get(client_id, [])


@pytest.fixture
def load_expected(load_json):
    return load_json('expected_database_data.json')


@pytest.fixture
def load_expected_notices(load_json):
    return load_json('expected_notices_events.json')


@pytest.mark.config(CORP_COUNTRIES_SUPPORTED=CORP_COUNTRIES_SUPPORTED)
async def test_new_contract(
        get_client_contracts_mock, mock_corp_edo, db, load_expected,
):
    await run_cron.main(['corp_clients.crontasks.sync_contracts', '-t', '0'])
    contract_after_cron = await db.secondary.corp_contracts.find_one(
        {'contract_external_id': 'new_contract'},
    )
    created = contract_after_cron.pop('created')
    updated = contract_after_cron.pop('updated')
    assert created and updated
    assert contract_after_cron == load_expected['new_contract']


@pytest.mark.config(CORP_COUNTRIES_SUPPORTED=CORP_COUNTRIES_SUPPORTED)
async def test_new_without_vat_contract(
        get_client_contracts_mock, mock_corp_edo, db, load_expected,
):
    await run_cron.main(['corp_clients.crontasks.sync_contracts', '-t', '0'])
    contract_after_cron = await db.secondary.corp_contracts.find_one(
        {'contract_external_id': 'new_without_vat_contract'},
    )
    created = contract_after_cron.pop('created')
    updated = contract_after_cron.pop('updated')
    assert created and updated
    assert contract_after_cron == load_expected['new_without_vat_contract']

    client = await db.secondary.corp_clients.find_one(
        {'billing_id': 'without_vat_billing_id'},
    )
    assert client['without_vat_contract']


@pytest.mark.config(CORP_COUNTRIES_SUPPORTED=CORP_COUNTRIES_SUPPORTED)
async def test_skip_contract(
        get_client_contracts_mock, mock_corp_edo, db, load_expected,
):
    await run_cron.main(['corp_clients.crontasks.sync_contracts', '-t', '0'])
    contract_after_cron = await db.secondary.corp_contracts.find_one(
        {'contract_external_id': 'skip_contract'},
    )
    assert not contract_after_cron


@pytest.mark.config(CORP_COUNTRIES_SUPPORTED=CORP_COUNTRIES_SUPPORTED)
@pytest.mark.filldb(corp_clients='dont_update')
@pytest.mark.filldb(corp_contracts='dont_update')
async def test_dont_update(
        get_client_contracts_mock, mock_corp_edo, db, load_expected,
):
    await run_cron.main(['corp_clients.crontasks.sync_contracts', '-t', '0'])
    contract_after_cron = await db.secondary.corp_contracts.find_one(
        {'contract_external_id': 'dont_update'},
    )
    assert 'updated' not in contract_after_cron


@pytest.mark.config(CORP_COUNTRIES_SUPPORTED=CORP_COUNTRIES_SUPPORTED)
async def test_different_contracts(
        get_client_contracts_mock, mock_corp_edo, db, load_expected,
):
    await run_cron.main(['corp_clients.crontasks.sync_contracts', '-t', '0'])
    contracts_after_cron = await db.secondary.corp_contracts.find().to_list(
        None,
    )
    for contract in contracts_after_cron:
        if 'created' in contract:
            contract.pop('created')
        contract.pop('updated')
        assert contract == load_expected[contract['contract_external_id']]


@pytest.mark.config(
    CORP_COUNTRIES_SUPPORTED={
        'rus': {'currency': 'RUB', 'deactivate_threshold': 1000},
    },
)
async def test_default_threshold(
        get_client_contracts_mock, mock_corp_edo, db, load_expected,
):
    await run_cron.main(['corp_clients.crontasks.sync_contracts', '-t', '0'])
    contract_after_cron = await db.secondary.corp_contracts.find_one(
        {'contract_external_id': 'new_contract'},
    )
    assert (
        contract_after_cron['settings']['prepaid_deactivate_threshold']
        == '1000'
    )


async def test_balance_billing_error(patch):
    @patch('taxi.clients.billing_v2.BalanceClient.get_client_contracts')
    async def _get_client_contracts(client_id, **kwargs):
        raise billing_v2.BillingError

    await run_cron.main(['corp_clients.crontasks.sync_contracts', '-t', '0'])


@pytest.mark.config(CORP_COUNTRIES_SUPPORTED={'rus': {'currency': 'rub'}})
async def test_country_not_found(
        get_client_contracts_mock, mock_corp_edo, caplog,
):
    await run_cron.main(['corp_clients.crontasks.sync_contracts', '-t', '0'])

    for log in (r for r in caplog.records if r.levelname == 'ERROR'):
        assert log.message.startswith('(\'Country not found for contract')
