# pylint: disable=redefined-outer-name, too-many-lines
import datetime
import decimal
import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
import uuid

import psycopg2
import psycopg2.extras
import pytest
import pytz


pytest_plugins = ['eats_picker_orders_plugins.pytest_plugins']


@pytest.fixture()
def mock_processing(mockserver):
    @mockserver.json_handler(
        '/processing/v1/eda/picker_order_history/create-event',
    )
    def _mock_processing(request):
        assert 'event_type' in request.json
        assert 'order_nr' in request.json
        assert 'order_status' in request.json
        assert 'place_id' in request.json
        return mockserver.make_response(
            status=200, json={'event_id': request.json['order_nr']},
        )

    return _mock_processing


@pytest.fixture()
def mock_apply_state(mockserver):
    @mockserver.json_handler(f'/eats-core/v1/picker-orders/apply-state')
    def _mock_apply_state(request):
        assert request.method == 'POST'
        assert 'eats_id' in request.json
        assert 'status' in request.json
        return mockserver.make_response(json={'issuccess': True}, status=200)

    return _mock_apply_state


@pytest.fixture()
def mock_edadeal(mockserver, generate_integration_item_data):
    def do_mock_edadeal(is_catch_weight, measure_quantum=1, measure_value=500):
        @mockserver.json_handler(
            """/eats-nomenclature/v1/place/products/"""
            """search-by-barcode-or-vendor-code""",
        )
        def _mock_edadeal(_):
            matched_items: List[Dict[str, Any]] = [
                {
                    'item': generate_integration_item_data(
                        origin_id=f'item-{i}',
                        is_catch_weight=is_catch_weight,
                        barcodes=[str(i)],
                        vendor_code=str(i),
                        measure_value=measure_value,
                        measure_quantum=measure_quantum,
                    ),
                    'barcode': str(i),
                    'sku': str(i),
                }
                for i in range(1, 7)
            ]
            for item in matched_items:
                item['item']['price'] = str(item['item']['price'])
            return {'matched_items': matched_items, 'not_matched_items': []}

        return _mock_edadeal

    return do_mock_edadeal


@pytest.fixture()
def mock_eatspickeritemcategories(mockserver):
    def do_mock(place_id=1, categories=tuple()):
        @mockserver.json_handler(
            f'/eats-picker-item-categories/api/v1/items/categories',
        )
        def _mock_eatspickeritemcategories(request):
            assert request.method == 'POST'
            assert int(request.json['place_id']) == place_id
            return mockserver.make_response(
                status=200, json={'items_categories': categories},
            )

        return _mock_eatspickeritemcategories

    return do_mock


@pytest.fixture()
def mock_eats_products_public_id(mockserver):
    def do_mock(product_ids=None, status=200):
        @mockserver.json_handler(
            '/eats-products/internal/v2/products/public_id_by_origin_id',
        )
        def _mock_eats_products(_):
            return mockserver.make_response(
                status=status,
                json={'products_ids': product_ids if product_ids else []},
            )

        return _mock_eats_products

    return do_mock


@pytest.fixture()
def mock_nmn_products_info(mockserver):
    def do_mock(products_info=None, status=200):
        @mockserver.json_handler('/eats-nomenclature/v1/products/info')
        def _mock_eats_nomenclature(_):
            return mockserver.make_response(
                status=status,
                json={'products': products_info if products_info else []},
            )

        return _mock_eats_nomenclature

    return do_mock


@pytest.fixture(name='mock_personal_phones_fixture', autouse=True)
def mock_personal_phones(mockserver):
    @mockserver.json_handler(f'/personal/v1/phones/bulk_retrieve')
    def _mock_personal_phones(request):
        assert request.method == 'POST'
        assert request.json['items']
        items = request.json['items']
        result = []
        for item in items:
            result.append({'id': item['id'], 'value': '+7123456789'})
        return mockserver.make_response(status=200, json={'items': result})

    return _mock_personal_phones


@pytest.fixture()
def get_cursor(pgsql):
    def create_cursor():
        return pgsql['picker_orders'].dict_cursor()

    return create_cursor


@pytest.fixture()
def create_measure_unit(get_cursor):
    def do_create_measure_unit(
            okei_code: int = 1,
            okei_name: str = 'GRM',
            okei_sign_ru: str = 'г',
            okei_sign: str = 'g',
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_picker_orders.measure_units '
            '(okei_code, okei_name, okei_sign_ru, okei_sign) '
            'VALUES (%s, %s, %s, %s) '
            'RETURNING id',
            (okei_code, okei_name, okei_sign_ru, okei_sign),
        )
        return cursor.fetchone()[0]

    return do_create_measure_unit


