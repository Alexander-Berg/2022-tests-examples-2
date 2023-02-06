def product_static_info(public_id, name, shipping_type, sku_id=None):
    return {
        'id': public_id,
        'origin_id': 'origin_id_101',
        'description': {'general': 'Описание'},
        'place_brand_id': '1',
        'name': name,
        'is_choosable': True,
        'is_catch_weight': False,
        'adult': False,
        'shipping_type': shipping_type,
        'barcodes': [],
        'images': [],
        'is_sku': False,
        'sku_id': sku_id,
        'is_alcohol': False,
        'is_fresh': False,
    }
