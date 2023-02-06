# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from eats_launch_plugins import *  # noqa: F403 F401

# Generated using ya tool:
#   ya tool tvm unittest user --default 123 --scopes eats:all
USER_TICKET = (
    '3:user:CA0Q__________9_GhgKAgh7EHsaCGVhdHM6YWxsINKF2MwEKAE:InkbJveudHso'
    'lNC3ykQK3umnthMQLs3sqXHnN7TYdIZBc-1pVC1ST1Uskqwrp5Yh1W29gL6ZV9uULajs14F'
    'RDg4tjPKAiAPLpv1YEU5zJAx3J6_br4Z5dj6bZJf81JI-nwW2Sw8CzDBNTnuGcEcId9Ilvg'
    '85lzJcgq3oZuZgFfA'
)

# ya tool tvmknife unittest service -s 404 -d 2345
SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIlAMQqRI:Ta6H2YvxBztdoylkA5V9jOsk_ZoEfPw8MEr1N'
    'et0nrw84sTLgkL3iw6Db4qL7-GifB4Pm06RAoQAseBmmCTdHmYjd0Vk-py6lFR6iQK9QprtN'
    '3Z5_k4fDQ-JLEY9cI6L5qGs2Dcsprt8zTXjmCQPY5CdQnWPOSuU6iu9AqHYWPY'
)


@pytest.fixture(name='common_values')
async def _common_values(mockserver):
    return {
        'user_ticket': USER_TICKET,
        'mock_service_ticket': SERVICE_TICKET,
        'blackbox_eater_name': 'Козьма П.',
        'blackbox_email': 'coolhacker@yandex.ru',
        'blackbox_email_id': 'blackbox_email_id',
        'blackbox_default_phone': '+79990001122',
        'blackbox_default_phone_id': 'blackbox_default_phone_id',
        'blackbox_secured_phone': '+79990001133',
        'blackbox_secured_phone_id': 'blackbox_secured_phone_id',
        'eap_email_id': 'eap_email_id',
        'eap_phone_id': 'eap_phone_id',
        'requested_passport_uid': '123',
        'passport_uid_type_phonish': 'phonish',
        'passport_uid_type_portal': 'portal',
        'pass_flags_phonish': 'phonish',
        'pass_flags_portal': 'portal',
        'pass_flags_pdd': 'pdd',
        'inner_token': 'inner_token',
        'registered_eater_id': 'registered_eater_id',
        'session_eater_id': 'session_eater_id',
        'passport_eater_id': 'passport_eater_id',
        'passport_and_session_eater_id': 'passport_and_session_eater_id',
        'login_id': 'default_login_id',
        'device_id': 'default_device_id',
    }


@pytest.fixture(name='make_eater')
def _make_eater():
    def _wrapper(
            eater_id='some_eater_id',
            passport_uid=None,
            passport_uid_type=None,
            personal_phone_id=None,
            personal_email_id=None,
            banned_at=None,
    ):
        eater = {
            'id': eater_id,
            'uuid': 'a5f3aa68-53b7-4c98-a52a-d1551b8b3f7d',
            'created_at': '2019-12-31T10:59:59+03:00',
            'updated_at': '2019-12-31T10:59:59+03:00',
        }
        if passport_uid:
            eater['passport_uid'] = passport_uid
        if passport_uid_type:
            eater['passport_uid_type'] = passport_uid_type
        if personal_phone_id:
            eater['personal_phone_id'] = personal_phone_id
        if personal_email_id:
            eater['personal_email_id'] = personal_email_id
        if banned_at:
            eater['banned_at'] = banned_at

        return eater

    return _wrapper


