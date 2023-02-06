import datetime
import json

from aiohttp import web
import pytest

from supportai_api.generated.service.swagger.models import api as api_models

# Generated via `tvmknife unittest service -s 222 -d 111`
TEST_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUI3gEQbw:Tc0fid-P9vc-dPS_UEQcQoDtM25vXU'
    '-seEZpTLaLla8WDsG5swfFS46FQilr41TH9XHBgIVoaNC-aNFuuLqdqGB8zifyjig'
    'XReodgtA-Qy5hkJ4qv6dCpmez6bmeMl_wQxVqds35ZxfT1EWyjfHHoalP2EzS-dAem'
    '3V5k_EwBsE'
)


@pytest.fixture(name='simple_dialog_dict')
def gen_simple_dialog_dict():
    return {
        'dialog': {
            'messages': [
                {'text': 'help help help', 'author': 'user'},
                {'text': 'I\'m on my way', 'author': 'support'},
                {'text': 'still need help', 'author': 'user'},
            ],
        },
        'features': [{'key': 'tariff', 'value': 'business'}],
    }


@pytest.fixture(name='simple_dialog')
def gen_simple_dialog_str(simple_dialog_dict):
    return json.dumps(simple_dialog_dict)


@pytest.fixture(name='feedback_dialog')
def gen_feedback_dialog_str(simple_dialog_dict):
    simple_dialog_dict['feedback'] = True
    return json.dumps(simple_dialog_dict)


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai_api_tokens', files=['tokens.sql']),
]


async def test_smoke_support(web_app_client, mockserver, simple_dialog):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler(request):
        assert request.query['simulated'] == 'false'
        assert 'chat_id' in request.json
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )

    response = await web_app_client.post(
        '/supportai-api/v1/support',
        params={'project_id': 'sample_project'},
        headers={'X-Real-IP': '127.0.0.1', 'X-YaTaxi-API-Key': 'XXX'},
        data=simple_dialog,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'reply': {'text': 'hello', 'texts': ['hello']}}


@pytest.mark.config(SUPPORTAI_API_CONTEXT={'projects': 'all'})
async def test_convert_support_response(
        web_app_client, mockserver, simple_dialog, mocked_context,
):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler(request):
        return web.json_response(
            data={
                'reply': {'text': 'hello', 'texts': ['hello']},
                'features': {
                    'probabilities': [{'topic_name': '1', 'probability': 0.9}],
                    'features': [
                        {'key': '1', 'value': '1'},
                        {'key': '2', 'value': None},
                        {'key': '2', 'value': ['1']},
                    ],
                },
                'version': 'version',
            },
        )

    response = await web_app_client.post(
        '/supportai-api/v1/support',
        params={'project_id': 'sample_project'},
        headers={'X-Real-IP': '127.0.0.1', 'X-YaTaxi-API-Key': 'XXX'},
        data=simple_dialog,
    )
    assert response.status == 200
    content = await response.json()

    assert content['reply']['text'] == 'hello'
    assert content['features']['features'] == [{'key': '1', 'value': '1'}]


async def test_disable_auth(web_app_client, simple_dialog, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={'reply': {'text': 'Hello', 'texts': ['Hello']}},
        )

    response = await web_app_client.post(
        '/supportai-api/v1/support',
        params={'project_id': 'project_without_token'},
        headers={'X-Real-IP': '185.39.80.146'},
        data=simple_dialog,
    )
    assert response.status == 200


