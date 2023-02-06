import json

import pytest


@pytest.fixture(autouse=True)
def tags_topics_mocks(mockserver):
    @mockserver.json_handler('/tags_topics/v1/index')
    def handler(request):
        args = request.args.to_dict()
        revision = int(args['revision'])
        return mockserver.make_response(
            json.dumps({'revision': revision, 'updates': []}), status=200,
        )
