import json

import pytest


@pytest.fixture(name='nirvana_reactor', autouse=True)
def _nirvana_reactor(mockserver):
    path_prefix = '/nirvana-reactor-production'

    def _extract_key(request):
        return request.path[len(path_prefix) + 1 :]

    @mockserver.handler(path_prefix, prefix=True)
    def _mock_all(request):

        key = _extract_key(request)

        if request.method == 'POST' and key == 'api/v1/a/i/instantiate':
            return mockserver.make_response(
                json.dumps(
                    {
                        'artifactInstanceId': 'dummy_instance_id',
                        'creationTimestamp': 'dummy_timestamp',
                    },
                ),
                200,
            )
        if request.method == 'POST' and key == 'api/v1/a/i/get/last':
            return mockserver.make_response(
                json.dumps(
                    {
                        'result': {
                            'id': 'dummy_id',
                            'artifactId': 'dummy_artifact_id',
                            'creatorLogin': 'dummy_login',
                            'metadata': {
                                '@type': (
                                    '/yandex.reactor.artifact.'
                                    + 'YtPathArtifactValueProto'
                                ),
                                'path': 'dummy_path',
                            },
                            'creationTimestamp': 'dummy_stamp',
                            'status': 'ACTIVE',
                            'source': 'API',
                        },
                    },
                ),
                200,
            )
        return mockserver.make_response('Not found or invalid method', 404)
