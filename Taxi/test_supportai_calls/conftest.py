#  pylint: disable=protected-access
import datetime

import pytest

import supportai_calls.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['supportai_calls.generated.service.pytest_plugins']


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'disable_standard_auth: disable standard auth from supportai-tasks',
    )


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


@pytest.fixture(name='calls_statistics_batches')
def _get_batches():
    return []


@pytest.fixture(name='mock_calls_statistics')
def _mock_statistics(calls_statistics_batches, mockserver):
    @mockserver.json_handler(
        '/supportai-statistics/supportai-statistics/v1/calls_statistics',
    )
    async def _statistics_handle(request):
        calls_statistics_batches.append(request.json.get('records'))
        return {}
