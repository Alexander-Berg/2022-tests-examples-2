import datetime
import functools

import pytest

from tests_ivr_dispatcher import utils

ORIGINATING = 'originating'
ANSWERING = 'answering'
ORDER_INFO_SPEAKING = 'order_info_speaking'


def context_assert_final_state(state, session_id, db):
    db_session_doc = db.ivr_disp_sessions.find_one({'_id': session_id})
    assert 'context' in db_session_doc
    assert 'state' in db_session_doc['context']
    assert db_session_doc['context']['state'] == state


DISPATCHER_ANSWER_REPLY = {
    'type': 'answer',
    'params': {'start_recording': False},
}

DISPATCHER_ORIGINATE_REPLY = {
    'params': {
        'answer_timeout': 30,
        'call_from': utils.DEFAULT_TAXI_PHONE,
        'call_to': utils.DEFAULT_USER_PHONE,
        'early_answer': 1,
        'progress_timeout': 65,
        'start_recording': False,
        'gateways': 'ivr_order_informer',
    },
    'type': 'originate',
}

DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY = {
    'params': {
        'engine': 'ya_speechkit',
        'language': 'ru-RU',
        'speed': 0.9,
        'text': (
            'Здравствуйте. В 22:40 приедет синий Audi A8. Номер A666MP77.'
            'Цена поездки 75 рублей.'
        ),
        'voice': 'alena',
    },
    'type': 'speak',
}

DISPATCHER_ON_ASSIGNED_HIGHER_CLASS_EXACT_SPEAK_REPLY = {
    'params': {
        'engine': 'ya_speechkit',
        'language': 'ru-RU',
        'speed': 0.9,
        'text': (
            'Здравствуйте. Приедет машина класса Комфорт Плюс! '
            'В 22:40 приедет синий Audi A8. '
            'Номер A666MP77.Цена поездки 75 рублей.'
        ),
        'voice': 'alena',
    },
    'type': 'speak',
}

DISPATCHER_ON_ASSIGNED_SPEAK_REPLY = {
    'params': {
        'engine': 'ya_speechkit',
        'language': 'ru-RU',
        'speed': 0.9,
        'text': (
            'Через 1 минуту приедет синий Audi A8. Номер A666MP77.'
            'Цена поездки 75 рублей.'
        ),
        'voice': 'alena',
    },
    'type': 'speak',
}

DISPATCHER_ON_ASSIGNED_HIGHER_CLASS_SPEAK_REPLY = {
    'params': {
        'engine': 'ya_speechkit',
        'language': 'ru-RU',
        'speed': 0.9,
        'text': (
            'Приедет машина класса Комфорт Плюс! '
            'Через 1 минуту приедет синий Audi A8. '
            'Номер A666MP77.Цена поездки 75 рублей.'
        ),
        'voice': 'alena',
    },
    'type': 'speak',
}

# Configs
IVR_DISPATCHER_PROMPT_SETS = {
    'ivr_workers': {
        'oiw.partner_dtmf': {
            'text': 'PDYA',
            'tts_speed': 1.1,
            'prompt_id': 'oiw.partner_dtmf.wav',
        },
        'oiw.partner_not_found': {
            'text': 'PNF',
            'prompt_id': 'oiw.partner_not_found.wav',
        },
    },
    'override_kz_call_center': {
        'oiw.partner_dtmf': {
            'text': 'PDKZ',
            'tts_speed': 1.1,
            'prompt_id': 'oiw.partner_dtmf.wav',
        },
        'oiw.partner_not_found': {
            'text': 'PNFKZ',
            'prompt_id': 'oiw.partner_not_found.wav',
        },
    },
}

APPLICATION_MAP_TRANSLATION_KZ = {
    'kz_call_center': {
        'ivr_workers': 'override_kz_call_center',
        'notify': 'override_kz_call_center',
    },
}

# Octonode action results
OCTONODE_OIW_INITIAL_RESULT_OK = {
    'caller_number': utils.DEFAULT_TAXI_PHONE,  # call_from
    'called_number': utils.DEFAULT_USER_PHONE,  # call_to
    'status': 'ok',
    'type': 'initial',
}
OCTONODE_OSW_INITIAL_RESULT_OK = {
    'caller_number': utils.DEFAULT_USER_PHONE,  # call_from
    'called_number': utils.DEFAULT_TAXI_PHONE,  # call_to
    'status': 'ok',
    'type': 'initial',
    'call_guid': 'SOME_CALL_GUID',
    'origin_called_number': utils.DEFAULT_TAXI_PHONE,
}
OCTONODE_ORIGINATED_RESULT_OK = {'status': 'ok', 'type': 'originate'}
OCTONODE_ANSWER_RESULT_OK = {'status': 'ok', 'type': 'answer'}


def oiw_scenario(enabled: bool):
    return [
        (
            OCTONODE_OIW_INITIAL_RESULT_OK,
            DISPATCHER_ORIGINATE_REPLY,
            [
                functools.partial(
                    context_assert_final_state,
                    ORIGINATING,
                    utils.DEFAULT_SESSION_ID,
                ),
            ],
        ),
        (
            OCTONODE_ORIGINATED_RESULT_OK,
            DISPATCHER_ON_ASSIGNED_HIGHER_CLASS_EXACT_SPEAK_REPLY
            if enabled
            else DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY,
            [
                functools.partial(
                    context_assert_final_state,
                    ORDER_INFO_SPEAKING,
                    utils.DEFAULT_SESSION_ID,
                ),
            ],
        ),
    ]


