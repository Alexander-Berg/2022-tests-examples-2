import typing

import pytest

from tests_cc_sf_cti import helpers
from tests_cc_sf_cti import ivr_notice_requests as ivr_requests


MULTIREGION_FLOW = 'multiregion_flow'

CC_PHONE2FLOW = {
    '+79876543210': {'cc_sf_flow_name': MULTIREGION_FLOW},
    '+3749876543210': {'cc_sf_flow_name': MULTIREGION_FLOW},
    '+77876543210': {'cc_sf_flow_name': MULTIREGION_FLOW},
}
CC_QUEUES = {
    'managers_rus': {
        'short_number': '11111',
        'ivr_route': 'cc_sf_internal_call_route',
    },
    'managers_am': {
        'short_number': '22222',
        'ivr_route': 'cc_sf_internal_call_route',
    },
    'managers_kz': {
        'short_number': '33333',
        'ivr_route': 'cc_sf_internal_call_route',
    },
    'support': {'short_number': '12345', 'ivr_route': 'trunk_route'},
    'delivery': {'short_number': '54321', 'ivr_route': 'trunk_route'},
    'b2c_support': {'short_number': '98765', 'ivr_route': 'trunk_route'},
}
CC_REGIONS: typing.Dict[str, typing.Any] = {
    'default_region': 'rus',
    'rus': {
        'outgoing_call_server_number': '+79876543210',
        'managers_queue': 'managers_rus',
        'abonent_numbers_prefixes': [
            '+70',
            '+71',
            '+72',
            '+73',
            '+74',
            '+75',
            '+71',
            '+78',
            '+79',
        ],
    },
    'am': {
        'outgoing_call_server_number': '+3749876543210',
        'managers_queue': 'managers_am',
        'abonent_numbers_prefixes': ['+374'],
    },
    'kz': {
        'outgoing_call_server_number': '+77876543210',
        'managers_queue': 'managers_kz',
        'abonent_numbers_prefixes': ['+76', '+77'],
    },
}
CC_FLOWS_CONFIG = {
    'multiregion_flow': {
        'external_call_route': 'cc_sf_external_call_route',
        'internal_call_route': 'cc_sf_internal_call_route',
        'ivr_flow_id': 'multiregion_flow',
        'dtmf_config': {
            'interdigit_timeout_ms': 3000,
            'min_digits': 4,
            'max_digits': 7,
        },
    },
}
DEFAULT_ONGOING_FLOW = 'multiregion_flow'

SERVICE_NUMBER = CC_REGIONS['rus']['outgoing_call_server_number']


async def imitate_until_ask_number(call_notifier: helpers.CallNotifier):
    await call_notifier.send(['answer'])
    response = await call_notifier.send(['ask'])
    assert response.json()['actions'][0]['ask']['input_mode'] == 'dtmf'
    assert (
        response.json()['actions'][0]['ask']['playback']['play']['id']
        == 'taxi_cc_sf.intro_v2'
    )
    ask_status = {'state': 'completed', 'input_value': {'text': '1'}}
    response = await call_notifier.send(['ask'], status=ask_status)
    assert (
        response.json()['actions'][0]['ask']['playback']['play']['id']
        == 'taxi_cc_sf.managers_switch'
    )
    return response


async def imitate_until_forward_queue(
        call_notifier: helpers.CallNotifier, expected_queue, number='',
):
    await imitate_until_ask_number(call_notifier)
    ask_status = {'state': 'completed', 'input_value': {'text': number}}
    response = await call_notifier.send(['forward'], status=ask_status)
    assert (
        response.json()['actions'][0]['forward']['phone_number']
        == CC_QUEUES[expected_queue]['short_number']
    )
    return response


@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_PHONE2FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=CC_FLOWS_CONFIG)
@pytest.mark.config(CC_SF_CTI_REGIONS_CONFIG=CC_REGIONS)
@pytest.mark.config(CC_SF_CTI_QUEUES_CONFIG=CC_QUEUES)
async def test_manager_accept_call(
        mocked_time, _mock_sf_data_load, _mock_staff_api, taxi_cc_sf_cti,
):
    time_checker = helpers.TimeChecker(mocked_time)
    time_checker.mock_time(helpers.TimeChecker.CALL_INIT_TIME)

    call_notifier = helpers.CallNotifier(
        taxi_cc_sf_cti, direction='incoming', service_number=SERVICE_NUMBER,
    )
    await imitate_until_ask_number(call_notifier)
    ask_status = {
        'state': 'completed',
        'input_value': {'text': helpers.WORK_PHONE},
    }
    response = await call_notifier.send(['forward'], status=ask_status)
    assert (
        response.json()['actions'][0]['forward']['yandex_uid']
        == helpers.YANDEX_UID
    )

    time_checker.mock_time(helpers.TimeChecker.CALL_START_TIME)
    await call_notifier.answer_forward()
    time_checker.mock_time(helpers.TimeChecker.CALL_END_TIME)
    await call_notifier.send(['hangup'])

    helpers.check_sf_request(helpers.WORK_PHONE, 'incoming', 'answer')
    assert time_checker.check()

    await call_notifier.send([])


