from typing import Dict
from typing import List
from typing import Optional

import pytest

from generated.clients_libs.supportai import supportai_lib as supportai_models

from supportai_api.generated.service.swagger.models import api as api_models
from supportai_api.ivr_integration import common as ivr_common
from supportai_api.ivr_integration import postprocessing

TEST_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUI3gEQbw:Tc0fid-P9vc-dPS_UEQcQoDtM25vXU'
    '-seEZpTLaLla8WDsG5swfFS46FQilr41TH9XHBgIVoaNC-aNFuuLqdqGB8zifyjig'
    'XReodgtA-Qy5hkJ4qv6dCpmez6bmeMl_wQxVqds35ZxfT1EWyjfHHoalP2EzS-dAem'
    '3V5k_EwBsE'
)

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
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
    ),
    pytest.mark.usefixtures('mocked_tvm'),
]

NO_LISTEN_TAG = postprocessing.NO_LISTEN_TAG

PROJECT_SLUG = 'sample_project'
CHAT_ID = '123456789'
CALL_RECORD_ID = '0987654321'
CALL_GUID = '0000-SOMETHING-0000'
ABONENT_NUMBER = '77777777777'
CALLCENTER_NUMBER = '88005553535'


def _check_common_features(
        features_dict: Dict, with_call_record_id: bool = False,
):
    if with_call_record_id:
        assert features_dict.pop('call_record_id', None) == CALL_RECORD_ID
    assert features_dict.pop('project_slug', None) == PROJECT_SLUG
    assert features_dict.pop('callcenter_number', None) == CALLCENTER_NUMBER
    assert features_dict.pop('abonent_number', None) == ABONENT_NUMBER
    assert features_dict.pop('call_guid', None) == CALL_GUID


def _create_support_response(
        ai_text: Optional[str] = None,
        tags: Optional[List[str]] = None,
        forward_line: Optional[str] = None,
        close: Optional[bool] = None,
) -> supportai_models.SupportResponse:
    return supportai_models.SupportResponse(
        close=supportai_models.Close() if close else None,
        forward=supportai_models.Forward(forward_line)
        if forward_line
        else None,
        reply=supportai_models.Reply(text=ai_text) if ai_text else None,
        tag=supportai_models.Tag(add=tags) if tags else None,
    )


def _create_call_action(
        action_type: ivr_common.ActionType,
        user_text: Optional[str] = None,
        status: ivr_common.ActionState = ivr_common.ActionState.COMPLETED,
        is_fallback: bool = False,
        error_cause: Optional[str] = None,
) -> api_models.CallAction:
    typed_action: Dict = {'status': {'state': status.value}}
    if status == ivr_common.ActionState.FAILED:
        typed_action['status']['error_cause'] = error_cause
    if action_type == ivr_common.ActionType.ASK:
        assert user_text
        typed_action['status']['input_value'] = {'text': user_text}
    if action_type in (
            ivr_common.ActionType.PLAYBACK,
            ivr_common.ActionType.ASK,
    ):
        typed_action['playback'] = {}
    if action_type in (
            ivr_common.ActionType.FORWARD,
            ivr_common.ActionType.ORIGINATE,
    ):
        typed_action['phone_number'] = '937-9992'

    external_id = '1234567890' if not is_fallback else 'fallback_action'

    call_action_dict = {
        'external_id': external_id,
        action_type.value: typed_action,
    }

    return api_models.CallAction.deserialize(call_action_dict)


async def _make_ivr_request(
        web_app_client, call_notice: api_models.CallNotice,
):
    return await web_app_client.post(
        'v1/ivr-framework/call-notify',
        headers={
            'X-Idempotency-Token': '1245678901234567890',
            'X-Ya-Service-Ticket': TEST_SERVICE_TICKET,
        },
        json=call_notice.serialize(),
    )


def _create_call_notice(
        action_types: List[ivr_common.ActionType],
        direction: str = 'outgoing',
        problem_status: ivr_common.ActionState = ivr_common.ActionState.FAILED,
        user_text: Optional[str] = None,
        is_fallback: bool = False,
        problem_index: Optional[int] = None,
        error_cause: Optional[str] = None,
        call_record_id: Optional[str] = None,
        features: Optional[List[dict]] = None,
) -> api_models.CallNotice:
    actions = [
        _create_call_action(
            action_type,
            user_text=user_text,
            is_fallback=is_fallback,
            error_cause=error_cause,
        )
        for action_type in action_types
    ]
    if problem_index is not None:
        problem_action_type = action_types[problem_index]
        typed_action = getattr(
            actions[problem_index], problem_action_type.value,
        )
        typed_action.status.state = problem_status.value
        if problem_status == ivr_common.ActionState.FAILED:
            typed_action.status.error_cause = error_cause

        for idx in range(problem_index + 1, len(action_types)):
            action_type = action_types[idx]
            typed_action = getattr(actions[idx], action_type.value)
            typed_action.status.state = ivr_common.ActionState.PROCESSING

    return api_models.CallNotice(
        abonent_number=ABONENT_NUMBER,
        actions=actions,
        call_external_id=CHAT_ID,
        call_record_id=call_record_id,
        call_guid=CALL_GUID,
        ivr_flow_id=PROJECT_SLUG,
        direction=direction,
        last_action=problem_index if problem_index else len(action_types) - 1,
        service_number=CALLCENTER_NUMBER,
        context={'features': features} if features else None,
    )


