import datetime

from aiohttp import web
import pytest


SUPPORT_REQUEST_CLS = (
    'generated.clients_libs.supportai.supportai_lib.SupportRequest'
)

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai_api_tokens', files=['tokens.sql']),
    pytest.mark.config(
        SUPPORTAI_API_PROJECT_TO_HANDLER={
            'projects': [
                {
                    'project_id': 'sample_project',
                    'client_name': 'supportai',
                    'handler_name': 'support_v1',
                    'request_class_path': SUPPORT_REQUEST_CLS,
                },
            ],
        },
    ),
]


@pytest.fixture(name='support_request')
def gen_support_request():
    return {
        'chat_id': '1',
        'dialog': {'messages': [{'text': 'm1', 'author': 'user'}]},
        'features': [{'key': 'exp_feature', 'value': 'exp_feature_value'}],
    }


@pytest.fixture(name='support_response')
def gen_support_response():
    return {
        'reply': {'text': 'ai_reply', 'texts': ['ai_reply']},
        'features': {
            'most_probable_topic': 'topic',
            'sure_topic': 'topic',
            'probabilities': [],
        },
    }


@pytest.fixture(name='context_response')
def gen_context_response(support_request, support_response):
    return {
        'chat_id': '1',
        'created_at': str(datetime.datetime.now()),
        'dialog': {
            'messages': [
                {'text': 'm1', 'author': 'user'},
                {'text': 'ai_reply', 'author': 'ai'},
            ],
        },
    }


async def make_support_request(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
):

    if context_response:

        @mockserver.json_handler('/supportai-context/v1/context/dialog')
        # pylint: disable=unused-variable
        async def context_handler(request):
            return web.json_response(data=context_response)

        @mockserver.json_handler('/supportai-context/v1/context/record')
        # pylint: disable=unused-variable
        async def context_record_handler(request):
            return web.json_response(status=200)

    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def backend_handler(request):
        return web.json_response(data=support_response)

    response = await web_app_client.post(
        '/supportai-api/v1/support',
        params={'project_id': 'sample_project'},
        headers={'X-Real-IP': '127.0.0.1', 'X-YaTaxi-API-Key': 'XXX'},
        json=support_request,
    )
    assert response.status == 200

    return await response.json()


@pytest.mark.client_experiments3(
    consumer='supportai-api/sample_project',
    experiment_name='sample',
    args=[
        {
            'name': 'exp_feature',
            'type': 'string',
            'value': 'exp_feature_value',
        },
    ],
    value={'iteration': 2},
)
@pytest.mark.config(
    SUPPORTAI_API_PROJECT_ITERATION_EXPERIMENTS={
        'projects': [
            {
                'project_id': 'sample_project',
                'experiments3_consumer': 'supportai-api/sample_project',
                'experiments3_feature': 'exp_feature',
                'default_iteration': 1,
            },
        ],
    },
    SUPPORTAI_API_CONTEXT={'projects': 'all'},
)
async def test_iter_exp_enabled_resp_not_empty(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
):

    response_json = await make_support_request(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
    )

    assert 'reply' in response_json


@pytest.mark.client_experiments3(
    consumer='supportai-api/sample_project',
    experiment_name='sample',
    args=[
        {
            'name': 'exp_feature',
            'type': 'string',
            'value': 'exp_feature_value',
        },
    ],
    value={'iteration': 1},
)
@pytest.mark.config(
    SUPPORTAI_API_PROJECT_ITERATION_EXPERIMENTS={
        'projects': [
            {
                'project_id': 'sample_project',
                'experiments3_consumer': 'supportai-api/sample_project',
                'experiments3_feature': 'exp_feature',
                'default_iteration': 0,
            },
        ],
    },
    SUPPORTAI_API_CONTEXT={'projects': 'all'},
)
async def test_iter_exp_enabled_resp_empty(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
):
    response_json = await make_support_request(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
    )

    assert 'reply' not in response_json


@pytest.mark.config(
    SUPPORTAI_API_PROJECT_ITERATION_EXPERIMENTS={
        'projects': [{'project_id': 'sample_project', 'default_iteration': 0}],
    },
    SUPPORTAI_API_CONTEXT={'projects': 'all'},
)
async def test_iter_exp_default_iter(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
):
    response_json = await make_support_request(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
    )

    assert 'reply' not in response_json


