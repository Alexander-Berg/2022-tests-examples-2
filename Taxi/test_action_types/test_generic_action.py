import json

import aiohttp
import pytest

from supportai_actions.action_types import generic_action
from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import params as params_module
from supportai_actions.actions import state as state_module


@pytest.mark.parametrize(
    '_call_param',
    [
        pytest.param(
            [
                params_module.ActionParam({'url': 'http://testurl.com'}),
                params_module.ActionParam({'method': 'GET'}),
                params_module.ActionParam(
                    {'headers': {'some_header': 'some_header'}},
                ),
                params_module.ActionParam(
                    {'query_params': {'some_query_param': 'some_query_param'}},
                ),
                params_module.ActionParam(
                    {'body': {'some_body_param': 'some_body_param'}},
                ),
                params_module.ActionParam(
                    {'featured_query_params': {'some_param': 'some_param'}},
                ),
                params_module.ActionParam(
                    {'featured_body': {'some_param': 'some_param'}},
                ),
                params_module.ActionParam(
                    {
                        'response_mapping': [
                            {'feature_name': 'some_param', 'json_path': '$'},
                        ],
                    },
                ),
                params_module.ActionParam({'timeout_s': 300}),
                params_module.ActionParam({'retries': 5}),
                params_module.ActionParam({'backoff_factor': 2}),
                params_module.ActionParam(
                    {'basic_auth': {'login': 'some_login'}},
                ),
            ],
        ),
        pytest.param(
            [
                params_module.ActionParam({'url': 'http://www.testurl.com'}),
                params_module.ActionParam({'method': 'POST'}),
                params_module.ActionParam({'headers': {}}),
                params_module.ActionParam({'query_params': {}}),
                params_module.ActionParam({'body': {}}),
                params_module.ActionParam({'featured_query_params': {}}),
                params_module.ActionParam({'featured_body': {}}),
                params_module.ActionParam({'response_mapping': []}),
                params_module.ActionParam({'body_format': 'json'}),
            ],
        ),
        pytest.param(
            [
                params_module.ActionParam({'url': 'http://www.testurl.com'}),
                params_module.ActionParam({'method': 'POST'}),
                params_module.ActionParam({'body': '<a></a>'}),
                params_module.ActionParam({'response_mapping': []}),
                params_module.ActionParam({'body_format': 'xml'}),
            ],
        ),
        pytest.param(
            [
                params_module.ActionParam({'url': 'http://www.testurl.com'}),
                params_module.ActionParam({'method': 'POST'}),
                params_module.ActionParam({'body': '<a></a>'}),
                params_module.ActionParam({'featured_body': {}}),
                params_module.ActionParam({'response_mapping': []}),
                params_module.ActionParam({'body_format': 'xml'}),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam({'url': 'http://testurl.com'}),
                params_module.ActionParam({'method': 'GET'}),
            ],
        ),
        pytest.param(
            [
                params_module.ActionParam({'url': 'jnkjxnvk'}),
                params_module.ActionParam({'method': 'GET'}),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [params_module.ActionParam({'url': 'http://testurl.com'})],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [params_module.ActionParam({'method': 'GET'})],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam({'url': 'http://testurl.com'}),
                params_module.ActionParam({'method': 'GET'}),
                params_module.ActionParam({'headers': 'headers'}),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam({'url': 'http://testurl.com'}),
                params_module.ActionParam({'method': 'GET'}),
                params_module.ActionParam({'query_params': 'query_params'}),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam({'url': 'http://testurl.com'}),
                params_module.ActionParam({'method': 'GET'}),
                params_module.ActionParam({'body': 'body_params'}),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam({'url': 'http://testurl.com'}),
                params_module.ActionParam({'method': 'GET'}),
                params_module.ActionParam({'timeout_s': '300'}),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam({'url': 'http://testurl.com'}),
                params_module.ActionParam({'method': 'GET'}),
                params_module.ActionParam({'retries': '5'}),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam({'url': 'http://testurl.com'}),
                params_module.ActionParam({'method': 'GET'}),
                params_module.ActionParam({'backoff_factor': '2'}),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam({'url': 'http://testurl.com'}),
                params_module.ActionParam({'method': 'GET'}),
                params_module.ActionParam({'basic_auth': {}}),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
    ],
)
async def test_validate(_call_param):
    generic_action.GenericAction('echo', 'echo', '0', _call_param)


@pytest.mark.parametrize(
    'state, _call_param',
    [
        pytest.param(
            state_module.State(features=feature_module.Features(features=[])),
            [
                params_module.ActionParam({'url': 'http://testurl.com'}),
                params_module.ActionParam({'method': 'GET'}),
                params_module.ActionParam({'featured_query_params': {}}),
                params_module.ActionParam({'featured_body': {}}),
            ],
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'a', 'value': 'b'},
                        {'key': 'c', 'value': 'd'},
                    ],
                ),
            ),
            [
                params_module.ActionParam({'url': 'http://testurl.com'}),
                params_module.ActionParam({'method': 'GET'}),
                params_module.ActionParam({'featured_query_params': {}}),
                params_module.ActionParam({'featured_body': {}}),
            ],
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'a', 'value': 'b'},
                        {'key': 'c', 'value': 'd'},
                    ],
                ),
            ),
            [
                params_module.ActionParam({'url': 'http://testurl.com'}),
                params_module.ActionParam({'method': 'GET'}),
                params_module.ActionParam(
                    {'featured_query_params': {'val1': 'a', 'val2': 'c'}},
                ),
                params_module.ActionParam({'featured_body': {}}),
            ],
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'a', 'value': 'b'},
                        {'key': 'c', 'value': 'd'},
                    ],
                ),
            ),
            [
                params_module.ActionParam({'url': 'http://testurl.com'}),
                params_module.ActionParam({'method': 'GET'}),
                params_module.ActionParam({'featured_query_params': {}}),
                params_module.ActionParam(
                    {'featured_body': {'val1': 'a', 'val2': 'c'}},
                ),
            ],
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'a', 'value': 'b'},
                        {'key': 'c', 'value': 'd'},
                    ],
                ),
            ),
            [
                params_module.ActionParam({'url': 'http://testurl.com'}),
                params_module.ActionParam({'method': 'GET'}),
                params_module.ActionParam(
                    {'featured_query_params': {'val1': 'a'}},
                ),
                params_module.ActionParam({'featured_body': {'val2': 'c'}}),
            ],
        ),
        pytest.param(
            state_module.State(features=feature_module.Features(features=[])),
            [
                params_module.ActionParam({'url': 'http://testurl.com'}),
                params_module.ActionParam({'method': 'GET'}),
                params_module.ActionParam(
                    {'featured_query_params': {'val1': 'a', 'val2': 'c'}},
                ),
                params_module.ActionParam({'featured_body': {}}),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationStateError, strict=True,
            ),
        ),
        pytest.param(
            state_module.State(features=feature_module.Features(features=[])),
            [
                params_module.ActionParam({'url': 'http://testurl.com'}),
                params_module.ActionParam({'method': 'GET'}),
                params_module.ActionParam({'featured_query_params': {}}),
                params_module.ActionParam(
                    {'featured_body': {'val1': 'a', 'val2': 'c'}},
                ),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationStateError, strict=True,
            ),
        ),
        pytest.param(
            state_module.State(features=feature_module.Features(features=[])),
            [
                params_module.ActionParam({'url': 'http://testurl.com'}),
                params_module.ActionParam({'method': 'GET'}),
                params_module.ActionParam(
                    {'featured_query_params': {'val1': 'a'}},
                ),
                params_module.ActionParam({'featured_body': {'val1': 'c'}}),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationStateError, strict=True,
            ),
        ),
    ],
)
async def test_validate_state(state, _call_param):
    action = generic_action.GenericAction('echo', 'echo', '0', _call_param)
    action.validate_state(state)