def osw_scenario(enabled: bool):
    return [
        (
            OCTONODE_OSW_INITIAL_RESULT_OK,
            DISPATCHER_ANSWER_REPLY,
            [
                functools.partial(
                    context_assert_final_state,
                    ANSWERING,
                    utils.ANOTHER_SESSION_ID,
                ),
            ],
        ),
        (
            OCTONODE_ANSWER_RESULT_OK,
            DISPATCHER_ON_ASSIGNED_HIGHER_CLASS_SPEAK_REPLY
            if enabled
            else DISPATCHER_ON_ASSIGNED_SPEAK_REPLY,
            [
                functools.partial(
                    context_assert_final_state,
                    ORDER_INFO_SPEAKING,
                    utils.ANOTHER_SESSION_ID,
                ),
            ],
        ),
    ]


@pytest.mark.experiments3(filename='experiments3_higher_class.json')
@pytest.mark.parametrize(
    ('personal_phone_id', 'higher_class_enabled'),
    (
        pytest.param(
            utils.DEFAULT_PERSONAL_PHONE_ID,
            True,
            marks=pytest.mark.config(
                IVR_DISPATCHER_ALLOWED_HIGHER_CLASSES=['econom', 'business'],
            ),
            id='exp enabled, config enabled',
        ),
        pytest.param(
            utils.DEFAULT_PERSONAL_PHONE_ID,
            False,
            id='exp enabled, config disabled',
        ),
        pytest.param(
            utils.DEFAULT_DRIVER_PERSONAL_PHONE_ID,
            False,
            id='exp disabled, config enabled',
            marks=pytest.mark.config(
                IVR_DISPATCHER_ALLOWED_HIGHER_CLASSES=['econom', 'business'],
            ),
        ),
    ),
)
@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_OIW_SETTINGS={
        'originate_attempts': 1,
        'originate_retry_delay': 60,
        'sufficient_speak_time': 4,
    },
    IVR_DISPATCHER_PROMPT_SETS=IVR_DISPATCHER_PROMPT_SETS,
    APPLICATION_MAP_TRANSLATIONS=APPLICATION_MAP_TRANSLATION_KZ,
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.KZ_NUMBER: {
            'application': 'kz_call_center',
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
)
async def test_order_informer_worker(
        taxi_ivr_dispatcher,
        mongodb,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        mock_fleet_parks,
        mock_tariffs,
        mock_parks,
        load_json,
        mockserver,
        personal_phone_id,
        higher_class_enabled,
):
    @mockserver.json_handler('/user-api/v2/user_phones/get')
    async def _retrieve_personal_id(request):
        data = request.json
        return {'id': data['id'], 'personal_phone_id': personal_phone_id}

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['order']['preorder_request_id'] = 'tadada'
        response['fields']['order']['request']['class'] = ['econom']
        response['fields']['candidates'][0]['driver_classes'] = [
            'econom',
            'business',
        ]
        return response

    for action, reply, checks in oiw_scenario(higher_class_enabled):
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
        for check in checks:
            check(mongodb)


@pytest.mark.experiments3(filename='experiments3_higher_class.json')
@pytest.mark.parametrize(
    ('personal_phone_id', 'higher_class_enabled'),
    (
        pytest.param(
            utils.DEFAULT_PERSONAL_PHONE_ID,
            True,
            marks=pytest.mark.config(
                IVR_DISPATCHER_ALLOWED_HIGHER_CLASSES=['econom', 'business'],
            ),
            id='exp enabled, config enabled',
        ),
        pytest.param(
            utils.DEFAULT_PERSONAL_PHONE_ID,
            False,
            id='exp enabled, config disabled',
        ),
        pytest.param(
            utils.DEFAULT_DRIVER_PERSONAL_PHONE_ID,
            False,
            marks=pytest.mark.config(
                IVR_DISPATCHER_ALLOWED_HIGHER_CLASSES=['econom', 'business'],
            ),
            id='exp disabled, config enabled',
        ),
    ),
)
@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.DEFAULT_TAXI_PHONE: {
            'application': utils.DEFAULT_APPLICATION,
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '__default__': {'metaqueue': utils.DEFAULT_METAQUEUE},
        utils.DEFAULT_TAXI_PHONE: {'metaqueue': utils.DEFAULT_METAQUEUE},
    },
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {
                'name': 'order_status_worker_2_0',
                'type': 'native_worker',
            },
        },
    },
)
async def test_order_status_worker(
        taxi_ivr_dispatcher,
        mongodb,
        mock_int_authproxy,
        mock_personal,
        mock_user_api,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        mock_fleet_parks,
        mock_tariffs,
        mock_parks,
        mockserver,
        load_json,
        personal_phone_id,
        higher_class_enabled,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['order']['request']['due'] = (
            datetime.datetime.now() + datetime.timedelta(minutes=1)
        ).isoformat() + '+0000'
        response['fields']['order']['request']['class'] = ['econom']
        response['fields']['candidates'][0]['driver_classes'] = [
            'econom',
            'business',
        ]
        return response

    @mockserver.json_handler('/user-api/v2/user_phones/get')
    async def _retrieve_personal_id(request):
        data = request.json
        return {'id': data['id'], 'personal_phone_id': personal_phone_id}

    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_search(request, *args, **kwargs):
        assert request.json['user']['user_id'] == utils.DEFAULT_USER_ID
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == utils.DEFAULT_APPLICATION
        status = 'driving'
        return {
            'orders': [
                {
                    'orderid': '9b0ef3c5398b3e07b59f03110563479d',
                    'status': status,
                },
            ],
        }

    for action, reply, checks in osw_scenario(higher_class_enabled):
        request = {'session_id': utils.ANOTHER_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
        for check in checks:
            check(mongodb)