@pytest.fixture()
def create_currency(get_cursor):
    def do_create_currency(
            okv_code: int = 1,
            okv_name: str = 'Российский рубль',
            okv_str: str = 'RUB',
            sign: str = 'Р',
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_picker_orders.currencies '
            '(okv_code, okv_name, okv_str, sign) '
            'VALUES (%s, %s, %s, %s) '
            'RETURNING id',
            (okv_code, okv_name, okv_str, sign),
        )
        return cursor.fetchone()[0]

    return do_create_currency


@pytest.fixture()
def order_statuses_list(get_cursor):
    cursor = get_cursor()
    cursor.execute(
        'SELECT enum_range(NULL::eats_picker_orders.order_states)::text[]',
    )
    return cursor.fetchone()[0]


@pytest.fixture()
def update_order(get_cursor):
    def do_update_order(eats_id, **kwargs):
        cursor = get_cursor()
        set_statement = ''
        for i, k in enumerate(kwargs):
            set_statement += k + '=%s'
            if i < len(kwargs) - 1:
                set_statement += ','
        cursor.execute(
            'UPDATE eats_picker_orders.orders SET '
            + set_statement
            + ' WHERE eats_id = %s RETURNING id',
            (*list(kwargs.values()), eats_id),
        )
        order_id = cursor.fetchone()[0]
        return order_id

    return do_update_order


@pytest.fixture()
def create_order(
        get_cursor, create_order_status, create_order_talk, init_currencies,
):
    def do_create_order(
            eats_id='123',
            last_version=0,
            place_id=1,
            picker_id=None,
            payment_value=3000,
            payment_limit=4000,
            state='assigned',
            currency_id=1,
            picker_card_type='TinkoffBank',
            picker_card_value='cid_1',
            require_approval=None,
            customer_name='Vasya Pupkin',
            customer_phone_id='789',
            comment='some comment',
            flow_type='picking_only',
            brand_id=None,
            finish_picking_at=None,
            estimated_picking_time=None,
            picker_comment='Picker comments',
            picker_phone_id='123',
            picker_name='Picker name',
            courier_id='2',
            courier_name='Courier Name',
            courier_phone_id='456',
            pack_description=None,
            picker_phone=(
                '+7-999-888-77-66',
                '2030-01-19T15:00:27.010000+03:00',
            ),
            courier_phone=(
                '+7-555-444-33-22',
                '2030-01-19T15:00:27.010000+03:00',
            ),
            customer_forwarded_phone=(
                '+7-800-555-35-35',
                '2030-01-19T15:00:27.010000+03:00',
            ),
            customer_picker_phone_forwarding=(
                '+7-800-555-35-35',
                '2030-01-19T15:00:27.010000+03:00',
            ),
            receipt='{}',
            soft_check_id=None,
            claim_id='CLAIM_ID_20',
            place_starts_work_at='1976-01-19T12:00:00+03:00',
            place_finishes_work_at='1976-01-19T23:30:00+03:00',
            reserved=False,
            place_name='PLACE',
            place_address='Moscow, place plaza, 21',
            picker_customer_talks=None,
            courier_pickup_expected_at=None,
            courier_delivery_expected_at=None,
            courier_location=None,
            cargo_order_status=None,
            cargo_order_status_changed_at=None,
            created_at=None,
            spent=0,
            customer_id=None,
            customer_orders_count=None,
            slot_start=None,
            slot_end=None,
            estimated_delivery_time=None,
            region_id=None,
            is_asap=True,
            estimated_delivery_duration=None,
            partner_order_id=None,
            orders_group_id=None,
    ):
        if isinstance(spent, int):
            spent = decimal.Decimal(spent)

        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_picker_orders.orders '
            '(eats_id, last_version, place_id, picker_id, payment_value, '
            'payment_currency_id, payment_limit, state, '
            'picker_card_type, picker_card_value, require_approval, '
            'customer_name, customer_phone_id, '
            'comment, flow_type, brand_id, finish_picking_at, '
            'estimated_picking_time, picker_comment, '
            'picker_phone_id, picker_name, courier_id, courier_name, '
            'courier_phone_id, pack_description, picker_phone, '
            'courier_phone, customer_forwarded_phone, '
            'customer_picker_phone_forwarding, receipt, soft_check_id, '
            'claim_id, place_starts_work_at, place_finishes_work_at, '
            'reserved, place_name, place_address, '
            'courier_pickup_expected_at, courier_delivery_expected_at, '
            'courier_location, cargo_order_status, '
            'cargo_order_status_changed_at, created_at, updated_at, spent, '
            'customer_id, customer_orders_count, slot_start, slot_end, '
            'estimated_delivery_time, region_id, external_updated_at, '
            'is_asap, estimated_delivery_duration, partner_order_id, '
            'orders_group_id)'
            'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
            '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
            '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
            'COALESCE(%s, CURRENT_TIMESTAMP), '
            'COALESCE(%s, CURRENT_TIMESTAMP), %s, %s, %s, %s, %s, %s, %s, '
            'COALESCE(%s, CURRENT_TIMESTAMP), %s, %s, %s, %s) '
            'RETURNING id, require_approval',
            (
                eats_id,
                last_version,
                place_id,
                picker_id,
                payment_value,
                currency_id,
                decimal.Decimal(payment_limit),
                state,
                picker_card_type,
                picker_card_value,
                require_approval,
                customer_name,
                customer_phone_id,
                comment,
                flow_type,
                brand_id,
                finish_picking_at,
                estimated_picking_time,
                picker_comment,
                picker_phone_id,
                picker_name,
                courier_id,
                courier_name,
                courier_phone_id,
                pack_description,
                picker_phone,
                courier_phone,
                customer_forwarded_phone,
                customer_picker_phone_forwarding,
                receipt,
                soft_check_id,
                claim_id,
                place_starts_work_at,
                place_finishes_work_at,
                reserved,
                place_name,
                place_address,
                courier_pickup_expected_at,
                courier_delivery_expected_at,
                courier_location,
                cargo_order_status,
                cargo_order_status_changed_at,
                created_at,
                created_at,
                spent,
                customer_id,
                customer_orders_count,
                slot_start,
                slot_end,
                estimated_delivery_time,
                region_id,
                created_at,
                is_asap,
                estimated_delivery_duration,
                partner_order_id,
                orders_group_id,
            ),
        )
        order_id = cursor.fetchone()[0]
        create_order_status(
            order_id,
            state,
            last_version,
            created_at=created_at,
            author_id=picker_id,
        )
        if picker_customer_talks:
            for talk in picker_customer_talks:
                create_order_talk(order_id, *talk)
        return order_id

    return do_create_order


