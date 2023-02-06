import copy
import json
import requests
import statistics
import time
import uuid

from library.urls import OFFER_CREATE_URL, OFFER_CONFIRM_URL

requestsHeaders = {
        'Authorization': 'Bearer AgAAAADzeAQMAAAPeISvM_9LUkxCijQoFXOH5QE',
        'Content-Type': 'application/json'
    }

operator_id = str(uuid.uuid4())

platform_id = "e03f0622-92d5-4934-bed7-557937ffe33f"

location = {
                "latitude": 55.723967,
                "longitude": 37.568408,
                "details": {
                    "country": "Россия",
                    "region": "Москва",
                    "street": "улица Доватора",
                    "house": "6/6к8",
                    "housing": "1",
                    "full_address": "119048, Москва, улица Доватора, 6/6к8, кв.29"
                }
}

item = {
                "count": 1,
                "name": "Товар в ассортименте по заказу И8000402353-1",
                "article": "И8000402353-1",
                "barcode": "И8000402353-1",
                "billing_details": {
                    "unit_price": 2992,
                    "assessed_unit_price": 2992
                },
                "physical_dims": {
                    "dx": 19,
                    "dy": 20,
                    "dz": 21,
                    "weight_gross": 9240
                },
                "place_barcode": "001-8000402353-1"
}

place = {
                "physical_dims": {
                    "dx": 19,
                    "dy": 20,
                    "dz": 21
                },
                "description": "",
                "barcode": "001-8000402353-1"
}

recipient_info = {
            "first_name": "Михаил",
            "last_name": "Грузднев",
            "partonymic": "Витальевич",
            "phone": "79036745169"
}


def test_inn_create():
    url = OFFER_CREATE_URL

    payload = json.dumps({
        "info": {
            "operator_request_id": operator_id,
        },
        "source": {
            "type": "platform_station",
            "platform_station": {
                "platform_id": platform_id
            }
        },
            "destination": {
            "type": 2,
            "custom_location": location,
            "interval": {
                "from": int(time.time() + 86400),
                "to": int(time.time() + 86400 * 3)
            }
        },
        "items": [
            item
        ],
        "places": [
            place
        ],
        "billing_info": {
            "payment_method": 0
        },
        "recipient_info": recipient_info,
        "last_mile_policy": 0
    })
    headers = requestsHeaders

    r = requests.request("POST", url, headers=headers, data=payload)
    offer_id = r.json()['offers'][0]['offer_id']
    r.raise_for_status()

    print("offer_id = " + offer_id)

    return offer_id

def test_inn_confirm(offer_id):
    url = OFFER_CONFIRM_URL

    payload = json.dumps({
        "offer_id": offer_id
    })
    headers = requestsHeaders
    r = requests.request("POST", url, headers=headers, data=payload)

    request_id = r.json()['request_id']

    tmp = "https://tariff-editor.taxi.tst.yandex-team.ru/dragon-orders?cluster=platform&request_id="
    print(tmp + request_id)

    return request_id


def test_inn_checkInn(request_id):
    STATUS_URL = 'http://logistic-platform.taxi.tst.yandex.net/api/b2b/platform/request/info'

    r = requests.get(
        STATUS_URL,
        params={
            'request_id': request_id
        }
    )

    if r.status_code != 200:
        print(r.status_code, r.json())

    assert isinstance(r.json()['request']['items'][0]['billing_details']['inn'], int) is False, 'Инн пришел пустым'

    r.raise_for_status()


if __name__ == '__main__':
    create_response = test_inn_create()
    request_id = test_inn_confirm(offer_id=create_response)
    test_inn_checkInn(request_id)
