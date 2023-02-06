BRAND_ID = 1
PLACE_ID = 1
PLACE_SLUG = 'slug'

EATER_ID = '123'
HEADERS = {'X-Eats-User': f'user_id={EATER_ID}'}
HEADERS_PARTNER = {'X-Eats-User': f'partner_user_id={EATER_ID}'}

PUBLIC_IDS = [
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b005',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b006',
]
SKU_IDS = ['sku_id_1', 'sku_id_2', 'sku_id_3', 'sku_id_4', 'sku_id_5']
ORIGIN_IDS = [
    'origin_id_1',
    'origin_id_2',
    'origin_id_3',
    'origin_id_4',
    'origin_id_5',
]


class Handlers:
    # core handlers:
    CORE_BRANDS = '/eats-core-retail/v1/brands/retrieve'
    CORE_RETAIL_BRAND_PLACES = '/eats-core-retail/v1/brand/places/retrieve'

    # eats-ordershistory handlers:
    ORDERSHISTORY_ORDERS = '/eats-ordershistory/v1/get-orders'

    # eats-products
    PRODUCTS_PUBLIC_BY_ORIGIN_ID = (
        '/eats-products/internal/v2/products/public_id_by_origin_id'
    )

    # eats-retail-categories
    USER_PRODUCTS_BRAND = '/v1/orders-history/products/brand'
    USER_PRODUCTS_CROSS_BRAND = '/v1/orders-history/products/cross-brand'

    # eats-nomenclature handlers:
    NOMENCLATURE_PRODUCTS_INFO = '/eats-nomenclature/v1/products/info'
    NOMENCLATURE_PUBLIC_ID_BY_SKU_ID = (
        '/eats-nomenclature/v1/place/products/id-by-sku-id'
    )

    # eats-eaters handlers:
    FIND_BY_PASPORT_UIDS = '/eats-eaters/v1/eaters/find-by-passport-uids'


def sort_by_public_id(products):
    return sorted(products, key=lambda item: item['public_id'])


def sort_by_sku_id(products):
    return sorted(products, key=lambda item: item['sku_id'])