@pytest.fixture()
def create_order_item(get_cursor):
    cursor = get_cursor()

    def do_create_order_item(
            order_id=1,
            eats_item_id='eats-123',
            version=0,
            name='Foo bar',
            sku='4214FSD',
            show_vendor_code=None,
            category_id='14',
            category_name='Milk',
            barcodes=('Foo bar',),
            barcode_weight_algorithm='ean13-tail-gram-4',
            quantity=1.0,
            package_info='can',
            measure_unit_id=1,
            measure_value=1,
            measure_max_overweight=200,
            measure_quantum=None,
            quantum_price=None,
            absolute_quantity=None,
            quantum_quantity=None,
            relative_quantum=None,
            transport_volume_value=1,
            transport_volume_unit_id=1,
            sold_by_weight=False,
            price=10,
            location='foo',
            images=('https://example.org/product1/orig',),
            author=None,
            author_type=None,
            is_deleted_by=None,
            deleted_by_type=None,
            reason=None,
            replacements=tuple(),
            top_level_categories=None,
            in_stock=None,
            price_updated_at=None,
            require_marks=None,
    ):
        if not top_level_categories:
            top_level_categories = [
                (category_id, category_name, None, None, None),
            ]
        else:
            top_level_categories[0] = (
                category_id,
                category_name,
                None,
                None,
                None,
            )

        if measure_quantum is None:
            measure_quantum = measure_value
        if quantum_price is None:
            quantum_price = (
                round(price * (measure_quantum / measure_value), 2)
                if measure_value > 0
                else price
            )
        if quantum_quantity is None:
            quantum_quantity = (
                quantity * (measure_value / measure_quantum)
                if measure_quantum > 0
                else quantity
            )
        if absolute_quantity is None:
            absolute_quantity = quantity * measure_value

        cursor.execute(
            'INSERT INTO eats_picker_orders.order_items '
            '(order_id, eats_item_id, version, name, sku, category_id, '
            'category_name, barcodes, barcode_weight_algorithm, quantity, '
            'package_info, measure_unit_id, measure_value, '
            'measure_max_overweight, measure_quantum, quantum_price, '
            'absolute_quantity, quantum_quantity, relative_quantum, '
            'transport_volume_value, '
            'transport_volume_unit_id, sold_by_weight, price, location, '
            'images, author, author_type, is_deleted_by, deleted_by_type, '
            'reason, show_vendor_code, top_level_categories, in_stock, '
            'price_updated_at, require_marks) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
            '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
            '%s, CAST (%s AS eats_picker_orders.category_v2[]), %s, %s, %s)'
            'RETURNING id',
            [
                order_id,
                eats_item_id,
                version,
                name,
                sku,
                category_id,
                category_name,
                list(barcodes),
                barcode_weight_algorithm,
                quantity,
                package_info,
                measure_unit_id,
                measure_value,
                measure_max_overweight,
                measure_quantum,
                quantum_price,
                absolute_quantity,
                quantum_quantity,
                relative_quantum,
                transport_volume_value,
                transport_volume_unit_id,
                sold_by_weight,
                decimal.Decimal(price),
                location,
                list(images),
                author,
                author_type,
                is_deleted_by,
                deleted_by_type,
                reason,
                show_vendor_code,
                top_level_categories,
                in_stock,
                price_updated_at,
                require_marks,
            ],
        )
        item_id = cursor.fetchone()[0]
        if replacements:
            replacement_of, replacement_of_id = zip(*replacements)
            cursor.execute(
                'INSERT INTO eats_picker_orders.items_replacements '
                '(order_item_id, replacement_of, replacement_of_id) '
                'SELECT %s, r.replacement_of, r.replacement_of_id '
                'FROM UNNEST(%s::text[], %s::bigint[]) '
                'AS r (replacement_of, replacement_of_id)',
                [item_id, list(replacement_of), list(replacement_of_id)],
            )
        return item_id

    return do_create_order_item


