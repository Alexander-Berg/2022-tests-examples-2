# pylint: disable=redefined-outer-name
import pytest


pytest_plugins = ['eats_picker_orders_postprocessing_plugins.pytest_plugins']


@pytest.fixture()
def generate_picker_order():
    def do_generate_picker_order(
            order_id='123456',
            eats_id='eats_id1',
            status='new',
            created_at='1976-01-19T12:00:00+03:00',
            updated_at='1976-01-19T12:00:00+03:00',
            status_updated_at='1976-01-19T12:00:00+03:00',
            ordered_total='1000.00',
            pickedup_total='1000.00',
            total_weight=1000,
            currency_code='810',
            currency_sign='RUB',
            categories=None,
            picker_items=None,
            require_approval=False,
            flow_type='picking_packing',
            place_id=1234,
            version=0,
            picker_id='picker1',
            brand_id=None,
    ) -> dict:
        return {
            'id': order_id,
            'eats_id': eats_id,
            'status': status,
            'created_at': created_at,
            'updated_at': updated_at,
            'status_updated_at': status_updated_at,
            'ordered_total': ordered_total,
            'pickedup_total': pickedup_total,
            'total_weight': total_weight,
            'currency': {'code': currency_code, 'sign': currency_sign},
            'categories': (categories if categories else []),
            'picker_items': (picker_items if picker_items else []),
            'require_approval': require_approval,
            'flow_type': flow_type,
            'place_id': place_id,
            'version': version,
            'picker_id': picker_id,
            'brand_id': brand_id,
        }

    return do_generate_picker_order


@pytest.fixture()
def generate_picker_item():
    def do_generate_picker_item(
            item_id='eats_item_id1',
            name='Milk',
            barcodes=None,
            weight_barcode_type='ean13-tail-gram-4',
            is_catch_weight=False,
            vendor_code='vendor_code1',
            measure=None,
            measure_v2=None,
            count=None,
            price='10.00',
            goods_check_text='some text',
            max_overweight=50,
            category_id='1',
            images=None,
            location='location',
    ) -> dict:
        return {
            'id': item_id,
            'name': name,
            'barcodes': (barcodes if barcodes else ['12345678']),
            'weight_barcode_type': weight_barcode_type,
            'is_catch_weight': is_catch_weight,
            'vendor_code': vendor_code,
            'measure': measure,
            'measure_v2': measure_v2,
            'count': count,
            'price': price,
            'goods_check_text': goods_check_text,
            'max_overweight': max_overweight,
            'category_id': category_id,
            'images': (images if images else []),
            'location': location,
        }

    return do_generate_picker_item
