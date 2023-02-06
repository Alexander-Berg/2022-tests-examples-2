import typing

from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/v1/phones/store', self.phones_store_v1)
        self.router.add_post('/v1/emails/store', self.emails_store_v1)
        self.router.add_post('/phones/store', self.phones_store)
        self.router.add_post('/emails/store', self.emails_store)
        self.router.add_post('/v1/phones/retrieve', self.phones_retrieve)
        self.router.add_post('/phones/retrieve', self.handle_phones_retrieve)
        self.router.add_post('/v1/{data_type}/bulk_store', self.bulk_store)
        self.storage: typing.List[typing.Dict] = []
        self._secret = []

    async def phones_store_v1(self, request):
        data = await request.json()
        response: typing.Dict = {
            'id': data['value'][2:] + '_id',
            'value': data['value'],
        }
        self.storage.append(response)
        return web.json_response(response)

    async def emails_store_v1(self, request):
        data = await request.json()
        response: typing.Dict = {
            'id': data['value'] + '_id',
            'value': data['value'],
        }
        self.storage.append(response)
        return web.json_response(response)

    async def phones_store(self, request):
        data = await request.json()
        response: typing.Dict = {
            'id': data['phone'] + '_id',
            'phone': data['phone'],
        }
        self.storage.append(response)
        return web.json_response(response)

    async def emails_store(self, request):
        data = await request.json()
        response: typing.Dict = {
            'id': data['email'] + '_id',
            'phone': data['email'],
        }
        self.storage.append(response)
        return web.json_response(response)

    async def phones_retrieve(self, request):
        data = await request.json()
        response: typing.Dict = {'id': data['id'], 'value': '+79160125597'}
        return web.json_response(response)

    async def handle_phones_retrieve(self, request):
        data = await request.json()
        self._secret.append(data)
        _id = data['id']
        _phones = {
            '9aef863cae894bb39a9fabaea851fcd1': '+79682777450',
            '9aef863cae894bb39a9fabaea851fabc': '+79682777000',
            '9aef863cae894bb39a9fabaea851fcde': '+79682777666',
        }
        response: typing.Dict = {'id': _id, 'phone': _phones[_id]}
        return web.json_response(response)

    async def bulk_store(self, request):
        data = await request.json()
        return web.json_response(
            {
                'items': [
                    {'id': x['value'] + '_id', 'value': x['value']}
                    for x in data['items']
                ],
            },
        )
