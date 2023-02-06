import os
from datetime import datetime
import time
import requests
import uuid
import sys

AUTHORIZATION = '70a499f9eec844e9a758f4bc33e667c0'
LOGISTIC_PLATFORM_URL = 'http://logistic-platform.taxi.tst.yandex.net'
CREATE_URL = os.path.join(LOGISTIC_PLATFORM_URL, 'api/b2b/platform/offers/create')
CONFIRM_URL = os.path.join(LOGISTIC_PLATFORM_URL, 'api/b2b/platform/offers/confirm')
ADMIN_URL = 'https://tariff-editor.taxi.tst.yandex-team.ru/'
ADMIN_REQUEST_PAGE = os.path.join(ADMIN_URL, 'dragon-orders/{}/info?cluster=platform')

PAYLOAD = {
   "info":{
      "operator_request_id": str(uuid.uuid4()),
   },
   "source":{
      "type":"platform_station",
      "platform_station":{
         "platform_id":"8c9b7de9-579b-475e-811e-c74005af2b75"
      }
   },
    "destination": {
        "type": 2,
        "custom_location": {
            "latitude": 55.723967,
            "longitude": 37.568408,
            "details": {
                "country": "Россия",
                "region": "Москва",
                "street": "улица Доватора",
                "house": "6/6к8",
                "housing": "1",
                "full_address": "119048, улица Доватора, 6/6к8, кв.29"
            }
        },
        "interval": {
            "from": int(time.time()) + 86400,
            "to": int(time.time()) + 86400*3
        }
    },
    "items": [
        {
            "count": 1,
            "name": "Товар в ассортименте по заказу И8000402353-1",
            "article": "И8000402353-1",
            "barcode": "И8000402353-1",
            "billing_details": {
                "unit_price": 2992,
                "assessed_unit_price": 2992
            },
            "physical_dims": {
                "predefined_volume": 71936235,
                "weight_gross": 9240
            },
            "place_barcode": "001-8000402353-1"
        }
    ],
    "places": [
        {
            "physical_dims": {
                "predefined_volume": 71936235
            },
            "description": "",
            "barcode": "001-8000402353-1"
        }
    ],
    "billing_info": {
        "payment_method": 0
    },
    "recipient_info": {
        "first_name": "Михаил",
        "last_name": "Грузднев",
        "partonymic": "Витальевич",
        "phone": "79036745169"
    },
    "last_mile_policy": 0,
}
def create():

    print("Request delivery interval from: ", datetime.utcfromtimestamp(PAYLOAD["destination"]["interval"]["from"]).strftime('%Y-%m-%d %H:%M:%S'))
    print("Request delivery interval to: ", datetime.utcfromtimestamp(PAYLOAD["destination"]["interval"]["to"]).strftime('%Y-%m-%d %H:%M:%S'))

    r = requests.post(
        CREATE_URL,
        headers={
            'Authorization': AUTHORIZATION,
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
            'Authorization': AUTHORIZATION,
        },
        json={
            'offer_id':offer_id
        }
    )
    r.raise_for_status()
    print(r.text)
    # request_id = r.json()['request_id']
    # print(f'\nRequest_id: {request_id}')
    # print(f'Request in admin: {ADMIN_REQUEST_PAGE.format(request_id)}')


if __name__ == '__main__':

    for param in sys.argv:
        if param == 'need_pricing':
            CREATE_URL += '?need_pricing=true'
            print(CREATE_URL)
        elif param.startswith('+7'):
            PAYLOAD['recipient_info']['phone'] = param


    offer_id = create()
    confirm(offer_id)
