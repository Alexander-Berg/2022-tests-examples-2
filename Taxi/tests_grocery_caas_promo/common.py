DEPOT = {
    'depot_id': 'test_depot_id',
    'external_depot_id': '70134',
    'country_iso3': 'RUS',
    'region_id': 213,
    'timezone': 'Europe/Moscow',
}

DISCOUNT_REQUEST = {'depot': DEPOT, 'layout_id': 'layout-1'}


def build_tree(category_tree):
    categories = {}
    products = {}
    for category_idx, category in enumerate(category_tree):
        categories[category['id']] = {'id': category['id']}
        for product_idx, product_id in enumerate(category['products']):
            if product_id in products:
                products[product_id]['category_ids'].append(category['id'])
            else:
                products[product_id] = {
                    'full_price': '123.456',
                    'id': product_id,
                    'category_ids': [category['id']],
                    'rank': category_idx * 10 + product_idx,
                }

    return {
        'categories': list(categories.values()),
        'products': list(products.values()),
        'markdown_products': [],
    }