@pytest.fixture(name='mock_service', autouse=True)
def _mock_service(monkeypatch, response_mock):
    def request(**kwargs):
        url = kwargs.get('url')
        data = kwargs['data']
        content_type = None
        if isinstance(data, aiohttp.Payload):
            content_type = kwargs['data'].headers['Content-Type']
        elif isinstance(data, dict):
            content_type = 'form-data'

        class JsonRequestContextManager:
            async def __aenter__(self):
                return response_mock(
                    status=200 if '200' in url else 500,
                    json={
                        'test_data_1': 'test_data',
                        'test_data_2': 'test_data',
                        'test_data_3': 'test_data',
                        'test_data_list': ['first_list_item', None],
                        'test_data_objects_list': [
                            {'key': None},
                            {'key': 'value'},
                            {'other_key': 'other_value'},
                        ],
                        'test_data_objects_nested_list': [
                            {'a': {'b': 1}},
                            {'a': {'c': 2}},
                            None,
                            {'a': None},
                        ],
                        'test_data_irregular': [
                            [{'a': '1_1'}, {'a': '1_2'}, {}],
                            [{'a': '2_1'}, {'a': None}, {'b': '2'}],
                            {'something': 'something else'},
                        ],
                    },
                )

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        class XmlRequestContextManager:
            async def __aenter__(self):
                body = (
                    b'<body>'
                    b'<key>obj_value</key>'
                    b'<item>value_one</item>'
                    b'<item attribute="attr_two">value_two</item>'
                    b'<item attribute="attr_three">value_three</item>'
                    b'<item attribute="attr_four"></item>'
                    b'<inner_object>'
                    b'lal<item>inner_value_one</item>lol'
                    b'</inner_object>'
                    b'<inner><a></a><b><c>teeext</c></b></inner>'
                    b'</body>'
                )
                return response_mock(
                    status=200 if '200' in url else 500, text=body,
                )

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        if content_type == 'application/json':
            return JsonRequestContextManager()
        if content_type == 'form-data':
            assert data == {
                'some_body_param': 'some_body_param',
                'some_param_2': 'b',
            }
            return JsonRequestContextManager()
        if content_type == 'application/xml':
            assert (
                kwargs['data']._value  # pylint: disable=protected-access
                == (
                    b'<body>'
                    b'<constant_value>just_value</constant_value>'
                    b'<feature attr=attr_value>feature_value</feature>'
                    b'</body>'
                )
            )
            return XmlRequestContextManager()
        raise ValueError(f'Unknown content-type: {content_type}')

    monkeypatch.setattr(aiohttp, 'request', request)