async def test_smoke_livetex(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def handler(request):
        return web.json_response(
            data={
                'reply': {'text': 'You got it', 'texts': ['You got it']},
                'features': {
                    'most_probable_topic': 'first',
                    'sure_topic': 'first',
                    'probabilities': [
                        {'topic_name': 'first', 'probability': 0.9},
                        {'topic_name': 'second', 'probability': 0.1},
                    ],
                },
            },
        )

    response = await web_app_client.post(
        '/supportai-api/v1/livetex',
        params={'project_id': 'livetex_project'},
        headers={'X-Real-IP': '127.0.0.1', 'X-YaTaxi-API-Key': 'XXX'},
        data=json.dumps(
            {
                'searchText': 'help',
                'visitorId': '79029992330',
                'channelType': 'WhatsAppMfms',
                'conversationId': 'b7c3ef63-4d01-4fa7-a141-8528151115dd',
                'maxButtons': 5,
                'boolProperty': True,
                'incorrect_property1': {'incorrect_sub': 'sub'},
                'incorrect_property2': [],
            },
        ),
    )
    assert response.status == 200
    content = await response.json()
    assert 'sendText' in content
    assert handler.times_called == 1


async def test_smoke_livetex_buttons(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def handler(request):
        return web.json_response(
            data={
                'reply': {'text': 'You got it', 'texts': ['You got it']},
                'features': {
                    'most_probable_topic': 'first',
                    'sure_topic': 'first',
                    'probabilities': [
                        {'topic_name': 'first', 'probability': 0.9},
                        {'topic_name': 'second', 'probability': 0.1},
                    ],
                    'features': [
                        {'key': 'buttons_notice', 'value': 'Text to show.'},
                        {'key': 'buttons_showInput', 'value': True},
                    ],
                },
                'buttons_block': {
                    'buttons': [
                        {
                            'text': '{"type":"textButton","label":"Button label","payload":"smth-data-1","cssClassName":"redButtonClass"}',  # noqa: E501 pylint: disable=line-too-long
                        },
                        {
                            'text': '{"type":"linkButton","url":"http://link.to","newtab":true,"payload":"smth-data-2"}',  # noqa: E501 pylint: disable=line-too-long
                        },
                    ],
                },
            },
        )

    response = await web_app_client.post(
        '/supportai-api/v1/livetex',
        params={'project_id': 'livetex_project'},
        headers={'X-Real-IP': '127.0.0.1', 'X-YaTaxi-API-Key': 'XXX'},
        data=json.dumps(
            {
                'searchText': 'help',
                'visitorId': '79029992330',
                'channelType': 'WhatsAppMfms',
                'conversationId': 'b7c3ef63-4d01-4fa7-a141-8528151115dd',
                'maxButtons': 5,
                'boolProperty': True,
                'incorrect_property1': {'incorrect_sub': 'sub'},
                'incorrect_property2': [],
            },
        ),
    )
    assert response.status == 200
    content = await response.json()
    assert 'sendText' in content
    assert content['notice'] == 'Text to show.'
    assert content['showInput']
    assert len(content['buttons']) == 2
    assert handler.times_called == 1


@pytest.mark.config(
    SUPPORTAI_API_INTERNAL_USERS={
        'users': [
            {
                'tvm_service_name': 'sample_client',
                'project_ids': ['sample_project'],
            },
        ],
    },
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'sample_client', 'dst': 'supportai-api'}],
    TVM_SERVICES={'supportai-api': 111, 'sample_client': 222},
    TVM_API_URL='$mockserver/tvm',
)
@pytest.mark.usefixtures('mocked_tvm')
async def test_smoke_support_internal(
        web_app_client, mockserver, simple_dialog,
):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler(request):
        assert request.query['simulated'] == 'true'
        assert request.query['version'] == 'draft'

        return web.json_response(data={})

    response = await web_app_client.post(
        '/supportai-api/v1/support_internal',
        params={
            'project_id': 'sample_project',
            'simulated': 'true',
            'version': 'draft',
        },
        headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
        data=simple_dialog,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}

    response = await web_app_client.post(
        '/supportai-api/v1/support_internal',
        params={
            'project_id': 'sample_project',
            'simulated': 'true',
            'version': 'draft',
        },
        headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
        data=simple_dialog,
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/supportai-api/v1/support_internal',
        params={
            'project_id': 'sample_project',
            'simulated': 'true',
            'version': 'draft',
        },
        headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
        data=simple_dialog,
    )
    assert response.status == 200


