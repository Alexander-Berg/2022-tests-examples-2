import os
import requests
import uuid
import time
import re

LOGISTIC_PLATFORM_URL = 'http://logistic-platform.taxi.tst.yandex.net'
CREATE_URL = os.path.join(LOGISTIC_PLATFORM_URL, 'api/b2b/platform/offers/create')
CONFIRM_URL = os.path.join(LOGISTIC_PLATFORM_URL, 'api/b2b/platform/offers/confirm')
EDIT_URL = os.path.join(LOGISTIC_PLATFORM_URL, 'api/b2b/platform/request/edit')
ADMIN_URL = 'https://tariff-editor.taxi.tst.yandex-team.ru/'
ADMIN_REQUEST_PAGE = os.path.join(ADMIN_URL, 'dragon-orders/{}/info?cluster=platform')

def get_tvm_ticket():
    os.popen('ssh-add >/dev/null 2>/dev/null')
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

AUTHORIZATION = '2283221488'
PAYLOAD = {
    "billing_info": {
        "payment_method": "card_on_receipt"
    },
    "source": {
        "platform_station": {
            "platform_id": "068f933a-0f84-431e-a998-f9dcf300414b"  # забиякин ПВЗ
        }
    },
    "last_mile_policy": "self_pickup",
    "destination": {
        "platform_station": {
            "platform_id": "95551dac-6017-4806-b5be-faa849cc4401" #Пункт выдачи заказов Яндекс Маркета
        },
        "type": "platform_station",
        "interval": {
            "from": TimeInFuture,
            "to": TimeInFuture  #помним, что для пвз время одинаковое
        }
    },
    "info": {
        "operator_request_id": str(uuid.uuid4())
    },
    "items": [
        {
            "article": "4137537",
            "count": 1,
            "name": "1984. Оруэлл Д",
            "place_barcode": "YD_4400069216",
            "marking_code": "",
            "physical_dims": {
                "dx": 11,
                "dy": 5,
                "dz": 12,
                "weight_gross": 721
            },
            "billing_details": {
                "unit_price": 528 * 100,
                "nds": 20,
                "assessed_unit_price": 52800
            }
        },
        {
            "article": "4136627",
            "count": 1,
            "name": "Сталин. Избранные сочинения. Сталин И.В.",
            "place_barcode": "YD_4400069216",
            "marking_code": "",
            "physical_dims": {
                "dx": 15,
                "dy": 4,
                "dz": 11,
                "weight_gross": 924
            },
            "billing_details": {
                "unit_price": 72000,
                "nds": 10,
                "assessed_unit_price": 72000
            }
        },
        {
            "article": "1130707",
            "count": 1,
            "name": "Тайна двух революций. Пыжиков А.В.",
            "place_barcode": "YD_4400069216",
            "marking_code": "",
            "physical_dims": {
                "dx": 9,
                "dy": 4,
                "dz": 11,
                "weight_gross": 221
            },
            "billing_details": {
                "unit_price": 80000,
                "nds": 0,
                "assessed_unit_price": 80000
            }
        },
        {
            "article": "000000002029668001",
            "count": 1,
            "name": "Сапоги черные: 42",
            "place_barcode": "YD_00102000000008589467",
            "marking_code": "010942102361011221oPJf79NVw;8so\u001d91TWFxiUG;06\u001d92SWthRXp6NXEnMGtEM3FyMWpVVTYleTtiamluPmdFM3hGJVMieiVIMSpXO3JXY2NUVVdxN0U3Tk9VZGswakFUYzI=",
            "physical_dims": {
                "predefined_volume": 10000,
                "weight_gross": 221
            },
            "billing_details": {
                "inn": "7729355029",
                "unit_price": 199900,
                "assessed_unit_price": 19998 * 100,
                "nds": -1,
            }
        },
        {
            "article": "000000002029668001",
            "count": 1,
            "name": "Сапоги черные: 42",
            "place_barcode": "YD_00102000000008589467",
            "marking_code": "010942102361011221oPJf79NVw;8so\u001d91TWFxiUG;06\u001d92SWthRXp6NXEnMGtEM3FyMWpVVTYleTtiamluPmdFM3hGJVMieiVIMSpXO3JXY2NUVVdxN0U3Tk9VZGswakFUYzG=",
            "physical_dims": {
                "predefined_volume": 10000,
                "weight_gross": 221
            },
            "billing_details": {
                "inn": "7729355029",
                "unit_price": 199900,
                "assessed_unit_price": 19998 * 100,
                "nds": -1,
            }
        },
    ],
    "particular_items_refuse": False,
    "places": [
        {
            "barcode": "YD_4400069216",
            "physical_dims": {
                "dx": 19,
                "dy": 32,
                "dz": 21,
                "predefined_volume": 1500,
                "weight_gross": 2450

            }
        },
        {
            "barcode": "YD_00102000000008589467",
            "physical_dims": {
                "predefined_volume": 20001,
                "weight_gross": 4450

            }
        },
    ],
    "recipient_info": {
        "email": "ytugator@ya.ru",
        "phone": "+79258425522",
        "first_name": "Абдул",
        "last_name": "АбульАбасович"
    },

}


def create():
    r = requests.post(
        CREATE_URL,
        headers={
            'X-B2B-Client-id': AUTHORIZATION,
            'X-Ya-Service-Ticket': tvm
        },
        json=PAYLOAD
    )
    if r.status_code != 200:
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


def makeOrder():
    global tvm
    tvm = get_tvm_ticket()
    offer_id = create()
    confirm(offer_id)


if __name__ == '__main__':
    makeOrder()
