import logging

logger = logging.getLogger(__name__)


def test_accounts_num_orders(library_context):
    my_spending = library_context.corp_spending
    accounts = my_spending.make_user_accounts(
        client_id='test_client_id',
        user_id='test_user_id',
        service='eats2',
        num_orders='true',
    )
    assert len(accounts) == 1
    assert (
        accounts[0].entity_external_id
        == 'corp/client_employee/test_client_id/test_user_id'
    )
    assert accounts[0].agreement_id == 'eats/orders/limit'
    assert accounts[0].currency == 'XXX'
    assert accounts[0].sub_account == 'num_orders'


def test_accounts_payment_sub_accounts(library_context):
    my_spending = library_context.corp_spending
    my_accounts = my_spending.make_user_accounts(
        client_id='clntid', user_id='usrid', service='eats2', currency='BCoin',
    )
    assert len(my_accounts) == 2
    assert my_accounts[0].currency == 'BCoin'
    assert my_accounts[1].currency == 'BCoin'
    assert (
        my_accounts[0].entity_external_id
        == 'corp/client_employee/clntid/usrid'
    )
    assert (
        my_accounts[1].entity_external_id
        == 'corp/client_employee/clntid/usrid'
    )
    assert my_accounts[0].agreement_id == 'eats/orders/limit'
    assert my_accounts[1].agreement_id == 'eats/orders/limit'
    assert (
        (
            (my_accounts[0].sub_account == 'payment')
            and (my_accounts[1].sub_account == 'payment/vat')
        )
        or (
            (my_accounts[0].sub_account == 'payment/vat')
            and (my_accounts[1].sub_account == 'payment')
        )
    )


def test_user_entry_key(library_context):
    my_spending = library_context.corp_spending
    my_entry_key = my_spending.make_user_entry_key(
        client_id='vipClient777', user_id='YaroslavTheWise', service='eats2',
    )
    assert (
        my_entry_key.entity_external_id
        == 'corp/client_employee/vipClient777/YaroslavTheWise'
    )
    assert my_entry_key.agreement_id == 'eats/orders/limit'
    assert my_entry_key.currency == 'XXX'
