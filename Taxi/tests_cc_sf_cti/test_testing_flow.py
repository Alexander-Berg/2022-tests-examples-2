import pytest

from tests_cc_sf_cti import helpers


MULTIREGION_FLOW = 'multiregion_flow'
SERVICE_NUMBER = '+79999999999'
CC_PHONE2FLOW = {
    SERVICE_NUMBER: {'cc_sf_flow_name': MULTIREGION_FLOW},
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
    'sipuni': {'short_number': '6767', 'ivr_route': 'trunk_sipuni_route'},
    'support': {'short_number': '12345', 'ivr_route': 'trunk_route'},
    'delivery': {'short_number': '54321', 'ivr_route': 'trunk_route'},
    'b2c_support': {'short_number': '98765', 'ivr_route': 'trunk_route'},
}
CC_REGIONS = {
    'rus': {
        'outgoing_call_server_number': SERVICE_NUMBER,
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
CC_TESTING_SETTINGS = {
    'use_test_flow': True,
    'tanua_numbers_whitelist': [helpers.WORK_PHONE],
    'originate_to_abonent_first': True,
}
DEFAULT_ONGOING_FLOW = 'multiregion_flow'


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


@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_PHONE2FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=CC_FLOWS_CONFIG)
@pytest.mark.config(CC_SF_CTI_REGIONS_CONFIG=CC_REGIONS)
@pytest.mark.config(CC_SF_CTI_QUEUES_CONFIG=CC_QUEUES)
@pytest.mark.config(CC_SF_CTI_TESTING_SETTINGS=CC_TESTING_SETTINGS)
async def test_manager_whitelist_accept_call(
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
@pytest.mark.config(CC_SF_CTI_TESTING_SETTINGS=CC_TESTING_SETTINGS)
async def test_abonent_misclick(
        _mock_sf_data_load, _mock_staff_api, taxi_cc_sf_cti,
):
    call_notifier = helpers.CallNotifier(
        taxi_cc_sf_cti, direction='incoming', service_number=SERVICE_NUMBER,
    )
    await imitate_until_ask_number(call_notifier)
    ask_status = {'state': 'completed', 'input_value': {'text': '00000'}}
    await call_notifier.send(['ask'], status=ask_status)
    ask_status = {
        'state': 'completed',
        'input_value': {'text': helpers.WORK_PHONE},
    }
    response = await call_notifier.send(['forward'], status=ask_status)
    assert (
        response.json()['actions'][0]['forward']['yandex_uid']
        == helpers.YANDEX_UID
    )

    await call_notifier.answer_forward()
    await call_notifier.send(['hangup'])

    helpers.check_sf_request(helpers.WORK_PHONE, 'incoming', 'answer')

    await call_notifier.send([])


INTERNAL_NUMBER = '100'


@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_PHONE2FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=CC_FLOWS_CONFIG)
@pytest.mark.config(CC_SF_CTI_REGIONS_CONFIG=CC_REGIONS)
@pytest.mark.config(CC_SF_CTI_QUEUES_CONFIG=CC_QUEUES)
@pytest.mark.config(CC_SF_CTI_TESTING_SETTINGS=CC_TESTING_SETTINGS)
async def test_sipuni_trunk(
        _mock_sf_data_load, _mock_staff_api, taxi_cc_sf_cti,
):
    call_notifier = helpers.CallNotifier(
        taxi_cc_sf_cti, direction='incoming', service_number='+79999999999',
    )
    await imitate_until_ask_number(call_notifier)

    ask_status = {
        'state': 'completed',
        'input_value': {'text': INTERNAL_NUMBER},
    }
    response = await call_notifier.send(
        ['playback', 'forward'], status=ask_status,
    )
    await call_notifier.skip_intermediate()
    assert (
        response.json()['actions'][1]['forward']['phone_number']
        == CC_QUEUES['sipuni']['short_number']
    )
    assert (
        response.json()['actions'][1]['forward']['route']
        == CC_QUEUES['sipuni']['ivr_route']
    )
    assert not response.json()['actions'][1]['forward']['use_deflect']
    await call_notifier.send(['hangup'])
    await call_notifier.send([])


EXTERNAL_NUMBER = '+74445556677'


@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_PHONE2FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=CC_FLOWS_CONFIG)
@pytest.mark.config(CC_SF_CTI_REGIONS_CONFIG=CC_REGIONS)
@pytest.mark.config(CC_SF_CTI_QUEUES_CONFIG=CC_QUEUES)
@pytest.mark.config(CC_SF_CTI_TESTING_SETTINGS=CC_TESTING_SETTINGS)
async def test_old_originate(
        _mock_sf_data_load,
        _mock_staff_api,
        _mock_ivr_create_call,
        taxi_cc_sf_cti,
):
    call_notifier = helpers.CallNotifier(
        taxi_cc_sf_cti, direction='outgoing', service_number=SERVICE_NUMBER,
    )
    response = await call_notifier.originate(
        EXTERNAL_NUMBER,
        helpers.YANDEX_UID,
        expect_originate_by_phone=True,
        expected_action_list=['originate'],
    )
    assert (
        response['actions'][0]['originate']['phone_number'] == EXTERNAL_NUMBER
    )
    response = await call_notifier.send(['forward'])
    assert (
        response.json()['actions'][0]['forward']['yandex_uid']
        == helpers.YANDEX_UID
    )

    await call_notifier.answer_forward()

    await call_notifier.send(['hangup'])
    await call_notifier.send([])
