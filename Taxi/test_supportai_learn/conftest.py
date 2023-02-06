# pylint: disable=redefined-outer-name
import datetime

import pytest

import supportai_learn.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['supportai_learn.generated.service.pytest_plugins']


@pytest.fixture(autouse=True, name='standard_auth')
def mock_supportai_tasks(request, mockserver):
    mark = request.node.get_closest_marker(name='disable_standard_auth')

    if mark is None:

        @mockserver.json_handler(
            '/supportai-tasks/supportai-tasks/v1/users/.*/projects/.*',
            regex=True,
        )
        async def _(_):
            return mockserver.make_response(
                status=200,
                json={
                    'id': '1',
                    'slug': 'project',
                    'title': 'Project',
                    'capabilities': [],
                    'is_chatterbox': False,
                    'permissions': ['read', 'write'],
                },
            )

    @mockserver.json_handler('/supportai-tasks/supportai-tasks/v1/events')
    async def _(req):
        response = {
            'id': '1',
            'created': str(datetime.datetime.now()),
            'project_id': '1',
            'user_login': 'Test',
            'type': req.json.get('type'),
        }

        if 'object_type' in req.json:
            response['object_type'] = req.json['object_type']

        if 'object_id' in req.json:
            response['object_id'] = req.json['object_id']

        if 'object_description' in req.json:
            response['object_description'] = req.json['object_description']

        return mockserver.make_response(status=200, json=response)
