import pytest

from supportai_actions.action_types import send_mail
from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import params as params_module
from supportai_actions.actions import state as state_module


@pytest.mark.parametrize(
    '_call_param',
    [
        pytest.param(
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [params_module.ActionParam({'to_emails': ['test@test.com']})],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [params_module.ActionParam({'message': 'some_message'})],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam({'message': 'some_message'}),
            ],
        ),
        pytest.param(
            [
                params_module.ActionParam(
                    {'to_emails': ['test@test.com', 'teasddom']},
                ),
                params_module.ActionParam({'message': 'some_message'}),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam({'message': 123}),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam({'message': 'some_message'}),
                params_module.ActionParam(
                    {'default_args': {'test_arg': 'test_arg'}},
                ),
            ],
        ),
        pytest.param(
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam({'message': 'some_message'}),
                params_module.ActionParam({'default_args': 'test_arg'}),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam({'message': 'some_message'}),
                params_module.ActionParam(
                    {
                        'attachments': [
                            {
                                'filename': 'test_name',
                                'mime_type': 'image/jpeg',
                                'data': 'base64data',
                            },
                        ],
                    },
                ),
            ],
        ),
        pytest.param(
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam({'message': 'some_message'}),
                params_module.ActionParam(
                    {
                        'attachments': [
                            {'mime_type': 'image/jpeg'},
                            {'data': 'base64data'},
                        ],
                    },
                ),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam({'message': 'some_message'}),
                params_module.ActionParam(
                    {
                        'attachments': [
                            {'filename': 'test_name'},
                            {'data': 'base64data'},
                        ],
                    },
                ),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam({'message': 'some_message'}),
                params_module.ActionParam(
                    {
                        'attachments': [
                            {'filename': 'test_name'},
                            {'mime_type': 'image/jpeg'},
                        ],
                    },
                ),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam({'message': 'some_message'}),
                params_module.ActionParam({'attachments': 'asdasdasd'}),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam({'message': 'some_message'}),
                params_module.ActionParam(
                    {'headers': {'test_header': 'test_headers'}},
                ),
            ],
        ),
        pytest.param(
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam({'message': 'some_message'}),
                params_module.ActionParam({'headers': 'test_headers'}),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam({'message': 'some_message'}),
                params_module.ActionParam({'from_email': 'test@test.com'}),
            ],
        ),
        pytest.param(
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam({'message': 'some_message'}),
                params_module.ActionParam({'from_email': 'tesom'}),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam({'message': 'some_message'}),
                params_module.ActionParam({'from_name': 12345}),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam({'message': 'some_message'}),
                params_module.ActionParam({'from_name': 'test_name'}),
            ],
        ),
    ],
)
async def test_validate(_call_param):
    send_mail.SendMail('echo', 'echo', '0', _call_param)


@pytest.mark.parametrize(
    'state, _call_param',
    [
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'arg1', 'value': 'arg1'},
                        {'key': 'arg2', 'value': 'arg2'},
                        {'key': 'arg3', 'value': 'arg3'},
                    ],
                ),
            ),
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam(
                    {
                        'message': (
                            'Hey! Here are some features: '
                            '{arg1}, {arg2}, {arg3}'
                        ),
                    },
                ),
            ],
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'arg1', 'value': 'arg1'},
                        {'key': 'arg2', 'value': 'arg2'},
                        {'key': 'arg3', 'value': 'arg3'},
                    ],
                ),
            ),
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam(
                    {
                        'message': (
                            'Hey! Here are some features: ' 'arg1, arg2, arg3'
                        ),
                    },
                ),
            ],
        ),
        pytest.param(
            state_module.State(features=feature_module.Features(features=[])),
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam(
                    {
                        'message': (
                            'Hey! Here are some features: ' 'arg1, arg2, arg3'
                        ),
                    },
                ),
            ],
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'arg2', 'value': 'arg2'},
                        {'key': 'arg3', 'value': 'arg3'},
                    ],
                ),
            ),
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam(
                    {
                        'message': (
                            'Hey! Here are some features: '
                            '{arg1}, {arg2}, {arg3}'
                        ),
                    },
                ),
                params_module.ActionParam(
                    {
                        'default_args': {
                            'arg1': 'arg1',
                            'arg2': 'arg4',
                            'arg3': 'arg5',
                        },
                    },
                ),
            ],
        ),
    ],
)
def test_get_message_text(state, _call_param):
    action = send_mail.SendMail('echo', 'echo', '0', _call_param)
    message_text = action.get_message_text(state)
    assert message_text == 'Hey! Here are some features: arg1, arg2, arg3'


@pytest.mark.parametrize(
    'state, _call_param',
    [
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'arg1', 'value': 'arg1'},
                        {'key': 'arg2', 'value': 'arg2'},
                        {'key': 'arg3', 'value': 'arg3'},
                    ],
                ),
            ),
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam(
                    {
                        'message': (
                            'Hey! Here are some features: '
                            '{arg1}, {arg2}, {arg3}'
                        ),
                    },
                ),
            ],
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'arg1', 'value': 'arg1'},
                        {'key': 'arg2', 'value': 'arg2'},
                        {'key': 'arg3', 'value': 'arg3'},
                    ],
                ),
            ),
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam(
                    {
                        'message': (
                            'Hey! Here are some features: ' 'arg1, arg2, arg3'
                        ),
                    },
                ),
            ],
        ),
        pytest.param(
            state_module.State(features=feature_module.Features(features=[])),
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam(
                    {
                        'message': (
                            'Hey! Here are some features: ' 'arg1, arg2, arg3'
                        ),
                    },
                ),
            ],
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'arg2', 'value': 'arg2'},
                        {'key': 'arg3', 'value': 'arg3'},
                    ],
                ),
            ),
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam(
                    {
                        'message': (
                            'Hey! Here are some features: '
                            '{arg1}, {arg2}, {arg3}'
                        ),
                    },
                ),
                params_module.ActionParam(
                    {
                        'default_args': {
                            'arg1': 'arg1',
                            'arg2': 'arg4',
                            'arg3': 'arg5',
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            state_module.State(features=feature_module.Features(features=[])),
            [
                params_module.ActionParam({'to_emails': ['test@test.com']}),
                params_module.ActionParam(
                    {
                        'message': (
                            'Hey! Here are some features: '
                            '{arg1}, {arg2}, {arg3}'
                        ),
                    },
                ),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
    ],
)
def test_validate_state(state, _call_param):
    action = send_mail.SendMail('echo', 'echo', '0', _call_param)
    action.validate_state(state)