@pytest.mark.parametrize(
    'state, _call_param',
    [
        pytest.param(
            state_module.State(features=feature_module.Features(features=[])),
            [
                params_module.ActionParam({'url': 'http://localhost/500'}),
                params_module.ActionParam({'method': 'GET'}),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ActionException, strict=True,
            ),
        ),
        pytest.param(
            state_module.State(features=feature_module.Features(features=[])),
            [
                params_module.ActionParam({'url': 'http://localhost/500'}),
                params_module.ActionParam({'method': 'POST'}),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ActionException, strict=True,
            ),
        ),
    ],
)
async def test_call_500(web_context, _call_param, state):
    action = generic_action.GenericAction('echo', 'echo', '0', _call_param)
    await action(web_context, state)


@pytest.mark.parametrize(
    'state, _call_param',
    [
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'some_param_1', 'value': 'a'},
                        {'key': 'some_param_2', 'value': 'b'},
                        {'key': 'some_param_3', 'value': 'c'},
                        {'key': 'code', 'value': '200'},
                    ],
                ),
            ),
            [
                params_module.ActionParam({'url': 'http://localhost/{code}'}),
                params_module.ActionParam({'method': 'POST'}),
                params_module.ActionParam(
                    {'headers': {'some_header': 'some_header'}},
                ),
                params_module.ActionParam(
                    {'body': {'some_body_param': 'some_body_param'}},
                ),
                params_module.ActionParam(
                    {'featured_body': {'some_param_2': 'some_param_2'}},
                ),
                params_module.ActionParam(
                    {
                        'response_mapping': [
                            {
                                'feature_name': 'test_data_1',
                                'json_path': '$.test_data_1',
                            },
                            {
                                'feature_name': 'test_data_4',
                                'json_path': '$.test_data_4',
                            },
                            {
                                'feature_name': 'test_data_list',
                                'json_path': '$.test_data_list',
                            },
                            {
                                'feature_name': 'test_data_list_with_null',
                                'json_path': 'keep_null#$.test_data_list',
                            },
                            {
                                'feature_name': 'values_from_objects_list',
                                'json_path': (
                                    'all#$.test_data_objects_list[*].key'
                                ),
                            },
                            {
                                'feature_name': (
                                    'values_from_objects_list_with_null'
                                ),
                                'json_path': (
                                    'all&keep_null#'
                                    '$.test_data_objects_list[*].key'
                                ),
                            },
                            {
                                'feature_name': 'values_from_nested_list',
                                'json_path': (
                                    'all#'
                                    '$.test_data_objects_nested_list[*].a.b'
                                ),
                            },
                            {
                                'feature_name': (
                                    'values_from_nested_list_with_null'
                                ),
                                'json_path': (
                                    'all&keep_null#'
                                    '$.test_data_objects_nested_list[*].a.b'
                                ),
                            },
                            {
                                'feature_name': 'values_from_irregular',
                                'json_path': (
                                    'all&keep_null#'
                                    '$.test_data_irregular[*][*].a'
                                ),
                            },
                        ],
                    },
                ),
                params_module.ActionParam({'timeout_s': 300}),
                params_module.ActionParam({'retries': 5}),
                params_module.ActionParam({'backoff_factor': 2}),
                params_module.ActionParam(
                    {'basic_auth': {'login': 'some_login'}},
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize('body_format', ['json', 'form-data'])
async def test_call_200_json_and_form_data(
        web_context, _call_param, state, mock_service, body_format,
):
    call_params = _call_param + [
        params_module.ActionParam({'body_format': body_format}),
    ]
    action = generic_action.GenericAction('echo', 'echo', '0', call_params)
    new_state = await action(web_context, state)

    feature_key_to_expected_value = {
        'test_data_1': 'test_data',
        'test_data_list': ['first_list_item'],
        'test_data_list_with_null': ['first_list_item', ''],
        'values_from_objects_list': ['value'],
        'values_from_objects_list_with_null': ['', 'value', ''],
        'values_from_nested_list': [1],
        'values_from_nested_list_with_null': [1, '', '', ''],
        'values_from_irregular': ['1_1', '1_2', '', '2_1', '', '', ''],
        'test_data_4': None,
    }

    response_body = new_state.features.get('__DEBUG_INFO__')
    assert response_body is not None
    assert isinstance(response_body, str)
    response_json = json.loads(response_body)
    assert 'test_data_objects_nested_list' in response_json

    for feature_key, expected_value in feature_key_to_expected_value.items():
        assert (
            new_state.features.get(feature_key, 'sentinel-like')
            == expected_value
        )


async def test_call_200_xml(web_context, mock_service):
    call_params = {
        'url': 'http://localhost/{code}',
        'method': 'POST',
        'headers': {'some_header': 'some_header'},
        'body': (
            '<body>'
            '<constant_value>just_value</constant_value>'
            '<feature attr=attr_value>feature_value</feature>'
            '</body>'
        ),
        'response_mapping': [
            {'feature_name': 'just_key', 'xpath': 'key'},
            {'feature_name': 'first_item', 'xpath': 'item'},
            {'feature_name': 'all_items', 'xpath': 'all#item'},
            {
                'feature_name': 'first_item_with_attribute',
                'xpath': 'item[@attribute]',
            },
            {
                'feature_name': 'items_with_attribute',
                'xpath': 'all#item[@attribute]',
            },
            {
                'feature_name': 'items_with_attribute_two',
                'xpath': 'all#item[@attribute="attr_two"]',
            },
            {'feature_name': 'items_with_null', 'xpath': 'keep_null&all#item'},
            {'feature_name': 'inner_object', 'xpath': 'inner_object'},
            {
                'feature_name': 'inner_object_full',
                'xpath': 'full_text#inner_object',
            },
            {'feature_name': 'inner_item', 'xpath': 'inner_object/item'},
            {
                'feature_name': 'first_item_attribute_value',
                'xpath': 'item->attribute',
            },
            {
                'feature_name': 'all_item_attribute_values',
                'xpath': 'all#item->attribute',
            },
            {
                'feature_name': 'all_item_attribute_values_with_nulls',
                'xpath': 'all&keep_null#item->attribute',
            },
            {
                'feature_name': 'full_text_but_no_text',
                'xpath': 'full_text#inner',
            },
        ],
        'timeout_s': 300,
        'retries': 5,
        'backoff_factor': 2,
        'basic_auth': {'login': 'some_login'},
        'body_format': 'xml',
    }
    state = state_module.State(
        features=feature_module.Features([{'key': 'code', 'value': '200'}]),
    )

    action = generic_action.GenericAction(
        'echo', 'echo', '0', [params_module.ActionParam(call_params)],
    )
    new_state = await action(web_context, state)
    feature_key_to_expected_value = {
        'just_key': 'obj_value',
        'first_item': 'value_one',
        'all_items': ['value_one', 'value_two', 'value_three'],
        'first_item_with_attribute': 'value_two',
        'items_with_attribute': ['value_two', 'value_three'],
        'items_with_attribute_two': ['value_two'],
        'items_with_null': ['value_one', 'value_two', 'value_three', ''],
        'inner_object': 'lal',
        'inner_object_full': 'lallol',
        'inner_item': 'inner_value_one',
        'first_item_attribute_value': None,
        'all_item_attribute_values': ['attr_two', 'attr_three', 'attr_four'],
        'all_item_attribute_values_with_nulls': [
            '',
            'attr_two',
            'attr_three',
            'attr_four',
        ],
        'full_text_but_no_text': None,
    }

    response_body = new_state.features.get('__DEBUG_INFO__')
    assert response_body is not None
    assert isinstance(response_body, str)

    for feature_key, expected_value in feature_key_to_expected_value.items():
        assert (
            new_state.features.get(feature_key, 'sentinel-like')
            == expected_value
        ), feature_key