@pytest.mark.config(
    SUPPORTAI_API_INTERNAL_USERS={
        'users': [{'tvm_service_name': 'all_client', 'project_ids': 'any'}],
    },
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'all_client', 'dst': 'supportai-api'}],
    TVM_SERVICES={'supportai-api': 111, 'all_client': 222},
    TVM_API_URL='$mockserver/tvm',
)
@pytest.mark.usefixtures('mocked_tvm')
async def test_support_internal_all_access(
        web_app_client, mockserver, simple_dialog,
):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler(request):
        return web.json_response(data={})

    response = await web_app_client.post(
        '/supportai-api/v1/support_internal',
        params={'project_id': 'sample_project', 'simulated': 'true'},
        headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
        data=simple_dialog,
    )
    assert response.status == 200


async def test_unauthorised_livetex(web_app_client):
    response = await web_app_client.post(
        '/supportai-api/v1/livetex',
        params={'project_id': 'some_project'},
        headers={'X-Real-IP': '127.0.0.1', 'X-YaTaxi-API-Key': 'abcent_token'},
        data=json.dumps(
            {
                'searchText': 'help',
                'visitorId': '79029992330',
                'channelType': 'WhatsAppMfms',
                'conversationId': 'b7c3ef63-4d01-4fa7-a141-8528151115dd',
            },
        ),
    )
    assert response.status == 403


async def test_unauthrozed_support(web_app_client, simple_dialog):
    response = await web_app_client.post(
        '/supportai-api/v1/support',
        params={'project_id': 'unauthrozed_project'},
        headers={'X-Real-IP': '127.0.0.1', 'X-YaTaxi-API-Key': 'XXX'},
        data=simple_dialog,
    )
    assert response.status == 403


async def test_unauthrozed_support_internal(web_app_client, simple_dialog):
    response = await web_app_client.post(
        '/supportai-api/v1/support_internal',
        params={'token': 'XXX', 'project_id': 'sample_project'},
        headers={'X-Real-IP': '127.0.0.1'},
        data=simple_dialog,
    )
    assert response.status == 403


async def test_feedback_request(web_app_client, mockserver, feedback_dialog):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler(request):
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )

    response = await web_app_client.post(
        '/supportai-api/v1/support',
        params={'project_id': 'sample_project'},
        headers={'X-Real-IP': '127.0.0.1', 'X-YaTaxi-API-Key': 'XXX'},
        data=feedback_dialog,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}


@pytest.fixture(name='mocked_context')
def mock_context(mockserver):
    context_storage = {}

    @mockserver.json_handler('/supportai-context/v1/context/dialog')
    # pylint: disable=unused-variable
    async def context_handler(request):
        key = request.query['project_id'] + ':' + request.query['chat_id']
        if request.method == 'GET':
            if key in context_storage:
                return web.json_response(data=context_storage[key])
            return web.json_response(status=204)
        assert False, 'Unsupported method'

    @mockserver.json_handler('/supportai-context/v1/context/record')
    # pylint: disable=unused-variable
    async def context_record_handler(request):
        key = request.query['project_id'] + ':' + request.query['chat_id']

        if request.method == 'POST':

            if key not in context_storage:
                context_storage[key] = {
                    'chat_id': request.query['chat_id'],
                    'created_at': str(datetime.datetime.now()),
                    'dialog': {
                        'messages': [
                            *request.json['request']['dialog']['messages'],
                            *[
                                {'text': text, 'author': 'ai'}
                                for text in request.json['response']
                                .get('reply', {})
                                .get('texts', [])
                            ],
                        ],
                    },
                }

            return web.json_response(status=200)
        assert False, 'Unsupported method'

    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def backend_handler(request):
        reply_text = ' - '.join(
            [
                message['text'] + ':' + message.get('author', 'none')
                for message in request.json['dialog']['messages']
            ],
        )
        return web.json_response(
            data={
                'reply': {'text': reply_text, 'texts': [reply_text]},
                'features': {
                    'most_probable_topic': 'topic1',
                    'sure_topic': 'topic1',
                    'probabilities': [],
                    'features': request.json['features'],
                },
            },
        )

    return context_storage


