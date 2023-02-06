import os
from datetime import datetime
import time
import requests
import uuid
import sys

LOGISTIC_PLATFORM_PRE_URL = 'http://tbbsvq7fwowvfhuh.vla.yp-c.yandex.net/'
CREATE_URL = os.path.join(LOGISTIC_PLATFORM_PRE_URL, 'api/b2b/platform/offers/create')
CONFIRM_URL = os.path.join(LOGISTIC_PLATFORM_PRE_URL, 'api/b2b/platform/offers/confirm')
EDIT_URL = os.path.join(LOGISTIC_PLATFORM_PRE_URL, 'api/b2b/platform/request/edit')
ADMIN_URL = 'https://tariff-editor.taxi.yandex-team.ru/'
ADMIN_REQUEST_PAGE = os.path.join(ADMIN_URL, 'dragon-orders/{}/info?cluster=platform')

import datetime

end_date = datetime.datetime.now() + datetime.timedelta(days=3)
DATE = end_date.strftime("%Y-%m-%d %H:%M:%S")
TOKEN = ''

def make_time_in_future(days=4, hours=14):
    t = int(time.time())
    t -= t % 86400
    t += 86400 * days + 3600 * hours
    return t

FourdaysInFuture = make_time_in_future()
Tommorow = make_time_in_future(1)
SevenDaysInFuture = make_time_in_future(7)

AUTHORIZATION = '585b653b774b42569a058d86d4a34ce7'
PAYLOAD = {
    "info": {
        "operator_request_id": str(uuid.uuid1())
    },
    "source": {
        "platform_station": {
            # "platform_id": "ae3a6f41-3664-49d1-ae15-f9de3ea81c9b"
            "platform_id": "f43a9f99-212a-44fe-acf3-54541401773b"
        }
    },
    # "last_mile_policy": "self_pickup",
    # "destination": {
    #     "type": "platform_station",
    #     "platform_station": {
    #         "platform_id": "328af435-d6d7-4bb9-b011-45e3d66c89ea"  # Пункт выдачи заказов Яндекс Маркета
    #     },
    #     "interval": {
    #         "from": FourdaysInFuture,
    #         "to": FourdaysInFuture  # помним, что для пвз время одинаковое
    #     }
    # },
    "destination": {
        "type": 2,
        "custom_location": {
            "details": {
                "full_address": "Москва, улица Азовская, 24к1"
            }
        },
        "interval_utc": {
            "from": "2022-05-27T10:00:00.000000Z",
            "to": "2022-05-27T23:00:00.000000Z"
        }
    },

    "items": [
        {
            "article": "test-article",
            "count": 1,
            "name": "test",
            "barcode": "super-test-barcode_spb",
            "place_barcode": "super-test-barcode_spb",
            "physical_dims": {
                "weight_gross": 0,
                "predefined_volume": 0
            },
            "billing_details": {
                "unit_price": 1000,
                "assessed_unit_price": 1000,
                "inn": "7716760301",
                "nds": 20
            }
        }
    ],
    "places": [
        {
            "physical_dims": {
                "dx": 1,
                "dy": 10,
                "dz": 1,
                "weight_gross": 1000,
                "predefined_volume": 10
            },
            "barcode": "super-test-barcode_spb"
        }
    ],
    "billing_info": {
        "payment_method": "already_paid"
        # "payment_method": "card_on_receipt"
    },
    "recipient_info": {
        "first_name": "Никита",
        "last_name": "Сапун",
        "partonymic": "Сергеевич",
        "phone": "79258425522"
    },
    "particular_items_refuse": False
}


def create():

    r = requests.post(
        CREATE_URL,
        headers={
            'X-B2B-Client-Id': AUTHORIZATION,
            'X-Ya-Service-Ticket': TOKEN
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
            'X-B2B-Client-Id': AUTHORIZATION,
            'X-Ya-Service-Ticket': TOKEN
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

    offer_id = create()
    # confirm(offer_id)