@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_PHONE2FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=CC_FLOWS_CONFIG)
@pytest.mark.config(CC_SF_CTI_REGIONS_CONFIG=CC_REGIONS)
@pytest.mark.config(CC_SF_CTI_QUEUES_CONFIG=CC_QUEUES)
async def test_manager_accept_abonent_hangup(
        mocked_time, _mock_sf_data_load, _mock_staff_api, taxi_cc_sf_cti,
):
    time_checker = helpers.TimeChecker(mocked_time)
    time_checker.mock_time(helpers.TimeChecker.CALL_INIT_TIME)

    call_notifier = helpers.CallNotifier(
        taxi_cc_sf_cti, direction='incoming', service_number=SERVICE_NUMBER,
    )
    await imitate_until_ask_number(call_notifier)
    ask_status = {
        'state': 'completed',
        'input_value': {'text': helpers.WORK_PHONE},
    }
    await call_notifier.send(['forward'], status=ask_status)
    time_checker.mock_time(helpers.TimeChecker.CALL_START_TIME)
    await call_notifier.answer_forward()
    time_checker.mock_time(helpers.TimeChecker.CALL_END_TIME)
    await call_notifier.send([], status=ivr_requests.ABONENT_HANGUP_STATUS)

    helpers.check_sf_request(helpers.WORK_PHONE, 'incoming', 'answer')
    assert time_checker.check()


@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_PHONE2FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=CC_FLOWS_CONFIG)
@pytest.mark.config(CC_SF_CTI_REGIONS_CONFIG=CC_REGIONS)
@pytest.mark.config(CC_SF_CTI_QUEUES_CONFIG=CC_QUEUES)
async def test_personal_manager_miss_call(
        mocked_time, _mock_sf_data_load, _mock_staff_api, taxi_cc_sf_cti,
):
    time_checker = helpers.TimeChecker(mocked_time)
    time_checker.mock_time(helpers.TimeChecker.CALL_INIT_TIME)

    call_notifier = helpers.CallNotifier(
        taxi_cc_sf_cti, direction='incoming', service_number=SERVICE_NUMBER,
    )
    await imitate_until_ask_number(call_notifier)
    ask_status = {
        'state': 'completed',
        'input_value': {'text': helpers.WORK_PHONE},
    }
    await call_notifier.send(['forward'], status=ask_status)

    response = await call_notifier.send(
        ['playback', 'forward'], status=ivr_requests.NO_ANSWER_STATUS,
    )
    assert (
        response.json()['actions'][0]['playback']['playback']['play']['id']
        == 'taxi_cc_sf.support_switch'
    )
    assert (
        response.json()['actions'][1]['forward']['phone_number']
        == CC_QUEUES['support']['short_number']
    )
    assert (
        response.json()['actions'][1]['forward']['route']
        == CC_QUEUES['support']['ivr_route']
    )

    await call_notifier.skip_intermediate()

    time_checker.mock_time(helpers.TimeChecker.CALL_END_TIME)
    await call_notifier.send(['hangup'])

    helpers.check_sf_request(helpers.WORK_PHONE, 'incoming', 'answer')
    assert time_checker.check()
    await call_notifier.send([])


