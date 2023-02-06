def check_csv_equality(val1, val2, message):
    assert set(x.strip() for x in val1.split(',')) == set(
        x.strip() for x in val2.split(',')
    ), message


async def test_happy_path(taxi_userver_sample, mockserver):
    headers = {
        'X-Login-Id': '123',
        'X-Yandex-UID': '123',
        'X-Eats-Session': '123',
        'X-Eats-Session-Type': 'appclip',
        'X-YaTaxi-Pass-Flags': 'portal,no-login',
        'X-YaTaxi-User': (
            'personal_phone_id=1,personal_email_id=2,'
            'eats_user_id=3,eats_partner_user_id=4'
        ),
        'X-Eats-User': (
            'user_id=eater1,personal_phone_id=4,'
            'personal_email_id=5,partner_user_id=partner1,'
            'eater_uuid=yd7d8s9dud'
        ),
        'Cookie': 'PHPSESSID=123',
        'X-Remote-IP': '127.0.0.0',
        'X-Request-Language': 'ru',
        'X-Request-Application': (
            'x=y,app_name=xxx,app_ver1=1,app_ver2=2,app_brand=eats-clip'
        ),
        'X-Device-Id': 'qwerty123456',
        'X-YaTaxi-Bound-Sessions': (
            'taxi:taxi_old_session,eats:eats_old_session'
        ),
        'X-YaTaxi-Session': 'taxi:taxi_session',
        'X-AppMetrica-DeviceId': 'some-app-metrica-device-id',
    }

    @mockserver.json_handler('userver-sample/eats/v1/test')
    async def _mock(request):
        for header in headers:
            check_csv_equality(
                request.headers[header], headers[header], header,
            )
        return {
            'inner_session': '123',
            'login_id': '123',
            'session_type': 'appclip',
            'yandex_uid': '123',
            'eats_session': '123',
            'taxi_personal': {
                'phone_id': '1',
                'email_id': '2',
                'eats_id': '3',
                'eats_partner_user_id': '4',
            },
            'eats_personal': dict(
                user_id='eater1',
                phone_id='4',
                email_id='5',
                partner_user_id='partner1',
                eater_uuid='eater_uuid=yd7d8s9dud',
            ),
            'flags': {'portal': True, 'no-login': True},
            'locale': 'ru',
            'is_eats_session_domain': False,
            'is_taxi_session_domain': True,
            'app_vars': {
                'x': 'y',
                'app_name': 'xxx',
                'app_ver1': '1',
                'app_ver2': '2',
                'app_brand': 'eats-clip',
            },
            'remote_ip': '127.0.0.0',
            'device_id': 'qwerty123456',
            'bound_sessions': [
                'taxi:taxi_old_session',
                'eats:eats_old_session',
            ],
            'taxi_session': 'taxi:taxi_session',
            'raw_app_var': (
                'app_brand=eats-clip,app_ver1=1,app_name=xxx,app_ver2=2,x=y'
            ),
            'raw_eats_personal': (
                'user_id=eater1,personal_phone_id=4,'
                'personal_email_id=5,partner_user_id=partner1,'
                'eater_uuid=yd7d8s9dud'
            ),
            'raw_app_metrics_device_id': 'some-app-metrica-device-id',
        }

    response = await taxi_userver_sample.post('/eats/v1/test', headers=headers)
    response_json = response.json()

    assert response.status_code == 200
    assert response_json['inner_session'] == '123'
    assert response_json['login_id'] == '123'
    assert response_json['session_type'] == 'appclip'
    assert response_json['yandex_uid'] == '123'
    assert response_json['eats_session'] == '123'
    assert response_json['taxi_personal']['phone_id'] == '1'
    assert response_json['taxi_personal']['email_id'] == '2'
    assert response_json['eats_personal']['user_id'] == 'eater1'
    assert response_json['eats_personal']['phone_id'] == '4'
    assert response_json['eats_personal']['email_id'] == '5'
    assert response_json['eats_personal']['partner_user_id'] == 'partner1'
    assert response_json['taxi_personal']['eats_id'] == '3'
    assert response_json['eats_personal']['eater_uuid'] == 'yd7d8s9dud'
    assert response_json['flags'] == {'portal': True, 'no-login': True}
    assert response_json['locale'] == 'ru'
    assert response_json['app_vars'] == {
        'x': 'y',
        'app_name': 'xxx',
        'app_ver1': '1',
        'app_ver2': '2',
        'app_brand': 'eats-clip',
    }
    assert response_json['remote_ip'] == '127.0.0.0'
    assert response_json['device_id'] == 'qwerty123456'
    assert set(response_json['bound_sessions']) == set(
        ['taxi:taxi_old_session', 'eats:eats_old_session'],
    )
    assert response_json['taxi_session'] == 'taxi:taxi_session'
    assert not response_json['is_eats_session_domain']
    assert response_json['is_taxi_session_domain']
    check_csv_equality(
        response_json['raw_eats_personal'],
        'user_id=eater1,personal_phone_id=4,'
        'personal_email_id=5,partner_user_id=partner1,eater_uuid=yd7d8s9dud',
        'raw_eats_personal',
    )
    check_csv_equality(
        response_json['raw_app_var'],
        'app_brand=eats-clip,app_ver1=1,app_name=xxx,app_ver2=2,x=y',
        'raw_app_var',
    )

    assert _mock.has_calls


