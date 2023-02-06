import os
import time
import requests
import uuid

LOGISTIC_PLATFORM_URL = 'http://logistic-platform.taxi.tst.yandex.net/platform/'
ADD_SIMPLE_URL = os.path.join(LOGISTIC_PLATFORM_URL, 'requests/add_simple')
ADMIN_URL = 'https://tariff-editor.taxi.tst.yandex-team.ru/'
ADMIN_REQUEST_PAGE = os.path.join(ADMIN_URL, 'dragon-orders/{}/info?cluster=platform')


def make_time_next_week_morning():
    t = int(time.time())
    t -= t % 86400
    t += 86400 * 7 + 3600 * 8
    return t

NextWeekMorning = make_time_next_week_morning()

AUTHORIZATION = 'beru'
PAYLOAD = {
    "request": {
        "nodes": {
            "objects": [
                {
                    "node_code": "n_from",
                    "node_location": {
                        "description": "Стартовая точка доставки",
                        "search_context": {
                            "input_intervals": [
                                {
                                    "from": NextWeekMorning,
                                    "to": NextWeekMorning + 3600 * 4
                                }
                            ],
                            "output_intervals": [
                                {
                                    "from": NextWeekMorning + 3600 * 2,
                                    "to": NextWeekMorning + 3600 * 5
                                },
                                {
                                    "from": NextWeekMorning + 86400 + 3600 * 5,
                                    "to": NextWeekMorning + 86400 + 3600 * 8
                                },
                                {
                                    "from": NextWeekMorning + 86400 * 2 + 3600 * 8,
                                    "to": NextWeekMorning + 86400 * 2 + 3600 * 10
                                }
                            ]
                        },
                        "class_name": "auto_detected"
                    }
                },
                {
                    "node_code": "n_to",
                    "node_location": {
                        "coord": {
                            "lat": 55.751312,
                            "lon": 37.584618
                        },
                        "details": {
                            "street": "Новинский бульвар",
                            "locality": "Москва",
                            "country": "Россия",
                            "house": "8",
                            "settlement": "Москва",
                            "region": "Москва и Московская область",
                            "district": "Центральный административный округ"
                        },
                        "class_name": "tmp"
                    }
                }
            ],
            "from": "n_from",
            "to": "n_to",
            "return": "n_from"
        },
        "delivery_time": {
            "min": NextWeekMorning + 3600,
            "max": NextWeekMorning + 86400 * 2 + 3600 * 10,
            "policy": "min_by_request"
        },
        "request_code": str(uuid.uuid4().hex),
        "decision_deadline": 0,
        "resource": {
            "start_is_ready": False,
            "recipient": {
                "yandex_uid": "13899599811",
                "payment_method": "already_paid",
                "first_name": "Робосклад",
                "last_name": "Проверкин",
                "contacts": [
                    {
                        "class_name": "phone",
                        "phone_contact": {
                            "phone_number": "+70000000034"
                        }
                    },
                    {
                        "class_name": "email",
                        "email_contact": {
                            "email_address": "ytugator@yandex-team.ru"
                        }
                    }
                ]
            },
            "resource_physical_feature": {
                "weight": 100,
                "d_x": 80,
                "d_y": 30,
                "d_z": 10,
                "rotatable": True,
                "items": [
                    {
                        "d_x": 80,
                        "d_y": 30,
                        "d_z": 10,
                        "article": "33040387",
                        "name": "Заказ №33040387",
                        "count": 1,
                        "weight_net": 100,
                        "weight_gross": 100,
                        "weight_tare": 0,
                        "unit_price": 232,
                        "assessed_unit_price": 232
                    }
                ]
            }

        }
    }
}


def create():

    r = requests.post(
        ADD_SIMPLE_URL,
        headers={
            'Authorization': AUTHORIZATION,
        },
        json=PAYLOAD
    )
    r.raise_for_status()
    request_id = r.json()['request_id']
    print(f"\noffers/create response headers: {r.headers}\n")
    print(f"offers/create response json: {r.json()}")
    print(f'\nRequest_id: {request_id}')
    print(f'Request in admin: {ADMIN_REQUEST_PAGE.format(request_id)}')
    return

if __name__ == '__main__':

    offer_id = create()