@pytest.mark.parametrize(
    'abonent_number, expected_region, text',
    [
        pytest.param('+554443332211', 'rus', '', id='unusual_region'),
        pytest.param('+554443332211', 'rus', '000000', id='abonent_misclick'),
        pytest.param('+79836666666', 'rus', '', id='rus1'),
        pytest.param('+71116666666', 'rus', '', id='rus2'),
        pytest.param('+3747777777777', 'am', '', id='am'),
        pytest.param('+77888888888', 'kz', '', id='kz1'),
        pytest.param('+76888888888', 'kz', '', id='kz2'),
    ],
)
@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_PHONE2FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=CC_FLOWS_CONFIG)
@pytest.mark.config(CC_SF_CTI_REGIONS_CONFIG=CC_REGIONS)
@pytest.mark.config(CC_SF_CTI_QUEUES_CONFIG=CC_QUEUES)
async def test_different_regions_accept_call(
        mocked_time,
        _mock_sf_data_load,
        _mock_staff_api,
        taxi_cc_sf_cti,
        abonent_number,
        expected_region,
        text,
):
    time_checker = helpers.TimeChecker(mocked_time)
    time_checker.mock_time(helpers.TimeChecker.CALL_INIT_TIME)

    service_number = CC_REGIONS[expected_region]['outgoing_call_server_number']
    current_queue = CC_REGIONS[expected_region]['managers_queue']

    call_notifier = helpers.CallNotifier(
        taxi_cc_sf_cti,
        direction='incoming',
        service_number=service_number,
        abonent_number=abonent_number,
    )

    await imitate_until_forward_queue(
        call_notifier, current_queue, number=text,
    )
    time_checker.mock_time(helpers.TimeChecker.CALL_START_TIME)
    await call_notifier.answer_forward()
    time_checker.mock_time(helpers.TimeChecker.CALL_END_TIME)
    await call_notifier.send(['hangup'])

    helpers.check_sf_request(
        current_queue, 'incoming', 'answer', external_phone=abonent_number,
    )
    assert time_checker.check()

    await call_notifier.send([])


@pytest.mark.parametrize(
    'abonent_number, expected_region',
    [
        pytest.param('+554443332211', 'rus', id='unusual_region'),
        pytest.param('+79836666666', 'rus', id='rus'),
        pytest.param('+3747777777777', 'am', id='am'),
        pytest.param('+77888888888', 'kz', id='kz'),
    ],
)
@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_PHONE2FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=CC_FLOWS_CONFIG)
@pytest.mark.config(CC_SF_CTI_REGIONS_CONFIG=CC_REGIONS)
@pytest.mark.config(CC_SF_CTI_QUEUES_CONFIG=CC_QUEUES)
async def test_different_regions_abonent_hangup(
        mocked_time,
        _mock_sf_data_load,
        _mock_staff_api,
        taxi_cc_sf_cti,
        abonent_number,
        expected_region,
):
    time_checker = helpers.TimeChecker(mocked_time)
    time_checker.mock_time(helpers.TimeChecker.CALL_INIT_TIME)

    service_number = CC_REGIONS[expected_region]['outgoing_call_server_number']
    current_queue = CC_REGIONS[expected_region]['managers_queue']
    call_notifier = helpers.CallNotifier(
        taxi_cc_sf_cti,
        direction='incoming',
        service_number=service_number,
        abonent_number=abonent_number,
    )
    await imitate_until_forward_queue(call_notifier, current_queue)
    time_checker.mock_time(helpers.TimeChecker.CALL_START_TIME)
    await call_notifier.answer_forward()
    time_checker.mock_time(helpers.TimeChecker.CALL_END_TIME)
    await call_notifier.send([], status=ivr_requests.ABONENT_HANGUP_STATUS)

    helpers.check_sf_request(
        current_queue, 'incoming', 'answer', external_phone=abonent_number,
    )
    assert time_checker.check()


@pytest.mark.parametrize(
    'abonent_number, expected_region',
    [
        pytest.param('+554443332211', 'rus', id='unusual_region'),
        pytest.param('+79836666666', 'rus', id='rus'),
        pytest.param('+3747777777777', 'am', id='am'),
        pytest.param('+77888888888', 'kz', id='kz'),
    ],
)
@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_PHONE2FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=CC_FLOWS_CONFIG)
@pytest.mark.config(CC_SF_CTI_REGIONS_CONFIG=CC_REGIONS)
@pytest.mark.config(CC_SF_CTI_QUEUES_CONFIG=CC_QUEUES)
async def test_different_regions_missed_call(
        mocked_time,
        _mock_sf_data_load,
        _mock_staff_api,
        taxi_cc_sf_cti,
        abonent_number,
        expected_region,
):
    time_checker = helpers.TimeChecker(mocked_time)
    time_checker.mock_time(helpers.TimeChecker.CALL_INIT_TIME)

    service_number = CC_REGIONS[expected_region]['outgoing_call_server_number']
    current_queue = CC_REGIONS[expected_region]['managers_queue']

    call_notifier = helpers.CallNotifier(
        taxi_cc_sf_cti,
        direction='incoming',
        service_number=service_number,
        abonent_number=abonent_number,
    )

    await imitate_until_forward_queue(call_notifier, current_queue)

    response = await call_notifier.send(
        ['playback', 'forward'], status=ivr_requests.NO_ANSWER_STATUS,
    )
    assert (
        response.json()['actions'][0]['playback']['playback']['play']['id']
        == 'taxi_cc_sf.support_switch'
    )
    assert (
        response.json()['actions'][1]['forward']['phone_number']
        == CC_QUEUES['support']['short_number']
    )

    await call_notifier.skip_intermediate()

    time_checker.mock_time(helpers.TimeChecker.CALL_END_TIME)
    await call_notifier.send(['hangup'])

    helpers.check_sf_request(
        current_queue, 'incoming', 'answer', external_phone=abonent_number,
    )
    assert time_checker.check()
    await call_notifier.send([])


