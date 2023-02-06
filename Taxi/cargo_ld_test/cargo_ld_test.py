import argparse
import datetime
import json
import random
import os
import time
import copy

import requests
from requests.sessions import session

from generator import get_tvm_ticket
from orders import REGULAR_REQUEST_PAYLOAD, PULL_DISPATCH_REQUEST_PAYLOAD

EATS_CORP_CLIENT_ID = 'b8cfabb9d01d48079e35655c253035a9'
GROCERY_CORP_CLIENT_ID = '63f14a6fcce64e4d9ca49ad6958ababf'

CLAIM_ADMIN_URL = 'http://cargo-claims.taxi.tst.yandex.net/api/b2b/cargo-claims'
COURIER_SHIFTS_URL = 'http://ctt.eda.tst.yandex.net/driver/v1/courier_timetable/v1/courier-shifts'
CARGO_DISPATCH_URL = 'http://cargo-dispatch.taxi.tst.yandex.net/v1/admin'
TAXIMETER_URL = 'https://taximeter-core.tst.mobile.yandex.net/driver'
TARIFF_EDITOR_URL = 'https://tariff-editor.taxi.tst.yandex-team.ru'

DEFAULT_PULL_DISPATCH_LOGISTIC_GROUP = '28'

BASE_REQUEST_PAYLOAD = {
    'regular': REGULAR_REQUEST_PAYLOAD,
    'pull': PULL_DISPATCH_REQUEST_PAYLOAD,
}


LD_TESTING_TVM_ID = 2020943
CARGO_TESTING_TVM_ID = 2017979
CTT_EDA_TAESTING_TVM_ID = 2011736
CARGO_DISPATCH_TEST_TVM_ID = 2017977

def create_cargo_claim_id():
    result = ''
    for _ in range(32):
        result += random.choice('0123456789abcdef')
    return result


def get_corp_client_id(flow, corp_client_id):
    if not corp_client_id and flow == 'pull':
        corp_client_id = GROCERY_CORP_CLIENT_ID
    elif not corp_client_id:
        corp_client_id = EATS_CORP_CLIENT_ID
    return corp_client_id


def get_external_order_id():
    result = datetime.date.today().strftime('%y%m%d') + '-'
    for _ in range(6):
         result += random.choice('0123456789')
    return result


def create_cargo_claim(flow, corp_client_id, claim_kind, due_from_now, target_contractor_id=None, target_logistic_group=None, target_meta_group=None, force_no_batch=None, allow_rovers=None):
    request_payload = copy.deepcopy(BASE_REQUEST_PAYLOAD[flow])

    request_payload['due'] = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=due_from_now)).isoformat()
    request_payload['claim_kind'] = claim_kind

    external_order_id = get_external_order_id()

    for i in range(len(request_payload['route_points'])):
        if request_payload['route_points'][i]['type'] == 'return':
            continue
        route_points_data = request_payload['route_points'][i]
        route_points_data['external_order_id'] = external_order_id

    if target_contractor_id:
        request_payload['comment'] = '$$${"target_contractor_id": "' + target_contractor_id + '"}'

    if target_logistic_group is not None or target_meta_group is not None or flow == 'pull':
        soft_requirement = {
            'type': 'performer_group'
        }

        if target_logistic_group == 'null':
            target_logistic_group = None
        elif flow == 'pull' and target_logistic_group is None:
            target_logistic_group = DEFAULT_PULL_DISPATCH_LOGISTIC_GROUP

        if target_logistic_group is not None:
            soft_requirement['logistic_group'] = target_logistic_group
        if target_meta_group is not None:
            soft_requirement['meta_group'] = target_meta_group

        if len(soft_requirement) > 1:
            request_payload['requirements']['soft_requirements'].append(soft_requirement)

    request_payload['custom_context']['delivery_flags'] = {}
    if force_no_batch is not None:
        request_payload['custom_context']['delivery_flags']['is_forbidden_to_be_in_batch'] = force_no_batch
    if allow_rovers is not None:
        request_payload['custom_context']['delivery_flags']['is_rover_allowed'] = allow_rovers

    ticket = get_tvm_ticket(LD_TESTING_TVM_ID, CARGO_TESTING_TVM_ID)
    r = requests.post(
        CLAIM_ADMIN_URL + '/v2/claims/create?request_id=' + create_cargo_claim_id(),
        headers={
            'X-Ya-Service-Ticket':ticket,
            'X-B2B-Client-Id':corp_client_id,
            'X-Yandex-Login':'PERSONAL_DATA',
            'X-Yandex-UID':'123',
            'Accept-Language':'RU',
            'X-Remote-IP':'123',
            'Content-Type':'application/json',
        },
        json=request_payload
    )
    if r.status_code != 200:
        print('Erroneous response:', r.status_code, r.text)
        print('Request body', r.request.body)
    r.raise_for_status()
    claim_id = r.json()['id']
    return claim_id


