from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/v1/driver/login', driver_login_handler)


async def driver_login_handler(request: web.Request):
    body_bytes = await request.read()
    body = body_bytes.decode('utf8')
    if 'send_sms' in body:
        return web.json_response(
            {'domains': [], 'step': 'select_db', 'token': 'fake token'},
        )
    return web.json_response(
        {
            'step': 'login',
            'login': {
                'session': '3ace3901ce434dcbbd64a9314c4b3153',
                'guid': 'c5d1f9bdbb13456ca2fdc345bb63a3b0',
            },
        },
    )
