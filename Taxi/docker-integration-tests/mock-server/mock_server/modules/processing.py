from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get(
            '/processing/v1/eda/picker_order_history/create-event',
            handle_processing,
        )


async def handle_processing(request):
    return web.json_response({'event_id': request.json['order_nr']})
