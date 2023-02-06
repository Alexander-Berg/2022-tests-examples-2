import pytest
import requests


def test_default_card(client_maker):
    client = client_maker()
    client.init_phone(phone='random')
    client.add_card()
    client.launch()
    data = client.paymentmethods()
    assert data == {
        'card': {
            'available_cards': [
                {
                    'busy': False,
                    'currency': 'RUB',
                    'expiration_month': 11,
                    'expiration_time': '2022-11-30T00:00:00+0000',
                    'expiration_year': 2022,
                    'id': 'card-x1111',
                    'number': '****1111',
                    'system': 'VISA',
                    'usable': True,
                },
            ],
            'payment_available': True,
        },
        'corp': {
            'available_accounts': [],
            'payment_available': False,
        },
    }


def test_custom_card(client_maker):
    client = client_maker()
    client.init_phone(phone='random')
    client.add_card({
        'auth_type': 'token',
        'name': '',
        'expiration_year': '2023',
        'proto': 'fake',
        'type': 'card',
        'expired': 0,
        'system': 'VISA',
        'number': '411111****1112',
        'expiration_month': '10',
        'currency': 'RUB',
        'binding_ts': 1484049109.142617,
        'service_labels': [],
        'holder': 'yyy',
        'id': 'x2222',
        'region_id': '225',
    })
    client.launch()
    data = client.paymentmethods()
    assert data == {
        'card': {
            'available_cards': [
                {
                    'busy': False,
                    'currency': 'RUB',
                    'expiration_month': 10,
                    'expiration_time': '2023-10-31T00:00:00+0000',
                    'expiration_year': 2023,
                    'id': 'card-x2222',
                    'number': '****1112',
                    'system': 'VISA',
                    'usable': True,
                },
            ],
            'payment_available': True,
        },
        'corp': {
            'available_accounts': [],
            'payment_available': False,
        },
    }


def test_no_card(client_maker):
    client = client_maker()
    client.init_phone(phone='random')
    client.launch()
    data = client.paymentmethods()
    assert data == {
        'card': {
            'available_cards': [],
            'payment_available': True,
        },
        'corp': {
            'available_accounts': [],
            'payment_available': False,
        },
    }


def test_billing_error(client_maker):
    client = client_maker()
    client.init_phone(phone='random')
    client.add_card(status='error')
    client.launch()
    with pytest.raises(requests.HTTPError) as exc:
        client.paymentmethods()
    assert exc.value.response.status_code == 500