@pytest.mark.config(
    SUPPORTAI_API_PROJECT_ITERATION_EXPERIMENTS={
        'projects': [
            {'project_id': 'sample_project', 'default_iteration': -1},
        ],
    },
    SUPPORTAI_API_CONTEXT={'projects': 'all'},
)
async def test_iter_exp_default_iter_unlimited(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
):
    response_json = await make_support_request(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
    )

    assert 'reply' in response_json


@pytest.mark.config(
    SUPPORTAI_API_PROJECT_ITERATION_EXPERIMENTS={
        'projects': [{'project_id': 'sample_project', 'default_iteration': 2}],
    },
    SUPPORTAI_API_CONTEXT={'projects': 'none'},
)
async def test_iter_exp_without_context(
        web_app_client, mockserver, support_response,
):
    response_json = await make_support_request(
        web_app_client,
        mockserver,
        support_response=support_response,
        support_request={
            'chat_id': '1',
            'dialog': {
                'messages': [
                    {'text': 'm1', 'author': 'user'},
                    {'text': 'm1-resp', 'author': 'ai'},
                    {'text': 'm2', 'author': 'user'},
                ],
            },
            'features': [{'key': 'exp_feature', 'value': 'exp_feature_value'}],
        },
        context_response=None,
    )

    assert 'reply' in response_json


@pytest.mark.client_experiments3(
    consumer='supportai-api/not_sample_project',
    experiment_name='sample',
    args=[
        {
            'name': 'exp_feature',
            'type': 'string',
            'value': 'exp_feature_value',
        },
    ],
    value={'iteration': 2},
)
@pytest.mark.config(
    SUPPORTAI_API_PROJECT_ITERATION_EXPERIMENTS={
        'projects': [
            {
                'project_id': 'sample_project',
                'experiments3_consumer': 'supportai-api/sample_project',
                'experiments3_feature': 'exp_feature',
                'default_iteration': 1,
            },
        ],
    },
    SUPPORTAI_API_CONTEXT={'projects': 'all'},
)
async def test_no_experiment_project(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
):
    response_json = await make_support_request(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
    )

    assert 'reply' not in response_json


@pytest.mark.client_experiments3(
    consumer='supportai-api/sample_project',
    experiment_name='sample',
    args=[
        {
            'name': 'exp_feature',
            'type': 'string',
            'value': 'exp_feature_value',
        },
    ],
    value={'iteration': 2},
)
@pytest.mark.config(
    SUPPORTAI_API_PROJECT_ITERATION_EXPERIMENTS={
        'projects': [
            {
                'project_id': 'sample_project',
                'experiments3_consumer': 'supportai-api/sample_project',
                'experiments3_feature': 'exp_feature',
                'default_iteration': 1,
            },
        ],
    },
    SUPPORTAI_API_CONTEXT={'projects': 'all'},
)
async def test_no_experiment_feature(
        web_app_client, mockserver, support_response,
):
    response_json = await make_support_request(
        web_app_client,
        mockserver,
        support_request={
            'chat_id': '1',
            'dialog': {'messages': [{'text': 'm1', 'author': 'user'}]},
            'features': [
                {'key': 'not_exp_feature', 'value': 'exp_feature_value'},
            ],
        },
        support_response={'features': {'probabilities': []}},
        context_response={
            'chat_id': '1',
            'created_at': str(datetime.datetime.now()),
            'dialog': {'messages': [{'text': 'm1', 'author': 'user'}]},
        },
    )

    assert 'reply' not in response_json


@pytest.mark.client_experiments3(
    consumer='supportai-api/sample_project',
    experiment_name='sample',
    args=[
        {
            'name': 'exp_feature',
            'type': 'string',
            'value': 'exp_feature_value',
        },
    ],
    value={'available': True},
)
@pytest.mark.config(
    SUPPORTAI_API_PROJECT_TOPIC_EXPERIMENTS={
        'projects': [
            {
                'project_id': 'sample_project',
                'experiment_topics': [
                    {
                        'topic': 'topic',
                        'experiments3_consumer': (
                            'supportai-api/sample_project'
                        ),
                        'experiments3_feature': 'exp_feature',
                        'default_availability': False,
                    },
                ],
            },
        ],
    },
    SUPPORTAI_API_CONTEXT={'projects': 'all'},
)
async def test_topic_exp_enabled_resp_not_empty(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
):

    response_json = await make_support_request(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
    )

    assert 'reply' in response_json


