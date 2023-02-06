import os
import requests
import uuid
import time

AUTHORIZATION = '2283221488'
LOGISTIC_PLATFORM_URL = 'http://logistic-platform.taxi.tst.yandex.net'
CREATE_URL = os.path.join(LOGISTIC_PLATFORM_URL, 'api/b2b/platform/offers/create')
CONFIRM_URL = os.path.join(LOGISTIC_PLATFORM_URL, 'api/b2b/platform/offers/confirm')
ADMIN_URL = 'https://tariff-editor.taxi.tst.yandex-team.ru/'
ADMIN_REQUEST_PAGE = os.path.join(ADMIN_URL, 'dragon-orders/{}/info?cluster=platform')


def make_time_in_future(days=4, hours=14):
    t = int(time.time())
    t -= t % 86400
    t += 86400 * days + 3600 * hours
    return t

FourdaysInFuture = make_time_in_future()
Tommorow = make_time_in_future(1)
SevenDaysInFuture = make_time_in_future(7)


SC_PVZ = { #ок
    "source": {
        "platform_station": {
            "platform_id": "863b4ca0-e469-40f1-a1d9-5d93ec6b76ad"  # сц софьино
        }
    },
    "last_mile_policy": "self_pickup",
    "destination": {
        "type": "platform_station",
        "platform_station": {
            "platform_id": "95551dac-6017-4806-b5be-faa849cc4401" #Пункт выдачи заказов Яндекс Маркета
        },
        "interval": {
            "from": FourdaysInFuture,
            "to": FourdaysInFuture  #помним, что для пвз время одинаковое
        }
    },
}

PVZ_CS_PVZ = { #ок
    "source": {
        "platform_station": {
            "platform_id": "068f933a-0f84-431e-a998-f9dcf300414b"  # забиякин ПВЗ
        }
    },
    "last_mile_policy": "self_pickup",
    "destination": {
        "type": "platform_station",
        "platform_station": {
            "platform_id": "95551dac-6017-4806-b5be-faa849cc4401" #Пункт выдачи заказов Яндекс Маркета
        },
        "interval": {
            "from": FourdaysInFuture,
            "to": FourdaysInFuture  #помним, что для пвз время одинаковое
        }
    },
}

PVZ_CUR = { #не пашет
    "source": {
        "platform_station": {
            "platform_id": "068f933a-0f84-431e-a998-f9dcf300414b"  # забиякин ПВЗ
        }
    },
    "destination": {
        "type": "custom_location",
        "custom_location": {
            "details": {
                "full_address": "117452, Москва, Азовская, 24, кв.1"
            }
        },
        "interval": {
            "from": Tommorow,
            "to": SevenDaysInFuture
        }
    },
}

SC_CUR = { #ок
    "source": {
        "platform_station": {
            "platform_id": "863b4ca0-e469-40f1-a1d9-5d93ec6b76ad"  # сц софьино
        }
    },
    "destination": {
        "type": "custom_location",
        "custom_location": {
            "details": {
                "full_address": "117452, Москва, Азовская, 24, кв.1"
            }
        },
        "interval": {
            "from": Tommorow,
            "to": SevenDaysInFuture
        }
    },
}

SC_SC_PVZ = { #ОК
    "source": {
        "platform_station": {
            "platform_id": "e7a877bf-c462-4b19-a091-bcd6fafe298f"  # Тарный
        }
    },
    "last_mile_policy": "self_pickup",
    "destination": {
        "type": "platform_station",
        "platform_station": {
            "platform_id": "2b56434f-e506-47a6-91dd-063d5e800bfd"  # Пункт выдачи заказов Яндекс Маркета
        },
        "interval": {
            "from": FourdaysInFuture,
            "to": FourdaysInFuture  # помним, что для пвз время одинаковое
        }
    },
}


INFO = {
    "billing_info": {
        "payment_method": "card_on_receipt"
    },
    "info": {
        "operator_request_id": ""
    },
    "items": [
        {
            "article": "00699",
            "count": 1,
            "name": "Домалогика контактор R63-20 230V модульный ETI",
            "place_barcode": "28127346",
            "marking_code": " ",
            "billing_details": {
                "unit_price": 395800,
                "nds": 0,
                "assessed_unit_price": 0
            }
        }
    ],
    "particular_items_refuse": False,
    "places": [
        {
            "barcode": "28127346",
            "physical_dims": {
                "dx": 1,
                "dy": 10,
                "dz": 1,
                "weight_gross": 1
            }
        }
    ],
    "recipient_info": {
        "email": "ytugator@ya.ru",
        "phone": "+79258425522",
        "first_name": "Абдул",
        "last_name": "АбульАбасович"
    },

}


def make_payload(Type):
    request_id = {
        "info": {
            "operator_request_id": str(uuid.uuid4())
        },
    }
    Info = INFO | request_id
    return Info | Type


def create(payload):
    r = requests.post(
        CREATE_URL,
        headers={
            'Authorization': AUTHORIZATION,
        },
        json=payload
    )
    # print(f"\noffers/create response headers: {r.headers}\n")
    # print(f"offers/create response json: {r.json()}\n")
    offer_id = r.json()['offers'][0]['offer_id']
    # print('offer_id = ' + offer_id)
    r.raise_for_status()
    return offer_id


def confirm(offer_id):
    r = requests.post(
        CONFIRM_URL,
        headers={
            'Authorization': AUTHORIZATION,
        },
        json={
            'offer_id': offer_id
        }
    )
    r.raise_for_status()
    request_id = r.json()['request_id']
    # print(f'\nRequest_id: {request_id}')
    # print(f'Request in admin: {ADMIN_REQUEST_PAGE.format(request_id)}')


if __name__ == '__main__':

    types = [SC_PVZ, PVZ_CS_PVZ, SC_CUR, SC_SC_PVZ]

    for type in types:
        try:
            payload = make_payload(type)
            offer_id = create(payload)
            confirm(offer_id)
            print("ok")
            time.sleep(3)
        except:
            print("fail: \n", type)