@pytest.mark.config(SUPPORTAI_API_CONTEXT={'projects': 'all'})
async def test_context_usage(web_app_client, mocked_context):
    response1 = await web_app_client.post(
        '/supportai-api/v1/support',
        params={'project_id': 'sample_project'},
        headers={'X-Real-IP': '127.0.0.1', 'X-YaTaxi-API-Key': 'XXX'},
        json={
            'chat_id': '1',
            'dialog': {'messages': [{'text': 'm1', 'author': 'user'}]},
            'features': [
                {'key': 'feature1', 'value': 'Feature 1'},
                {'key': 'feature2', 'value': 'Feature 2'},
            ],
        },
    )
    assert response1.status == 200
    assert (await response1.json())['reply']['text'] == 'm1:user'

    response2 = await web_app_client.post(
        '/supportai-api/v1/support',
        params={'project_id': 'sample_project'},
        headers={'X-Real-IP': '127.0.0.1', 'X-YaTaxi-API-Key': 'XXX'},
        json={
            'chat_id': '1',
            'dialog': {'messages': [{'text': 'm2', 'author': 'user'}]},
            'features': [
                {'key': 'feature2', 'value': 'new Feature 2'},
                {'key': 'feature3', 'value': 'Feature 3'},
            ],
        },
    )
    assert response2.status == 200
    response_json = await response2.json()
    assert response_json['reply']['text'] == 'm1:user - m1:user:ai - m2:user'

    assert (
        'features' in response_json and 'features' in response_json['features']
    )
    features = response_json['features']['features']

    assert len(features) == 2

    assert features[1]['value'] == 'Feature 3'

    assert features[0]['key'] == 'feature2'
    assert features[0]['value'] == 'new Feature 2'