@pytest.mark.parametrize(
    ('action_state', 'error_cause', 'is_fallback'),
    [
        (ivr_common.ActionState.COMPLETED, None, False),
        (ivr_common.ActionState.COMPLETED, None, True),
        (ivr_common.ActionState.ABONENT_HANGUP, None, False),
        (ivr_common.ActionState.TIMEOUT, None, False),
        (ivr_common.ActionState.FAILED, 'something went wrong', False),
    ],
)
async def test_abortion(
        mockserver, web_app_client, action_state, error_cause, is_fallback,
):
    action_state_to_error_descr = {
        ivr_common.ActionState.ABONENT_HANGUP: (
            'answer action interrupted with hangup'
        ),
        ivr_common.ActionState.TIMEOUT: (
            'timeout during processing answer action'
        ),
        ivr_common.ActionState.FAILED: (
            f'answer action failed with error: {error_cause}'
        ),
    }
    action_state_to_error_code = {
        ivr_common.ActionState.ABONENT_HANGUP: 'ABONENT_HANGUP',
        ivr_common.ActionState.TIMEOUT: 'ACTION_TIMEOUT',
        ivr_common.ActionState.FAILED: error_cause,
    }
    expected_error_descr = action_state_to_error_descr.get(action_state)
    expected_error_code = action_state_to_error_code.get(action_state)
    call_notice = _create_call_notice(
        [ivr_common.ActionType.ANSWER],
        problem_status=action_state,
        is_fallback=is_fallback,
        problem_index=0,
        error_cause=error_cause,
    )

    @mockserver.json_handler('supportai/supportai/v1/support')
    async def _(request):
        support_request = supportai_models.SupportRequest.deserialize(
            request.json,
        )
        features_dict = {
            feature.key: feature.value for feature in support_request.features
        }
        _check_common_features(features_dict)
        assert features_dict.pop('event_type', None) == 'dial'
        if not action_state == ivr_common.ActionState.COMPLETED:
            assert (
                features_dict.pop('error_description', None)
                == expected_error_descr
            )
            assert features_dict.pop('error_code', None) == expected_error_code
        if is_fallback:
            assert features_dict.pop('ivr_framework_fallback', None) is True
        else:
            assert features_dict.pop('ivr_framework_fallback', None) is False
        assert not features_dict
        return _create_support_response('hello!', ['speak']).serialize()

    response = await _make_ivr_request(web_app_client, call_notice)
    assert response.status == 200
    response_obj = api_models.CallScript.deserialize(await response.json())
    if not action_state == ivr_common.ActionState.COMPLETED or is_fallback:
        assert not response_obj.actions
        return
    assert len(response_obj.actions) == 1
    new_action = response_obj.actions[0]
    assert new_action.ask
    assert new_action.ask.playback.speak.text == 'hello!'


@pytest.mark.parametrize('is_failed', [True, False])
async def test_immediate_answer(mockserver, web_app_client, is_failed):
    call_action_types = [
        ivr_common.ActionType.FORWARD,
        ivr_common.ActionType.HANGUP,
    ]
    error_text = 'some error' if is_failed else None
    error_index = 0 if is_failed else None

    @mockserver.json_handler('supportai/supportai/v1/support')
    async def _(request):
        if not is_failed:
            assert False
        assert error_text is not None
        features_dict = {
            feature['key']: feature['value']
            for feature in request.json['features']
        }
        assert isinstance(features_dict.get('error_description'), str)
        assert f'action failed with error: {error_text}' in features_dict.pop(
            'error_description', None,
        )
        assert features_dict.pop('error_code', None) == error_text
        assert features_dict.pop('event_type', None) == 'message'
        assert features_dict.pop('ivr_framework_fallback', None) is False
        _check_common_features(features_dict)
        assert not features_dict
        return _create_support_response('hello!', ['speak']).serialize()

    for call_action_type in call_action_types:
        call_notice = _create_call_notice(
            [call_action_type],
            problem_index=error_index,
            error_cause=error_text,
        )
        response = await _make_ivr_request(web_app_client, call_notice)
        assert response.status == 200
        response_obj = api_models.CallScript.deserialize(await response.json())
        assert not response_obj.actions