ABONENT_NUMBER = '+79876543210'


@pytest.mark.parametrize(
    'text, expected_trunk',
    [
        pytest.param('0', 'support', id='support'),
        pytest.param('2', 'b2c_support', id='b2c_support'),
        pytest.param('3', 'delivery', id='delivery'),
        pytest.param('7', 'support', id='other_digit'),
        pytest.param('', 'support', id='nothing_entered'),
    ],
)
@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_PHONE2FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=CC_FLOWS_CONFIG)
@pytest.mark.config(CC_SF_CTI_REGIONS_CONFIG=CC_REGIONS)
@pytest.mark.config(CC_SF_CTI_QUEUES_CONFIG=CC_QUEUES)
async def test_external_trunk(
        _mock_sf_data_load,
        _mock_staff_api,
        taxi_cc_sf_cti,
        text,
        expected_trunk,
):

    service_number = CC_REGIONS['rus']['outgoing_call_server_number']

    call_notifier = helpers.CallNotifier(
        taxi_cc_sf_cti,
        direction='incoming',
        service_number=service_number,
        abonent_number=ABONENT_NUMBER,
    )

    await call_notifier.send(['answer'])
    await call_notifier.send(['ask'])
    ask_status = {'state': 'completed', 'input_value': {'text': text}}
    response = await call_notifier.send(['forward'], status=ask_status)
    assert (
        response.json()['actions'][0]['forward']['phone_number']
        == CC_QUEUES[expected_trunk]['short_number']
    )
    if expected_trunk == 'support':
        assert (
            response.json()['actions'][0]['forward']['outbound_number']
            == ABONENT_NUMBER
        )
    await call_notifier.send(['hangup'])
    await call_notifier.send([])


@pytest.mark.parametrize(
    'use_form_create_call', [pytest.param(True), pytest.param(False)],
)
@pytest.mark.parametrize(
    'external_number, expected_region_number',
    [
        pytest.param('+554443332211', None, id='unusual_region'),
        pytest.param('+79836666666', 'rus', id='rus'),
        pytest.param('+3747777777777', 'am', id='am'),
        pytest.param('+77888888888', 'kz', id='kz'),
    ],
)
@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_PHONE2FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=CC_FLOWS_CONFIG)
@pytest.mark.config(CC_SF_CTI_REGIONS_CONFIG=CC_REGIONS)
@pytest.mark.config(CC_SF_CTI_QUEUES_CONFIG=CC_QUEUES)
@pytest.mark.config(
    CC_SF_CTI_DEFAULT_FLOW_ON_ONGOING_CALLS=DEFAULT_ONGOING_FLOW,
)
async def test_initiate_call(
        mocked_time,
        _mock_sf_data_load,
        _mock_ivr_create_call,
        _mock_staff_api,
        taxi_cc_sf_cti,
        use_form_create_call,
        external_number,
        expected_region_number,
):
    time_checker = helpers.TimeChecker(mocked_time)
    time_checker.mock_time(helpers.TimeChecker.CALL_INIT_TIME)
    expected_service_number = CC_REGIONS['rus']['outgoing_call_server_number']
    if expected_region_number:
        expected_service_number = CC_REGIONS[expected_region_number][
            'outgoing_call_server_number'
        ]

    call_notifier = helpers.CallNotifier(
        taxi_cc_sf_cti,
        direction='outgoing',
        service_number=expected_service_number,
    )
    if use_form_create_call:
        response = (
            await call_notifier.send_form_create_call_notify(
                external_number,
                helpers.YANDEX_UID,
                expected_action_list=['originate'],
            )
        ).json()
    else:
        response = await call_notifier.originate(
            external_number,
            helpers.YANDEX_UID,
            expect_originate_by_phone=False,
            expected_action_list=['originate'],
        )
    assert response['actions'][0]['originate']['yandex_uid'] == (
        helpers.YANDEX_UID
    )
    response = await call_notifier.send(['forward'])
    assert (
        response.json()['actions'][0]['forward']['phone_number']
        == external_number
    )
    assert response.json()['actions'][0]['forward']['enable_provision']
    time_checker.mock_time(helpers.TimeChecker.CALL_START_TIME)

    await call_notifier.answer_forward()

    time_checker.mock_time(helpers.TimeChecker.CALL_END_TIME)

    await call_notifier.send(['hangup'])
    await call_notifier.send([])

    helpers.check_sf_request(
        helpers.WORK_PHONE,
        'outgoing',
        'answer',
        external_phone=external_number,
    )
    assert time_checker.check()


