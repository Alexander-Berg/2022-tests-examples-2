# pylint: disable=relative-beyond-top-level,invalid-name,too-many-instance-attributes,unused-argument
# pylint: disable=anomalous-backslash-in-string,too-many-lines, too-many-branches,too-many-locals
import datetime
import logging
import os
import json
import time
from unittest.mock import patch
from freezegun import freeze_time
from odoo.tests.common import SavepointCase, TransactionCase
from odoo.tests.common import tagged
from common.client.wms import WMSConnector
from random import randrange

_logger = logging.getLogger(__name__)

FIXTURE_PATH = 'refund_test'


def datetime_to_iso(dtt):
    str_date = dtt.strftime("%Y-%m-%dT%H:%M:%S")
    str_date = f'{str_date}+00:00'
    return str_date


class Fixtures:
    """
    all non object data for mock and test stored here
    """
    order_id_0 = 'order_id_0'
    del_ns_order_id_0 = 'del_not_shipped_order_id_0'
    del_s_order_id_0 = 'del_shipped_order_id_0'
    sample_product_0_wms_id_0 = 'sample_product_0_wms_id_0'
    package_product_wms_id_0 = 'data_package_product_wms_id_0'
    parent_order_id = 'parent_order_id_0'
    stowage_id_0 = 'stowage_id_0'
    child_order_id_0 = 'child_order_id_0'
    product_wms_id_0 = 'product_wms_id_0'
    product_wms_id_1 = 'product_wms_id_1'
    product_wms_id_2 = 'product_wms_id_2'

    warehouse_wms_id_0 = 'warehouse_wms_id_0'
    warehouse_wms_id_1 = 'warehouse_wms_id_1'
    product_qty_before_after = {
        'product_wms_id_0': [10, 8],
        'product_wms_id_1': [16, 14]
    }
    check_qty = {
        'product_wms_id_0': 1,
        'product_wms_id_1': -1,
    }

    data_sample_product_0 = {
        'wms_id': sample_product_0_wms_id_0,
        'image_url': 'http:\\127.0.0.0\S_image.jpg',
        'name': 'sample_0',
        'default_code': 'sample_code_0',
        'categ_id': 1,
        'type': 'product',
        'description': 'sample_description_0',
        'description_sale': 'sample_long_title_0'}

    data_package_product_0 = {
        'wms_id': package_product_wms_id_0,
        'image_url': 'http:\\127.0.0.0\P_image.jpg',
        'name': 'package_0',
        'default_code': 'package_code_0',
        'categ_id': 1,
        'type': 'product',
        'taxes_id': 1,
        'description': 'package_description_0',
        'description_sale': 'package_long_title_0'}

    data_product_0 = {
        'wms_id': product_wms_id_0,
        'image_url': 'http:\\127.0.0.0\image.jpg',
        'name': 'product_0',
        'default_code': 'code_0',
        'categ_id': 1,
        'type': 'product',
        'taxes_id': 1,
        'description': 'description_0',
        'description_sale': 'long_title_0'}

    data_product_1 = {
        'wms_id': product_wms_id_1,
        'image_url': 'http:\\127.0.0.0\image1.jpg',
        'default_code': 'code_1',
        'name': 'product_1',
        'categ_id': 1,
        'type': 'product',
        'taxes_id': 1,
        'description': 'description_1',
        'description_sale': 'long_title_1'}

    data_product_2 = {
        'wms_id': product_wms_id_2,
        'image_url': 'http:\\127.0.0.0\image2.jpg',
        'default_code': 'code_2',
        'name': 'product_2',
        'categ_id': 1,
        'taxes_id': 1,
        'type': 'product',
        'description': 'description_2',
        'description_sale': 'long_title_2'}

    data_product_3 = {
        'wms_id': 'product_wms_id_312',
        'image_url': 'http:\\127.0.0.0\image3.jpg',
        'default_code': 'code_3',
        'name': 'product_3',
        'categ_id': 1,
        'taxes_id': 1,
        'type': 'product',
        'description': 'description_3',
        'description_sale': 'long_title_3'}

    sample_0_init_qty = 12
    package_0_init_qty = 15
    product_0_init_qty = 5
    product_1_init_qty = 7
    product_2_init_qty = 12

    product_0_count_qty = 6
    product_1_count_qty = 3
    product_2_count_qty = 12

    product_0_wms_qty = 5
    product_1_wms_qty = 8
    product_2_wms_qty = 11

    type_inventory_order_data = [
        {
            "acks": [],
            "approved": None,
            "attr": {
                "doc_date": "2021-02-08",
                "doc_number": "210208-84686c"
            },
            "client_address": None,
            "company_id": "b3d892aa29e14e199ac08974b49d9bdb000200010000",
            "courier": None,
            "courier_id": None,
            "courier_pri": None,
            "created": "2021-02-08T14:41:52+00:00",
            "delivery_promise": "2021-02-08T14:41:52+00:00",
            "dispatch_type": None,
            "eda_status": None,
            "en_route_timer": None,
            "estatus": "done",
            "estatus_vars": {},
            "external_id": "84686c8c-ca3c-4f0a-aec2-c0d8d03b2035",
            "lsn": 52759,
            "order_id": order_id_0,
            "parent": [],
            "problems": [],
            "products": [],
            "required": [],
            "revision": 13,
            "serial": 3187,
            "shelves": [],
            "signals": [
                {
                    "data": {
                        "user": "f9933a42586c40a3a884b54094dd7cae000300010000"
                    },
                    "done": None,
                    "sent": "2021-02-08T18:00:22+03:00",
                    "sigid": "c1b39f763ea2401da173d510cc69e5e1",
                    "type": "inventory_done"
                }
            ],
            "source": "dispatcher",
            "status": "complete",
            "store_id": warehouse_wms_id_0,
            "study": False,
            "target": "complete",
            "timeout_approving": None,
            "total_price": None,
            "type": "inventory",
            "updated": "2021-02-08T15:00:24+00:00",
            "user_done": "f9933a42586c40a3a884b54094dd7cae000300010000",
            "user_id": "f9933a42586c40a3a884b54094dd7cae000300010000",
            "users": [],
            "vars": {
                "child_orders": [
                    "e7f6376507b4438ebfc0ef14a105cf60000300020001",
                    "9cd457454f754c43854fe532e2502571000300020001",
                    "9159950c610b450680d2b07d7c6c268d000200020001",
                    "f45e93a9bab94a9bb78bf2bc01d5e53d000300020002",
                    "addb9c9c60bc48ecabfa0e8f8377f02e000400020002",
                    "922f882ac4a44c0ea3593dcca08cec3f000100020000",
                    "1199cdb6a3864ffe88d698a835e5aebb000400020002",
                    "e05ab87f4b9b4e71a3b4a8a2e0a53cf8000400020002",
                    "c5fd519d30ac4d65bf2d1a7b957980c7000200020000",
                    "2fb2e1e35f0a4f7c8539c34beb969ab4000300020001",
                    "f3b3ee425e734b969548637123e8c437000200020001",
                    "3c1bdf50651f45768b627d038a83a6ef000100020000"
                ]
            },
            "version": 3,
            "wait_client_timer": None,
            "doc_date": "2021-02-08",
            "doc_number": "210208-84686c",
            "contractor": None
        }
    ]
    inventory_log_data = [
        {
            "count": product_0_wms_qty,
            "created": "2021-02-08T14:41:55+00:00",
            "lsn": 2044,
            "order_id": "45f289ff45474091bc02f4cec3189629000200020001",
            "product_id": product_wms_id_0,
            "quants": 1,
            "record_id": "4e28a4bbe7e4430ca16b98f0689eb1c9000400020001",
            "result_count": product_0_count_qty,
            "revision": 2,
            "serial": 1528,
            "shelf_type": "store",
            "updated": "2021-02-08T14:41:55+00:00"
        },
        {
            "count": product_1_wms_qty,
            "created": "2021-02-08T14:41:55+00:00",
            "lsn": 2112,
            "order_id": "45f289ff45474091bc02f4cec3189629000200020001",
            "product_id": product_wms_id_1,
            "quants": 1,
            "record_id": "5e9262575ab74df4b6ca60dde826d65d000200020001",
            "result_count": product_1_count_qty,
            "revision": 2,
            "serial": 1527,
            "shelf_type": "store",
            "updated": "2021-02-08T14:41:55+00:00"
        },
        {
            "count": product_2_wms_qty,
            "created": "2021-02-08T14:41:55+00:00",
            "lsn": 2122,
            "order_id": "45f289ff45474091bc02f4cec3189629000200020001",
            "product_id": product_wms_id_2,
            "quants": 1,
            "record_id": "8a8c170f01df444d8134e782169ad58d000200020001",
            "result_count": product_2_count_qty,
            "revision": 2,
            "serial": 1526,
            "shelf_type": "store",
            "updated": "2021-02-08T14:41:55+00:00"
        }]

    type_writeoff_order_data = [
        {
            "acks": [
                "f9933a42586c40a3a884b54094dd7cae000300010000"
            ],
            "approved": None,
            "attr": {
                "doc_date": "2021-01-21",
                "doc_number": "210121-2c717e",
                "complete": {}
            },
            "type": "writeoff",
            "status": "complete",
            "estatus": "done",
            "order_id": order_id_0,
            "store_id": warehouse_wms_id_0,
            "client_address": None,
            "company_id": "b3d892aa29e14e199ac08974b49d9bdb000200010000",
            "courier": None,
            "courier_id": None,
            "courier_pri": None,
            "created": "2021-01-21T14:37:23+00:00",
            "delivery_promise": "2021-01-21T14:37:23+00:00",
            "dispatch_type": None,
            "eda_status": None,
            "en_route_timer": None,
            "estatus_vars": {},
            "external_id": "2c717e90-5bf6-11eb-a704-8fa4c4194f48",
            "lsn": 219986,

            "parent": [],
            "problems": [],
            "products": [],
            "required": [],
            "revision": 15,
            "serial": 3108,
            "shelves": [],
            "signals": [],
            "source": "dispatcher",

            "study": False,
            "target": "complete",
            "timeout_approving": None,
            "total_price": None,

            "updated": "2021-01-25T08:53:54+00:00",
            "user_done": "f9933a42586c40a3a884b54094dd7cae000300010000",
            "user_id": "f9933a42586c40a3a884b54094dd7cae000300010000",
            "users": [
                "f9933a42586c40a3a884b54094dd7cae000300010000"
            ],
            "vars": {},
            "version": 5,
            "wait_client_timer": None,
            "doc_date": "2021-01-21",
            "doc_number": "210121-2c717e",
            "contractor": None
        }
    ]
    write_off_log_data = [
        {
            "company_id": "b3d892aa29e14e199ac08974b49d9bdb000200010000",
            "count": 2,
            "created": "2021-01-25T08:53:38+00:00",
            "delta_count": 0,
            "delta_reserve": 2,
            "log_id": "1e795d82dcd347d19cf0b65b79562cac000100020000",
            "lot": "",
            "lsn": 44119,
            "order_id": order_id_0,
            "order_type": "writeoff",
            "product_id": product_wms_id_0,
            "quants": 1,
            "reason": None,
            "recount": None,
            "reserve": 10,
            "reserves": {
                "9dd6598e67314f42b951857ac99e3246000300020000": 2
            },
            "serial": 44106,
            "shelf_id": "b58b5e6af43f48a7ab411f87ea603d43000200010000",
            "shelf_type": "trash",
            "stock_id": "8d9ee67f1c824aa2bee8d86cdb1ccee3000200020000",
            "store_id": "42a184f0cbc94732b8aff4664b6121f9000200010001",
            "type": "reserve",
            "user_id": None,
            "valid": None,
            "vars": {}
        },
        {
            "company_id": "b3d892aa29e14e199ac08974b49d9bdb000200010000",
            "count": 0,
            "created": "2021-01-25T08:53:54+00:00",
            "delta_count": -10,
            "delta_reserve": -10,
            "log_id": "350e4e2e109a4eb5895d90a278249a2b000300020000",
            "lot": "",
            "lsn": 44120,
            "order_id": order_id_0,
            "order_type": "writeoff",
            "product_id": product_wms_id_0,
            "quants": 1,
            "reason": None,
            "recount": None,
            "reserve": 0,
            "reserves": {},
            "serial": 44107,
            "shelf_id": "b58b5e6af43f48a7ab411f87ea603d43000200010000",
            "shelf_type": "trash",
            "stock_id": "8d9ee67f1c824aa2bee8d86cdb1ccee3000200020000",
            "store_id": "42a184f0cbc94732b8aff4664b6121f9000200010001",
            "type": "write_off",
            "user_id": None,
            "valid": None,
            "vars": {
                # в reasons лежит лог, где указаны какие доки положили и остаток
                'reasons':
                    [{'95ae00a4e9394872b49f0373fda8271e000300010000': {'count': 7, 'reason_code': 'TRASH_TTL'}},
                     {'05f4779ace4d444c9608f80b2e3b19c9000200010000': {'count': 5, 'reason_code': 'DAMAGE'}}],
                #  тут указано, какую причину списали и какое кол-во
                # сейчас могут прилетать колва как больше так и меньше чем delta_count
                'write_off':
                    [
                        {'some_random_id': [
                            {'count': 7,
                             'order_id': '95ae00a4e9394872b49f0373fda8271e000300010000',
                             'reason_code': 'TRASH_TTL'},
                            {'count': 5,
                             'order_id': '95ae00a4e9394872b49f0373fda8271e000300010012',
                             'reason_code': 'DAMAGE'},
                        ]
                        },
                        {
                            order_id_0: []
                        }
                    ]
            },

        },
    ]

    write_off_log_data_empty_vars = [
        {
            "company_id": "b3d892aa29e14e199ac08974b49d9bdb000200010000",
            "count": 2,
            "created": "2021-01-25T08:53:38+00:00",
            "delta_count": 0,
            "delta_reserve": 2,
            "log_id": "1e795d82dcd347d19cf0b65b79562cac000100020000",
            "lot": "",
            "lsn": 44119,
            "order_id": "order_id_00",
            "order_type": "writeoff",
            "product_id": product_wms_id_0,
            "quants": 1,
            "reason": None,
            "recount": None,
            "reserve": 10,
            "reserves": {
                "9dd6598e67314f42b951857ac99e3246000300020000": 2
            },
            "serial": 44106,
            "shelf_id": "b58b5e6af43f48a7ab411f87ea603d43000200010000",
            "shelf_type": "trash",
            "stock_id": "8d9ee67f1c824aa2bee8d86cdb1ccee3000200020000",
            "store_id": "42a184f0cbc94732b8aff4664b6121f9000200010001",
            "type": "reserve",
            "user_id": None,
            "valid": None,
            "vars": {}
        },
        {
            "company_id": "b3d892aa29e14e199ac08974b49d9bdb000200010000",
            "count": 0,
            "created": "2021-01-25T08:53:54+00:00",
            "delta_count": -10,
            "delta_reserve": -10,
            "log_id": "350e4e2e109a4eb5895d90a278249a2b000300020000",
            "lot": "",
            "lsn": 44120,
            "order_id": "order_id_00",
            "order_type": "writeoff",
            "product_id": product_wms_id_0,
            "quants": 1,
            "reason": None,
            "recount": None,
            "reserve": 0,
            "reserves": {},
            "serial": 44107,
            "shelf_id": "b58b5e6af43f48a7ab411f87ea603d43000200010000",
            "shelf_type": "trash",
            "stock_id": "8d9ee67f1c824aa2bee8d86cdb1ccee3000200020000",
            "store_id": "42a184f0cbc94732b8aff4664b6121f9000200010001",
            "type": "write_off",
            "user_id": None,
            "valid": None,
            "vars": {},
        },
    ]

    write_off_log_data_empty_write_off_in_vars = [
        {
            "company_id": "b3d892aa29e14e199ac08974b49d9bdb000200010000",
            "count": 2,
            "created": "2021-01-25T08:53:38+00:00",
            "delta_count": 0,
            "delta_reserve": 2,
            "log_id": "1e795d82dcd347d19cf0b65b79562cac000100020000",
            "lot": "",
            "lsn": 44119,
            "order_id": "order_id_000",
            "order_type": "writeoff",
            "product_id": product_wms_id_0,
            "quants": 1,
            "reason": None,
            "recount": None,
            "reserve": 10,
            "reserves": {
                "9dd6598e67314f42b951857ac99e3246000300020000": 2
            },
            "serial": 44106,
            "shelf_id": "b58b5e6af43f48a7ab411f87ea603d43000200010000",
            "shelf_type": "trash",
            "stock_id": "8d9ee67f1c824aa2bee8d86cdb1ccee3000200020000",
            "store_id": "42a184f0cbc94732b8aff4664b6121f9000200010001",
            "type": "reserve",
            "user_id": None,
            "valid": None,
            "vars": {}
        },
        {
            "company_id": "b3d892aa29e14e199ac08974b49d9bdb000200010000",
            "count": 0,
            "created": "2021-01-25T08:53:54+00:00",
            "delta_count": -10,
            "delta_reserve": -10,
            "log_id": "350e4e2e109a4eb5895d90a278249a2b000300020000",
            "lot": "",
            "lsn": 44120,
            "order_id": "order_id_000",
            "order_type": "writeoff",
            "product_id": product_wms_id_0,
            "quants": 1,
            "reason": None,
            "recount": None,
            "reserve": 0,
            "reserves": {},
            "serial": 44107,
            "shelf_id": "b58b5e6af43f48a7ab411f87ea603d43000200010000",
            "shelf_type": "trash",
            "stock_id": "8d9ee67f1c824aa2bee8d86cdb1ccee3000200020000",
            "store_id": "42a184f0cbc94732b8aff4664b6121f9000200010001",
            "type": "write_off",
            "user_id": None,
            "valid": None,
            "vars": {
                'reasons': [],
                'write_off': []
            },
        },
    ]

    write_off_log_data_less_than_needed_reason = [
        {
            "company_id": "b3d892aa29e14e199ac08974b49d9bdb000200010000",
            "count": 2,
            "created": "2021-01-25T08:53:38+00:00",
            "delta_count": 0,
            "delta_reserve": 2,
            "log_id": "1e795d82dcd347d19cf0b65b79562cac000100020000",
            "lot": "",
            "lsn": 44119,
            "order_id": "order_id_0000",
            "order_type": "writeoff",
            "product_id": product_wms_id_0,
            "quants": 1,
            "reason": None,
            "recount": None,
            "reserve": 10,
            "reserves": {
                "9dd6598e67314f42b951857ac99e3246000300020000": 2
            },
            "serial": 44106,
            "shelf_id": "b58b5e6af43f48a7ab411f87ea603d43000200010000",
            "shelf_type": "trash",
            "stock_id": "8d9ee67f1c824aa2bee8d86cdb1ccee3000200020000",
            "store_id": "42a184f0cbc94732b8aff4664b6121f9000200010001",
            "type": "reserve",
            "user_id": None,
            "valid": None,
            "vars": {}
        },
        {
            "company_id": "b3d892aa29e14e199ac08974b49d9bdb000200010000",
            "count": 0,
            "created": "2021-01-25T08:53:54+00:00",
            "delta_count": -10,
            "delta_reserve": -10,
            "log_id": "350e4e2e109a4eb5895d90a278249a2b000300020000",
            "lot": "",
            "lsn": 44120,
            "order_id": "order_id_0000",
            "order_type": "writeoff",
            "product_id": product_wms_id_0,
            "quants": 1,
            "reason": None,
            "recount": None,
            "reserve": 0,
            "reserves": {},
            "serial": 44107,
            "shelf_id": "b58b5e6af43f48a7ab411f87ea603d43000200010000",
            "shelf_type": "trash",
            "stock_id": "8d9ee67f1c824aa2bee8d86cdb1ccee3000200020000",
            "store_id": "42a184f0cbc94732b8aff4664b6121f9000200010001",
            "type": "write_off",
            "user_id": None,
            "valid": None,
            "vars": {
                # в reasons лежит лог, где указаны какие доки положили и остаток
                'reasons':
                    [{'95ae00a4e9394872b49f0373fda8271e000300010000': {'count': 7, 'reason_code': 'TRASH_TTL'}},
                     {'05f4779ace4d444c9608f80b2e3b19c9000200010000': {'count': 5, 'reason_code': 'DAMAGE'}}],
                #  тут указано, какую причину списали и какое кол-во
                # сейчас могут прилетать колва как больше так и меньше чем delta_count
                'write_off':
                    [
                        {'some_random_id': [
                            {'count': 2,
                             'order_id': '95ae00a4e9394872b49f0373fda8271e000300010000',
                             'reason_code': 'TRASH_TTL'},
                            {'count': 3,
                             'order_id': '95ae00a4e9394872b49f0373fda8271e000300010012',
                             'reason_code': 'DAMAGE'},
                        ]
                        },
                        {
                            order_id_0: []
                        }
                    ]
            },

        },
    ]

    write_off_log_data_overloaded = [
        {
            "company_id": "b3d892aa29e14e199ac08974b49d9bdb000200010000",
            "count": 2,
            "created": "2021-01-25T08:53:38+00:00",
            "delta_count": 0,
            "delta_reserve": 2,
            "log_id": "1e795d82dcd347d19cf0b65b79562cac000100020000",
            "lot": "",
            "lsn": 44119,
            "order_id": "order_id_00000",
            "order_type": "writeoff",
            "product_id": product_wms_id_0,
            "quants": 1,
            "reason": None,
            "recount": None,
            "reserve": 10,
            "reserves": {
                "9dd6598e67314f42b951857ac99e3246000300020000": 2
            },
            "serial": 44106,
            "shelf_id": "b58b5e6af43f48a7ab411f87ea603d43000200010000",
            "shelf_type": "trash",
            "stock_id": "8d9ee67f1c824aa2bee8d86cdb1ccee3000200020000",
            "store_id": "42a184f0cbc94732b8aff4664b6121f9000200010001",
            "type": "reserve",
            "user_id": None,
            "valid": None,
            "vars": {}
        },
        {
            "company_id": "b3d892aa29e14e199ac08974b49d9bdb000200010000",
            "count": 0,
            "created": "2021-01-25T08:53:54+00:00",
            "delta_count": -10,
            "delta_reserve": -10,
            "log_id": "350e4e2e109a4eb5895d90a278249a2b000300020000",
            "lot": "",
            "lsn": 44120,
            "order_id": "order_id_00000",
            "order_type": "writeoff",
            "product_id": product_wms_id_0,
            "quants": 1,
            "reason": None,
            "recount": None,
            "reserve": 0,
            "reserves": {},
            "serial": 44107,
            "shelf_id": "b58b5e6af43f48a7ab411f87ea603d43000200010000",
            "shelf_type": "trash",
            "stock_id": "8d9ee67f1c824aa2bee8d86cdb1ccee3000200020000",
            "store_id": "42a184f0cbc94732b8aff4664b6121f9000200010001",
            "type": "write_off",
            "user_id": None,
            "valid": None,
            "vars": {
                # в reasons лежит лог, где указаны какие доки положили и остаток
                'reasons':
                    [{'95ae00a4e9394872b49f0373fda8271e000300010000': {'count': 7, 'reason_code': 'TRASH_TTL'}},
                     {'05f4779ace4d444c9608f80b2e3b19c9000200010000': {'count': 2, 'reason_code': 'DAMAGE'}}],
                #  тут указано, какую причину списали и какое кол-во
                # сейчас могут прилетать колва как больше так и меньше чем delta_count
                'write_off':
                    [
                        {
                            'some_random_id': [
                                {'count': 2,
                                 'order_id': '95ae00a4e9394872b49f0373fda8271e000300010000',
                                 'reason_code': 'TRASH_TTL'},
                                {'count': 1,
                                 'order_id': '95ae00a4e9394872b49f0373fda8271e000300010012',
                                 'reason_code': 'DAMAGE'},
                            ]
                        },
                        {
                            order_id_0: [
                                {'count': 4,
                                 'order_id': '95ae00a4e9394872b49f0373fda8271e000300010001',
                                 'reason_code': 'TRASH_TTL'},
                                {'count': 2,
                                 'order_id': '95ae00a4e9394872b49f0373fda8271e000300010022',
                                 'reason_code': 'DECAYED'},
                            ]
                        }
                    ]
            },

        },
    ]

    check_product_on_shelf_data = [
        {
            "wait_client_timer": False,
            "version": 4,
            "vars": {},
            "users": [
                "f9933a42586c40a3a884b54094dd7cae000300010000"
            ],
            "user_id": "f9933a42586c40a3a884b54094dd7cae000300010000",
            "user_done": "f9933a42586c40a3a884b54094dd7cae000300010000",
            "updated": "2021-02-03T12:59:27+00:00",
            "type": "check_product_on_shelf",
            "total_price": False,
            "timeout_approving": False,
            "target": "complete",
            "study": False,
            "store_id": warehouse_wms_id_0,
            "status": "complete",
            "source": "dispatcher",
            "signals": [],
            "shelves": [
                "69a3d5637d74476c93b9fcf32b1c7ac6000100010001"
            ],
            "serial": 3325,
            "revision": 20,
            "required": [
                {
                    "update_valids": False,
                    "shelf_id": "69a3d5637d74476c93b9fcf32b1c7ac6000100010001",
                    "product_id": product_wms_id_0,
                    "price_type": "store",
                    "sum": False
                }
            ],
            "products": [
                "a05fb378fe9f4a9487bc0f38650bd96f000200010000"
            ],
            "problems": [],
            "parent": [],
            "order_id": 'test_id',
            "lsn": 229795,
            "external_id": "9d2f3c70-661f-11eb-b8a3-ebf35e25da67",
            "estatus_vars": {},
            "estatus": "done",
            "en_route_timer": False,
            "eda_status": False,
            "dispatch_type": False,
            "delivery_promise": "2021-02-03T12:59:11+00:00",
            "created": "2021-02-03T12:59:11+00:00",
            "courier_pri": False,
            "courier_id": False,
            "courier": False,
            "company_id": "b3d892aa29e14e199ac08974b49d9bdb000200010000",
            "client_address": False,
            "attr": {
                "doc_date": "2021-02-03",
                "doc_number": "210203-9d2f3c",
                "complete": {}
            },
            "approved": False,
            "acks": [
                "f9933a42586c40a3a884b54094dd7cae000300010000"
            ],
            "doc_date": "2021-02-03",
            "doc_number": "210203-9d2f3c",
            "contractor": False,
        }]
    check_product_on_shelf_log_data = [
        {
            "vars": {
                "order": "09dad5d733234c99afd53ff2960a9e2d000200020000"
            },
            "valid": "2020-10-19",
            "user_id": False,
            "type": "put",
            "store_id": "store_id_0",
            "stock_id": "a2ac57b606eb4721ada70af36914ef4e000500020002",
            "shelf_type": "lost",
            "shelf_id": "f49efe466d904b56861440860a18953c000300020001",
            "serial": 1060,
            "reserves": {
                "09dad5d733234c99afd53ff2960a9e2d000200020000": 1
            },
            "reserve": 1,
            "recount": False,
            "reason": False,
            "quants": 1,
            "product_id": product_wms_id_0,
            "order_type": "check_product_on_shelf",
            "order_id": "09dad5d733234c99afd53ff2960a9e2d000200020000",
            "lsn": 1060,
            "lot": "6f34848066ce441aafb846a46344c28f000200010001",
            "log_id": "41b11ce8349d4fb6872321ee835ac2e7000400020002",
            "delta_reserve": 1,
            "delta_count": 1,
            "created": "2021-02-03T12:59:26+00:00",
            "count": 1,
            "company_id": "b3d892aa29e14e199ac08974b49d9bdb000200010000"
        },
        {
            "vars": {
                "order": "09dad5d733234c99afd53ff2960a9e2d000200020000"
            },
            "valid": "2020-10-19",
            "user_id": False,
            "type": "unreserve",
            "store_id": "store_id_0",
            "stock_id": "a2ac57b606eb4721ada70af36914ef4e000500020002",
            "shelf_type": "lost",
            "shelf_id": "f49efe466d904b56861440860a18953c000300020001",
            "serial": 1061,
            "reserves": {},
            "reserve": 0,
            "recount": False,
            "reason": False,
            "quants": 1,
            "product_id": product_wms_id_0,
            "order_type": "check_product_on_shelf",
            "order_id": 'test_id',
            "lsn": 1061,
            "lot": "6f34848066ce441aafb846a46344c28f000200010001",
            "log_id": "213bb76362474365a03cfd6e3fa747fc000300020002",
            "delta_reserve": -1,
            "delta_count": 0,
            "created": "2021-02-03T12:59:26+00:00",
            "count": 1,
            "company_id": "b3d892aa29e14e199ac08974b49d9bdb000200010000"
        },
        {
            "vars": {},
            "valid": "2020-10-19",
            "user_id": False,
            "type": "reserve",
            "store_id": "store_id_0",
            "stock_id": "a81e40074f9f4ef7a920fc6cf3296d05000200010001",
            "shelf_type": "store",
            "shelf_id": "69a3d5637d74476c93b9fcf32b1c7ac6000100010001",
            "serial": 46854,
            "reserves": {
                "09dad5d733234c99afd53ff2960a9e2d000200020000": 1
            },
            "reserve": 1,
            "recount": False,
            "reason": False,
            "quants": 1,
            "product_id": product_wms_id_0,
            "order_type": "check_product_on_shelf",
            "order_id": "09dad5d733234c99afd53ff2960a9e2d000200020000",
            "lsn": 46893,
            "lot": "6f34848066ce441aafb846a46344c28f000200010001",
            "log_id": "3c44c0accb914d02b9a57a8f8d1fddeb000200020001",
            "delta_reserve": 1,
            "delta_count": 0,
            "created": "2021-02-03T12:59:25+00:00",
            "count": 7,
            "company_id": "b3d892aa29e14e199ac08974b49d9bdb000200010000"
        },
        {
            "vars": {},
            "valid": "2020-10-19",
            "user_id": False,
            "type": "get",
            "store_id": "store_id_0",
            "stock_id": "a81e40074f9f4ef7a920fc6cf3296d05000200010001",
            "shelf_type": "store",
            "shelf_id": "69a3d5637d74476c93b9fcf32b1c7ac6000100010001",
            "serial": 46855,
            "reserves": {},
            "reserve": 0,
            "recount": False,
            "reason": False,
            "quants": 1,
            "product_id": product_wms_id_0,
            "order_type": "check_product_on_shelf",
            "order_id": "09dad5d733234c99afd53ff2960a9e2d000200020000",
            "lsn": 46894,
            "lot": "6f34848066ce441aafb846a46344c28f000200010001",
            "log_id": "debd852621be42fb9220b0ae1745b868000200020001",
            "delta_reserve": -1,
            "delta_count": -1,
            "created": "2021-02-03T12:59:25+00:00",
            "count": 6,
            "company_id": "b3d892aa29e14e199ac08974b49d9bdb000200010000"
        }
    ]

    type_order_data = [{
        "wait_client_timer": None,
        "version": 3,
        "vars": {
            "editable": True,
            "problems": []
        },
        "users": [],
        "user_id": None,
        "user_done": None,
        "updated": "2021-03-15T14:53:37+00:00",
        "type": "order",
        "total_price": "30.00",
        "timeout_approving": "2021-03-15T14:30:23+00:00",
        "target": "complete",
        "study": False,
        "store_id": warehouse_wms_id_0,
        "status": "complete",
        "source": "external",
        "signals": [],
        "shelves": [],
        "serial": 1444,
        "revision": 15,
        "required": [
            {
                "vat": "10.00",
                "product_id": product_wms_id_0,
                "price_unit": 1,
                "price_type": "store",
                "price": "30.00",
                "discount": "0.00",
                "count": 2,
                "sum": "60.00"
            },
            {
                "vat": "10.00",
                "product_id": product_wms_id_1,
                "price_unit": 1,
                "price_type": "store",
                "price": "40.00",
                "discount": "0.00",
                "count": 3,
                "sum": "120.00"
            }
        ],
        "products": [],
        "problems": [],
        "parent": [],
        "order_id": order_id_0,
        "lsn": 25777,
        "external_id": "a93d7713b35b4a288a2b63025317dc34-grocery",
        "estatus_vars": {},
        "estatus": "done",
        "en_route_timer": None,
        "eda_status": "PICKUP",
        "dispatch_type": "external",
        "delivery_promise": "2021-03-15T14:15:23+00:00",
        "created": "2021-03-15T14:00:23+00:00",
        "courier_pri": None,
        "courier_id": None,
        "courier": None,
        "company_id": "b3d892aa29e14e199ac08974b49d9bdb000200010000",
        "client_address": {
            "lon": 37.56243376791175,
            "lat": 55.7228924074624,
            "fullname": "Россия, Москва, улица Савельева, 5с6"
        },
        "attr": {
            "doc_date": "2021-03-15",
            "doc_number": "test_doc_number",
            "client_id": "taxi_user_id:407727781e904192a8e5d9e25aeec1bd",
            "client_phone_id": "a4bec08b65124eba80f596ef372bf546"
        },
        "approved": "2021-03-15T14:01:35+00:00",
        "acks": [],
        "doc_date": "2021-03-15",
        "doc_number": "test_doc_number",
        "contractor": None
    }]

    shipment_data = [
        {
            "acks": [
                "35d4fb3a69b34658a622662a87abb2b0000200010000"
            ],
            "approved": "2021-04-21T11:49:56+00:00",
            "attr": {
                "doc_date": "2021-04-21",
                "doc_number": "test_doc_number",
                "complete": {}
            },
            "client_address": None,
            "company_id": "fcc89d85e5e444268628bbdbe6795c21000200010000",
            "courier": None,
            "courier_id": None,
            "courier_pri": None,
            "created": "2021-04-21T11:49:56+00:00",
            "delivery_promise": "2021-04-21T11:49:56+00:00",
            "dispatch_type": None,
            "eda_status": None,
            "en_route_timer": None,
            "estatus": "done",
            "estatus_vars": {},
            "external_id": "251b7043-271e-4cf0-9157-f0fd90edb484",
            "lsn": 492448339,
            "order_id": order_id_0,
            "parent": [],
            "problems": [],
            "products": [],
            "required": [
                {
                    "count": 80,
                    "price_type": "store",
                    "product_id": product_wms_id_0,
                    "result_count": 80,
                    "sum": None
                },
                {
                    "count": 20,
                    "price_type": "store",
                    "product_id": product_wms_id_1,
                    "result_count": 20,
                    "sum": None
                },

            ],
            "revision": 22,
            "serial": 13436533,
            "shelves": [],
            "signals": [],
            "source": "dispatcher",
            "status": "complete",
            "store_id": warehouse_wms_id_0,
            "study": False,
            "target": "complete",
            "timeout_approving": None,
            "total_price": None,
            "type": "shipment",
            "updated": "2021-04-21T12:09:48+00:00",
            "user_done": "35d4fb3a69b34658a622662a87abb2b0000200010000",
            "user_id": "a30d4bedbb46447f8f78790a0e2a2587000100010001",
            "users": [
                "35d4fb3a69b34658a622662a87abb2b0000200010000"
            ],
            "vars": {},
            "version": 6,
            "wait_client_timer": None,
            "doc_date": "2021-04-21",
            "doc_number": "test_doc_number",
            "contractor": None
        },
    ]

    type_canceled_not_shipped_order_data = [{
        "wait_client_timer": None,
        "version": 4,
        "vars": {
            "editable": True,
            "problems": []
        },
        "users": [],
        "user_id": None,
        "user_done": None,
        "updated": "2021-03-15T14:53:37+00:00",
        "type": "order",
        "total_price": "30.00",
        "timeout_approving": "2021-03-15T14:30:23+00:00",
        "target": "complete",
        "study": False,
        "store_id": warehouse_wms_id_0,
        "status": "canceled",
        "source": "external",
        "signals": [],
        "shelves": [],
        "serial": 1444,
        "revision": 15,
        "required": [
            {
                "vat": "10.00",
                "product_id": product_wms_id_0,
                "price_unit": 1,
                "price_type": "store",
                "price": "30.00",
                "discount": "0.00",
                "count": 2,
                "sum": "60.00"
            },
            {
                "vat": "10.00",
                "product_id": product_wms_id_1,
                "price_unit": 1,
                "price_type": "store",
                "price": "40.00",
                "discount": "0.00",
                "count": 3,
                "sum": "120.00"
            }
        ],
        "products": [],
        "problems": [],
        "parent": [],
        "order_id": del_ns_order_id_0,
        "lsn": 25777,
        "external_id": "a93d7713b35b4a288a2b63025317dc34-grocery",
        "estatus_vars": {},
        "estatus": "done",
        "en_route_timer": None,
        "eda_status": "PICKUP",
        "dispatch_type": "external",
        "delivery_promise": "2021-03-15T14:15:23+00:00",
        "created": "2021-03-15T14:00:23+00:00",
        "courier_pri": None,
        "courier_id": None,
        "courier": None,
        "company_id": "b3d892aa29e14e199ac08974b49d9bdb000200010000",
        "client_address": {
            "lon": 37.56243376791175,
            "lat": 55.7228924074624,
            "fullname": "Россия, Москва, улица Савельева, 5с6"
        },
        "attr": {
            "doc_date": "2021-03-15",
            "doc_number": "test_doc_number",
            "client_id": "taxi_user_id:407727781e904192a8e5d9e25aeec1bd",
            "client_phone_id": "a4bec08b65124eba80f596ef372bf546"
        },
        "approved": "2021-03-15T14:01:35+00:00",
        "acks": [],
        "doc_date": "2021-03-15",
        "doc_number": "test_doc_number",
        "contractor": None
    }]

    type_canceled_shipped_order_data = [{
        "wait_client_timer": None,
        "version": 4,
        "vars": {
            "editable": True,
            "problems": []
        },
        "users": [],
        "user_id": None,
        "user_done": None,
        "updated": "2021-03-15T14:53:37+00:00",
        "type": "order",
        "total_price": "30.00",
        "timeout_approving": "2021-03-15T14:30:23+00:00",
        "target": "complete",
        "study": False,
        "store_id": warehouse_wms_id_0,
        "status": "canceled",
        "source": "external",
        "signals": [],
        "shelves": [],
        "serial": 1444,
        "revision": 15,
        "required": [
            {
                "vat": "10.00",
                "product_id": product_wms_id_0,
                "price_unit": 1,
                "price_type": "store",
                "price": "30.00",
                "discount": "0.00",
                "count": 2,
                "sum": "60.00"
            },
            {
                "vat": "10.00",
                "product_id": product_wms_id_1,
                "price_unit": 1,
                "price_type": "store",
                "price": "40.00",
                "discount": "0.00",
                "count": 3,
                "sum": "120.00"
            }
        ],
        "products": [],
        "problems": [],
        "parent": [],
        "order_id": del_s_order_id_0,
        "lsn": 25777,
        "external_id": "a93d7713b35b4a288a2b63025317dc34-grocery",
        "estatus_vars": {},
        "estatus": "done",
        "en_route_timer": None,
        "eda_status": "PICKUP",
        "dispatch_type": "external",
        "delivery_promise": "2021-03-15T14:15:23+00:00",
        "created": "2021-03-15T14:00:23+00:00",
        "courier_pri": None,
        "courier_id": None,
        "courier": None,
        "company_id": "b3d892aa29e14e199ac08974b49d9bdb000200010000",
        "client_address": {
            "lon": 37.56243376791175,
            "lat": 55.7228924074624,
            "fullname": "Россия, Москва, улица Савельева, 5с6"
        },
        "attr": {
            "doc_date": "2021-03-15",
            "doc_number": "test_doc_number",
            "client_id": "taxi_user_id:407727781e904192a8e5d9e25aeec1bd",
            "client_phone_id": "a4bec08b65124eba80f596ef372bf546"
        },
        "approved": "2021-03-15T14:01:35+00:00",
        "acks": [],
        "doc_date": "2021-03-15",
        "doc_number": "test_doc_number",
        "contractor": None
    }]

    order_log_data = [
        {
            "company_id": "2fda2157e6ba4e84b65efdd93626adfe000100010001",
            "count": 1,
            "created": "2021-04-15T13:18:14+00:00",
            "delta_count": -1,
            "delta_reserve": 1,
            "log_id": "0bcaf87b813f45869e35af3f5334f01b000300010000",
            "lot": "86ca83818e8e4fa684acb56e49ce9a4a000300010000-e9b17ae905c940f1a1fe816894db6330000200010001",
            "lsn": 163383908,
            "order_id": order_id_0,
            "order_type": "order",
            "product_id": package_product_wms_id_0,
            "quants": 1,
            "reason": None,
            "recount": None,
            "reserve": 1,
            "reserves": {
                "ab44a39660f5474bac65ac073651f35d000100010001": 1
            },
            "serial": 163383908,
            "shelf_id": "4f73f61ea4b94697acc93347f88b8418000200010000",
            "shelf_type": "store",
            "stock_id": "8bd353dd6b334421b1e99c542832dafe000300010000",
            "store_id": warehouse_wms_id_0,
            "type": "sample",
            "user_id": None,
            "valid": "2034-12-04",
            "vars": {
                "tags": [
                    "packaging"
                ]
            }
        },
        {
            "company_id": "2fda2157e6ba4e84b65efdd93626adfe000100010001",
            "count": 1,
            "created": "2021-04-15T13:18:14+00:00",
            "delta_count": -1,
            "delta_reserve": -1,
            "log_id": "e09bf4c623fd47e697cab181197c36be000300010000",
            "lot": "86ca83818e8e4fa684acb56e49ce9a4a000300010000-e9b17ae905c940f1a1fe816894db6330000200010001",
            "lsn": 163383909,
            "order_id": order_id_0,
            "order_type": "order",
            "product_id": sample_product_0_wms_id_0,
            "quants": 1,
            "reason": None,
            "recount": None,
            "reserve": 0,
            "reserves": {},
            "serial": 163383909,
            "shelf_id": "4f73f61ea4b94697acc93347f88b8418000200010000",
            "shelf_type": "store",
            "stock_id": "8bd353dd6b334421b1e99c542832dafe000300010000",
            "store_id": warehouse_wms_id_0,
            "type": "sample",
            "user_id": None,
            "valid": "2034-12-04",
            "vars": {
                "tags": [
                    "sample"
                ]
            }
        },
        {
            "company_id": "2fda2157e6ba4e84b65efdd93626adfe000100010001",
            "count": 10,
            "created": "2021-04-15T13:18:15+00:00",
            "delta_count": -1,
            "delta_reserve": -1,
            "log_id": "b93db162dab34376ae0abdc565027e1b000200010000",
            "lot": "0f03c7ec146440ef865be5393381164b000100010001-f07e8a50ab5946f49eb80514c7d940fa000200010000",
            "lsn": 163383910,
            "order_id": order_id_0,
            "order_type": "order",
            "product_id": product_wms_id_1,
            "quants": 1,
            "reason": None,
            "recount": None,
            "reserve": 0,
            "reserves": {},
            "serial": 163383910,
            "shelf_id": "477b0cbcdc75450e99a6539061178df8000200010001",
            "shelf_type": "store",
            "stock_id": "8470f0b250b248109bae46bf35deb698000300010000",
            "store_id": warehouse_wms_id_0,
            "type": "sale",
            "user_id": None,
            "valid": "2021-10-13",
            "vars": {}
        }]

    deleted_non_shipped_order_log_data = [
        {
            "company_id": "2fda2157e6ba4e84b65efdd93626adfe000100010001",
            "count": 1,
            "created": "2021-04-15T13:18:14+00:00",
            "delta_count": 0,
            "delta_reserve": 1,
            "log_id": "0bcaf87b813f45869e35af3f5334f01b000300010000",
            "lot": "86ca83818e8e4fa684acb56e49ce9a4a000300010000-e9b17ae905c940f1a1fe816894db6330000200010001",
            "lsn": 163383908,
            "order_id": del_ns_order_id_0,
            "order_type": "order",
            "product_id": package_product_wms_id_0,
            "quants": 1,
            "reason": None,
            "recount": None,
            "reserve": 1,
            "reserves": {
                "ab44a39660f5474bac65ac073651f35d000100010001": 1
            },
            "serial": 163383908,
            "shelf_id": "4f73f61ea4b94697acc93347f88b8418000200010000",
            "shelf_type": "store",
            "stock_id": "8bd353dd6b334421b1e99c542832dafe000300010000",
            "store_id": warehouse_wms_id_0,
            "type": "sample",
            "user_id": None,
            "valid": "2034-12-04",
            "vars": {
                "tags": [
                    "packaging"
                ]
            }
        },
        {
            "company_id": "2fda2157e6ba4e84b65efdd93626adfe000100010001",
            "count": 1,
            "created": "2021-04-15T13:18:14+00:00",
            "delta_count": -1,
            "delta_reserve": -1,
            "log_id": "e09bf4c623fd47e697cab181197c36be000300010000",
            "lot": "86ca83818e8e4fa684acb56e49ce9a4a000300010000-e9b17ae905c940f1a1fe816894db6330000200010001",
            "lsn": 163383909,
            "order_id": del_ns_order_id_0,
            "order_type": "order",
            "product_id": sample_product_0_wms_id_0,
            "quants": 1,
            "reason": None,
            "recount": None,
            "reserve": 0,
            "reserves": {},
            "serial": 163383909,
            "shelf_id": "4f73f61ea4b94697acc93347f88b8418000200010000",
            "shelf_type": "store",
            "stock_id": "8bd353dd6b334421b1e99c542832dafe000300010000",
            "store_id": warehouse_wms_id_0,
            "type": "sample",
            "user_id": None,
            "valid": "2034-12-04",
            "vars": {
                "tags": [
                    "sample"
                ]
            }
        },
        {
            "company_id": "2fda2157e6ba4e84b65efdd93626adfe000100010001",
            "count": 10,
            "created": "2021-04-15T13:18:15+00:00",
            "delta_count": 0,
            "delta_reserve": -1,
            "log_id": "b93db162dab34376ae0abdc565027e1b000200010000",
            "lot": "0f03c7ec146440ef865be5393381164b000100010001-f07e8a50ab5946f49eb80514c7d940fa000200010000",
            "lsn": 163383910,
            "order_id": del_ns_order_id_0,
            "order_type": "order",
            "product_id": product_wms_id_1,
            "quants": 1,
            "reason": None,
            "recount": None,
            "reserve": 0,
            "reserves": {},
            "serial": 163383910,
            "shelf_id": "477b0cbcdc75450e99a6539061178df8000200010001",
            "shelf_type": "store",
            "stock_id": "8470f0b250b248109bae46bf35deb698000300010000",
            "store_id": warehouse_wms_id_0,
            "type": "sale",
            "user_id": None,
            "valid": "2021-10-13",
            "vars": {}
        }]

    deleted_shipped_order_log_data = [
        {
            "company_id": "2fda2157e6ba4e84b65efdd93626adfe000100010001",
            "count": 1,
            "created": "2021-04-15T13:18:14+00:00",
            "delta_count": -1,
            "delta_reserve": 1,
            "log_id": "0bcaf87b813f45869e35af3f5334f01b000300010000",
            "lot": "86ca83818e8e4fa684acb56e49ce9a4a000300010000-e9b17ae905c940f1a1fe816894db6330000200010001",
            "lsn": 163383908,
            "order_id": del_s_order_id_0,
            "order_type": "order",
            "product_id": package_product_wms_id_0,
            "quants": 1,
            "reason": None,
            "recount": None,
            "reserve": 1,
            "reserves": {
                "ab44a39660f5474bac65ac073651f35d000100010001": 1
            },
            "serial": 163383908,
            "shelf_id": "4f73f61ea4b94697acc93347f88b8418000200010000",
            "shelf_type": "store",
            "stock_id": "8bd353dd6b334421b1e99c542832dafe000300010000",
            "store_id": warehouse_wms_id_0,
            "type": "sample",
            "user_id": None,
            "valid": "2034-12-04",
            "vars": {
                "tags": [
                    "packaging"
                ]
            }
        },
        {
            "company_id": "2fda2157e6ba4e84b65efdd93626adfe000100010001",
            "count": 1,
            "created": "2021-04-15T13:18:14+00:00",
            "delta_count": -1,
            "delta_reserve": -1,
            "log_id": "e09bf4c623fd47e697cab181197c36be000300010000",
            "lot": "86ca83818e8e4fa684acb56e49ce9a4a000300010000-e9b17ae905c940f1a1fe816894db6330000200010001",
            "lsn": 163383909,
            "order_id": del_s_order_id_0,
            "order_type": "order",
            "product_id": sample_product_0_wms_id_0,
            "quants": 1,
            "reason": None,
            "recount": None,
            "reserve": 0,
            "reserves": {},
            "serial": 163383909,
            "shelf_id": "4f73f61ea4b94697acc93347f88b8418000200010000",
            "shelf_type": "store",
            "stock_id": "8bd353dd6b334421b1e99c542832dafe000300010000",
            "store_id": warehouse_wms_id_0,
            "type": "sample",
            "user_id": None,
            "valid": "2034-12-04",
            "vars": {
                "tags": [
                    "sample"
                ]
            }
        },
        {
            "company_id": "2fda2157e6ba4e84b65efdd93626adfe000100010001",
            "count": 10,
            "created": "2021-04-15T13:18:15+00:00",
            "delta_count": -1,
            "delta_reserve": -1,
            "log_id": "b93db162dab34376ae0abdc565027e1b000200010000",
            "lot": "0f03c7ec146440ef865be5393381164b000100010001-f07e8a50ab5946f49eb80514c7d940fa000200010000",
            "lsn": 163383910,
            "order_id": del_s_order_id_0,
            "order_type": "order",
            "product_id": product_wms_id_1,
            "quants": 1,
            "reason": None,
            "recount": None,
            "reserve": 0,
            "reserves": {},
            "serial": 163383910,
            "shelf_id": "477b0cbcdc75450e99a6539061178df8000200010001",
            "shelf_type": "store",
            "stock_id": "8470f0b250b248109bae46bf35deb698000300010000",
            "store_id": warehouse_wms_id_0,
            "type": "sale",
            "user_id": None,
            "valid": "2021-10-13",
            "vars": {}
        }]

    resp_sent_acceptance_to_wms_data = {

        "store_id": warehouse_wms_id_0,
        "external_id": "test-9d0e8bd5330447d3a3d22df1fab5da2c000100010001.fidsjm",
        "company_id": 1,
        "order_id": parent_order_id,
        "estatus": "done",
        "status": "complete",

        "wait_client_timer": None,
        "version": 4,
        "vars": {
            "editable": True,
            "stowage_id": [
                stowage_id_0
            ]
        },
        "users": [
            "9d0e8bd5330447d3a3d22df1fab5da2c000100010001"
        ],
        "user_id": "a5ca91399449493b952041e25c3dffa8000100010001",
        "user_done": "9d0e8bd5330447d3a3d22df1fab5da2c000100010001",
        "updated": "2021-03-16T11:44:58+00:00",
        "type": "acceptance",
        "total_price": None,
        "timeout_approving": None,
        "target": "complete",
        "study": False,
        "source": "dispatcher",
        "signals": [],
        "shelves": [],
        "serial": 1453,
        "revision": 17,
        "required": [
            {
                "valid": "2021-03-16",
                "result_valid": "2021-03-16",
                "result_count": product_qty_before_after.get(product_wms_id_0)[1],
                "product_id": product_wms_id_0,
                "price_unit": 1,
                "price_type": "store",
                "price": "50.0",
                "maybe_count": False,
                "count": product_qty_before_after.get(product_wms_id_0)[0],
                "sum": "500.00"
            },
            {
                "valid": "2021-03-16",
                "result_valid": "2021-03-16",
                "result_count": product_qty_before_after.get(product_wms_id_1)[1],
                "product_id": product_wms_id_1,
                "price_unit": 1,
                "price_type": "store",
                "price": "50.0",
                "maybe_count": False,
                "count": product_qty_before_after.get(product_wms_id_1)[0],
                "sum": "756.00"
            }
        ],
        "products": [],
        "problems": [],
        "parent": [],
        "lsn": 25921,
        "estatus_vars": {},
        "en_route_timer": None,
        "eda_status": None,
        "dispatch_type": None,
        "delivery_promise": "2021-03-16T11:43:01+00:00",
        "created": "2021-03-16T11:43:01+00:00",
        "courier_pri": None,
        "courier_id": None,
        "courier": None,
        "client_address": None,
        "attr": {
            "doc_date": "2021-03-16",
            "doc_number": "1111",
            "stat": {},
            "complete": {},
            "contractor": "поставщик"
        },
        "approved": "2021-03-16T11:43:01+00:00",
        "acks": [
            "9d0e8bd5330447d3a3d22df1fab5da2c000100010001"
        ],
        "doc_date": "2021-03-16",
        "doc_number": "1111",
        "contractor": "поставщик",
        # "exetrnal_id": "9d0e8bd5330447d3a3d22df1fab5da2c000100010001.fidsjm"
    }

    type_refund_data = [{
        "parent": [order_id_0],
        "order_id": f'{order_id_0}_refund',
        "store_id": warehouse_wms_id_0,
        "status": "complete",
        "required": [
            {
                "vat": "10.00",
                "result_count": 1,
                "product_id": product_wms_id_0,
                "price_unit": 1,
                "price_type": "store",
                "price": "30.00",
                "discount": "0.00",
                "count": 2,
                "sum": "30.00"
            }
        ],
        "wait_client_timer": None,
        "version": 3,
        "vars": {
            "editable": True,
            "problems": []
        },
        "users": [],
        "user_id": None,
        "user_done": None,
        "updated": "2021-03-15T14:53:37+00:00",
        "type": "refund",
        "total_price": "30.00",
        "timeout_approving": "2021-03-15T14:30:23+00:00",
        "target": "complete",
        "study": False,

        "source": "external",
        "signals": [],
        "shelves": [],
        "serial": 1444,
        "revision": 15,

        "products": [],
        "problems": [],

        "lsn": 25777,
        "external_id": "a93d7713b35b4a288a2b63025317dc34-refund",
        "estatus_vars": {},
        "estatus": "done",
        "en_route_timer": None,
        "eda_status": "PICKUP",
        "dispatch_type": "external",
        "delivery_promise": "2021-03-15T14:15:23+00:00",
        "created": "2021-03-15T14:00:23+00:00",
        "courier_pri": None,
        "courier_id": None,
        "courier": None,
        "company_id": "b3d892aa29e14e199ac08974b49d9bdb000200010000",
        "client_address": {
            "lon": 37.56243376791175,
            "lat": 55.7228924074624,
            "fullname": "Россия, Москва, улица Савельева, 5с6"
        },
        "attr": {
            "doc_date": "2021-03-15",
            "doc_number": "210315-595-7904",
            "client_id": "taxi_user_id:407727781e904192a8e5d9e25aeec1bd",
            "client_phone_id": "a4bec08b65124eba80f596ef372bf546"
        },
        "approved": "2021-03-15T14:01:35+00:00",
        "acks": [],
        "doc_date": "2021-03-15",
        "doc_number": "210315-595-7904",
        "contractor": None
    }]

    initial_stowage_data = [

        {
            "acks": [],
            "approved": None,
            "attr": {
                "doc_date": "2021-06-01",
                "doc_number": "210601-613119"
            },
            "client_address": None,
            "company_id": "company_id",
            "courier": None,
            "courier_id": None,
            "courier_pri": None,
            "created": "2021-06-01T14:11:03+00:00",
            "delivery_promise": "2021-06-01T14:11:03+00:00",
            "dispatch_type": None,
            "eda_status": None,
            "en_route_timer": None,
            "estatus": "done",
            "estatus_vars": {},
            "external_id": "5d8dfa986f6142c68ac5c484bbd9c6dc",
            "lsn": 117945,
            "order_id": "initial_stowage_id",
            "parent": [],
            "problems": [],
            "products": [],
            "required": [
                {
                    "count": 25,
                    "price_type": "store",
                    "product_id": product_wms_id_0,
                    "shelf_id": "8bbf4",
                    "sum": None
                },
                {
                    "count": 5,
                    "price_type": "store",
                    "product_id": product_wms_id_0,
                    "shelf_id": "8bbf",
                    "sum": None
                },
                {
                    "count": 10,
                    "price_type": "store",
                    "product_id": product_wms_id_1,
                    "shelf_id": "8bb",
                    "sum": None
                },
                {
                    "count": 13,
                    "price_type": "store",
                    "product_id": product_wms_id_2,
                    "shelf_id": "8bb",
                    "sum": None
                },
            ],
            "revision": 1,
            "serial": 9541,
            "shelves": [],
            "signals": [],
            "source": "1c",
            "status": "complete",
            "store_id": warehouse_wms_id_0,
            "study": False,
            "target": "complete",
            "timeout_approving": None,
            "total_price": None,
            "type": "stowage",
            "updated": "2021-06-01T14:11:03+00:00",
            "user_done": None,
            "user_id": None,
            "users": [],
            "vars": {},
            "version": 1,
            "wait_client_timer": None,
            "doc_date": "2021-06-01",
            "doc_number": "210601-613119",
            "contractor": None
        }
    ]