@pytest.mark.config(
    SUPPORTAI_API_CONTEXT={
        'projects': 'all',
        'projects_settings': [
            {'project_id': 'sample_project', 'dialog_concat_type': 'by_id'},
        ],
    },
)
async def test_context_concat_by_id(web_app_client, mocked_context):
    response = await web_app_client.post(
        '/supportai-api/v1/support',
        params={'project_id': 'sample_project'},
        headers={'X-Real-IP': '127.0.0.1', 'X-YaTaxi-API-Key': 'XXX'},
        json={
            'chat_id': '1',
            'dialog': {
                'messages': [{'id': '1', 'text': 'm1', 'author': 'user'}],
            },
            'features': [],
        },
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json['reply']['text'] == 'm1:user'

    response = await web_app_client.post(
        '/supportai-api/v1/support',
        params={'project_id': 'sample_project'},
        headers={'X-Real-IP': '127.0.0.1', 'X-YaTaxi-API-Key': 'XXX'},
        json={
            'chat_id': '1',
            'dialog': {
                'messages': [
                    {'id': '1', 'text': 'm1', 'author': 'user'},
                    {'text': 'm1:user', 'author': 'ai'},
                    {'id': '2', 'text': 'm2', 'author': 'user'},
                ],
            },
            'features': [],
        },
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json['reply']['text'] == 'm1:user - m1:user:ai - m2:user'

    assert len(mocked_context['sample_project:1']['dialog']['messages']) == 2


@pytest.mark.config(
    SUPPORTAI_API_CONTEXT={
        'projects': 'all',
        'projects_settings': [
            {'project_id': 'sample_project', 'max_text_length': 2},
        ],
    },
)
async def test_context_cut_message(web_app_client, mocked_context):
    response = await web_app_client.post(
        '/supportai-api/v1/support',
        params={'project_id': 'sample_project'},
        headers={'X-Real-IP': '127.0.0.1', 'X-YaTaxi-API-Key': 'XXX'},
        json={
            'chat_id': '1',
            'dialog': {
                'messages': [
                    {'id': '1', 'text': 'some_long_text', 'author': 'user'},
                ],
            },
            'features': [],
        },
    )
    assert response.status == 200

    assert (
        len(
            mocked_context['sample_project:1']['dialog']['messages'][0][
                'text'
            ],
        )
        == 2
    )


@pytest.mark.config(
    SUPPORTAI_API_WIDGET_SETTINGS={
        'projects': [
            {'project_id': 'sample_project', 'source': 'lk.pochta.ru'},
            {'project_id': 'another_project', 'source': 'any'},
        ],
        'access_control_allow_origin_header': 'site.com',
    },
)
async def test_dummy_support_widget(web_app_client, mockserver, simple_dialog):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler(request):
        assert request.query['simulated'] == 'false'
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )

    response = await web_app_client.post(
        '/supportai-api/v1/support_widget?source=lk.pochta.ru',
        params={'project_id': 'sample_project'},
        data=simple_dialog,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'reply': {'text': 'hello', 'texts': ['hello']}}
    assert response.headers['Access-Control-Allow-Origin'] == 'site.com'

    response = await web_app_client.post(
        '/supportai-api/v1/support_widget?source=yandex.ru',
        params={'project_id': 'another_project'},
        data=simple_dialog,
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/supportai-api/v1/support_widget?source=evil.ru',
        params={'project_id': 'sample_project'},
        data=simple_dialog,
    )
    assert response.status == 403


@pytest.mark.config(
    SUPPORTAI_API_INTERNAL_USERS={
        'users': [
            {
                'tvm_service_name': 'sample_client',
                'project_ids': ['sample_project_tvm'],
            },
        ],
    },
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'sample_client', 'dst': 'supportai-api'}],
    TVM_SERVICES={'supportai-api': 111, 'sample_client': 222},
    TVM_API_URL='$mockserver/tvm',
)
@pytest.mark.usefixtures('mocked_tvm')
async def test_internal_api_response(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler(request):
        assert request.query['simulated'] == 'true'
        assert request.query['version'] == 'draft'
        return web.json_response(
            data={
                'reply': {'text': 'hello', 'texts': ['hello']},
                'iteration_number': 1,
                'explanation': {},
                'requested_features': {
                    'features': [{'feature': 'order_id', 'suggestions': []}],
                },
            },
        )

    response = await web_app_client.post(
        '/supportai-api/v1/support_debug',
        params={'project_id': 'sample_project_tvm'},
        headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
        json={
            'chat_id': '2',
            'dialog': {'messages': [{'text': 'hello', 'author': 'user'}]},
            'features': [],
        },
    )
    assert response.status == 200

    content = await response.json()
    assert content == {
        'reply': {'text': 'hello', 'texts': ['hello']},
        'iteration_number': 1,
        'explanation': {},
        'requested_features': {
            'features': [{'feature': 'order_id', 'suggestions': []}],
        },
    }


@pytest.mark.parametrize('is_internal', [False, True])
@pytest.mark.parametrize('tag', ['speak', 'play'])
@pytest.mark.parametrize(
    (
        'direction',
        'is_dial',
        'reply_text',
        'reply_text_is_valid',
        'sai_calls_response_body',
        'sai_calls_client_error',
        'error_status',
    ),
    [
        (None, None, 'some_valid_text', True, 'some/url', None, None),
        (None, None, 'some invalid text', False, None, None, None),
        ('incoming', True, 'some invalid text', False, None, None, None),
        ('incoming', False, 'some invalid text', False, None, None, None),
        ('outgoing', None, 'some invalid text', False, None, None, None),
        (None, None, 'some_valid_text', True, None, True, 400),
        (None, None, 'some_valid_text', True, None, True, 500),
    ],
)
@pytest.mark.config(
    SUPPORTAI_API_INTERNAL_USERS={
        'users': [
            {
                'tvm_service_name': 'sample_client',
                'project_ids': ['some_project'],
            },
        ],
    },
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'sample_client', 'dst': 'supportai-api'}],
    TVM_SERVICES={'supportai-api': 111, 'sample_client': 222},
    TVM_API_URL='$mockserver/tvm',
)
@pytest.mark.usefixtures('mocked_tvm')
async def test_calls_support(
        web_app_client,
        mockserver,
        tag,
        direction,
        is_dial,
        reply_text,
        reply_text_is_valid,
        sai_calls_response_body,
        sai_calls_client_error,
        error_status,
        is_internal,
):
    features_dict = {
        'first_feature': 'first_feature_value',
        'second_feature': 'second_feature_value',
        'phone': '123',
    }
    if direction:
        features_dict['direction'] = direction
        if is_dial:
            features_dict['event_type'] = 'dial'

    user_text = 'some_text'
    url = 'some/url'

    @mockserver.handler(
        f'/supportai-calls/supportai-calls/v1/files'
        f'/audio/{reply_text}/link',
    )
    async def _(_):
        if tag == 'speak' or not reply_text_is_valid:
            assert False
        if sai_calls_client_error:
            return web.json_response(
                status=error_status,
                data={
                    'code': 'some_error_code',
                    'message': 'some error occurred',
                },
            )
        if sai_calls_response_body:
            return web.Response(status=200, body=sai_calls_response_body)
        return web.Response(status=204)

    @mockserver.json_handler(
        '/supportai-calls/supportai-calls/v1/calls/incoming/register',
    )
    async def _(request):
        if not direction == 'incoming' or not is_dial:
            assert False

        assert request.query['project_slug'] == 'some_project'
        assert request.json['chat_id'] == 'some_chat'
        assert request.json['phone'] == '123'
        assert request.json['call_service'] == 'voximplant'
        assert request.json['features'] == [
            {'key': 'first_feature', 'value': 'first_feature_value'},
            {'key': 'second_feature', 'value': 'second_feature_value'},
        ]

        return {}

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        assert request.json['dialog']['messages'][0]['text'] == user_text
        request_features = {
            feature['key']: feature['value']
            for feature in request.json['features']
        }
        for feature_name in ('first_feature', 'second_feature'):
            assert (
                request_features.get(feature_name) == feature_name + '_value'
            )

        return {'reply': {'text': reply_text}, 'tag': {'add': [tag]}}

    request_json = api_models.SupportRequest(
        chat_id='some_chat',
        dialog=api_models.Dialog([api_models.Message(user_text)]),
        features=[
            api_models.RequestFeature(key=key, value=value)
            for key, value in features_dict.items()
        ],
    ).serialize()

    link = (
        '/supportai-api/v1/support/calls_internal?'
        'project_id=some_project&call_service=voximplant'
        if is_internal
        else '/supportai-api/v1/support/calls?project_id=some_project'
    )

    response = await web_app_client.post(
        link,
        headers={
            'X-Ya-Service-Ticket': TEST_SERVICE_TICKET,
            'X-Real-Ip': '1.1.1.1',
        },
        json=request_json,
    )
    assert response.status == 200

    support_response = api_models.SupportResponse.deserialize(
        await response.json(),
    )

    if tag == 'speak':
        assert support_response.reply.text == reply_text

    if tag == 'play':
        if not reply_text_is_valid or sai_calls_client_error:
            assert not support_response.reply.text
            return
        if sai_calls_response_body:
            assert support_response.reply.text == url
        else:
            assert support_response.reply.text == reply_text