async def test_auth_fail(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        '/eats/v1/test',
        headers={
            'X-Login-Id': '123',
            'X-Yandex-UID': '123',
            'X-Eats-Session': '123',
            'X-YaTaxi-Pass-Flags': 'portal,no-login',
            'X-YaTaxi-User': 'personal_phone_id=1,personal_email_id=2',
            'Cookie': 'PHPSESSID=123',
            'X-Remote-IP': '127.0.0.0',
            'X-Request-Language': 'ru',
            'X-Request-Application': (
                'x=y,app_name=xxx,app_ver1=1,app_ver2=2,app_brand=eats-clip'
            ),
        },
    )
    assert response.status_code == 401


async def test_auth_by_partner(taxi_userver_sample, mockserver):
    @mockserver.json_handler('userver-sample/eats/v1/test')
    async def _mock(request):
        return {
            'inner_session': '123',
            'login_id': '123',
            'session_type': 'appclip',
            'yandex_uid': '123',
            'eats_session': '123',
            'taxi_personal': {
                'phone_id': '1',
                'email_id': '2',
                'eats_id': '3',
                'eats_partner_user_id': '4',
            },
            'eats_personal': dict(
                user_id='eater1',
                phone_id='4',
                email_id='5',
                partner_user_id='partner1',
                eater_uuid='yd7d8s9dud',
            ),
            'flags': {'portal': True, 'no-login': True},
            'locale': 'ru',
            'is_eats_session_domain': False,
            'is_taxi_session_domain': True,
            'app_vars': {
                'x': 'y',
                'app_name': 'xxx',
                'app_ver1': '1',
                'app_ver2': '2',
                'app_brand': 'eats-clip',
            },
            'remote_ip': '127.0.0.0',
            'device_id': 'qwerty123456',
            'bound_sessions': [
                'taxi:taxi_old_session',
                'eats:eats_old_session',
            ],
            'taxi_session': 'taxi:taxi_session',
            'raw_app_var': (
                'app_brand=eats-clip,app_ver1=1,app_name=xxx,app_ver2=2,x=y'
            ),
            'raw_eats_personal': 'partner_user_id=partner1',
            'raw_app_metrics_device_id': 'some-app-metrica-device-id',
        }

    response = await taxi_userver_sample.post(
        '/eats/v1/test',
        headers={
            'X-Eats-User': 'partner_user_id=partner1',
            'X-Login-Id': '123',
            'X-Yandex-UID': '123',
            'X-Eats-Session': '123',
            'X-YaTaxi-Pass-Flags': 'portal,no-login',
            'X-YaTaxi-User': 'personal_phone_id=1,personal_email_id=2',
            'Cookie': 'PHPSESSID=123',
            'X-Remote-IP': '127.0.0.0',
            'X-Request-Language': 'ru',
            'X-Request-Application': (
                'x=y,app_name=xxx,app_ver1=1,app_ver2=2,app_brand=eats-clip'
            ),
        },
    )
    assert response.status_code == 200


async def test_auth_with_only_eats(taxi_userver_sample, mockserver):
    @mockserver.json_handler('userver-sample/eats/v1/test')
    async def _mock(request):
        return {
            'inner_session': '123',
            'login_id': '123',
            'session_type': 'appclip',
            'yandex_uid': '123',
            'eats_session': '123',
            'taxi_personal': {
                'phone_id': '1',
                'email_id': '2',
                'eats_id': '3',
                'eats_partner_user_id': '4',
            },
            'eats_personal': dict(
                user_id='3',
                phone_id='4',
                email_id='5',
                partner_user_id='4',
                eater_uuid='yd7d8s9dud',
            ),
            'flags': {'portal': True, 'no-login': True},
            'locale': 'ru',
            'app_vars': {
                'x': 'y',
                'app_name': 'xxx',
                'app_ver1': '1',
                'app_ver2': '2',
                'app_brand': 'eats-clip',
            },
            'remote_ip': '127.0.0.0',
            'device_id': '',
            'taxi_session': 'eats:123',
            'is_eats_session_domain': True,
            'is_taxi_session_domain': False,
            'bound_sessions': [
                'taxi:taxi_old_session',
                'eats:eats_old_session',
            ],
            'raw_app_var': (
                'app_brand=eats-clip,app_ver1=1,app_name=xxx,app_ver2=2,x=y'
            ),
            'raw_eats_personal': (
                'user_id=eater1,personal_phone_id=4,'
                'personal_email_id=5,partner_user_id=partner1,'
                'eater_uuid=yd7d8s9dud'
            ),
            'raw_app_metrics_device_id': 'some-app-metrica-device-id',
        }

    response = await taxi_userver_sample.post(
        '/eats/v1/test',
        headers={
            'X-Login-Id': '123',
            'X-Yandex-UID': '123',
            'X-Eats-Session': '123',
            'X-YaTaxi-Pass-Flags': 'portal,no-login',
            'X-Eats-User': 'user_id=3,partner_user_id=4,eater_uuid=yd7d8s9dud',
            'Cookie': 'PHPSESSID=123',
            'X-Remote-IP': '127.0.0.0',
            'X-Request-Language': 'ru',
            'X-Request-Application': (
                'x=y,app_name=xxx,app_ver1=1,app_ver2=2,app_brand=eats-clip'
            ),
            'X-YaTaxi-Session': 'eats:123',
            'X-YaTaxi-Bound-Sessions': (
                'taxi:taxi_old_session,eats:eats_old_session'
            ),
        },
    )
    assert response.status_code == 200