@tagged('lavka', 'autoorder', 'orders')
class TestPurchaseOrderYTImport(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.wh_tag1 = cls.env['stock.warehouse.tag'].create(
            {
                'type': 'geo',
                'name': 'Paris 1',
            }
        )

        cls.wh_tag2 = cls.env['stock.warehouse.tag'].create(
            {
                'type': 'geo',
                'name': 'Paris 2',
            }
        )

        cls.wh1 = cls.env['stock.warehouse'].create(
            {
                'name': 'wh-1',
                'code': '1',
                'wms_id': '1',
                'active': True,
                'warehouse_tag_ids': [cls.wh_tag1.id],
            }
        )

        cls.wh2 = cls.env['stock.warehouse'].create(
            {
                'name': 'wh-2',
                'code': '2',
                'wms_id': '2',
                'active': True,
                'warehouse_tag_ids': [cls.wh_tag2.id],
            }
        )

        cls.p1 = cls.env['product.product'].create(
            {
                'name': 'p-1',
                'default_code': '1',
                'wms_id': '1',
            }
        )

        cls.p2 = cls.env['product.product'].create(
            {
                'name': 'p-2',
                'default_code': '2',
                'wms_id': '2',
            }
        )

        cls.p3 = cls.env['product.product'].create(
            {
                'name': 'p-3',
                'default_code': '3',
                'wms_id': '3',
            }
        )

        cls.p4 = cls.env['product.product'].create(
            {
                'name': 'p-4',
                'default_code': '4',
                'wms_id': '4',
            }
        )

        cls.v1 = cls.env['res.partner'].create(
            {
                'name': 'v-1',
                'is_company': True,
                'supplier_rank': 1,
            }
        )

        cls.v2 = cls.env['res.partner'].create(
            {
                'name': 'v-2',
                'is_company': True,
                'supplier_rank': 1,
            }
        )

        cls.v3 = cls.env['res.partner'].create(
            {
                'name': 'v-3',
                'is_company': True,
                'supplier_rank': 1,
            }
        )

        cls.v4 = cls.env['res.partner'].create(
            {
                'name': 'v-4',
                'is_company': True,
                'supplier_rank': 1,
            }
        )

        cls.pr1 = cls.env['purchase.requisition'].create(
            {
                'vendor_id': cls.v1.id,
                'state': 'ongoing',
                'warehouse_tag_ids': [cls.wh_tag1.id],
            }
        )

        cls.pr2 = cls.env['purchase.requisition'].create(
            {
                'vendor_id': cls.v2.id,
                'state': 'ongoing',
                'warehouse_tag_ids': [cls.wh_tag2.id],
            }
        )

        cls.pr3 = cls.env['purchase.requisition'].create(
            {
                'vendor_id': cls.v2.id,
                'state': 'ongoing',
                'warehouse_tag_ids': [cls.wh_tag1.id],
            }
        )

        cls.pr4 = cls.env['purchase.requisition'].create(
            {
                'vendor_id': cls.v3.id,
                'state': 'ongoing',
                'warehouse_tag_ids': [cls.wh_tag1.id],
            }
        )

        products_lines_data = (
            (cls.pr1, cls.p1, 100, 1, 1, 1, True, True, True, True,),
            (cls.pr1, cls.p2, 200, 2, 2, 2, True, True, True, True,),
            (cls.pr2, cls.p3, 300, 3, 3, 3, True, True, True, True,),
            (cls.pr2, cls.p4, 400, 4, 4, 2, True, True, True, True,),
            (cls.pr3, cls.p3, 500, 5, 5, 5, True, True, True, True,),
            (cls.pr3, cls.p4, 600, 6, 6, 3, True, True, True, True,),
            (cls.pr4, cls.p4, 600, 6, 6, 3, True, True, True, True,),
        )

        with freeze_time('2020-12-01 12:00:00'):
            req_lines = [
                cls.env['purchase.requisition.line'].create(
                    {
                        'requisition_id': pr.id,
                        'product_id': p.id,
                        'start_date': datetime.datetime.now(),
                        'tax_id': p.supplier_taxes_id.id,
                        'product_uom_id': p.uom_id.id,
                        'price_unit': price,
                        'product_qty': qty,
                        'product_code': f'code-{p.id}',
                        'product_name': 'vendor product name',
                        'qty_multiple': qty_multiple,
                        'qty_in_box': qty_in_box,
                        'approve_price': approve_price,
                        'approve_tax': approve_tax,
                        'approve': approve,
                        'active': active,
                    }
                )
                for (pr, p, price, qty, qty_multiple, qty_in_box,
                     approve_price, approve_tax, approve, active)
                in products_lines_data
            ]
            for req_line in req_lines:
                req_line._compute_approve()

    def test_create_orders_from_yt_sorting_orders_lines(self):
        rows = (
            {
                'lavka_id': 1,
                'warehouse_id': 1,
                'supplier_id': self.v1.external_id,
                'order_date': '11.05.2021',
                'supply_date': '12.05.2021',
                'autoorder_total': 1,
            },
            {
                'lavka_id': 2,
                'warehouse_id': 1,
                'supplier_id': self.v1.external_id,
                'order_date': '11.05.2021',
                'supply_date': '12.05.2021',
                'autoorder_total': 0,
            },
            {
                'lavka_id': 2,
                'warehouse_id': 1,
                'supplier_id': self.v1.external_id,
                'order_date': '11.05.2021',
                'supply_date': '12.05.2021',
                'autoorder_total': 2,
            },
            {
                'lavka_id': 3,
                'warehouse_id': 2,
                'supplier_id': self.v2.external_id,
                'order_date': '11.05.2021',
                'supply_date': '12.05.2021',
                'autoorder_total': 3,
            },
            {
                'lavka_id': 4,
                'warehouse_id': 2,
                'supplier_id': self.v2.external_id,
                'order_date': '15.05.2021',
                'supply_date': '16.05.2021',
                'autoorder_total': 4,
            },
            {
                'lavka_id': 3,
                'warehouse_id': 1,
                'supplier_id': self.v2.external_id,
                'order_date': '20.05.2021',
                'supply_date': '21.05.2021',
                'autoorder_total': 5,
            },
            {
                'lavka_id': 4,
                'warehouse_id': 1,
                'supplier_id': self.v2.external_id,
                'order_date': '20.05.2021',
                'supply_date': '21.05.2021',
                'autoorder_total': 6,
            },
            {
                'lavka_id': 4,
                'warehouse_id': 1,
                'supplier_id': self.v3.external_id,
                'order_date': '20.05.2021',
                'supply_date': '21.05.2021',
                'autoorder_total': 2,
            },
        )

        self.env['ir.config_parameter'].set_param('round_autooreder_qty', True)

        self.env['purchase.order'].create_orders_from_yt(rows, test_mode=True)

        orders_1 = self.env['purchase.order'].search([
            ('partner_id', '=', self.v1.id),
            ('requisition_id', '=', self.pr1.id),
            ('date_order', '=', '2021-05-11 00:00:00'),
            ('picking_type_id', '=', self.wh1.in_type_id.id),
        ])
        self.assertEqual(len(orders_1), 1)
        self.assertEqual(len(orders_1.order_line), 2)

        self.assertEqual(orders_1.order_line[0].product_init_qty, 1.0)
        self.assertEqual(orders_1.order_line[0].qty_multiple, 1.0)
        self.assertEqual(orders_1.order_line[0].qty_in_box, 1.0)
        self.assertEqual(orders_1.order_line[0].boxes, 1)

        self.assertEqual(orders_1.order_line[1].product_init_qty, 2.0)
        self.assertEqual(orders_1.order_line[1].qty_multiple, 2.0)
        self.assertEqual(orders_1.order_line[1].qty_in_box, 2.0)
        self.assertEqual(orders_1.order_line[1].boxes, 1)

        orders_2 = self.env['purchase.order'].search([
            ('partner_id', '=', self.v2.id),
            ('requisition_id', '=', self.pr2.id),
            ('date_order', '=', '2021-05-11 00:00:00'),
            ('picking_type_id', '=', self.wh2.in_type_id.id),
        ])
        self.assertEqual(len(orders_2), 1)
        self.assertEqual(len(orders_2.order_line), 1)

        self.assertEqual(orders_2.order_line[0].product_init_qty, 3.0)
        self.assertEqual(orders_2.order_line[0].qty_multiple, 3.0)
        self.assertEqual(orders_2.order_line[0].qty_in_box, 3.0)
        self.assertEqual(orders_2.order_line[0].boxes, 1)

        orders_3 = self.env['purchase.order'].search([
            ('partner_id', '=', self.v2.id),
            ('requisition_id', '=', self.pr2.id),
            ('date_order', '=', '2021-05-15 00:00:00'),
            ('picking_type_id', '=', self.wh2.in_type_id.id),
        ])
        self.assertEqual(len(orders_3), 1)
        self.assertEqual(len(orders_3.order_line), 1)

        self.assertEqual(orders_3.order_line[0].product_init_qty, 4.0)
        self.assertEqual(orders_3.order_line[0].qty_multiple, 4.0)
        self.assertEqual(orders_3.order_line[0].qty_in_box, 2.0)
        self.assertEqual(orders_3.order_line[0].boxes, 2)

        orders_4 = self.env['purchase.order'].search([
            ('partner_id', '=', self.v2.id),
            ('requisition_id', '=', self.pr3.id),
            ('date_order', '=', '2021-05-20 00:00:00'),
            ('picking_type_id', '=', self.wh1.in_type_id.id),
        ])
        self.assertEqual(len(orders_4), 1)
        self.assertEqual(len(orders_4.order_line), 2)

        self.assertEqual(orders_4.order_line[0].product_init_qty, 5.0)
        self.assertEqual(orders_4.order_line[0].qty_multiple, 5.0)
        self.assertEqual(orders_4.order_line[0].qty_in_box, 5.0)
        self.assertEqual(orders_4.order_line[0].boxes, 1)

        self.assertEqual(orders_4.order_line[1].product_init_qty, 6.0)
        self.assertEqual(orders_4.order_line[1].qty_multiple, 6.0)
        self.assertEqual(orders_4.order_line[1].qty_in_box, 3.0)
        self.assertEqual(orders_4.order_line[1].boxes, 2)

        orders_5 = self.env['purchase.order'].search([
            ('partner_id', '=', self.v3.id),
            ('requisition_id', '=', self.pr4.id),
            ('date_order', '=', '2021-05-20 00:00:00'),
            ('picking_type_id', '=', self.wh1.in_type_id.id),
        ])

        self.assertEqual(len(orders_5), 0)

    def test_create_orders_from_yt_avoiding_order_duplicates(self):
        rows = (
            {
                'lavka_id': 1,
                'warehouse_id': 1,
                'supplier_id': self.v1.external_id,
                'order_date': '11.05.2021',
                'supply_date': '12.05.2021',
                'autoorder_total': 1,
            },
            {
                'lavka_id': 3,
                'warehouse_id': 2,
                'supplier_id': self.v2.external_id,
                'order_date': '11.05.2021',
                'supply_date': '12.05.2021',
                'autoorder_total': 3,
            },
        )

        self.env['purchase.order'].create_orders_from_yt(rows[:1], test_mode=True)

        orders = self.env['purchase.order'].search([])
        self.assertEqual(len(orders), 1)
        self.assertEqual(len(orders.order_line), 1)

        self.env['purchase.order'].create_orders_from_yt(rows, test_mode=True)

        orders = self.env['purchase.order'].search([])
        self.assertEqual(len(orders), 2)
        self.assertEqual(len(orders.order_line), 2)

    def test_create_orders_from_yt_group_by_supply_date(self):
        rows = (
            {
                'lavka_id': 1,
                'warehouse_id': 1,
                'supplier_id': self.v1.external_id,
                'order_date': '11.05.2021',
                'supply_date': '12.05.2021',
                'autoorder_total': 1,
            },
            {
                'lavka_id': 1,
                'warehouse_id': 1,
                'supplier_id': self.v1.external_id,
                'order_date': '11.05.2021',
                'supply_date': '14.05.2021',
                'autoorder_total': 1,
            },
        )

        self.env['purchase.order'].create_orders_from_yt(rows, test_mode=True)

        orders_1 = self.env['purchase.order'].search([
            ('partner_id', '=', self.v1.id),
            ('requisition_id', '=', self.pr1.id),
            ('date_order', '=', '2021-05-11 00:00:00'),
            ('picking_type_id', '=', self.wh1.in_type_id.id),
        ])
        self.assertEqual(len(orders_1), 2)

@tagged('lavka', 'imp_orders')
class TestImportsFromWMS(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_import_logs(self):
        wh = self.env['stock.warehouse']
        product = self.env['product.product']
        check_data, check_log = self.env['factory_common_wms'].get_get_checks_and_stock_log(
            wh,
            product,
            5,
            dummy=True)
        for log in check_log:
            log['created'] = datetime_to_iso(log['created'])

        check_data['created'] = datetime_to_iso(check_data['created'])
        check_data['updated'] = datetime_to_iso(check_data['updated'])
        check_data['attr'] = json.loads(check_data['attr'])
        if check_data.get('approved'):
            check_data['approved'] = datetime_to_iso(check_data['approved'])

        with patch('common.client.wms.WMSConnector.get_wms_data') as data:
            data.return_value = check_log, None
            self.env['wms_stock_log'].import_from_wms()

        self.env.cr.commit()
        self.env.cr.execute("SELECT * FROM wms_stock_log")
        res = self.env.cr.dictfetchall()
        _logger.debug(f'res: {res}')
        self.assertEqual(len(res), len(check_log))

        with patch('common.client.wms.WMSConnector.get_wms_data') as data:
            data.return_value = [check_data], None
            self.env['wms_integration.order'].import_from_wms()
        self.env.cr.commit()
        self.env.cr.execute("SELECT * FROM wms_integration_order")
        doc = self.env.cr.dictfetchall()
        _logger.debug(f'res: {doc}')
        # повторно
        wms_doc = self.env['wms_integration.order'].browse(doc[0]['id'])
        self.assertTrue(wms_doc)
        wms_doc.processing_status = 'ok'
        self.env.cr.commit()
        with patch('common.client.wms.WMSConnector.get_wms_data') as data:
            data.return_value = [check_data], None
            self.env['wms_integration.order'].import_from_wms()
        self.env.cr.commit()
        doc2 = self.env.cr.dictfetchall()
        self.assertFalse(doc2)
        wms_doc2 = self.env['wms_integration.order'].search([
            ('order_id', '=', check_data['order_id'])
        ])
        self.assertTrue(wms_doc2)
        self.assertTrue(wms_doc2.processing_status == 'ok')
        # повторно но не complete ok
        wms_doc = self.env['wms_integration.order'].browse(doc[0]['id'])
        wms_doc.processing_status = 'ok'
        wms_doc.status = 'processing'
        self.env.cr.commit()
        with patch('common.client.wms.WMSConnector.get_wms_data') as data:
            data.return_value = [check_data], None
            self.env['wms_integration.order'].import_from_wms()
        self.env.cr.commit()
        doc3 = self.env.cr.dictfetchall()
        self.assertFalse(doc3)
        wms_doc3 = self.env['wms_integration.order'].search([
            ('order_id', '=', check_data['order_id'])
        ])
        self.assertTrue(wms_doc2.processing_status == 'new')

        self.env.cr.execute("TRUNCATE TABLE wms_stock_log Cascade ")
        self.env.cr.execute("TRUNCATE TABLE wms_integration_order CASCADE ")
        self.env.cr.commit()

