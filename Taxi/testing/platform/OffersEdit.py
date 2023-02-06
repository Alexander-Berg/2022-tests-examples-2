import os
import requests
import uuid
import time
import re
import argparse

LOGISTIC_PLATFORM_URL = 'http://logistic-platform.taxi.tst.yandex.net'
CREATE_URL = os.path.join(LOGISTIC_PLATFORM_URL, 'api/b2b/platform/offers/create')
CONFIRM_URL = os.path.join(LOGISTIC_PLATFORM_URL, 'api/b2b/platform/offers/confirm')
EDIT_URL = os.path.join(LOGISTIC_PLATFORM_URL, 'api/b2b/platform/request/edit')
ADMIN_URL = 'https://tariff-editor.taxi.tst.yandex-team.ru/'
ADMIN_REQUEST_PAGE = os.path.join(ADMIN_URL, 'dragon-orders/{}/info?cluster=platform')

def get_tvm_ticket():
    os.popen('ssh-add')
    a = os.popen('ya tool tvmknife get_service_ticket sshkey --src 2013636 --dst 2024159').read()
    match = re.search(r'(3:serv:.*)$', a)
    ticket = match.group(0)
    return ticket

AUTHORIZATION = '2283221488'

EDIT_PAYLOAD = {

    "request_id": " ",

    "recipient_info": {
        "email": "ytugator@ya.ru",
        "phone": "+79258425522",
        "first_name": "Абдул",
        "last_name": "Изменёнович"
    },

    "places": [
        {
            "barcode": "YD_4400069216",
            "place": {
                "barcode": "YD_4400069210001",
                "physical_dims": {
                    "dx": 9,
                    "dy": 15,
                    "dz": 21,
                    "predefined_volume": 1500,
                    "weight_gross": 158

                }
            }
        }
    ],




}


def edit():

    r = requests.post(
        EDIT_URL,
        headers={
            'X-B2B-Client-id': AUTHORIZATION,
            'X-Ya-Service-Ticket': tvm
        },
        json=EDIT_PAYLOAD
    )
    print(f"\noffers/edit response headers: {r.headers}\n")
    print(f"offers/edit response json: {r.json()}\n")
    r.raise_for_status()



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='id')
    parser.add_argument('-r', '--request_id', type=str)
    args = parser.parse_args()

    EDIT_PAYLOAD.update(request_id=args.request_id)

    tvm = get_tvm_ticket()
    edit()