@pytest.fixture()
def create_picked_item(get_cursor):
    def do_create_picked_item(
            order_item_id: int,
            picker_id: str = '1',
            cart_version: int = 0,
            weight: Optional[int] = None,
            count: Optional[int] = None,
            eats_id: Optional[str] = None,
            eats_item_id: Optional[str] = None,
            order_version: Optional[int] = None,
            sent_to_partner: Optional[bool] = None,
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_picker_orders.picked_items '
            '(picker_id, order_item_id, cart_version, weight, count, '
            'eats_id, eats_item_id, order_version, sent_to_partner) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) '
            'RETURNING id',
            [
                picker_id,
                order_item_id,
                cart_version,
                weight,
                count,
                eats_id,
                eats_item_id,
                order_version,
                sent_to_partner,
            ],
        )
        return cursor.fetchone()[0]

    return do_create_picked_item


@pytest.fixture()
def create_picked_item_position(get_cursor):
    def do_create_picked_item_position(
            picked_item_id: int,
            weight: Optional[int] = None,
            count: Optional[int] = None,
            barcode: Optional[str] = None,
            mark: Optional[str] = None,
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_picker_orders.picked_item_positions '
            '(picked_item_id, weight, count, barcode, mark) '
            'VALUES (%s, %s, %s, %s, %s) '
            'RETURNING id',
            [picked_item_id, weight, count, barcode, mark],
        )
        return cursor.fetchone()[0]

    return do_create_picked_item_position


@pytest.fixture()
def get_order(get_cursor):
    def do_get_order(order_id):
        cursor = get_cursor()
        psycopg2.extras.register_composite(
            'eats_picker_orders.expiring_phone', cursor,
        )
        cursor.execute(
            'SELECT * FROM eats_picker_orders.orders WHERE id = %s',
            [order_id],
        )
        return cursor.fetchone()

    return do_get_order


@pytest.fixture()
def get_order_by_eats_id(get_cursor):
    def do_get_order(eats_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_picker_orders.orders WHERE eats_id = %s',
            [eats_id],
        )
        return cursor.fetchone()

    return do_get_order


@pytest.fixture()
def get_last_order_status(get_cursor):
    def do_get_order_status(order_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_picker_orders.order_statuses WHERE '
            'order_id = %s ORDER BY id DESC LIMIT 1',
            [order_id],
        )
        return cursor.fetchone()

    return do_get_order_status


@pytest.fixture()
def create_order_status(get_cursor):
    def do_create_order_status(
            order_id,
            state,
            last_version=0,
            comment=None,
            reason_code=None,
            created_at=None,
            author_id=None,
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_picker_orders.order_statuses '
            '(order_id, last_version, author_id, state, comment, '
            'reason_code, created_at) '
            'VALUES (%s, %s, %s, %s, %s, %s, '
            'COALESCE(%s, CURRENT_TIMESTAMP))',
            [
                order_id,
                last_version,
                author_id,
                state,
                comment,
                reason_code,
                created_at,
            ],
        )

    return do_create_order_status


@pytest.fixture()
def create_order_talk(get_cursor):
    def do_create_order_talk(order_id, talk_id, length, status=None):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_picker_orders.order_talks'
            '(order_id, talk_id, length, status) '
            'VALUES (%s, %s, %s, %s)',
            [order_id, talk_id, length, status],
        )

    return do_create_order_talk


@pytest.fixture()
def get_order_soft_check(get_cursor):
    def do_get_order_soft_check(order_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_picker_orders.order_soft_check WHERE '
            'order_id = %s',
            [order_id],
        )
        return cursor.fetchone()

    return do_get_order_soft_check


