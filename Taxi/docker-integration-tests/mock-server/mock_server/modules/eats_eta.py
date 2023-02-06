import datetime

from aiohttp import web


async def delivery_duration(_):
    return web.json_response(
        {
            **{'name': 'delivery_duration'},
            **get_duration_response(_),
        },
    )


async def picking_duration(_):
    return web.json_response(
        {
            **{'name': 'picking_duration'},
            **get_duration_response(_),
        },
    )


def get_duration_response(_):
    return {
        'duration': 1800,
        'remaining_duration': 1800,
        'calculated_at': datetime.datetime.now().strftime(
            '%Y-%m-%dT%H:%M:%S.%f+0000',
        ),
        'status': 'not_started',
    }


class Application(web.Application):
    def __init__(self):
        super().__init__()

        self.router.add_post(
            '/v1/eta/order/delivery-duration', delivery_duration,
        )
        self.router.add_post(
            '/v1/eta/order/picking-duration', picking_duration,
        )
        self.router.add_post(
            '/v1/eta/orders/estimate', self.order_estimation,
        )

    async def order_estimation(self, request):
        data = await request.json()

        response_orders = []
        not_found_orders = []
        for order_nr in data['orders']:
            response_estimations = []
            for estimation in data['estimations']:
                if estimation == 'delivery_duration':
                    response_estimations.append({
                       **{'name': 'delivery_duration'},
                       **get_duration_response(order_nr),
                    })
                else:
                    response_estimations.append({
                        **{'name': 'picking_duration'},
                        **get_duration_response(order_nr),
                    })
            response_orders.append(
                {
                    'order_nr': order_nr,
                    'estimations': response_estimations,
                },
            )
        return web.json_response(
            {
                'orders': response_orders,
                'not_found_orders': not_found_orders,
            },
        )