EATS_HEADERS = {
    'X-Login-Id': '123',
    'X-Yandex-UID': '123',
    'X-Eats-Session': '123',
    'X-Eats-Session-Type': 'appclip',
    'X-YaTaxi-Pass-Flags': 'portal,no-login',
    'X-YaTaxi-User': (
        'personal_phone_id=1,personal_email_id=2,'
        'eats_user_id=3,eats_partner_user_id=4'
    ),
    'X-Eats-User': 'user_id=3,partner_user_id=4',
    'Cookie': 'PHPSESSID=123',
    'X-Remote-IP': '127.0.0.0',
    'X-Request-Language': 'ru',
    'X-Request-Application': (
        'x=y,app_name=xxx,app_ver1=1,app_ver2=2,app_brand=eats-clip'
    ),
    'X-YaTaxi-Session': 'eats:123',
    'X-YaTaxi-Bound-Sessions': 'taxi:taxi_old_session,eats:eats_old_session',
    'X-AppMetrica-DeviceId': 'some-app-metrica-device-id',
}
SUPERAPP_HEADERS = {
    'X-Login-Id': '123',
    'X-Yandex-UID': '123',
    'X-YaTaxi-Pass-Flags': 'portal,no-login',
    'X-YaTaxi-User': (
        'personal_phone_id=1,personal_email_id=2,'
        'eats_user_id=3,eats_partner_user_id=4'
    ),
    'X-Remote-IP': '127.0.0.0',
    'X-Request-Language': 'ru',
    'X-Request-Application': (
        'x=y,app_name=xxx,app_ver1=1,app_ver2=2,app_brand=eats-clip'
    ),
    'X-YaTaxi-UserId': '123',
    'X-YaTaxi-Session': 'eats:123',
    'X-YaTaxi-Bound-Sessions': 'taxi:taxi_old_session,eats:eats_old_session',
    'X-AppMetrica-DeviceId': 'some-app-metrica-device-id',
}

HEADERS_FOR_CHECK = [
    'X-Login-Id',
    'X-Yandex-UID',
    'X-YaTaxi-Pass-Flags',
    'X-YaTaxi-User',
    'X-Remote-IP',
    'X-Request-Language',
    'X-Request-Application',
    'X-YaTaxi-Session',
    'X-YaTaxi-Bound-Sessions',
    'X-AppMetrica-DeviceId',
]


async def test_convert_eats_to_superapp(taxi_userver_sample, mockserver):
    @mockserver.json_handler(
        'userver-sample/eats/v1/test_superapp_to_eats_auth',
    )
    async def _mock(request):
        for header in HEADERS_FOR_CHECK:
            check_csv_equality(
                request.headers[header], SUPERAPP_HEADERS[header], header,
            )
        return {}

    response = await taxi_userver_sample.post(
        '/eats/v1/test_eats_auth_to_superapp', headers=EATS_HEADERS,
    )

    assert response.status_code == 200
    assert _mock.has_calls


async def test_convert_superapp_tp_eats(taxi_userver_sample, mockserver):
    @mockserver.json_handler(
        'userver-sample/eats/v1/test_eats_auth_to_superapp',
    )
    async def _mock(request):
        headers_for_check = HEADERS_FOR_CHECK.copy()
        headers_for_check.append('X-Eats-User')
        for header in headers_for_check:
            check_csv_equality(
                request.headers[header], EATS_HEADERS[header], header,
            )
        return {}

    response = await taxi_userver_sample.post(
        '/eats/v1/test_superapp_to_eats_auth', headers=SUPERAPP_HEADERS,
    )

    assert response.status_code == 200
    assert _mock.has_calls
