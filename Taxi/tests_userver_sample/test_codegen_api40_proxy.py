import collections


LIST_HEADERS = [
    'X-YaTaxi-User',
    'X-YaTaxi-Pass-Flags',
    'X-YaTaxi-Bound-Uids',
    'X-YaTaxi-Bound-UserIds',
    'X-Request-Application',
    'X-Ya-User-Ticket',
]

FLAGS = (
    'phonish,ya-plus,cashback-plus,no-login,phone_confirmation_required,'
    'credentials=session'
)


async def test_autogen_service_tvm_disabled(taxi_userver_sample, mockserver):
    headers = {
        'X-Yandex-Login': 'userx',
        'X-Login-Id': 'login_id_xx',
        'X-Yandex-UID': '999',
        'X-YaTaxi-UserId': 'test_user_id_xxx',
        'X-YaTaxi-PhoneId': 'test_phone_id_xxx',
        'X-Ya-User-Ticket': 'test_user_ticket',
        'X-YaTaxi-User': (
            'personal_phone_id=1,personal_email_id=2,eats_user_id=3'
        ),
        'X-YaTaxi-Pass-Flags': FLAGS,
        'X-YaTaxi-Bound-Uids': 'a,b,cc',
        'X-YaTaxi-Bound-UserIds': 'u1,u2,u3',
        'X-Request-Language': 'ru',
        'X-Request-Application': 'app_name=1,app_ver=2',
        'X-Remote-IP': '126.3.3.9',
    }

    @mockserver.handler('/userver-sample/4.0/proxy')
    async def mock_proxy(request):
        header_counter = collections.Counter(
            header.lower() for header, _ in request.headers.items()
        )
        for header in headers:
            assert header_counter[header.lower()] == 1
            if header in LIST_HEADERS:
                assert collections.Counter(
                    request.headers[header].split(','),
                ) == collections.Counter(headers[header].split(','))
            else:
                assert request.headers[header] == headers[header]

        return mockserver.make_response('', 200)

    response = await taxi_userver_sample.get('4.0/proxy', headers=headers)
    assert response.status_code == 200
    assert mock_proxy.times_called == 1
