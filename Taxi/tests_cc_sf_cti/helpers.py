import datetime
import random
import string

import dateutil.parser as timeparser

from tests_cc_sf_cti import ivr_notice_requests as ivr_requests
from tests_cc_sf_cti import request_container

WORK_PHONE = '1234'
YANDEX_UID = '1234_uid'

CC_FLOWS_CONFIG = {
    'default_flow': {
        'external_call_route': 'cc_sf_external_call_route',
        'internal_call_route': 'cc_sf_internal_call_route',
        'ivr_flow_id': 'taxi_cc_sf_flow',
        'dtmf_config': {
            'interdigit_timeout_ms': 3000,
            'min_digits': 4,
            'max_digits': 7,
        },
    },
}
_CC_HOST = 'https://cc-api.taxi.yandex-team.ru'
BASE_LINK_PATH = _CC_HOST + '/cc/v1/ivr-dispatcher/v1/recordings?session_id='


def check_sf_request(
        expected_internal_number,
        expected_subject,
        expected_result,
        external_phone=ivr_requests.ABONENT_NUMBER,
):
    sf_request = request_container.SingleRequestContainer.request.json
    assert sf_request['external_phone'] == external_phone
    assert sf_request['internal_phone'] == expected_internal_number
    assert sf_request['call_id'] == ivr_requests.CALL_EXTERNAL_ID
    assert sf_request['subject'] == expected_subject
    assert sf_request['call_result'] == expected_result
    assert (
        sf_request['call_record_url']
        == BASE_LINK_PATH + ivr_requests.CALL_RECORD_ID
    )


DEFAULT_STATUS = {'state': 'completed'}


class CallNotifier:
    def __init__(self, cc_sf_cti_client, **kwargs):
        self.cc_sf_cti_client = cc_sf_cti_client
        self.param_override = dict(**kwargs)
        self.current_request = ivr_requests.call_notify_start_request(
            **self.param_override,
        )
        self.current_action = -1

    async def originate(
            self,
            phone_number,
            yandex_uid,
            expect_originate_by_phone: bool = True,
            expected_action_list=tuple(['originate']),
    ):
        request = {
            'phone_number': phone_number,
            'call_external_id': ivr_requests.CALL_EXTERNAL_ID,
        }
        headers = {
            'X-Yandex-UID': yandex_uid,
            'X-Yandex-Login': 'some_yandex_login',
        }
        create_call_response = await self.cc_sf_cti_client.post(
            '/cc/v1/cc-sf-cti/v1/create-call/', headers=headers, json=request,
        )
        assert create_call_response.json() is not None
        assert create_call_response.status == 200
        cc_request = request_container.SingleRequestContainer.request.json
        originate_action = cc_request['actions'][0]['originate']
        if expect_originate_by_phone:
            assert originate_action['phone_number'] == phone_number
        else:
            assert originate_action['yandex_uid'] == yandex_uid
        self.current_request = ivr_requests.notify_request_by_create_call(
            cc_request, **self.param_override,
        )
        abonent_number = cc_request['actions'][0]['originate'].get(
            'phone_number', '',
        )
        self.current_action = 0
        self.param_override.update({'abonent_number': abonent_number})
        assert ivr_requests.emplace_actions(cc_request, expected_action_list)
        return cc_request

    async def send(self, expected_action_list, status=None, expected_code=200):
        idempotency_token = ''.join(
            random.choice(string.ascii_lowercase + string.digits)
            for _ in range(ivr_requests.IDEM_TOKEN_LENGTH)
        )
        status_to_set = status if status is not None else DEFAULT_STATUS
        if self.current_action != -1:
            action_type = ivr_requests.get_action_type(
                self.current_request['actions'][self.current_action],
            )
            self.current_request['actions'][self.current_action][action_type][
                'status'
            ] = status_to_set
        self.current_request['last_action'] = self.current_action
        response = await self.cc_sf_cti_client.post(
            '/v1/ivr-framework/call-notify',
            headers={'X-Idempotency-Token': idempotency_token},
            json=self.current_request,
        )
        assert response.status == int(expected_code)
        if expected_code != 200:
            return response
        assert ivr_requests.emplace_actions(
            response.json(), expected_action_list,
        )
        if expected_action_list is None:
            # not the last action in the sequence
            # or answer on processing action
            self.current_request['context'] = response.json()['context']
            if status_to_set.get('state') != 'processing':
                self.current_action += 1
                assert self.current_action < len(
                    self.current_request['actions'],
                )
            return response
        # the last action in the list
        self.current_request = ivr_requests.call_notify_request_by_response(
            response.json(), **self.param_override,
        )
        self.current_action = 0
        return response

    async def send_form_create_call_notify(
            self,
            phone_number,
            yandex_uid,
            expected_action_list,
            status=None,
            expected_code=200,
    ):
        self.current_request['context'] = {}
        self.current_request['context']['flow_arguments'] = {}
        flow_args = self.current_request['context']['flow_arguments']
        flow_args['operator_yandex_uid'] = yandex_uid
        flow_args['phone_number'] = phone_number
        return await self.send(expected_action_list, status, expected_code)

    async def answer_forward(self):
        return await self.send(
            expected_action_list=None, status={'state': 'processing'},
        )

    async def skip_intermediate(self):
        return await self.send(expected_action_list=None)


class TimeChecker:
    LOCAL_TIMEZONE = datetime.datetime.utcnow().astimezone().tzinfo
    CALL_INIT_TIME_MOCKED = timeparser.parse('2022-05-13T22:33:35').replace(
        tzinfo=LOCAL_TIMEZONE,
    )
    CALL_START_TIME_MOCKED = timeparser.parse('2022-05-13T22:33:44').replace(
        tzinfo=LOCAL_TIMEZONE,
    )
    CALL_END_TIME_MOCKED = timeparser.parse('2022-05-13T22:36:40').replace(
        tzinfo=LOCAL_TIMEZONE,
    )
    CALL_INIT_TIME = '2022-05-13T22:33:35'
    CALL_START_TIME = '2022-05-13T22:33:44'
    CALL_END_TIME = '2022-05-13T22:36:40'

    _TIME2MOCKED_TIME = {
        CALL_INIT_TIME: CALL_INIT_TIME_MOCKED,
        CALL_START_TIME: CALL_START_TIME_MOCKED,
        CALL_END_TIME: CALL_END_TIME_MOCKED,
    }

    _TIME2SF_FIELD = {
        CALL_INIT_TIME: 'call_init_datetime',
        CALL_START_TIME: 'call_start_datetime',
        CALL_END_TIME: 'call_end_datetime',
    }

    def __init__(self, mocked_time):
        self.mocked_time = mocked_time
        self.mocked_times_list = []

    def mock_time(self, time):
        self.mocked_times_list.append(time)
        mocked_time = TimeChecker._TIME2MOCKED_TIME[time]
        self.mocked_time.set(mocked_time)

    def check(self) -> bool:
        sf_request = request_container.SingleRequestContainer.request.json
        for time in self.mocked_times_list:
            if sf_request[TimeChecker._TIME2SF_FIELD[time]] != time:
                return False
        return True
