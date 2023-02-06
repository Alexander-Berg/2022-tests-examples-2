DEFAULT_CARD = {
    'card_id': 'card_id',
    'billing_card_id': 'card_id',
    'permanent_card_id': 'card_id',
    'currency': 'RUR',
    'expiration_year': 2020,
    'expiration_month': 10,
    'number': 'XXX1111',
    'owner': 'Owner',
    'possible_moneyless': False,
    'region_id': '3',
    'regions_checked': [],
    'system': 'visa',
    'valid': True,
    'bound': True,
    'unverified': False,
    'busy': False,
    'busy_with': [],
    'from_db': False,
}


def make_card(card_id: str = 'card_id', **extra):
    return {**DEFAULT_CARD, 'card_id': card_id, **extra}
