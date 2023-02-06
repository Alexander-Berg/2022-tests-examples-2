# pylint: disable=wildcard-import, unused-wildcard-import
# pylint: disable=import-error, redefined-outer-name
import json

import pytest

from ucommunications_plugins import *  # noqa: F403 F401


@pytest.fixture(autouse=True, name='mock_xiva')
def _mock_xiva(mockserver):
    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _subscribe_app(request, *args, **kwargs):
        return mockserver.make_response('OK', 200)

    @mockserver.json_handler('/xiva/v2/unsubscribe/app')
    def _unsubscribe_app(request):
        return mockserver.make_response('OK', 200)

    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        return mockserver.make_response('OK', 200, headers={'TransitID': 'id'})

    @mockserver.json_handler('/xiva/v2/list')
    def _list(request):
        return []


@pytest.fixture(name='mock_yasms')
def _mock_yasms(mockserver):
    @mockserver.json_handler('/yasms/sendsms')
    def _sendsms(request):
        return mockserver.make_response(
            '<doc><message-sent id="127000000003456" /></doc>', 200,
        )


# This mock is used in test_sms_status_collector.py only.
# We need to define this mock in global space, otherwise worker
# sms-status-collector-worker will be started before /infobip/sms/1/reports
# handler and test will be failed
@pytest.fixture(autouse=True, name='mock_infobip')
def _mock_infobip(mockserver, load_json):
    def _make_response(message_id):
        if message_id == 'infobip-service-error':
            return mockserver.make_response('', 500)

        status_mapping = load_json('infobip_status_mapping.json')
        status = status_mapping[message_id]
        return mockserver.make_response(
            json.dumps(
                {
                    'results': [
                        {
                            'messageId': message_id,
                            'to': '385981178',
                            'status': {
                                'groupId': status['group_id'],
                                'groupName': status['group_name'],
                                'id': status['id'],
                                'name': status['name'],
                                'description': status['description'],
                            },
                            'error': {
                                'groupId': status['error_group_id'],
                                'groupName': status['error_group_name'],
                                'id': status['error_id'],
                                'name': status['error_name'],
                                'description': status['error_description'],
                            },
                        },
                    ],
                },
            ),
            200,
        )

    @mockserver.json_handler('/infobip/sms/1/reports')
    def _sms_reports(request):
        return _make_response(request.args['messageId'])


@pytest.fixture(autouse=True, name='mock_user_api')
def _mock_user_api(mockserver):
    @mockserver.json_handler('/user-api/user_phones/by_personal/retrieve_bulk')
    def _phones_retrieve_bulk(request):
        return {'items': [{}]}

    @mockserver.json_handler('/user-api/user_phones/by-natural-id')
    def _phones_retrieve(request):
        return {
            'id': '557f191e810c19729de860ea',
            'phone': '+70001112233',
            'personal_phone_id': '775f191e810c19729de860ea',
            'stat': {
                'big_first_discounts': 10,
                'complete': 200,
                'complete_card': 180,
                'complete_apple': 2,
                'complete_google': 14,
                'fake': 0,
                'total': 222,
            },
            'is_loyal': True,
            'is_yandex_staff': True,
            'is_taxi_staff': True,
            'type': 'yandex',
        }

    @mockserver.json_handler('/user-api/users/search')
    def _users_search(request):
        return {
            'items': [
                {
                    'id': 'my_user_id',
                    'application': 'android',
                    'created': '2019-08-23T13:00:00+0000',
                    'updated': '2019-08-23T13:00:00+0000',
                },
            ],
        }


@pytest.fixture(autouse=True, name='mock_parks')
def _mock_parks(mockserver):
    @mockserver.json_handler('/parks/driver-profiles/search')
    def _get_driver_phone_id(request):
        assert request.method == 'POST'
        assert request.json == {
            'query': {
                'park': {'id': ['PARK_ID']},
                'driver': {'id': ['DRIVER_ID']},
            },
            'fields': {
                'driver': ['phone_pd_ids', 'locale'],
                'park': ['locale'],
            },
        }
        response = {
            'profiles': [
                {'driver': {'phone_pd_ids': ['557f191e810c19729de860ea']}},
            ],
        }
        return response


@pytest.fixture(autouse=True, name='mock_personal')
def _mock_personal(mockserver):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _phones_retrieve(request):
        return {'id': '557f191e810c19729de860ea', 'value': '+70001112233'}

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': '557f191e810c19729de860ea', 'value': '+70001112233'}


@pytest.fixture(autouse=True, name='mock_driver_profiles')
def _mock_driver_profiles(mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles_retrieve(request):
        return mockserver.make_response('{"profiles": []}', 200)

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_phone',
    )
    def _mock_driver_profiles_retrieve_by_phone(request):
        return mockserver.make_response('{"profiles_by_phone": []}', 200)

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_driver_profiles_driver_app_profiles_retrieve(request):
        return {
            'profiles': [
                {'data': {'locale': 'en'}, 'park_driver_profile_id': dbid_uuid}
                for dbid_uuid in request.json['id_in_set']
            ],
        }


@pytest.fixture(name='mock_fleet_parks', autouse=True)
def _mock_fleet_parks(mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks_v1_parks_list(request):
        return {}


@pytest.fixture(autouse=True, name='mock_sms_intents_admin')
def _mock_sms_intents_admin(mockserver, load_json):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')


@pytest.fixture(scope='session')
def regenerate_config_hooks(regenerate_stat_client_config):
    return [regenerate_stat_client_config]