@pytest.mark.config(SUPPORTAI_API_CONTEXT={'projects': 'all'})
async def test_creating_preprocessor_features(
        web_app_client, mockserver, mocked_context,
):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={
                'reply': {
                    'text': 'I\'ll try to help you',
                    'texts': ['I\'ll try to help you'],
                },
                'features': {
                    'most_probable_topic': 'first',
                    'sure_topic': 'first',
                    'probabilities': [
                        {'topic_name': 'first', 'probability': 0.9},
                        {'topic_name': 'second', 'probability': 0.1},
                    ],
                },
                'preprocessor_results': [
                    {
                        'spelled_message': 'hello, i have some problems',
                        'normalized_message': 'hello, i have some problem',
                        'translated_message': 'привет, у меня проблемы',
                    },
                ],
            },
        )

    response = await web_app_client.post(
        '/supportai-api/v1/support',
        params={'project_id': 'sample_project'},
        headers={'X-Real-IP': '127.0.0.1', 'X-YaTaxi-API-Key': 'XXX'},
        json={
            'chat_id': '1',
            'dialog': {
                'messages': [
                    {'text': 'Helo, i hav some prablems', 'author': 'user'},
                ],
            },
            'features': [],
        },
    )
    assert response.status == 200
    context_message = mocked_context['sample_project:1']['dialog']['messages'][
        -2
    ]
    print(context_message)

    assert (
        context_message['preprocessor_results']['spelled_message']
        == 'hello, i have some problems'
    )
    assert (
        context_message['preprocessor_results']['normalized_message']
        == 'hello, i have some problem'
    )
    assert (
        context_message['preprocessor_results']['translated_message']
        == 'привет, у меня проблемы'
    )