@pytest.mark.parametrize('with_call_record_id', [True, False])
@pytest.mark.parametrize('direction', ['incoming', 'outgoing'])
@pytest.mark.parametrize(
    'features', [[{'key': 'some_feature', 'value': 'some_value'}], None],
)
async def test_begin_dialog(
        web_app_client, mockserver, with_call_record_id, direction, features,
):
    @mockserver.json_handler('supportai/supportai/v1/support')
    async def _(request):
        assert request.json['chat_id'] == CHAT_ID
        features_dict = {
            ml_feature['key']: ml_feature['value']
            for ml_feature in request.json['features']
        }
        assert features_dict.pop('event_type') == 'dial'
        assert features_dict.pop('ivr_framework_fallback', None) is False
        if features:
            assert features_dict.pop('some_feature', None) == 'some_value'
        _check_common_features(features_dict, with_call_record_id)
        assert not features_dict
        return _create_support_response('hello!', ['speak']).serialize()

    @mockserver.json_handler(
        'supportai-calls/supportai-calls/v1/calls/incoming/register',
    )
    async def _(request):
        if direction == 'outgoing':
            assert False
        assert request.query['project_slug'] == 'sample_project'
        assert request.json['chat_id'] == CHAT_ID
        assert request.json['phone'] == ABONENT_NUMBER
        assert request.json['call_service'] == 'ivr_framework'
        assert request.json['features'] == (features or [])
        return {}

    call_notice = _create_call_notice(
        [
            ivr_common.ActionType.ANSWER
            if direction == 'incoming'
            else ivr_common.ActionType.ORIGINATE,
        ],
        direction=direction,
        call_record_id=CALL_RECORD_ID if with_call_record_id else None,
        features=features,
    )
    response = await _make_ivr_request(web_app_client, call_notice)
    assert response.status == 200


@pytest.mark.parametrize('playback_type', ['play', 'speak'])
@pytest.mark.parametrize('no_listen', [True, False])
async def test_continue_dialog(
        web_app_client, mockserver, playback_type, no_listen,
):
    tags = [playback_type]
    if no_listen:
        tags.append(NO_LISTEN_TAG)

    possible_types = [
        ivr_common.ActionType.PLAYBACK,
        ivr_common.ActionType.ASK,
    ]
    expected_type, unexpected_type = (
        possible_types if no_listen else reversed(possible_types)
    )
    expected_playback_type = playback_type
    playback_parameter = 'text' if playback_type == 'speak' else 'id'
    unexpected_playback_type = 'play' if playback_type == 'speak' else 'speak'

    @mockserver.json_handler('supportai/supportai/v1/support')
    async def _(request):
        assert request.json['chat_id'] == CHAT_ID
        features_dict = {
            ml_feature['key']: ml_feature['value']
            for ml_feature in request.json['features']
        }
        assert features_dict.pop('ivr_framework_fallback', None) is False
        assert features_dict.pop('event_type', None) == 'message'
        _check_common_features(
            features_dict=features_dict, with_call_record_id=True,
        )
        assert not features_dict
        return _create_support_response('hello!', tags).serialize()

    call_notice = _create_call_notice(
        [ivr_common.ActionType.PLAYBACK], call_record_id=CALL_RECORD_ID,
    )
    response = await _make_ivr_request(web_app_client, call_notice)
    assert response.status == 200
    response_obj = api_models.CallScript.deserialize(await response.json())
    assert len(response_obj.actions) == 1
    action = response_obj.actions[0]
    expected_typed_action = getattr(action, expected_type.value)
    assert expected_typed_action
    assert not getattr(action, unexpected_type.value)
    playback_obj: api_models.Playback = expected_typed_action.playback
    playback_option = getattr(playback_obj, expected_playback_type)
    assert playback_option
    assert not getattr(playback_obj, unexpected_playback_type)
    assert getattr(playback_option, playback_parameter) == 'hello!'


@pytest.mark.parametrize(
    ('ai_phrase', 'explicit_no_ai_phrase'),
    [('goodbye!', None), (None, True), (None, False)],
)
async def test_end_dialog(
        web_app_client, mockserver, ai_phrase, explicit_no_ai_phrase,
):
    forward_number = 'sOmEnUmBeR'
    kwargs_list = [{'close': True}, {'forward_line': forward_number}]
    ai_phrase = (
        ai_phrase if ai_phrase else None if explicit_no_ai_phrase else ''
    )
    expected_last_action_types = [
        ivr_common.ActionType.HANGUP,
        ivr_common.ActionType.FORWARD,
    ]
    for kwargs, expected_last_action_type in zip(
            kwargs_list, expected_last_action_types,
    ):

        @mockserver.json_handler('supportai/supportai/v1/support')
        # pylint: disable=cell-var-from-loop
        async def _(_):
            return _create_support_response(
                ai_phrase, ['speak'], **kwargs,
            ).serialize()

        call_notice = _create_call_notice([ivr_common.ActionType.ORIGINATE])

        response = await _make_ivr_request(web_app_client, call_notice)
        assert response.status == 200
        response_obj = api_models.CallScript.deserialize(await response.json())
        if ai_phrase:
            assert len(response_obj.actions) == 2
            assert response_obj.actions[0].playback
        else:
            assert len(response_obj.actions) == 1

        last_action = response_obj.actions[-1]
        last_typed_action = getattr(
            last_action, expected_last_action_type.value,
        )
        assert last_typed_action
        if expected_last_action_type == ivr_common.ActionType.FORWARD:
            phone_number = getattr(last_typed_action, 'phone_number')
            assert phone_number == forward_number
        else:
            assert (
                last_typed_action.serialize()
                == api_models.HangupAction().serialize()
            )