@pytest.mark.parametrize(
    'external_number, expected_region_number',
    [
        pytest.param('+554443332211', None, id='unusual_region'),
        pytest.param('+79836666666', 'rus', id='rus'),
        pytest.param('+3747777777777', 'am', id='am'),
        pytest.param('+77888888888', 'kz', id='kz'),
    ],
)
@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_PHONE2FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=CC_FLOWS_CONFIG)
@pytest.mark.config(CC_SF_CTI_REGIONS_CONFIG=CC_REGIONS)
@pytest.mark.config(CC_SF_CTI_QUEUES_CONFIG=CC_QUEUES)
@pytest.mark.config(
    CC_SF_CTI_DEFAULT_FLOW_ON_ONGOING_CALLS=DEFAULT_ONGOING_FLOW,
)
async def test_outgoing_failed(
        _mock_ivr_create_call,
        _mock_staff_api,
        taxi_cc_sf_cti,
        external_number,
        expected_region_number,
):
    expected_service_number = CC_REGIONS['rus']['outgoing_call_server_number']
    if expected_region_number:
        expected_service_number = CC_REGIONS[expected_region_number][
            'outgoing_call_server_number'
        ]

    call_notifier = helpers.CallNotifier(
        taxi_cc_sf_cti,
        direction='outgoing',
        service_number=expected_service_number,
    )
    await call_notifier.originate(
        external_number,
        helpers.YANDEX_UID,
        expect_originate_by_phone=False,
        expected_action_list=['originate'],
    )

    await call_notifier.send([], status=ivr_requests.NO_ANSWER_STATUS)


@pytest.mark.parametrize(
    'external_number, expected_region_number',
    [
        pytest.param('+554443332211', None, id='unusual_region'),
        pytest.param('+79836666666', 'rus', id='rus'),
        pytest.param('+3747777777777', 'am', id='am'),
        pytest.param('+77888888888', 'kz', id='kz'),
    ],
)
@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_PHONE2FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=CC_FLOWS_CONFIG)
@pytest.mark.config(CC_SF_CTI_REGIONS_CONFIG=CC_REGIONS)
@pytest.mark.config(CC_SF_CTI_QUEUES_CONFIG=CC_QUEUES)
@pytest.mark.config(
    CC_SF_CTI_DEFAULT_FLOW_ON_ONGOING_CALLS=DEFAULT_ONGOING_FLOW,
)
async def test_manages_miss_outgoing(
        mocked_time,
        _mock_sf_data_load,
        _mock_ivr_create_call,
        _mock_staff_api,
        taxi_cc_sf_cti,
        external_number,
        expected_region_number,
):
    time_checker = helpers.TimeChecker(mocked_time)
    time_checker.mock_time(helpers.TimeChecker.CALL_INIT_TIME)
    expected_service_number = None
    if expected_region_number:
        expected_service_number = CC_REGIONS[expected_region_number][
            'outgoing_call_server_number'
        ]

    call_notifier = helpers.CallNotifier(
        taxi_cc_sf_cti,
        direction='outgoing',
        service_number=(
            expected_service_number
            if expected_service_number is not None
            else CC_REGIONS['rus']['outgoing_call_server_number']
        ),
    )
    response = await call_notifier.originate(
        external_number,
        helpers.YANDEX_UID,
        expect_originate_by_phone=False,
        expected_action_list=['originate'],
    )
    if expected_service_number:
        assert (
            response['actions'][0]['originate']['outbound_number']
            == expected_service_number
        )
    response = await call_notifier.send(['forward'])
    assert (
        response.json()['actions'][0]['forward']['phone_number']
        == external_number
    )
    time_checker.mock_time(helpers.TimeChecker.CALL_END_TIME)

    await call_notifier.send(['hangup'], status=ivr_requests.NO_ANSWER_STATUS)
    await call_notifier.send([])

    helpers.check_sf_request(
        helpers.WORK_PHONE,
        'outgoing',
        'no_answer',
        external_phone=external_number,
    )
    assert time_checker.check()
