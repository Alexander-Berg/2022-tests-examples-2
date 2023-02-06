#!/usr/bin/env python
import requests
from taxi.core import async
from taxi.core import db


@async.inline_callbacks
def make_true_config_maps_disabled():
    """
    Make it right through the mongo (no other options now)
    May be fixed after:
    https://st.yandex-team.ru/TAXITOOLS-536
    """
    query = {'_id': 'MAPS_DISABLED'}
    update = {
        '$set': {
            'v': True,
        },
        '$currentDate': {
            'updated': True,
        },
    }
    yield db.config.update(query, update, upsert=True)


@async.inline_callbacks
def main():
    response = requests.post('http://blackbox.yandex.net/client_mode',
                             json={'value': True})
    response.raise_for_status()
    url = 'http://balance-simple.yandex.net:8018/change_payment_methods'
    response = requests.post(url, json={
        'uid': '4294967295',
        'status': 'success',
        'rules': {},
        'payment_methods': {
            'card-x1111': {
                'auth_type': 'token',
                'name': '',
                'expiration_year': '2022',
                'proto': 'fake',
                'type': 'card',
                'expired': 0,
                'system': 'VISA',
                'number': '411111****1111',
                'expiration_month': '11',
                'currency': 'RUB',
                'binding_ts': 1484049108.142617,
                'service_labels': [],
                'holder': 'vvv',
                'id': 'x1111',
                'region_id': '225',
            },
        },
    })
    response.raise_for_status()
    yield make_true_config_maps_disabled()


if __name__ == '__main__':
    main()
