from aiohttp import web


def _env_params():
    return {'domain': 'yandex.net', 'juggler_folder': 'folder'}


def env_params(project_prefix):
    return {
        'general': {'project_prefix': project_prefix, 'docker_image_tpl': ''},
        'stable': _env_params(),
        'testing': _env_params(),
        'unstable': _env_params(),
    }


ALL_PROJECTS = [
    {
        'id': 150,
        'name': 'taxi-infra',
        'env_params': env_params('taxi'),
        'namespace_id': 1,
    },
    {
        'id': 2,
        'name': 'taxi',
        'env_params': env_params('taxi'),
        'namespace_id': 2,
    },
    {
        'id': 3,
        'name': 'eda',
        'env_params': env_params('eda'),
        'namespace_id': 3,
    },
]


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post(
            '/v1/namespaces/retrieve/', self.v1_namespaces_retrieve,
        )
        self.router.add_get('/v1/projects/', self.v1_projects)
        self.router.add_get('/v1/services/', self.v1_services)

    @staticmethod
    async def v1_namespaces_retrieve(_):
        return web.json_response(
            {
                'namespaces': [
                    {'id': 3, 'name': 'lavka'},
                    {'id': 2, 'name': 'eda'},
                    {'id': 1, 'name': 'taxi'},
                ],
            },
        )

    @staticmethod
    async def v1_projects(_):
        return web.json_response({'projects': ALL_PROJECTS})

    @staticmethod
    async def v1_services(_):
        return web.json_response(
            {
                'services': [
                    {
                        'abc_slug': 'serviceabc',
                        'cluster_type': 'nanny',
                        'id': 1,
                        'name': 'service',
                        'project_id': 1,
                    },
                ],
            },
        )