def confirm_cargo_claim(claim_id, corp_client_id):
    ticket = get_tvm_ticket(LD_TESTING_TVM_ID, CARGO_TESTING_TVM_ID)
    for _ in range(100):
        r = requests.post(
            CLAIM_ADMIN_URL + '/v1/claims/accept?claim_id=' + claim_id,
            headers={
                'X-Ya-Service-Ticket':ticket,
                'X-B2B-Client-Id':corp_client_id,
                'X-Yandex-Login':'PERSONAL_DATA',
                'X-Yandex-UID':'123',
                'Accept-Language':'RU',
                'X-Remote-IP':'123',
                'Content-Type':'application/json',
            },
            json={
                'version': 1,
                'corp_client_id':corp_client_id
            }
        )
        if r.status_code == 409 or r.status_code == 404:
            time.sleep(0.1)
            continue
        if r.status_code == 200:
            return
        if r.status_code != 200:
            print('Erroneous response:', r.status_code, r.text)
        r.raise_for_status()
    raise RuntimeError('Confirmation of claim {} failed'.format(claim_id))


def courier_unplanned_start(courier_id, longitude, latitude):
    ticket = get_tvm_ticket(LD_TESTING_TVM_ID, CTT_EDA_TAESTING_TVM_ID)
    r = requests.post(
        COURIER_SHIFTS_URL + '/unplanned/start',
        headers={
            'X-YaEda-CourierId':courier_id,
            'X-Ya-Service-Ticket':ticket,
            'Content-Type':'application/json',
        },
        json={
            'id':'random-string',
            'location': {
                'latitude':latitude,
                'longitude':longitude
            },
            'duration': 7200,
            'ignoreWarnings': False
        }
    )
    if r.status_code == 204:
        return
    if r.status_code != 204:
        print('Erroneous response:', r.status_code, r.text)
    if r.status_code == 200:
        raise RuntimeError('Bad status code: 200')
    r.raise_for_status()


def courier_shifts_actual(courier_id):
    ticket = get_tvm_ticket(LD_TESTING_TVM_ID, CTT_EDA_TAESTING_TVM_ID)
    r = requests.get(
        COURIER_SHIFTS_URL + '/actual',
        headers={
            'X-YaEda-CourierId':courier_id,
            'X-Ya-Service-Ticket':ticket,
            'Content-Type':'application/json',
        }
    )
    if r.status_code == 200:
        return
    if r.status_code != 200:
        print('Erroneous response:', r.status_code, r.text)
    r.raise_for_status()
    print(r.request.body)