@pytest.fixture(name='make_launch_headers')
def _make_launch_headers(common_values):
    def _wrapper(
            session_eater_id,
            passport_eater_id,
            eap_phone_id=None,
            eap_email_id=None,
            inner_token=common_values['inner_token'],
            passport_uid=common_values['requested_passport_uid'],
            pass_flags=common_values['pass_flags_portal'],
            service_ticket=common_values['mock_service_ticket'],
            user_ticket=common_values['user_ticket'],
            login_id=common_values['login_id'],
            device_id=common_values['device_id'],
    ):
        headers = {
            'X-Ya-Service-Ticket': service_ticket,
            'X-Yandex-UID': passport_uid,
            'X-Ya-User-Ticket': user_ticket,
            'X-YaTaxi-Pass-Flags': pass_flags,
            'X-Eats-Session': inner_token,
            'X-Remote-IP': '127.0.0.1',
            'X-Login-Id': login_id,
            'X-Device-Id': device_id,
        }
        if session_eater_id:
            headers['X-YaTaxi-User'] = 'eats_user_id=' + session_eater_id
            if eap_phone_id:
                headers['X-YaTaxi-User'] += (
                    ',personal_phone_id=' + eap_phone_id
                )
            if eap_email_id:
                headers['X-YaTaxi-User'] += (
                    ',personal_email_id=' + eap_email_id
                )
        if passport_eater_id:
            headers['X-Eats-Passport-Eater-Id'] = passport_eater_id
        return headers

    return _wrapper


@pytest.fixture(name='make_merge_request')
def _make_merge_request(common_values):
    def _wrapper(
            eater_id,
            passport_uid=common_values['requested_passport_uid'],
            passport_uid_type=common_values['passport_uid_type_portal'],
            personal_phone_id=common_values['blackbox_default_phone_id'],
            personal_email_id=common_values['blackbox_email_id'],
            name=common_values['blackbox_eater_name'],
            inner_token=common_values['inner_token'],
    ):
        return {
            'eater_id': eater_id,
            'passport_uid': passport_uid,
            'passport_uid_type': passport_uid_type,
            'personal_phone_id': personal_phone_id,
            'personal_email_id': personal_email_id,
            'name': name,
            'inner_token': inner_token,
        }

    return _wrapper


@pytest.fixture(name='make_delete_phonish_and_merge_request')
def _make_delete_phonish_and_merge_request(common_values):
    def _wrapper(
            phonish_to_delete_id,
            eater_id,
            passport_uid=common_values['requested_passport_uid'],
            passport_uid_type=common_values['passport_uid_type_portal'],
            personal_phone_id=common_values['blackbox_default_phone_id'],
            personal_email_id=common_values['blackbox_email_id'],
            name=common_values['blackbox_eater_name'],
            inner_token=common_values['inner_token'],
    ):
        return {
            'to_delete': {'eater_id': phonish_to_delete_id},
            'to_merge': {
                'eater_id': eater_id,
                'passport_uid': passport_uid,
                'passport_uid_type': passport_uid_type,
                'personal_phone_id': personal_phone_id,
                'personal_email_id': personal_email_id,
                'name': name,
                'inner_token': inner_token,
            },
        }

    return _wrapper


@pytest.fixture(name='make_reset_uid_and_merge_request')
def _make_reset_uid_and_merge_request(common_values):
    def _wrapper(
            eater_to_reset_id,
            eater_id,
            passport_uid=common_values['requested_passport_uid'],
            passport_uid_type=common_values['passport_uid_type_portal'],
            personal_phone_id=common_values['blackbox_default_phone_id'],
            personal_email_id=common_values['blackbox_email_id'],
            name=common_values['blackbox_eater_name'],
            inner_token=common_values['inner_token'],
    ):
        return {
            'to_reset': {'eater_id': eater_to_reset_id},
            'to_merge': {
                'eater_id': eater_id,
                'passport_uid': passport_uid,
                'passport_uid_type': passport_uid_type,
                'personal_phone_id': personal_phone_id,
                'personal_email_id': personal_email_id,
                'name': name,
                'inner_token': inner_token,
            },
        }

    return _wrapper


