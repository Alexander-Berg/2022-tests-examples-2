import pytest

from taxi_billing_subventions.common import models


@pytest.mark.parametrize(
    'test_case_json',
    [
        'active_signed.json',
        'active_faxed.json',
        'inactive_unsigned.json',
        'inactive_datetime.json',
        'inactive_cancelled.json',
        'inactive_deactivated.json',
        'inactive_suspended.json',
    ],
)
@pytest.mark.nofilldb()
def test_is_active_at(test_case_json, load_py_json):
    test_case = load_py_json(f'test_is_active_at/{test_case_json}')
    contract: models.Contract = test_case['contract']
    datetime = test_case['datetime']
    expected = test_case['expected']
    assert contract.is_active_at(datetime) is expected


@pytest.mark.parametrize('test_case_json', ['linked.json', 'not_linked.json'])
@pytest.mark.nofilldb()
def test_is_linked_to(test_case_json, load_py_json):
    test_case = load_py_json(f'test_is_linked_to/{test_case_json}')
    main = test_case['main']
    other = test_case['other']
    expected = test_case['expected']
    assert main.is_linked_to(other) is expected


@pytest.mark.parametrize('test_case_json', ['offer.json', 'not_offer.json'])
@pytest.mark.nofilldb()
def test_is_offer(test_case_json, load_py_json):
    test_case = load_py_json(f'test_is_offer/{test_case_json}')
    contract: models.Contract = test_case['contract']
    expected = test_case['expected']
    assert contract.is_offer is expected


@pytest.mark.parametrize(
    'test_case_json',
    [
        'lonely_contract.json',
        'only_one_active_contract.json',
        'two_active_contracts_one_started_later.json',
    ],
)
@pytest.mark.nofilldb()
def test_select_currency(test_case_json, load_py_json):
    test_case = load_py_json(f'test_select_currency/{test_case_json}')
    contracts = test_case['contracts']
    expected = test_case['expected']
    assert models.Contract.select_currency(contracts) == expected


@pytest.mark.parametrize(
    'test_case_json',
    ['no_contracts.json', 'two_active_contracts_same_begin.json'],
)
@pytest.mark.nofilldb()
def test_select_currency_error(test_case_json, load_py_json):
    test_case = load_py_json(f'test_select_currency_error/{test_case_json}')
    contracts = test_case['contracts']
    with pytest.raises(models.UnknownContractCurrency):
        models.Contract.select_currency(contracts)


@pytest.mark.parametrize(
    'test_case_json',
    ['select_cash_contracts.json', 'select_not_cash_contracts.json'],
)
@pytest.mark.nofilldb()
def test_select_active_general_contracts(test_case_json, load_py_json):
    test_case = load_py_json(
        f'test_select_active_general_contracts/{test_case_json}',
    )
    contracts = test_case['contracts']
    for_cash = test_case['for_cash']
    datetime = test_case['datetime']
    expected = test_case['expected']
    actual = models.Contract.select_active_general_contracts(
        contracts=contracts,
        for_cash=for_cash,
        is_cargo=False,
        datetime=datetime,
    )
    assert actual == expected


@pytest.mark.parametrize('test_case_json', ['test_case.json'])
@pytest.mark.nofilldb()
def test_select_active_offer_contracts(test_case_json, load_py_json):
    test_case = load_py_json(
        f'test_select_active_offer_contracts/{test_case_json}',
    )
    spendable_contracts = test_case['spendable_contracts']
    general_contracts = test_case['general_contracts']
    datetime = test_case['datetime']
    expected = test_case['expected']
    actual = models.Contract.select_active_offer_contracts(
        spendable_contracts=spendable_contracts,
        general_contracts=general_contracts,
        datetime=datetime,
    )
    assert actual == expected


@pytest.mark.nofilldb()
def test_select_latest_contract_for_each_service(load_py_json):
    test_contracts = load_py_json('contracts.json')
    select = models.Contract.select_latest_contract_for_each_service
    service_to_contract = select(test_contracts)
    service_to_contract_id = {s: c.id for s, c in service_to_contract.items()}
    assert service_to_contract_id == {1: 1, 2: 2, 3: 2}
