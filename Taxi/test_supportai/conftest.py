# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import datetime
# https://github.com/spulec/freezegun/issues/98

import pandas  # noqa: F401
import pytest

# pylint: disable=redefined-outer-name
import supportai.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from supportai.common import configuration  # noqa: E402, I100


pytest_plugins = ['supportai.generated.service.pytest_plugins']


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'disable_standard_auth: disable standard auth from supportai-tasks',
    )
    config.addinivalue_line(
        'markers', 'supportai_actions: mock response of supportai-actions',
    )
    config.addinivalue_line('markers', 'core_flags')


@pytest.fixture(autouse=True, name='standard_auth')
def mock_supportai_tasks(request, mockserver):
    @mockserver.json_handler('/supportai-tasks/v1/authentication/token/check')
    async def _(_):
        return mockserver.make_response(status=200)

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


@pytest.fixture(autouse=True)
def mock_supportai_actions(request, mockserver):
    marks = request.node.iter_markers(name='supportai_actions')

    if not marks:
        return

    mock = {}

    for mark in marks:
        action_id = mark.kwargs.get('action_id')
        version = mark.kwargs.get('version')
        version = str(version)
        response = mark.kwargs.get('response')
        status = mark.kwargs.get('status')

        if not action_id or not version:
            continue

        if not status:
            status = 200

        if not response:
            response = {}

        if action_id in mock:
            mock_actions = mock[action_id]
        else:
            mock_actions = mock[action_id] = {}

        mock_actions[version] = {'status': status, 'response': response}

    @mockserver.json_handler('/supportai-actions/supportai-actions/v1/action')
    async def _(req):
        _action_id = req.query['action_id']
        _version = req.query['version']
        if _action_id not in mock or _version not in mock[_action_id]:
            return mockserver.make_response(status=404)

        return mockserver.make_response(
            status=mock[_action_id][_version]['status'],
            json=mock[_action_id][_version]['response'],
        )


@pytest.fixture(name='core_flags', scope='function')
def _core_flags(request):
    marks = request.node.iter_markers(name='core_flags')

    if not marks:
        return configuration.CoreFlags()

    flags = {}
    for mark in marks:
        flags.update(mark.kwargs)

    return configuration.CoreFlags(**flags)


@pytest.fixture(autouse=True)
def mock_supportai_models(mockserver):
    @mockserver.json_handler(
        '/supportai-models/internal/supportai-models/v1/shard_id',
    )
    async def _(request):
        return mockserver.make_response(status=200, json={'shard_id': 'alpha'})


@pytest.fixture(autouse=True)
def mock_supportai_ref_phrases(mockserver):
    @mockserver.json_handler(
        '/supportai-reference-phrases/supportai-reference-phrases/v1/apply-new-version',  # noqa pylint: disable=line-too-long
    )
    async def _(request):
        return mockserver.make_response(status=200)


@pytest.fixture(autouse=True)
def mock_model_info_by_slugs_versions(
        mockserver,
):  # noqa pylint: disable=C0103
    @mockserver.json_handler(
        '/supportai-models/internal/supportai-models/v1/model_info_by_slugs_versions',  # noqa pylint: disable=line-too-long
    )
    async def _(_):
        return mockserver.make_response(
            status=200,
            json={
                'models': [
                    {
                        'id': '5',
                        'title': 'Тестовая модель',
                        'slug': 'model_test',
                        'version': '1',
                        'type': 'one_message_text_classification',
                        'preprocess_type': 'one_message',
                        'language': 'ru',
                        'model_arch': 'sentence_bert',
                    },
                ],
            },
        )
