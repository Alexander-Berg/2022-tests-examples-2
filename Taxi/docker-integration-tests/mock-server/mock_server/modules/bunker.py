from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get('/v1/tree', self.handle_tree)
        self.router.add_get('/v1/cat', self.handle_cat)

    def handle_tree(self, request):
        return web.json_response([
            {
                'name': 'tanker',
                'fullName': '/taxi-tariff-editor/tanker',
                'version': 230,
                'isDeleted': False,
                'mime': 'application/json; charset=utf-8; ' +
                        'schema="bunker:/.schema/tjson#"',
                'saveDate': '2019-06-25T13:44:28.498Z',
                'publishDate': None,
                'flushDate': '2018-09-19T10:16:36.645Z',
            },
        ])

    def handle_cat(self, request):
        return web.json_response({
            'export_info': {
                'request': {
                    'project-id': 'taxi-tariff-editor',
                    'branch-id': 'master',
                },
                'name': 'taxi-tariff-editor',
                'branch': 'master',
            },
            'keysets': {
                'common': {
                    'keys': {},
                    'meta': {
                        'languages': ['ru', 'en'],
                        'context': '',
                    },
                },
            },
        })