@pytest.mark.config(SUPPORTAI_API_CONTEXT={'projects': 'all'})
async def test_creating_preprocessor_several_features(
        web_app_client, mockserver, mocked_context,
):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={
                'reply': {
                    'text': 'I\'ll try to help you',
                    'texts': ['I\'ll try to help you'],
                },
                'features': {
                    'most_probable_topic': 'first',
                    'sure_topic': 'first',
                    'probabilities': [
                        {'topic_name': 'first', 'probability': 0.9},
                        {'topic_name': 'second', 'probability': 0.1},
                    ],
                },
                'preprocessor_results': [
                    {
                        'spelled_message': 'hello, i have some problems',
                        'normalized_message': 'hello, i have some problem',
                        'translated_message': 'привет, у меня проблемы',
                    },
                    {
                        'spelled_message': 'I hope that you help me',
                        'normalized_message': 'I hope that you help me',
                        'translated_message': 'Я надеюсь ты мне поможешь',
                    },
                    {
                        'spelled_message': 'please',
                        'normalized_message': 'please',
                        'translated_message': 'пожалуйста',
                    },
                ],
            },
        )

    response = await web_app_client.post(
        '/supportai-api/v1/support',
        params={'project_id': 'sample_project'},
        headers={'X-Real-IP': '127.0.0.1', 'X-YaTaxi-API-Key': 'XXX'},
        json={
            'chat_id': '1',
            'dialog': {
                'messages': [
                    {'text': 'Helo, i hav some prablems', 'author': 'user'},
                    {'text': 'I hope that you help me', 'author': 'user'},
                    {'text': 'please', 'author': 'user'},
                ],
            },
            'features': [],
        },
    )
    assert response.status == 200
    context_messages = mocked_context['sample_project:1']['dialog'][
        'messages'
    ][:-1]
    spelled_messages = '\n'.join(
        msg['preprocessor_results']['spelled_message']
        for msg in context_messages
    )
    normalized_messages = '\n'.join(
        msg['preprocessor_results']['normalized_message']
        for msg in context_messages
    )
    translated_messages = '\n'.join(
        msg['preprocessor_results']['translated_message']
        for msg in context_messages
    )
    assert (
        spelled_messages
        == 'hello, i have some problems\nI hope that you help me\nplease'
    )
    assert (
        normalized_messages
        == 'hello, i have some problem\nI hope that you help me\nplease'
    )
    assert (
        translated_messages
        == 'привет, у меня проблемы\nЯ надеюсь ты мне поможешь\nпожалуйста'
    )
