import os
import requests
import uuid

LOGISTIC_PLATFORM_URL = 'http://logistic-platform.taxi.yandex.net'
CREATE_URL = os.path.join(LOGISTIC_PLATFORM_URL, 'api/b2b/platform/offers/create')
CONFIRM_URL = os.path.join(LOGISTIC_PLATFORM_URL, 'api/b2b/platform/offers/confirm')
ADMIN_URL = 'https://tariff-editor.taxi.yandex-team.ru/'
ADMIN_REQUEST_PAGE = os.path.join(ADMIN_URL, 'dragon-orders/{}/info?cluster=platform')

TOKEN = ''
AUTHORIZATION = '524a679347c047ceb2479b59dfdf7950'
PAYLOAD = {
    "info": {
        "operator_request_id": str(uuid.uuid1())
    },
    "source": {
        "platform_station": {
            # "platform_id": "448a44b4-2b61-405c-8b75-c82f97791678"  # Ева новинский
            #  "platform_id": "dbee4575-9a39-4d34-a1c3-2594d97ee2fd"  # Ева екб
            # "platform_id": "f43a9f99-212a-44fe-acf3-54541401773b"  # Тарный
            # "platform_id": "1c5f5c0b-c731-419e-92dd-ec292e868878"  # Дропоф арбат4
            #   "platform_id": "b483f782-4565-46c4-9204-1dd9c3f1cc29"  # ева 22 #yd_old
            # "platform_id": "8dc9f59e-d037-4882-bb1b-69ec409d86a1"
        }
    },
    # "last_mile_policy": "self_pickup",
    # "destination": {
    #     "type": "platform_station",
    #     "platform_station": {
    #         "platform_id": "1cfb3544-3a91-4530-8104-f53ccd6a3315"
    #     },
    #     "interval_utc": {
    #         "from": "2022-05-26T14:00:00.000000Z",
    #         "to": "2022-05-26T14:00:00.000000Z"
    #     }
    # },
    "destination": {
        "type": 2,
        "custom_location": {
            "details": {
                "full_address": "Москва, Новинский бульвар, 8"
            }
        },
        "interval_utc": {
            "from": "2022-06-22T10:00:00.000000Z",
            "to": "2022-06-22T23:00:00.000000Z"
        }
    },

    "items": [
        {
            "article": "test-article",
            "count": 1,
            "name": "test",
            "barcode": "super-test-barcode",
            "place_barcode": "super-test-barcode",
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
            "barcode": "super-test-barcode"
        }
    ],
    "billing_info": {
        "payment_method": "already_paid"
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
