from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post(
            '/eats-products/internal/v2/products/public_id_by_origin_id',
            handle_products_ids,
        )
        self.router.add_post(
            '/api/v2/menu/get-items', handle_eats_products_menu,
        )


async def handle_products_ids(request):
    return web.json_response([])


async def handle_eats_products_menu(request):
    return web.json_response(
        {
            'place_menu_items': [
                {
                    'adult': False,
                    'available': True,
                    'decimal_price': '100.00',
                    'decimal_promo_price': None,
                    'description': 'test item',
                    'id': 4,
                    'in_stock': None,
                    'is_catch_weight': True,
                    'name': 'Item from retail',
                    'options_groups': [],
                    'origin_id': 'test_retail_item',
                    'picture': {
                        'ratio': 1,
                        'scale': 'aspect_fill',
                        'uri': (
                            '/images/3534679/'
                            '3b74946353c15a68754bf5f8c183f0ef-{w}x{h}.jpeg'
                        ),
                    },
                    'price': 100,
                    'promo_price': None,
                    'promo_types': [],
                    'public_id': 'free_gift_wrapping_paper',
                    'shipping_type': 'all',
                    'weight': '0.05kg',
                    'weight_kilograms': '0.05',
                    'weight_number': 0,
                },
            ],
            'place_slug': 'retail_shop',
            'place_id': 2,
            'place_brand_business_type': 'shop',
        },
    )