@pytest.fixture()
def create_order_soft_check(get_cursor):
    def do_create_order_soft_check(
            order_id,
            eats_id,
            cart_version,
            picker_id,
            value,
            check_type='code128',
            description='',
            confirmation_type='barcode',
            place_id=None,
            brand_id=None,
            created_at=None,
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_picker_orders.order_soft_check '
            '(order_id, eats_id, cart_version, picker_id, value,'
            'type, description, confirmation_type, place_id, brand_id, '
            'created_at) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
            'COALESCE(%s, CURRENT_TIMESTAMP))',
            [
                order_id,
                eats_id,
                cart_version,
                picker_id,
                value,
                check_type,
                description,
                confirmation_type,
                place_id,
                brand_id,
                created_at,
            ],
        )

    return do_create_order_soft_check


@pytest.fixture()
def create_order_soft_check_lock(get_cursor):
    def do_create_order_soft_check_lock(eats_id, expires_at):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_picker_orders.order_soft_check_lock '
            '(eats_id, expires_at) '
            'VALUES (%s, %s)',
            [eats_id, expires_at],
        )

    return do_create_order_soft_check_lock


@pytest.fixture()
def delete_order_soft_check_lock(get_cursor):
    def do_delete_order_soft_check_lock(eats_id):
        cursor = get_cursor()
        cursor.execute(
            'DELETE FROM eats_picker_orders.order_soft_check_lock '
            'WHERE eats_id = %s',
            [eats_id],
        )

    return do_delete_order_soft_check_lock


@pytest.fixture()
def create_order_picking_policy(get_cursor):
    def do_create_order_picking_policy(
            eats_id, communication_policy, not_found_item_policy,
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_picker_orders.order_picking_policy'
            '(eats_id, communication_policy, not_found_item_policy) '
            'VALUES (%s, %s, %s)',
            [eats_id, communication_policy, not_found_item_policy],
        )

    return do_create_order_picking_policy


@pytest.fixture()
def get_order_items(get_cursor):
    def do_get_order_items(order_id, version=0):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_picker_orders.order_items '
            'WHERE order_id = %s AND version=%s',
            (order_id, version),
        )
        return cursor.fetchall()

    return do_get_order_items


@pytest.fixture()
def get_order_item_by_eats_item_id(get_cursor):
    def do_get_order_item(order_id, eats_item_id, version=0):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_picker_orders.order_items '
            'WHERE order_id = %s and eats_item_id = %s AND version=%s',
            (order_id, eats_item_id, version),
        )
        return cursor.fetchone()

    return do_get_order_item


@pytest.fixture()
def get_picked_items(get_cursor):
    def do_get_picked_items(order_item_id=None, order_item_ids=None):
        if order_item_id:
            order_item_ids = (order_item_id,)
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_picker_orders.picked_items '
            'WHERE order_item_id IN %s',
            [order_item_ids],
        )
        return cursor.fetchall()

    return do_get_picked_items


@pytest.fixture()
def get_picked_item_positions(get_cursor):
    def do_get_picked_item_positions(
            picked_item_id=None, picked_item_ids=None,
    ):
        if picked_item_id:
            picked_item_ids = (picked_item_id,)
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_picker_orders.picked_item_positions '
            'WHERE picked_item_id IN %s',
            [picked_item_ids],
        )
        return cursor.fetchall()

    return do_get_picked_item_positions


@pytest.fixture()
def init_measure_units(create_measure_unit):
    create_measure_unit(163, 'GRM', 'г', 'g')
    create_measure_unit(111, 'MLT', 'мл', 'ml')
    create_measure_unit(111, 'CMQ', 'см^3', 'cm^3')
    create_measure_unit(112, 'DMQ', 'дм^3', 'dm^3')


@pytest.fixture()
def init_currencies(create_currency):
    create_currency(1, 'Российский рубль', 'RUB', 'р')


@pytest.fixture()
def generate_order_data():
    def do_generate_order_data(
            eats_id: str = '12345',
            place_id: int = 112223,
            place_slug: Optional[str] = 'place-slug-1',
            brand_id: Optional[str] = 'brand_id_1',
            brand_slug: Optional[str] = 'brand-slug-1',
            items: Optional[list] = None,
            payment_value: float = 1005,
            payment_limit: float = 1200,
            payment_currency_code: str = 'RUB',
            payment_currency_sign: str = 'Р',
            customer_name: str = 'Vasya Pupkin',
            customer_phone_id: str = '123',
            comment: Optional[str] = 'some comment',
            claim_id='CLAIM_ID_20',
            place_starts_work_at='1976-01-19T12:00:00+03:00',
            place_finishes_work_at='1976-01-19T23:30:00+03:00',
            reserved=False,
            place_name='PLACE',
            place_address='Moscow, place plaza, 21',
            estimated_picking_time=None,
    ) -> dict:
        return {
            'eats_id': eats_id,
            'place_id': place_id,
            'place_slug': place_slug,
            'brand_id': brand_id,
            'brand_slug': brand_slug,
            'items': items or [],
            'payment': {
                'value': payment_value,
                'limit': payment_limit,
                'currency': {
                    'code': payment_currency_code,
                    'sign': payment_currency_sign,
                },
            },
            'customer': {'name': customer_name},
            'customer_phone_id': customer_phone_id,
            'comment': comment,
            'claim_id': claim_id,
            'place_starts_work_at': place_starts_work_at,
            'place_finishes_work_at': place_finishes_work_at,
            'reserved': reserved,
            'place_name': place_name,
            'place_address': place_address,
            'estimated_picking_time': estimated_picking_time,
        }

    return do_generate_order_data


