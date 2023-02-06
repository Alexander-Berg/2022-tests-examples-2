# -*- coding: utf-8 -*-

import argparse
import json
import random
import requests
import string


from requests.packages.urllib3.exceptions import InsecureRequestWarning

from taxi.core import db
from taxi.core import async

# import logging
# logging.basicConfig(level=logging.DEBUG)

# suppress `verify=False` warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

INTEGRATION_API_URL = 'https://voucher-order-auth.taxi.tst.yandex.net'
PROTOCOL_API_URL = 'http://taxi-protocol.taxi.tst.yandex.net'


def create_order(car_number):
    url = '%s/svo/order' % PROTOCOL_API_URL
    data = json.dumps({
        'car_number': car_number,
        'polygon_id': 'BL2'
    })
    headers = {
        'Ya-Taxi-Token': 'edb7ca97fa6644dc97b273e566d63848'
    }
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()


def estimate():
    url = '%s/v1/offers/estimate' % INTEGRATION_API_URL
    data = json.dumps({
        'chainid': '380a588a-5ed2-4945-befa-2b26d5d4ed6c',
        'requirements': {},
        'route': [
            [37.409756, 55.961587], [37.646453, 55.822028]
        ],
        'selected_class': 'econom',
        'sourceid': 'svo_order',
        'user': {
            'phone': '+79151111111'
        }
    })
    headers = {
        'Authorization': 'Basic seekuy1zae9Eithu',
    }
    response = requests.post(url, data=data, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()


def _gen_random_string(length):
    return ''.join(random.choice(string.digits) for _ in range(length))


def confirm_offer(user_id, offer_id):
    url = '%s/v1/offers/confirm' % INTEGRATION_API_URL

    raw_cash_desk_data = 't=20180618T1603&s=1.00&fn={}&i={}&fp=1001001181&n=1'.format(
        _gen_random_string(16),
        _gen_random_string(5),
    )
    data = json.dumps({
        'chainid': '44612952-a505-43e7-9329-b1523af55d83',
        'class': 'econom',
        'id': user_id,
        'offer': offer_id,
        'payment': {
            'raw_cash_desk_data': raw_cash_desk_data,
            'type': u'prepaid'
        },
        'route': [
            {
                'place_id': 'ymapsbm1://geo?ll=37.409756%2C55.961587&spn=0.005%2C0.015&text=%d0%a0%d0%be%d1%81%d1%81%d0%b8%d1%8f%2c+%d0%9c%d0%be%d1%81%d0%ba%d0%be%d0%b2%d1%81%d0%ba%d0%b0%d1%8f+%d0%be%d0%b1%d0%bb%d0%b0%d1%81%d1%82%d1%8c%2c+%d0%b3%d0%be%d1%80%d0%be%d0%b4%d1%81%d0%ba%d0%be%d0%b9+%d0%be%d0%ba%d1%80%d1%83%d0%b3+%d0%a5%d0%b8%d0%bc%d0%ba%d0%b8%2c+%d0%b0%d1%8d%d1%80%d0%be%d0%bf%d0%be%d1%80%d1%82+%d0%a8%d0%b5%d1%80%d0%b5%d0%bc%d0%b5%d1%82%d1%8c%d0%b5%d0%b2%d0%be',
                'point': [37.409756, 55.961587]
            },
            {
                'place_id': 'ymapsbm1://geo?ll=37.646453%2C55.822028&spn=0.005%2C0.015&text=%d0%a0%d0%be%d1%81%d1%81%d0%b8%d1%8f%2c+%d0%9c%d0%be%d1%81%d0%ba%d0%b2%d0%b0%2c+%d0%bf%d1%80%d0%be%d1%81%d0%bf%d0%b5%d0%ba%d1%82+%d0%9c%d0%b8%d1%80%d0%b0%2c+150',
                'point': [37.646453, 55.822028]
            }
        ]
    })
    headers = {
        'Authorization': 'Basic seekuy1zae9Eithu',
    }
    response = requests.post(url, data=data, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()


@async.inline_callbacks
def requestconfirm(order_id, voucher_code, status):
    order_proc = yield db.order_proc.find_one(order_id,
                                              ['candidates', 'alias_id'])
    if not order_proc:
        print 'no order with id=%s found' % order_id
        async.return_value(None)

    if len(order_proc['candidates']) != 1:
        print 'offer must be assigned to 1 driver'
        async.return_value(None)

    alias_id = order_proc['candidates'][0]['alias_id']
    driver_id = order_proc['candidates'][0]['driver_id']
    clid, uuid = driver_id.split('_')

    url = '%s/1.x/requestconfirm' % PROTOCOL_API_URL
    params = {
        'orderid': alias_id,
        'status': status,
        'apikey': '4f502b7cdbd043b19cd381e307e5cdf2',
        'uuid': uuid,
        'clid': clid,
        'voucher_code': voucher_code
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    async.return_value(response.json())


@async.inline_callbacks
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command',
                        choices=['create_order', 'confirm_offer', 'requestconfirm'],
                        help='command to run')
    parser.add_argument('--car-number', help='car number for create_order')
    parser.add_argument('--order', help='order for requestconfirm')
    parser.add_argument('--voucher', help='voucher code for requestconfirm')
    parser.add_argument('--status', help='status for requestconfirm')
    args = parser.parse_args()

    if args.command == 'create_order':
        if not args.car_number:
            print 'usage: python %s %s --car-number КВ12877' % (__file__,
                                                               args.command)
            return
        order = create_order(args.car_number)
        order_id = order['order_id']
        print '>>> order_id=%s' % order_id
    elif args.command == 'confirm_offer':
        estimation = estimate()
        user_id = estimation['user_id']
        offer_id = estimation['offer']
        print '>>> user_id=%s' % user_id
        print '>>> offer_id=%s' % offer_id

        voucher = confirm_offer(user_id, offer_id)
        voucher_code = voucher['voucher_code']
        print '>>> voucher_code=%s' % voucher_code
    elif args.command == 'requestconfirm':
        if not args.order or not args.voucher or not args.status:
            print ('usage: python %s %s --order d648f842b2bd4b9b953a70bf339701f2 '
                   '--voucher 123456 --status transporting' % (__file__,
                                                              args.command))
            return
        yield requestconfirm(args.order, args.voucher, args.status)


if __name__ == '__main__':
    main()
