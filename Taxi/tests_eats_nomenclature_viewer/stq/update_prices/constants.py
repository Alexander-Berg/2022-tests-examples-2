import decimal as dec

BRAND_ID = 1
PLACE_ID = 1
FALLBACK_FILES_DIR = 'viewer/fallback/price'
DEFAULT_PRODUCT_VALUES = {
    'brand_id': BRAND_ID,
    'nmn_id': '00000000-0000-0000-0000-000000000001',
    'origin_id': 'origin_id_1',
}
DEFAULT_PLACE_PRODUCT_ITEM_VALUES = {
    'place_id': 1,
    'product_nmn_id': '00000000-0000-0000-0000-000000000001',
    'price': dec.Decimal('10.0'),
}