@pytest.fixture(name='make_register_request')
def _make_register_request(common_values):
    def _wrapper(has_phone, has_email, is_secured_phone=False):
        request = {
            'passport_uid': common_values['requested_passport_uid'],
            'passport_uid_type': common_values['passport_uid_type_portal'],
            'name': common_values['blackbox_eater_name'],
            'inner_token': common_values['inner_token'],
        }
        if has_phone:
            if is_secured_phone:
                request['personal_phone_id'] = common_values[
                    'blackbox_secured_phone_id'
                ]
            else:
                request['personal_phone_id'] = common_values[
                    'blackbox_default_phone_id'
                ]
        if has_email:
            request['personal_email_id'] = common_values['blackbox_email_id']

        return request

    return _wrapper


def build_phone_attributes(item_id, phone, is_default, is_secured):
    return {
        'attributes': {
            '102': phone,
            '107': '1' if is_default else '0',
            '4': '1556681858',
            '108': '1' if is_secured else '0',
        },
        'id': item_id,
    }


@pytest.fixture(name='mock_blackbox')
async def _mock_blackbox(mockserver, common_values):
    async def _wrapper(
            has_default_phone,
            has_email,
            has_secured_phone=False,
            user_ticket=common_values['user_ticket'],
    ):
        @mockserver.json_handler('/blackbox')
        async def _do_mock_blackbox(request):
            assert request.args == {
                'method': 'user_ticket',
                'emails': 'getall',
                'email_attributes': '1,3',
                'getphones': 'bound',
                'get_public_name': 'yes',
                'regname': 'yes',
                'format': 'json',
                'phone_attributes': '102,107,4,108',
                'dbfields': 'subscription.suid.669',
                'aliases': 'all',
            }
            assert request.form == {'user_ticket': user_ticket}

            phones = []
            if has_secured_phone:
                phones.append(
                    build_phone_attributes(
                        '557f191e810c19729de860e1',
                        common_values['blackbox_secured_phone'],
                        # Default phone always exists if there is any phone.
                        not has_default_phone,
                        True,
                    ),
                )
            if has_default_phone:
                phones.append(
                    build_phone_attributes(
                        '557f191e810c19729de860e2',
                        common_values['blackbox_default_phone'],
                        True,
                        False,
                    ),
                )

            emails = []
            if has_email:
                emails.append(
                    {
                        'attributes': {
                            '1': common_values['blackbox_email'],
                            '3': '1556681858',
                        },
                        'id': '557f191e810c19729de860e3',
                    },
                )

            data = {
                'users': [
                    {
                        'aliases': {'10': 'phne-4pvm324n'},
                        'dbfields': {'subscription.suid.669': ''},
                        'have_hint': False,
                        'have_password': False,
                        'id': '4031979996',
                        'karma': {'value': 0},
                        'karma_status': {'value': 0},
                        'login': '',
                        'phones': phones,
                        'emails': emails,
                        'uid': {
                            'hosted': False,
                            'lite': False,
                            'value': '123',
                        },
                        'display_name': {
                            'name': 'Козьма Прутков',
                            'public_name': common_values[
                                'blackbox_eater_name'
                            ],
                        },
                    },
                ],
            }

            return data

        return _do_mock_blackbox

    return _wrapper


@pytest.fixture(name='mock_register')
async def _mock_register(mockserver, common_values, make_eater):
    @mockserver.json_handler('/eats-core-eater/passport/register')
    async def _mock(request):
        eater = make_eater(
            eater_id=common_values['registered_eater_id'],
            passport_uid=common_values['requested_passport_uid'],
            passport_uid_type=common_values['passport_uid_type_portal'],
        )
        return mockserver.make_response(status=201, json={'eater': eater})

    return _mock


@pytest.fixture(name='mock_merge')
async def _mock_merge(mockserver, make_eater):
    @mockserver.json_handler('/eats-core-eater/passport/merge')
    async def _mock(request):
        eater = make_eater(
            eater_id=request.json['eater_id'],
            passport_uid=request.json['passport_uid'],
            passport_uid_type=request.json['passport_uid_type'],
            personal_phone_id=request.json['personal_phone_id'],
            personal_email_id=request.json['personal_email_id'],
        )
        return mockserver.make_response(status=200, json={'eater': eater})

    return _mock


