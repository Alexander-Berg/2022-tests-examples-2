import decimal as dec

BRAND_ID = 1
PLACE_ID = 1
FALLBACK_STOCK_DIR = 'viewer/fallback/stock'
FALLBACK_AVAILABILITY_DIR = 'viewer/fallback/availability'
S3_AVAILABILITY_FILE = (
    f'viewer/new/availability/1/00000000-0000-0000-0000-000000000001.json'
)
DEFAULT_PRODUCT_VALUES = {
    'brand_id': BRAND_ID,
    'nmn_id': '00000000-0000-0000-0000-000000000001',
    'origin_id': 'origin_id_1',
}
DEFAULT_STOCK_ITEM_VALUES = {
    'place_id': 1,
    'product_nmn_id': '00000000-0000-0000-0000-000000000001',
    'value': dec.Decimal('1.0'),
}
DEFAULT_AVAILABILITY_ITEM_VALUES = {
    'place_id': 1,
    'product_nmn_id': '00000000-0000-0000-0000-000000000001',
    'is_available': True,
}
