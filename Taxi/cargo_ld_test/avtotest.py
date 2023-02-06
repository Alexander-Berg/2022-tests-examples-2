import argparse
import copy
import datetime
import json
import os
import random
import time

import requests
from cargo_ld_test import (confirm_cargo_claim, courier_unplanned_start,
                           create_cargo_claim,
                           get_segment_id, get_waybill_id, open_waybill,
                           pro_accept, pro_authorization, pro_login, pro_polling_state)
from courier import (COURIER_LAVKA_DB_ID, COURIER_LAVKA_UUID_ID, COURIER_LAVKA_PHONE, COURIER_EDA_DB_ID, COURIER_EDA_UUID_ID, COURIER_LAVKA, COURIER_EDA, LAVKA_LATITUDE, LAVKA_LONGTITUDE, EDA_LATTITUDE, EDA_LONGTITUDE, COURIER_EDA_PHONE)
import tariff_editor


CLAIM_ADMIN_URL = 'https://tariff-editor.taxi.tst.yandex-team.ru/corp-claims/show/{}/info'
WAYBILL_URL = 'http://cargo-dispatch.taxi.tst.yandex.net/v1/admin/waybill/info'
TAXI_ADMIN_URL = 'https://tariff-editor.taxi.tst.yandex-team.ru/orders/{}'

LD_TESTING_TVM_ID = 2020943
CARGO_TESTING_TVM_ID = 2017979
CTT_EDA_TAESTING_TVM_ID = 2011736
CARGO_DISPATCH_TEST_TVM_ID = 2017977

DEVICE_ID_1 = '863817037878587'
DEVICE_ID_2 = '359462105707516'

DATE = datetime.datetime.now().isoformat(sep='T')
SERVER_TIME = int(time.time())



def lavka():
    token = pro_authorization(COURIER_LAVKA_PHONE, COURIER_LAVKA_UUID_ID,'{}'.format(LAVKA_LATITUDE),'{}'.format(LAVKA_LONGTITUDE),'{}'.format(DATE), DEVICE_ID_1)
    session = pro_login(COURIER_LAVKA_PHONE, COURIER_LAVKA_UUID_ID, token,COURIER_LAVKA_DB_ID, DEVICE_ID_1)
    pro_polling_state(DEVICE_ID_1, COURIER_LAVKA_DB_ID,'{}'.format(LAVKA_LATITUDE), '{}'.format(LAVKA_LONGTITUDE), session)
    courier_unplanned_start(COURIER_LAVKA, LAVKA_LONGTITUDE, LAVKA_LATITUDE)
    claim_id = create_cargo_claim(
        flow='pull',
        target_contractor_id=COURIER_LAVKA_DB_ID + '_' + COURIER_LAVKA_UUID_ID,
        corp_client_id='63f14a6fcce64e4d9ca49ad6958ababf',
        target_logistic_group='28',
        claim_kind='platform_usage',
        target_meta_group=None,
        force_no_batch=None,
        allow_rovers=None,
        due_from_now = 120
    )
    print('Claim created:', CLAIM_ADMIN_URL.format(claim_id))
    confirm_cargo_claim(claim_id, '63f14a6fcce64e4d9ca49ad6958ababf')
    print('Claim {} confirmed'.format(claim_id))
    segment_id = get_segment_id(claim_id)
    print('Segment_id {}'.format(segment_id))
    waybill_external_ref = get_waybill_id(segment_id)
    print('Waybill_id {}'.format(waybill_external_ref))
    taxi_order_id = open_waybill(waybill_external_ref)
    doc = tariff_editor.TARIFF_EDITOR_CLIENT.retrieve_order_entity(taxi_order_id,'order_proc')
    pro_order_id = doc['candidates'][-1]['alias_id']
    print('Taxi_order_id:', TAXI_ADMIN_URL.format(taxi_order_id))
    pro_accept(COURIER_LAVKA_UUID_ID,COURIER_LAVKA_DB_ID,'{}'.format(LAVKA_LATITUDE),'{}'.format(LAVKA_LONGTITUDE), session, pro_order_id, '{}'.format(DATE),'{}'.format(SERVER_TIME), DEVICE_ID_1)


def eda():
    token = pro_authorization(COURIER_EDA_PHONE, COURIER_EDA_UUID_ID, '{}'.format(EDA_LATTITUDE),'{}'.format(EDA_LONGTITUDE),'{}'.format(DATE), DEVICE_ID_2)
    session = pro_login(COURIER_EDA_PHONE, COURIER_EDA_UUID_ID, token, COURIER_EDA_DB_ID, DEVICE_ID_2)
    courier_unplanned_start(COURIER_EDA, EDA_LONGTITUDE, EDA_LATTITUDE)
    claim_id = create_cargo_claim(
        flow='regular',
        target_contractor_id=COURIER_EDA_DB_ID + '_' + COURIER_EDA_UUID_ID,
        corp_client_id='b8cfabb9d01d48079e35655c253035a9',
        target_logistic_group=None,
        claim_kind='platform_usage',
        target_meta_group=None,
        force_no_batch=None,
        allow_rovers=None,
        due_from_now =120
    )
    print('Claim created:', CLAIM_ADMIN_URL.format(claim_id))
    confirm_cargo_claim(claim_id, 'b8cfabb9d01d48079e35655c253035a9')
    print('Claim {} confirmed'.format(claim_id))
    segment_id = get_segment_id(claim_id)
    print('Segment_id {}'.format(segment_id))
    waybill_external_ref = get_waybill_id(segment_id)
    print('Waybill_id {}'.format(waybill_external_ref))
    taxi_order_id = open_waybill(waybill_external_ref)
    doc = tariff_editor.TARIFF_EDITOR_CLIENT.retrieve_order_entity(taxi_order_id,'order_proc')
    pro_order_id = doc['candidates'][-1]['alias_id']
    print('Taxi_order_id:', TAXI_ADMIN_URL.format(taxi_order_id))
    pro_accept(COURIER_EDA_UUID_ID,COURIER_EDA_DB_ID,'{}'.format(EDA_LATTITUDE),'{}'.format(EDA_LONGTITUDE), session, pro_order_id, '{}'.format(DATE),'{}'.format(SERVER_TIME), DEVICE_ID_2)


if __name__ == '__main__':
    lavka()
