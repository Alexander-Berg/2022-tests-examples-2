DONATION_CLIENT_ID = '93696285'
DONATION_CONTRACT_ID = '3636412'

SERVICE_FEE_CLIENT_ID_RUB = '95332016'
SERVICE_FEE_CONTRACT_ID_RUB = '4469918'

SERVICE_FEE_CLIENT_ID_KZT = '97543252'
SERVICE_FEE_CONTRACT_ID_KZT = '5339448'

SERVICE_FEE_CLIENT_ID_BYN = '97543826'
SERVICE_FEE_CONTRACT_ID_BYN = '5339784'


def make_product_id(product_type):
    return f'{product_type}/native'


def make_marketing_payment(marketing_type, amount, product_type):
    return {
        'product_id': make_product_id(product_type),
        'value_amount': amount,
        'type': marketing_type,
        'product_type': product_type,
        'entity_id': None,
    }


def make_place_compensations(product_type, amount):
    return {
        'product_id': make_product_id(product_type),
        'product_type': product_type,
        'amount': amount,
    }


def make_reimbursement_payment(payment_type, amount, product_type):
    return {
        'product_id': make_product_id(product_type),
        'value_amount': amount,
        'type': payment_type,
        'product_type': product_type,
    }


def make_unpaid_product(amount, product_type):
    return {
        'product_id': make_product_id(product_type),
        'value_amount': amount,
        'product_type': product_type,
    }


def make_compensation_discount(discount_type, amount):
    return {'type': discount_type, 'amount': amount}


def make_compensation_item(
        product_type, amount, product_id=None, discounts=None,
):
    return {
        'type': product_type,
        'amount': amount,
        'product_id': product_id or make_product_id(product_type),
        'discounts': discounts or [],
    }


class DefaultRule:
    name = 'default'


def set_rule_name(name):
    DefaultRule.name = name


def billing_event(
        client_id=None,
        contract_id='test_contract_id',
        client_info=None,
        rule=None,
        external_payment_id=None,
        geo_hierarchy=None,
        business=None,
        payload=None,
        transaction_date=None,
        **details,
):
    if client_info is None and client_id is None:
        raise 'billing_event has been client_id or client_info'
    event = details
    if transaction_date is not None:
        event['transaction_date'] = transaction_date
    else:
        event['transaction_date'] = '2021-07-10T09:22:00+00:00'
    event['version'] = '2.1'
    event['rule'] = rule if rule is not None else DefaultRule.name
    if client_info is not None:
        event['client'] = client_info
    else:
        event['client'] = {'id': client_id, 'contract_id': contract_id}
    event['external_payment_id'] = external_payment_id
    if geo_hierarchy:
        event['geo_hierarchy'] = geo_hierarchy
    if business:
        event['business'] = business
    if payload is not None:
        event['payload'] = payload
    return event


def payment(
        product_type,
        amount,
        payment_method,
        currency=None,
        product_id=None,
        payment_service=None,
        payment_terminal_id=None,
):
    details = {
        'product_type': product_type,
        'amount': amount,
        'payment_method': payment_method,
        'product_id': product_id or make_product_id(product_type),
    }
    if payment_service:
        details['payment_service'] = payment_service
    if payment_terminal_id:
        details['payment_terminal_id'] = payment_terminal_id
    if currency:
        details['currency'] = currency
    return details


def refund(
        product_type,
        amount,
        payment_method,
        product_id=None,
        currency=None,
        payment_service=None,
        payment_terminal_id=None,
):
    details = {
        'product_type': product_type,
        'amount': amount,
        'payment_method': payment_method,
        'product_id': product_id or make_product_id(product_type),
        'currency': currency,
    }
    if payment_service:
        details['payment_service'] = payment_service
    if payment_terminal_id:
        details['payment_terminal_id'] = payment_terminal_id
    return details


def make_commission(
        product_type,
        amount,
        product_id=None,
        currency=None,
        payment_service=None,
        commission_type=None,
):
    details = {
        'product_type': product_type,
        'amount': amount,
        'product_id': product_id or make_product_id(product_type),
        'currency': currency,
    }
    if payment_service:
        details['payment_service'] = payment_service
    if commission_type:
        details['type'] = commission_type
    return details


def make_courier_commission_rule(
        courier_id, commission_type, client_id, commission_info,
):
    return {
        'type': 'commission',
        'counterparty_type': 'courier',
        'courier_id': courier_id,
        'commission_type': commission_type,
        'client_id': client_id,
        'commission': commission_info,
    }


def make_place_commission_rule(
        place_id, commission_type, client_id, commission_info,
):
    return {
        'type': 'commission',
        'counterparty_type': 'place',
        'place_id': place_id,
        'commission_type': commission_type,
        'client_id': client_id,
        'commission': commission_info,
    }