@pytest.fixture()
def generate_order_item_data():
    def do_generate_order_item_data(
            id_: str = '12345',
            vendor_code: str = '1FS42',
            show_vendor_code: Optional[bool] = None,
            name: str = 'Хлеб',
            category_id: str = '51234',
            category_name: str = 'Хлебо-булочные изделия',
            barcodes: Optional[List[str]] = None,
            barcode_weight_encoding: Optional[str] = 'ean13-tail-gram-4',
            location: Optional[str] = 'Бакалея. Линия 8',
            package_info: Optional[str] = None,
            quantity: float = 2,
            price: Optional[float] = 25,
            measure_value: int = 500,
            measure_quantum: Optional[float] = None,
            quantum_price: Optional[float] = None,
            measure_v1: bool = True,
            measure_unit: str = 'MLT',
            measure_max_overweight: Optional[int] = 50,
            volume_value: int = 400,
            volume_unit: str = 'CMQ',
            is_catch_weight: bool = False,
            images: Optional[List[dict]] = None,
            use_string_prices: Optional[bool] = False,
    ) -> dict:
        if not barcodes:
            barcodes = ['987654321098']
        if not images:
            images = [{'url': 'https://yandex.ru/1.jpg'}]
        order_item_data: Dict[str, Any] = {
            'id': id_,
            'vendor_code': vendor_code,
            'show_vendor_code': show_vendor_code,
            'name': name,
            'category': {'id': category_id, 'name': category_name},
            'barcode': {
                'values': barcodes,
                'weight_encoding': barcode_weight_encoding,
            },
            'location': location,
            'quantity': quantity,
            'volume': {'value': volume_value, 'unit': volume_unit},
            'is_catch_weight': is_catch_weight,
            'images': images or [],
        }
        if price is not None:
            order_item_data['price'] = price
        if use_string_prices:
            order_item_data['price_string'] = str(price)
        if measure_v1:
            order_item_data['measure'] = {
                'value': measure_value,
                'unit': measure_unit,
                'max_overweight': measure_max_overweight,
            }
        if not measure_v1:
            if measure_quantum is None:
                measure_quantum = 0.75
            if price is not None and quantum_price is None:
                quantum_price = round(price * measure_quantum, 2)

            order_item_data['measure_v2'] = {
                'value': measure_value,
                'unit': measure_unit,
                'max_overweight': measure_max_overweight,
                'quantum': measure_quantum,
                'price': quantum_price,
            }
            if use_string_prices:
                order_item_data['measure_v2']['price_string'] = str(
                    quantum_price,
                )
        if package_info is not None:
            order_item_data['package_info'] = package_info
        return order_item_data

    return do_generate_order_item_data


@pytest.fixture()
def generate_integration_item_data():
    def do_generate_item_data(
            id_: Optional[str] = None,
            origin_id: Optional[str] = '12345',
            vendor_code: str = '1FS42',
            name: str = 'Хлеб',
            category_id: str = '51234',
            category_name: str = 'Хлебо-булочные изделия',
            barcodes: Optional[List[str]] = None,
            barcode_weight_encoding: Optional[str] = 'ean13-tail-gram-4',
            location: Optional[str] = 'Бакалея. Линия 8',
            package_info: Optional[str] = None,
            price: float = 25,
            measure_value: int = 500,
            measure_unit: str = 'MLT',
            measure_max_overweight: Optional[int] = 50,
            measure_quantum: float = 1,
            volume_value: Optional[int] = 400,
            volume_unit: Optional[str] = 'CMQ',
            is_catch_weight: bool = False,
            images: Optional[List[dict]] = None,
    ) -> dict:
        if id_ is None:
            id_ = str(uuid.uuid4())
        if barcodes is None:
            barcodes = ['987654321098']
        if images is None:
            images = [{'url': 'https://yandex.ru/1.jpg'}]
        return {
            'id': id_,
            'origin_id': origin_id,
            'vendor_code': vendor_code,
            'name': name,
            'category': {'id': category_id, 'name': category_name},
            'barcode': {
                'values': barcodes,
                'weight_encoding': barcode_weight_encoding,
            },
            'location': location,
            'package_info': package_info,
            'price': str(round(price * measure_quantum, 4)),
            'measure': {
                'value': measure_value,
                'unit': measure_unit,
                'max_overweight': measure_max_overweight,
                'quantum': measure_quantum,
            },
            'volume': {'value': volume_value, 'unit': volume_unit},
            'is_catch_weight': is_catch_weight,
            'images': images,
        }

    return do_generate_item_data


