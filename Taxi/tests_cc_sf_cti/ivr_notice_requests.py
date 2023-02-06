import typing


ABONENT_NUMBER = '+71234567890'
CALL_EXTERNAL_ID = 'some_id'
CALL_RECORD_ID = 'SOME_RECORD_ID'
IVR_FLOW = 'taxi_cc_sf_flow'

NO_ANSWER_STATUS = {'state': 'failed', 'error_cause': 'DESTINATION_NO_ANSWER'}
OTHER_ERROR_STATUS = {'state': 'failed', 'error_cause': 'OTHER_ERROR'}
ABONENT_HANGUP_STATUS = {'state': 'abonent-hangup'}


def base_call_notify_request():
    return {
        'call_external_id': CALL_EXTERNAL_ID,
        'service_number': '+74992296622',
        'ivr_flow_id': 'taxi_cc_sf_flow',
        'call_record_id': CALL_RECORD_ID,
        'call_guid': 'some_guid',
        'abonent_number': ABONENT_NUMBER,
    }


def call_notify_request(actions: list, **kwargs) -> dict:
    request: typing.Dict[str, typing.Any] = base_call_notify_request()
    request.update({'actions': actions})
    if not actions:
        request.update({'last_action': -1})
    else:
        request.update({'last_action': len(actions) - 1})
    request.update(**kwargs)
    return request


def get_action_type(action) -> str:
    action_type = list(action.keys())[0]
    if action_type == 'external_id':
        action_type = list(action.keys())[1]
    return action_type


def call_notify_request_by_response(response, **kwargs) -> dict:
    base_request: typing.Dict[str, typing.Any] = base_call_notify_request()
    base_request.update(response)
    base_request.update(**kwargs)
    return base_request


def call_notify_start_request(**kwargs) -> dict:
    return call_notify_request([], **kwargs)


def notify_request_by_create_call(request, **kwargs) -> dict:

    base_request: typing.Dict[str, typing.Any] = base_call_notify_request()
    if request['actions'][0]['originate'].get('phone_number') is not None:
        abonent_number = request['actions'][0]['originate']['phone_number']
    else:
        abonent_number = ''  # yandex_uid is given
    base_request.update({'abonent_number': abonent_number})
    base_request.update({'last_action': 0})
    base_request.update(request)
    base_request['actions'][0]['originate']['status'] = {'state': 'completed'}
    base_request['direction'] = 'outgoing'
    base_request.update(**kwargs)
    return base_request


def emplace_actions(response, actions_list: typing.Any) -> bool:
    actions = response.get('actions')
    if actions is None or actions_list is None:
        return actions_list is None and actions is None
    if len(actions) != len(actions_list):
        return False
    for i, action in enumerate(actions):
        if action.get(actions_list[i], None) is None:
            return False
    return True


IDEM_TOKEN_LENGTH = 20
DEFAULT_IDEMPOTENCY_TOKEN = '3212143241'