def get_segment_id(claim_id):
    ticket = get_tvm_ticket(LD_TESTING_TVM_ID, CARGO_TESTING_TVM_ID)
    for _ in range(100):
        r = requests.post(
            'http://cargo-claims.taxi.tst.yandex.net/v2/admin/claims/full',
            headers={
                'X-Ya-Service-Ticket':ticket,
                'Content-Type':'application/json',
            },
            params={
                'claim_id': claim_id
            }
        )
        if r.status_code == 409 or r.status_code == 404:
            time.sleep(0.1)
            continue
    segment_id = r.json()['claim']['segments'][0]['id']
    return segment_id


def get_waybill_id(segment_id):
    ticket = get_tvm_ticket(LD_TESTING_TVM_ID, CARGO_DISPATCH_TEST_TVM_ID)
    for _ in range(200):
        r = requests.post(
            CARGO_DISPATCH_URL +'/segment/info',
            headers={
                'X-Ya-Service-Ticket':ticket,
                'Content-Type':'application/json',
            },
            params={
                'segment_id': segment_id
            }
        )
        if (r.status_code != 200) or (hasattr(r.json()['dispatch'], 'chosen_waybill') == False):
            time.sleep(0.3)
            continue
    waybill_external_ref = r.json()['dispatch']['chosen_waybill']['external_ref']
    return waybill_external_ref


def open_waybill(waybill_external_ref):
    ticket = get_tvm_ticket(LD_TESTING_TVM_ID, CARGO_DISPATCH_TEST_TVM_ID)
    for _ in range(200):
        r = requests.post(
            CARGO_DISPATCH_URL + '/waybill/info',
                headers={
                    'X-Ya-Service-Ticket':ticket,
                    'Content-Type':'application/json',
                },
                params={
                    'waybill_external_ref':waybill_external_ref
                }
        )
        if r.status_code == 409 or r.status_code == 404:
            time.sleep(0.1)
            continue
    taxi_order_id  = r.json()['execution']['taxi_order_info']['order_id']
    return taxi_order_id


def get_pro_order_id(taxi_order_id):
    ticket = get_tvm_ticket(LD_TESTING_TVM_ID, CARGO_DISPATCH_TEST_TVM_ID)
    for _ in range(100):
        r = requests.post(
            TARIFF_EDITOR_URL + '/api-t/payments/orders_info/',
                headers={
                    'X-Ya-Service-Ticket':ticket,
                    'Content-Type':'application/json',
                },
                json={
                    'order_id': taxi_order_id
                }
        )
    print(r.text)
    print(r.request.body)
    pro_order_id = r.json()['orders'][0]['alias_id']
    return pro_order_id


def pro_authorization(mobile_courier, uuid_courier, latitude, longitude, date, device_id):
    r = requests.post(
        TAXIMETER_URL + '/authorization/login/new?proxy_block_id=default&device_id=' + device_id,
            headers={
               'Host':'taximeter-core.tst.mobile.yandex.net',
               'version':'9.71 (2147483647)',
                'x-user-agent-split':'Taximeter 9.71 (2147483647)',
                'accept-language':'en',
                'user-agent':'Taximeter 9.71 (2147483647)',
                'accept':'application/json',
                'content-type':'application/x-www-form-urlencoded',
            },
            data="step=send_sms&phone=%2B" + mobile_courier + "&token=&deviceId=" + device_id + "&deviceModel=SAMSUNG%20SM-A505FN&networkOperator=Android&uuid=" + uuid_courier + "&metricaDeviceId=931df3e487d81b52ab5eb101c8d25d8b&locale=ru&gdpr_accept_date=" + date + "&lat="+ latitude + "&lon=" + longitude + ""
    )
    token = r.json()['token']
    db_id = r.json()['domains'][0]['id']
    return token


