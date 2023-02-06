# pylint: disable=redefined-outer-name
import datetime

import pytest

pytest_plugins = ['eats_picker_timers_plugins.pytest_plugins']


@pytest.fixture()
def get_cursor(pgsql):
    def create_cursor():
        return pgsql['eats_picker_timers'].dict_cursor()

    return create_cursor


@pytest.fixture(name='now_utc')
def _now_utc(mocked_time):
    return mocked_time.now().replace(tzinfo=datetime.timezone.utc)


@pytest.fixture()
def get_timer(get_cursor):
    def do_get_timer(timer_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_picker_timers.timers WHERE id = %s',
            [timer_id],
        )
        return cursor.fetchone()

    return do_get_timer


@pytest.fixture()
def create_timer(get_cursor):
    def do_create_timer(
            eats_id='123',
            picker_id='111',
            timer_type='type1',
            duration=600,
            started_at='2021-01-19T14:00:27.010000+03:00',
            finished_at='2021-01-19T15:10:27.010000+03:00',
            spent_time=None,
            is_unreliable=None,
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_picker_timers.timers'
            '(eats_id, picker_id, timer_type, duration, '
            'started_at, finished_at, spent_time, is_unreliable) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
            'RETURNING id',
            (
                eats_id,
                picker_id,
                timer_type,
                duration,
                started_at,
                finished_at,
                spent_time,
                is_unreliable,
            ),
        )
        return cursor.fetchone()[0]

    return do_create_timer


@pytest.fixture()
def order_get_json():
    def do_order_get_json(eats_id, status, picker_id):
        return {
            'payload': {
                'id': eats_id,
                'status': status,
                'status_updated_at': '2021-02-16T18:00:00Z',
                'ordered_total': '1',
                'eats_id': eats_id,
                'currency': {'code': 'RUB', 'sign': 'Р'},
                'categories': [{'id': 'category_id', 'name': 'category_name'}],
                'picker_items': [
                    {
                        'id': '1',
                        'name': 'name1',
                        'barcodes': ['barcode'],
                        'weight_barcode_type': 'ean13-tail-gram-4',
                        'is_catch_weight': False,
                        'vendor_code': 'vendor_code',
                        'measure': {'value': 10, 'unit': 'GRM'},
                        'measure_v2': {
                            'value': 10,
                            'quantum': 10,
                            'quantum_price': '100.0',
                            'quantum_quantity': 1,
                            'absolute_quantity': 1,
                            'unit': 'GRM',
                        },
                        'count': 1,
                        'price': '100',
                        'goods_check_text': None,
                        'max_overweight': 200,
                        'category_id': 'category_id',
                        'images': [],
                        'location': 'location',
                    },
                    {
                        'id': '2',
                        'name': 'name2',
                        'barcodes': ['barcode'],
                        'weight_barcode_type': 'ean13-tail-gram-4',
                        'is_catch_weight': False,
                        'vendor_code': 'vendor_code',
                        'measure': {'value': 0, 'unit': ''},
                        'measure_v2': {
                            'value': 0,
                            'quantum': 1,
                            'quantum_price': '100.0',
                            'quantum_quantity': 1,
                            'absolute_quantity': 1,
                            'unit': 'GRM',
                        },
                        'count': 1,
                        'price': '100',
                        'goods_check_text': None,
                        'max_overweight': 200,
                        'category_id': 'category_id',
                        'images': [],
                        'location': 'location',
                    },
                ],
                'require_approval': True,
                'flow_type': 'picking_only',
                'place_id': 1,
                'picker_id': picker_id,
                'estimated_picking_time': 200,
                'created_at': '2020-10-15T14:59:59Z',
                'updated_at': '2020-10-15T15:00:00Z',
            },
            'meta': {},
        }

    return do_order_get_json
