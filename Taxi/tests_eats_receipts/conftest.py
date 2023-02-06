# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import json

import pytest

from eats_receipts_plugins import *  # noqa: F403 F401

pytest_plugins = ['eats_receipts_plugins.pytest_plugins']


@pytest.fixture(name='get_cursor')
def _get_cursor(pgsql):
    def create_cursor():
        return pgsql['eats_receipts'].dict_cursor()

    return create_cursor


@pytest.fixture
def create_send_receipt_request(get_cursor):
    def _create_send_receipt_request(**kwargs):
        params = {
            'document_id': '1',
            'is_refund': False,
            'order_id': '210623-123456',
            'country_code': 'RU',
            'payment_method': 'card',
            'personal_email_id': '1',
            'originator': 'originator',
            'status': 'created',
            'order_nr': '210623-123456',
            'personal_phone_id': '2',
            'products': [
                {
                    'id': 'big_mac',
                    'parent': None,
                    'price': '5.00',
                    'supplier_inn': '123456789012',
                    'tax': '20',
                    'title': 'Big Mac Burger',
                },
            ],
        }
        params.update(**kwargs)

        request = {
            'is_refund': params['is_refund'],
            'order': {
                k: params[k]
                for k in ('order_nr', 'country_code', 'payment_method')
            },
            'user_info': {
                k: params[k]
                for k in ('personal_email_id', 'personal_phone_id')
            },
            'products': params['products'],
        }

        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_receipts.send_receipt_requests('
            'document_id, '
            'is_refund, '
            'order_id, '
            'order_info.country_code, '
            'order_info.payment_method, '
            'user_info.personal_email_id, '
            'originator, '
            'request, '
            'status) '
            'VALUES({!r},{!r},{!r},{!r},{!r},{!r},{!r},{!r}::jsonb,{!r})'
            'RETURNING id'.format(
                params['document_id'],
                params['is_refund'],
                params['order_id'],
                params['country_code'],
                params['payment_method'],
                params['personal_email_id'],
                params['originator'],
                json.dumps(request),
                params['status'],
            ),
        )
        return cursor.fetchone()[0]

    return _create_send_receipt_request
