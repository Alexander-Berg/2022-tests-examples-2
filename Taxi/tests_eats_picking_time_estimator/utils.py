import pytest


def picking_formula():
    return pytest.mark.experiments3(filename='exp3_picking_formula.json')


def fill_item(item):
    item.setdefault('vendor_code', '1')
    item.setdefault('price', 1)
    item.setdefault('images', [])
    item.setdefault('measure', {})
    measure = item['measure']
    measure.setdefault('value', 1)
    measure.setdefault('unit', 'GRM')
    measure.setdefault('max_overweight', 0)
    return item


def fill_order(order):
    order.setdefault('flow_type', 'picking_only')
    order.setdefault('items', [{}])
    for item in order['items']:
        fill_item(item)
    return order