@pytest.fixture(name='mock_delete_phonish_and_merge')
async def _mock_delete_phonish_and_merge(mockserver, make_eater):
    @mockserver.json_handler(
        '/eats-core-eater/passport/delete-phonish-and-merge',
    )
    async def _mock(request):
        to_merge = request.json['to_merge']
        eater = make_eater(
            eater_id=to_merge['eater_id'],
            passport_uid=to_merge['passport_uid'],
            passport_uid_type=to_merge['passport_uid_type'],
            personal_phone_id=to_merge['personal_phone_id'],
            personal_email_id=to_merge['personal_email_id'],
        )
        return mockserver.make_response(status=200, json={'eater': eater})

    return _mock


@pytest.fixture(name='mock_reset_uid_and_merge')
async def _mock_reset_uid_and_merge(mockserver, make_eater):
    @mockserver.json_handler('/eats-core-eater/passport/reset-uid-and-merge')
    async def _mock(request):
        to_merge = request.json['to_merge']
        eater = make_eater(
            eater_id=to_merge['eater_id'],
            passport_uid=to_merge['passport_uid'],
            passport_uid_type=to_merge['passport_uid_type'],
            personal_phone_id=to_merge['personal_phone_id'],
            personal_email_id=to_merge['personal_email_id'],
        )
        return mockserver.make_response(status=200, json={'eater': eater})

    return _mock


@pytest.fixture(name='mock_find_by_id')
async def _mock_find_by_id(mockserver):
    async def _wrapper(eater):
        @mockserver.json_handler('/eats-core-eater/find-by-id')
        async def _mock(request):
            return mockserver.make_response(status=200, json={'eater': eater})

        return _mock

    return _wrapper


@pytest.fixture(name='mock_find_by_id_not_found')
async def _mock_find_by_id_not_found(mockserver):
    @mockserver.json_handler('/eats-core-eater/find-by-id')
    async def _mock(request):
        return mockserver.make_response(
            status=404,
            headers={'X-YaTaxi-Error-Code': 'eater_not_found'},
            json={'code': 'eater_not_found', 'message': 'Eater not found'},
        )

    return _mock


@pytest.fixture(name='mock_find_by_passport_uid')
async def _mock_find_by_passport_uid(mockserver):
    async def _wrapper(eater):
        @mockserver.json_handler('/eats-core-eater/find-by-passport-uid')
        async def _mock(request):
            return mockserver.make_response(status=200, json={'eater': eater})

        return _mock

    return _wrapper


@pytest.fixture(name='mock_ee_find_by_passport_uid')
async def _mock_ee_find_by_passport_uid(mockserver):
    async def _wrapper(eater):
        @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uid')
        async def _mock(request):
            return mockserver.make_response(status=200, json={'eater': eater})

        return _mock

    return _wrapper


@pytest.fixture(name='mock_find_by_passport_uid_not_found')
async def _mock_find_by_passport_uid_not_found(mockserver):
    @mockserver.json_handler('/eats-core-eater/find-by-passport-uid')
    async def _mock(request):
        return mockserver.make_response(
            status=404,
            headers={'X-YaTaxi-Error-Code': 'eater_not_found'},
            json={'code': 'eater_not_found', 'message': 'Eater not found'},
        )

    return _mock


@pytest.fixture(name='mock_find_by_id_multiple')
async def _mock_find_by_id_multiple(mockserver):
    async def _wrapper(eaters_by_ids):
        @mockserver.json_handler('/eats-core-eater/find-by-id')
        async def _mock(request):
            return mockserver.make_response(
                status=200, json={'eater': eaters_by_ids[request.json['id']]},
            )

        return _mock

    return _wrapper


@pytest.fixture(name='mock_ea_login')
async def _mock_ea_login(mockserver):
    @mockserver.json_handler('/eater-authorizer/v1/eater/sessions/login')
    async def _mock(request):
        return mockserver.make_response(json={}, status=200)

    return _mock