def pro_login(mobile_courier, uuid_courier, token, db_id, device_id):
    r = requests.post(
        TAXIMETER_URL + '/authorization/login/new?proxy_block_id=default&device_id=' + device_id,
         headers={
               'Host':'taximeter-core.tst.mobile.yandex.net',
               'version':'9.71 (2147483647)',
                'x-user-agent-split':'Taximeter 9.71 (2147483647)',
                'accept-language':'en',
                'user-agent':'Taximeter 9.71 (2147483647)',
                'accept':'application/json',
                'content-type':'application/x-www-form-urlencoded',
            },
        data="step=select_db&phone=%2B" + mobile_courier + "&token=" + token + "&deviceId=" + device_id + "&deviceModel=SAMSUNG%20SM-A505FN&networkOperator=&uuid=" + uuid_courier + "&metricaDeviceId=931df3e487d81b52ab5eb101c8d25d8b&locale=ru&db=" + db_id + ""
    )
    session = r.json()['login']['session']
    return session


def pro_accept(uuid_courier, db_id, latitude, longitude, session, pro_order_id, date, server_time, device_id):
    r = requests.post(
        TAXIMETER_URL + '/requestconfirm/set?proxy_block_id=default&device_id=' + device_id + '&park_id=' + db_id,
        headers={
                'Host':'taximeter-core.tst.mobile.yandex.net',
                'version':'9.71 (2147483647)',
                'x-user-agent-split':'Taximeter 9.71 (2147483647)',
                'accept-language':'en',
                'user-agent':'Taximeter 9.71 (2147483647)',
                'accept':'application/json',
                'content-type':'application/x-www-form-urlencoded',
                'x-driver-session':session,
            },
        data="" + date + "&is_yandex=false&statusDistance=0.0&is_offline=false&driver=" + uuid_courier + "&driverclientchat_enabled=true&total_distance=0.0&is_captcha=false&imei=" + device_id + "&coord_providers=%5B%7B%22accuracy%22%3A140.0%2C%22lat%22%3A" + latitude + "%2C%22lon%22%3A" + longitude + "%2C%22type%22%3A%22lbs-wifi%22%2C%22server_time%22%3A" + server_time + "%2C%22location_time%22%3A" + server_time + "%7D%2C%7B%22accuracy%22%3A18.501%2C%22lat%22%3A" + latitude + "%2C%22lon%22%3A" + longitude + "%2C%22type%22%3A%22network%22%2C%22server_time%22%3A" + server_time + "%2C%22location_time%22%3A"+ server_time +"%7D%5D&driverclientchat_translate_enabled=true&driver_status=free&is_airplanemode=false&order=" + pro_order_id  + "&status=2"
    )
    print(r.text)
    print(r.request.body)


def pro_polling_state(device_id, db_id, latitude, longitude, session):
    r = requests.post(
        TAXIMETER_URL + '/driver/polling/state',
        headers={
                'Host':'taximeter-core.tst.mobile.yandex.net',
                'version':'9.71 (2147483647)',
                'x-user-agent-split':'Taximeter 9.71 (2147483647)',
                'accept-language':'en',
                'user-agent':'Taximeter 9.71 (2147483647)',
                'accept':'application/json',
                'content-type':'application/x-www-form-urlencoded',
                'x-driver-session':session,
            },
        params={
            'lat':latitude,
            'lon':longitude,
            'driver_mode_policy':'cached',
            'proxy_block_id':'default',
            'device_id':device_id,
            'park_id':db_id
        }
    )


def pro_actual_timetable(device_id, db_id, session):
    r = requests.get(
        TAXIMETER_URL + '/driver/v1/courier_timetable/v1/courier-shifts/actual',
        headers={
                'Host':'taximeter-core.tst.mobile.yandex.net',
                'version':'9.71 (2147483647)',
                'x-user-agent-split':'Taximeter 9.71 (2147483647)',
                'accept-language':'en',
                'user-agent':'Taximeter 9.71 (2147483647)',
                'accept':'application/json',
                'content-type':'application/x-www-form-urlencoded',
                'x-driver-session':session,
            },
        params={
            'proxy_block_id':'default',
            'device_id':device_id,
            'park_id':db_id
        }
    )
    id_shift = r.json()['data'][0]['id']
    return id_shift
