import collections


async def test_happy_path(taxi_userver_sample, mockserver):
    headers = {
        'X-YaTaxi-Pass-Flags': 'portal,no-login',
        'X-YaTaxi-User': (
            'personal_phone_id=1,personal_email_id=2,'
            'eats_user_id=3,eats_partner_user_id=4'
        ),
        'X-YaTaxi-Session': 'eats:123',
        'X-YaTaxi-Bound-Sessions': 'eats:xxx, eats:yyy',
        'X-Remote-IP': '127.0.0.0',
        'X-Request-Language': 'ru',
        'X-Request-Application': 'x=y,app_name=xxx,app_ver1=1,app_ver2=2',
        'X-YaTaxi-UserId': '123',
    }

    @mockserver.json_handler('userver-sample/superapp/test')
    async def _mock(request):
        for header in headers:
            assert set(
                x.strip() for x in request.headers[header].split(',')
            ) == set(x.strip() for x in headers[header].split(','))
        return {}

    response = await taxi_userver_sample.post(
        '/superapp/test', headers=headers,
    )
    assert response.status_code == 200


async def test_auth_fail(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        '/superapp/test',
        headers={
            'X-YaTaxi-Pass-Flags': 'portal,no-login',
            'X-YaTaxi-User': (
                'personal_phone_id=1,personal_email_id=2,'
                'eats_uesr_id=3,eats_partner_user_id=4'
            ),
            'X-YaTaxi-Bound-Sessions': 'eats:xxx, eats:yyy',
        },
    )
    assert response.status_code == 403


async def test_40_to_superapp(taxi_userver_sample, mockserver):
    api40_headers = {
        'X-YaTaxi-Pass-Flags': 'portal,no-login',
        'X-YaTaxi-User': (
            'personal_phone_id=1,personal_email_id=2,'
            'eats_user_id=3,eats_partner_user_id=4'
        ),
        'X-Yandex-Uid': '1',
        'X-YaTaxi-UserId': '123',
        'X-YaTaxi-Bound-UserIds': 'xxx, yyy',
        'X-YaTaxi-Bound-Sessions': 'taxi:xxx, taxi:yyy',
        'X-Remote-IP': '127.0.0.0',
        'X-Request-Language': 'ru',
        'X-Request-Application': 'x=y,app_name=xxx,app_ver1=1,app_ver2=2',
    }
    superapp_headers = {
        'X-YaTaxi-Pass-Flags': 'portal,no-login',
        'X-YaTaxi-User': (
            'personal_phone_id=1,personal_email_id=2,'
            'eats_user_id=3,eats_partner_user_id=4'
        ),
        'X-Yandex-Uid': '1',
        'X-YaTaxi-UserId': '123',
        'X-YaTaxi-Session': 'taxi:123',
        'X-YaTaxi-Bound-UserIds': 'xxx, yyy',
        'X-YaTaxi-Bound-Sessions': 'taxi:xxx, taxi:yyy',
        'X-Remote-IP': '127.0.0.0',
        'X-Request-Language': 'ru',
        'X-Request-Application': 'x=y,app_name=xxx,app_ver1=1,app_ver2=2',
    }

    @mockserver.json_handler('userver-sample/superapp/test')
    async def _mock(request):
        header_counter = collections.Counter(
            header.lower() for header, _ in request.headers.items()
        )
        for header in superapp_headers:
            assert header_counter[header.lower()] == 1
            assert set(
                x.strip() for x in request.headers[header].split(',')
            ) == set(x.strip() for x in superapp_headers[header].split(','))
        return {}

    response = await taxi_userver_sample.post(
        '/superapp/4.0/proxy-to-superapp', headers=api40_headers,
    )
    assert response.status_code == 200