@pytest.mark.client_experiments3(
    consumer='supportai-api/sample_project',
    experiment_name='sample',
    args=[
        {
            'name': 'exp_feature',
            'type': 'string',
            'value': 'exp_feature_value',
        },
    ],
    value={'available': False},
)
@pytest.mark.config(
    SUPPORTAI_API_PROJECT_TOPIC_EXPERIMENTS={
        'projects': [
            {
                'project_id': 'sample_project',
                'experiment_topics': [
                    {
                        'topic': 'topic',
                        'experiments3_consumer': (
                            'supportai-api/sample_project'
                        ),
                        'experiments3_feature': 'exp_feature',
                        'default_availability': True,
                    },
                ],
            },
        ],
    },
    SUPPORTAI_API_CONTEXT={'projects': 'all'},
)
async def test_topic_exp_enabled_resp_empty(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
):
    response_json = await make_support_request(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
    )

    assert 'reply' not in response_json


@pytest.mark.config(
    SUPPORTAI_API_PROJECT_TOPIC_EXPERIMENTS={
        'projects': [
            {
                'project_id': 'sample_project',
                'experiment_topics': [
                    {'topic': 'topic', 'default_availability': False},
                ],
            },
        ],
    },
    SUPPORTAI_API_CONTEXT={'projects': 'all'},
)
async def test_topic_exp_default_iter(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
):
    response_json = await make_support_request(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
    )

    assert 'reply' not in response_json


@pytest.mark.config(
    SUPPORTAI_API_PROJECT_TOPIC_EXPERIMENTS={
        'projects': [
            {
                'project_id': 'sample_project',
                'experiment_topics': [
                    {'topic': 'another_topic', 'default_availability': False},
                ],
            },
        ],
    },
    SUPPORTAI_API_CONTEXT={'projects': 'all'},
)
async def test_topic_exp_not_in_project(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
):
    response_json = await make_support_request(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
    )

    assert 'reply' in response_json


@pytest.mark.config(
    SUPPORTAI_API_PROJECT_TOPIC_EXPERIMENTS={'projects': []},
    SUPPORTAI_API_CONTEXT={'projects': 'all'},
)
async def test_project_not_in_topic_experiment(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
):
    response_json = await make_support_request(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
    )

    assert 'reply' in response_json


@pytest.mark.now('2019-01-01T12:00:00+0000')
@pytest.mark.client_experiments3(
    consumer='supportai-api/sample_project',
    experiment_name='control',
    args=[
        {
            'name': 'control_exp',
            'type': 'string',
            'value': 'exp_feature_value',
        },
    ],
    value={'in_control': False},
)
@pytest.mark.config(
    SUPPORTAI_API_PROJECT_CONTROL_EXPERIMENTS={
        'projects': [
            {
                'project_id': 'sample_project',
                'experiments3_consumer': 'supportai-api/sample_project',
                'experiments3_feature': 'control_exp',
                'experiment3_value': 'in_control',
                'target_feature_name': 'exp_feature',
                'control_tag': 'IN_CONTROL',
            },
        ],
    },
    SUPPORTAI_API_CONTEXT={'projects': 'all'},
)
async def test_project_control_experiment_false(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
):
    response_json = await make_support_request(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
    )

    assert 'reply' in response_json


@pytest.mark.now('2019-01-01T12:00:00+0000')
@pytest.mark.client_experiments3(
    consumer='supportai-api/sample_project',
    experiment_name='control',
    args=[
        {
            'name': 'control_exp',
            'type': 'string',
            'value': '01-2019-exp_feature_value',
        },
    ],
    value={'in_control': True},
)
@pytest.mark.config(
    SUPPORTAI_API_PROJECT_CONTROL_EXPERIMENTS={
        'projects': [
            {
                'project_id': 'sample_project',
                'experiments3_consumer': 'supportai-api/sample_project',
                'experiments3_feature': 'control_exp',
                'experiment3_value': 'in_control',
                'target_feature_name': 'exp_feature',
                'control_tag': 'IN_CONTROL',
                'add_date': True,
            },
        ],
    },
    SUPPORTAI_API_CONTEXT={'projects': 'all'},
)
async def test_project_control_experiment_true(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
):
    response_json = await make_support_request(
        web_app_client,
        mockserver,
        support_request,
        support_response,
        context_response,
    )

    assert 'reply' not in response_json
    assert 'tag' in response_json
    assert 'IN_CONTROL' in response_json['tag']['add']