@pytest.fixture()
def generate_product_info():
    def do_generate_product_info(public_id, name, images, marking_type=None):
        response_images = []
        for i, image in enumerate(images):
            response_images += [{'url': image, 'sort_order': i}]
        return {
            'adult': False,
            'barcodes': [],
            'description': {'general': 'Some description'},
            'id': public_id,
            'images': response_images,
            'is_catch_weight': True,
            'is_choosable': True,
            'is_sku': False,
            'name': name,
            'origin_id': f'origin_id_{public_id}',
            'place_brand_id': '1',
            'shipping_type': 'all',
            'marking_type': marking_type,
        }

    return do_generate_product_info


@pytest.fixture()
def get_item_replacement_of(get_cursor):
    def do_get_item_replacement_of(item_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT replacement_of FROM eats_picker_orders.items_replacements '
            'WHERE order_item_id = %s',
            (item_id,),
        )
        return {row[0] for row in cursor}

    return do_get_item_replacement_of


@pytest.fixture()
def get_order_talks(get_cursor):
    def do_get_order_talks(order_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT order_id, talk_id, length, status '
            'FROM eats_picker_orders.order_talks '
            'WHERE order_id = %s',
            [order_id],
        )
        return list(map(dict, cursor.fetchall()))

    return do_get_order_talks


@pytest.fixture()
def get_order_picking_policy(get_cursor):
    def do_get_order_picking_policy(eats_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT id, eats_id, communication_policy, not_found_item_policy '
            'FROM eats_picker_orders.order_picking_policy '
            'WHERE eats_id = %s',
            [eats_id],
        )
        return cursor.fetchone()

    return do_get_order_picking_policy