@pytest.fixture(name='mock_ea_logout')
async def _mock_ea_logout(mockserver, common_values):
    @mockserver.json_handler('/eater-authorizer/v1/eater/sessions/logout')
    async def _mock(request):
        assert request.json == {
            'inner_session_id': common_values['inner_token'],
        }
        return {}

    return _mock


@pytest.fixture(name='mock_ea_logout_404')
async def _mock_ea_logout_404(mockserver, common_values):
    @mockserver.json_handler('/eater-authorizer/v1/eater/sessions/logout')
    async def _mock(request):
        assert request.json == {
            'inner_session_id': common_values['inner_token'],
        }
        return mockserver.make_response(
            json={
                'code': 'session_data_not_found',
                'message': 'Session is not found',
            },
            status=404,
        )

    return _mock


@pytest.fixture(name='mock_bb_personal_phone_store')
async def _mock_personal_phone_store(mockserver, common_values):
    @mockserver.json_handler('/personal/v1/phones/store')
    async def _mock(request):
        assert request.json['validate'] is True

        if request.json['value'] == common_values['blackbox_secured_phone']:
            return mockserver.make_response(
                json={
                    'id': common_values['blackbox_secured_phone_id'],
                    'value': common_values['blackbox_secured_phone'],
                },
                status=200,
            )

        if request.json['value'] == common_values['blackbox_default_phone']:
            return mockserver.make_response(
                json={
                    'id': common_values['blackbox_default_phone_id'],
                    'value': common_values['blackbox_default_phone'],
                },
                status=200,
            )

        assert False

    return _mock


@pytest.fixture(name='mock_bb_personal_email_store')
async def _mock_bb_personal_email_store(mockserver, common_values):
    @mockserver.json_handler('/personal/v1/emails/store')
    async def _mock(request):
        assert request.json == {
            'value': common_values['blackbox_email'],
            'validate': True,
        }
        return mockserver.make_response(
            json={
                'id': common_values['blackbox_email_id'],
                'value': common_values['blackbox_email'],
            },
            status=200,
        )

    return _mock


@pytest.fixture(name='mock_find_by_personal_phone_id_not_found')
async def _mock_find_by_personal_phone_id_not_found(mockserver):
    @mockserver.json_handler('/eats-core-eater/find-one-by-personal-phone-id')
    async def _mock(request):
        return mockserver.make_response(
            headers={'X-YaTaxi-Error-Code': 'eater_not_found'},
            json={'code': 'eater_not_found', 'message': ''},
            status=404,
        )

    return _mock


@pytest.fixture(name='mock_find_by_personal_phone_id')
async def _mock_find_by_personal_phone_id(mockserver):
    async def _wrapper(eater):
        @mockserver.json_handler(
            '/eats-core-eater/find-one-by-personal-phone-id',
        )
        async def _mock(request):
            return mockserver.make_response(json={'eater': eater}, status=200)

        return _mock

    return _wrapper


@pytest.fixture(name='mock_delete_phonish')
async def _mock_delete_phonish(mockserver):
    @mockserver.json_handler('/eats-core-eater/passport/delete-phonish')
    async def _mock(request):
        return mockserver.make_response(status=204)

    return _mock


@pytest.fixture(name='mock_reset_uid')
async def _mock_reset_uid(mockserver):
    @mockserver.json_handler('/eats-core-eater/passport/reset-uid')
    async def _mock(request):
        return mockserver.make_response(status=204)

    return _mock


@pytest.fixture(name='mock_core_login')
async def _mock_core_login(mockserver):
    @mockserver.json_handler('/eats-core-eater/passport/login')
    async def _mock(request):
        return mockserver.make_response(json={}, status=204)

    return _mock


@pytest.fixture(name='mock_fail_stq_transfer_card')
async def _mock_fail_stq_transfer_card(mockserver):
    @mockserver.json_handler('/stq-agent/queues/api/add/eats_transfer_card')
    async def _mock(request):
        return mockserver.make_response(json={}, status=500)

    return _mock
