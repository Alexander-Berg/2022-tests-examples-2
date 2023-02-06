import os
import requests
import uuid
import time
import re

LOGISTIC_PLATFORM_URL = 'http://logistic-platform.taxi.tst.yandex.net'
CREATE_URL = os.path.join(LOGISTIC_PLATFORM_URL, 'api/b2b/platform/offers/create')
CONFIRM_URL = os.path.join(LOGISTIC_PLATFORM_URL, 'api/b2b/platform/offers/confirm')
ADMIN_URL = 'https://tariff-editor.taxi.tst.yandex-team.ru/'
ADMIN_REQUEST_PAGE = os.path.join(ADMIN_URL, 'dragon-orders/{}/info?cluster=platform')

def get_tvm_ticket():
    os.popen('ssh-add')
    a = os.popen('ya tool tvmknife get_service_ticket sshkey --src 2013636 --dst 2024159').read()
    match = re.search(r'(3:serv:.*)$', a)
    ticket = match.group(0)
    return ticket

def make_time_in_future():
    t = int(time.time())
    t -= t % 86400
    t += 86400 * 2 + 3600 * 14
    return t

TimeInFuture = make_time_in_future()


AUTHORIZATION = 'corp_client_id'
PAYLOAD = {
    "info": {
        "operator_request_id": str(uuid.uuid4()),
        "comment": "Это ТЕСТОВЫЙ ЗАКАЗ. Вывозить его НЕ НУЖНО"
    },
    "source": {
        "type": 1,
        "platform_station": {
            "platform_id": "076127e1-cbff-464c-8725-4da73ac104bd"
        }
    },
    "destination": {
        "type": 2,
         "custom_location": {
        "details": {
            "full_address": "117321, Профсоюзная улица 146, кв.29"
        }
        },
        "interval": {
            "from": int(time.time()) + 0,
            "to": int(time.time()) + 86400 * 3
        }
    },
    "items": [
        {
            "count": 1,
            "name": "Это ТЕСТОВЫЙ ЗАКАЗ. Вывозить его НЕ НУЖНО",
            "article": "article",
            "barcode": "barcode",
            "billing_details": {
                "unit_price": 2626,
                "assessed_unit_price": 2626,
                "inn": "666"
            },
            "physical_dims": {
                "predefined_volume": 1,
                "weight_gross": 4
            },
            "place_barcode": "barcode"
        },
    ],
    "places": [
        {
            "physical_dims": {
                "predefined_volume": 1000
            },
            "description": "Описание места",
            "barcode": "barcode"
        },
    ],
    "billing_info": {
        "payment_method": 1
    },
    "recipient_info": {
        "yandex_uid":1,
        "first_name": "Михаил",
        "last_name": "Грузднев",
        "partonymic": "Витальевич",
        "phone": "79036745169",
        "yandex_uid": "387904147_2",
    },
    "last_mile_policy": 0,
}


def create():

    r = requests.post(
        CREATE_URL,
        headers={
            'X-B2B-Client-id': AUTHORIZATION,
            'X-Ya-Service-Ticket': tvm
        },
        params={
            'need_pricing': 'true',
            'dump': 'eventlog'
        },
        json=PAYLOAD
    )
    print(f"\noffers/create response headers: {r.headers}\n")
    print(f"offers/create response json: {r.json()}\n")
    offer_id = r.json()['offers'][0]['offer_id']
    print('offer_id = ' + offer_id)
    r.raise_for_status()
    return offer_id


def confirm(offer_id):
    r = requests.post(
        CONFIRM_URL,
        headers={
            'X-B2B-Client-id': AUTHORIZATION,
            'X-Ya-Service-Ticket': tvm
        },
        json={
            'offer_id': offer_id
        }
    )
    r.raise_for_status()
    request_id = r.json()['request_id']
    print(f'\nRequest_id: {request_id}')
    print(f'Request in admin: {ADMIN_REQUEST_PAGE.format(request_id)}')


if __name__ == '__main__':

    tvm = get_tvm_ticket()

    offer_id = create()
    confirm(offer_id)