@pytest.fixture(name='cargo_environment')
def _cargo_environment(mockserver, mocked_time):
    class Environment:
        def __init__(self):
            self._phones = {}
            self._couriers = {}
            self._points = {}
            self._claims = {}
            self._build_mocks()

        def create_phone(self, phone: str, ext: str, ttl_seconds: int) -> int:
            phone_id = len(self._phones)
            self._phones[phone_id] = {
                'phone': phone,
                'ext': ext,
                'ttl_seconds': ttl_seconds,
            }
            return phone_id

        def create_courier(
                self,
                courier_id: str,
                courier_name: str,
                phone_id: int,
                lat: int,
                lon: int,
        ) -> str:
            self._couriers[courier_id] = {
                'id': courier_id,
                'name': courier_name,
                'phone': self._phones[phone_id],
                'lat': lat,
                'lon': lon,
            }
            return courier_id

        def create_point(
                self, point_type: str, visit_status: str, expected: datetime,
        ) -> int:
            point_id = len(self._points)
            self._points[point_id] = {
                'id': point_id,
                'type': point_type,
                'visit_status': visit_status,
                'expected': expected,
            }
            return point_id

        def create_claim(
                self,
                claim_id: str,
                status: str,
                courier_id: str,
                point_ids: list,
        ) -> str:
            self._claims[claim_id] = {
                'id': claim_id,
                'status': status,
                'courier': self._couriers[courier_id],
                'points': [self._points[point_id] for point_id in point_ids],
            }
            return claim_id

        def _datetime_to_string(self, date_time: datetime.datetime) -> str:
            return date_time.astimezone().isoformat()

        def _make_route_point(self, point: dict):
            return {
                'id': point['id'],
                'type': point['type'],
                'visit_status': point['visit_status'],
                'contact': {'phone': 'phone', 'name': 'name'},
                'address': {'fullname': 'fullname', 'coordinates': [0, 0]},
                'visited_at': {
                    'expected': self._datetime_to_string(point['expected']),
                },
                'visit_order': point['id'],
            }

        def _make_route_points(self, claim: dict):
            return [self._make_route_point(point) for point in claim['points']]

        def _make_claim(self, claim_id: str):
            claim = self._claims[claim_id]
            return {
                'id': claim['id'],
                'items': [
                    {
                        'pickup_point': 0,
                        'droppof_point': 0,
                        'title': 'title',
                        'cost_value': '0.00',
                        'cost_currency': 'RUB',
                        'quantity': 1,
                    },
                ],
                'route_points': self._make_route_points(claim),
                'status': claim['status'],
                'performer_info': {
                    'courier_name': claim['courier']['name'],
                    'legal_name': 'legal_name',
                },
                'created_ts': self._datetime_to_string(
                    mocked_time.now().replace(tzinfo=pytz.utc)
                    - datetime.timedelta(hours=1),
                ),
                'updated_ts': self._datetime_to_string(
                    mocked_time.now().replace(tzinfo=pytz.utc)
                    - datetime.timedelta(hours=1),
                ),
                'revision': 1,
                'version': 0,
            }

        def _build_mocks(self):
            @mockserver.json_handler(
                '/b2b-taxi/b2b/cargo/integration/v2/claims/bulk_info',
            )
            def _mock_cargo_claims_bulk_info(request):
                assert request.method == 'POST'
                claim_ids = request.json['claim_ids']
                for claim_id in claim_ids:
                    assert claim_id in self._claims.keys()
                return mockserver.make_response(
                    status=200,
                    json={
                        'claims': [
                            self._make_claim(claim_id)
                            for claim_id in claim_ids
                        ],
                    },
                )

            @mockserver.json_handler(
                '/cargo-claims/internal/external-performer',
            )
            def _mock_cargo_external_performer(request):
                assert request.method == 'GET'
                claim = self._claims[request.query['sharing_key']]
                courier = claim['courier']
                return mockserver.make_response(
                    status=200, json={'eats_profile_id': courier['id']},
                )

            @mockserver.json_handler(
                '/b2b-taxi/b2b/cargo/integration/v1/driver-voiceforwarding',
            )
            def _mock_cargo_driver_voiceforwarding(request):
                assert request.method == 'POST'
                claim = self._claims[request.json['claim_id']]
                courier = claim['courier']
                phone = courier['phone']
                return mockserver.make_response(
                    status=200,
                    json={
                        'phone': phone['phone'],
                        'ext': phone['ext'],
                        'ttl_seconds': phone['ttl_seconds'],
                    },
                )

            @mockserver.json_handler(
                '/b2b-taxi/b2b/cargo/integration/v1/claims/performer-position',
            )
            def _mock_cargo_performer_position(request):
                assert request.method == 'GET'
                claim = self._claims[request.query['claim_id']]
                courier = claim['courier']
                return mockserver.make_response(
                    status=200,
                    json={
                        'position': {
                            'timestamp': 0,
                            'lat': courier['lat'],
                            'lon': courier['lon'],
                        },
                    },
                )

            self.mock_cargo_claims_bulk_info = _mock_cargo_claims_bulk_info
            self.mock_cargo_external_performer = _mock_cargo_external_performer
            # pylint: disable=invalid-name
            self.mock_cargo_driver_voiceforwarding = (
                _mock_cargo_driver_voiceforwarding
            )
            self.mock_cargo_performer_position = _mock_cargo_performer_position

    return Environment()


@pytest.fixture(name='phone_forwarding_allow_all', autouse=True)
def _phone_forwarding_allow_all(experiments3):
    experiments3.add_config(
        name='eats_picker_orders_allowed_phone_forwardings',
        consumers=['eats-picker-orders/allowed-phone-forwardings'],
        default_value={
            'phone_forwarding_allowed': True,
            'empty_requester_phone_id_allowed': True,
        },
    )


@pytest.fixture()
def set_latest_globus_soft_check(get_cursor):
    def do_get_latest_globus_soft_check(value):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_picker_orders.latest_globus_soft_check'
            ' (value) VALUES(%s)',
            [value],
        )

    return do_get_latest_globus_soft_check


@pytest.fixture()
def get_latest_globus_soft_check(get_cursor):
    def do_get_latest_globus_soft_check():
        cursor = get_cursor()
        cursor.execute(
            'SELECT value FROM eats_picker_orders.latest_globus_soft_check',
        )
        return cursor.fetchone()[0]

    return do_get_latest_globus_soft_check


@pytest.fixture()
def add_failed_receipt(get_cursor):
    def do_add_failed_receipt(failed_receipt):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_picker_orders.failed_receipts'
            ' (order_nr, receipt, retry_cnt) VALUES(%s, %s, %s)',
            [
                failed_receipt['order_nr'],
                json.dumps(failed_receipt['receipt']),
                failed_receipt['retry_cnt'],
            ],
        )

    return do_add_failed_receipt


@pytest.fixture()
def get_failed_receipts(get_cursor):
    def do_get_failed_receipts():
        cursor = get_cursor()
        cursor.execute(
            'SELECT id, order_nr, receipt, retry_cnt, updated_at '
            'FROM eats_picker_orders.failed_receipts',
        )
        return list(map(dict, cursor.fetchall()))

    return do_get_failed_receipts
