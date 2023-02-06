import json


async def test_route_personal_ids_phone(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/personal_ids/phone/test')
    def _test(request):
        stats['call-test'] += 1

        assert request.headers['X-Yandex-UID'] == '1001026'
        assert request.headers['X-YaTaxi-User'] == 'personal_phone_id=1026001'

        return mockserver.make_response('{"text": "smth"}', status=201)

    blackbox_service.set_token_info(
        'test_token', uid='1001026', user_ticket='USER_TICKET',
    )

    response = await taxi_passenger_authorizer.post(
        '4.0/personal_ids/phone/test',
        data=json.dumps({}),
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '123451026'},
    )
    assert stats['call-test'] == 1
    assert response.status_code == 201
    assert response.json() == {'text': 'smth'}


async def test_route_personal_ids_email_by_phone(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/personal_ids/email/test')
    def _test(request):
        stats['call-test'] += 1

        assert request.headers['X-Yandex-UID'] == '1001026'
        assert request.headers['X-YaTaxi-User'] == 'personal_email_id=1026501'

        return mockserver.make_response('{"text": "smth"}', status=201)

    blackbox_service.set_token_info(
        'test_token', uid='1001026', user_ticket='USER_TICKET',
    )

    response = await taxi_passenger_authorizer.post(
        '4.0/personal_ids/email/test',
        data=json.dumps({}),
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '123451026'},
    )
    assert stats['call-test'] == 1
    assert response.status_code == 201
    assert response.json() == {'text': 'smth'}


async def test_unauth_no_personal_request(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    @mockserver.json_handler('/4.0/personal_ids/email/test')
    def _test(request):
        assert False

    response = await taxi_passenger_authorizer.post(
        '4.0/personal_ids/email/test',
        data=json.dumps({}),
        # No bearer
        headers={'X-YaTaxi-UserId': '123451026'},
    )
    assert response.status_code == 401


async def test_route_personal_ids_email_by_phone_noemail_nocache(
        taxi_passenger_authorizer, blackbox_service, mockserver, mongodb,
):
    stats = {'call-test': 0, 'expect-user': None}

    @mockserver.json_handler('/4.0/personal_ids/email/test')
    def _test(request):
        stats['call-test'] += 1

        assert request.headers['X-Yandex-UID'] == '1111026'
        if stats['expect-user']:
            assert request.headers['X-YaTaxi-User'] == stats['expect-user']
        else:
            assert 'X-YaTaxi-User' not in request.headers

        return mockserver.make_response('{"text": "smth"}', status=201)

    blackbox_service.set_token_info(
        'test_token11', uid='1111026', user_ticket='USER_TICKET',
    )

    response = await taxi_passenger_authorizer.post(
        '4.0/personal_ids/email/test',
        data=json.dumps({}),
        bearer='test_token11',
        headers={'X-YaTaxi-UserId': '123511026'},
    )
    assert stats['call-test'] == 1
    assert response.status_code == 201
    assert response.json() == {'text': 'smth'}

    # Insert email for the user and check that missing email is not cached
    mongodb.user_emails.insert(
        {
            'confirmation_code': 'f35c2b0f6ae024a22812b46e6f9452b6dcd6',
            'personal_email_id': '1026500',
            'yandex_uid': '1111026',
        },
    )

    stats['expect-user'] = 'personal_email_id=1026500'
    response = await taxi_passenger_authorizer.post(
        '4.0/personal_ids/email/test',
        data=json.dumps({}),
        bearer='test_token11',
        headers={'X-YaTaxi-UserId': '123511026'},
    )
    assert stats['call-test'] == 2
    assert response.status_code == 201
    assert response.json() == {'text': 'smth'}


# test_route_personal_ids_email_by_yandex_uid
async def test_route_personal_ids_eml2(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/personal_ids/email/test')
    def _test(request):
        stats['call-test'] += 1

        assert request.headers['X-Yandex-UID'] == '1071026'
        assert request.headers['X-YaTaxi-User'] == 'personal_email_id=1026507'

        return mockserver.make_response('{"text": "smth"}', status=201)

    blackbox_service.set_token_info(
        'test_token', uid='1071026', user_ticket='USER_TICKET',
    )

    response = await taxi_passenger_authorizer.post(
        '4.0/personal_ids/email/test',
        data=json.dumps({}),
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '123471026'},
    )
    assert stats['call-test'] == 1
    assert response.status_code == 201
    assert response.json() == {'text': 'smth'}


# test_route_personal_ids_email_by_bound_phonishes_yandex_uids
async def test_route_personal_ids_eml3(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/personal_ids/email/test')
    def _test(request):
        stats['call-test'] += 1

        assert request.headers['X-Yandex-UID'] == '1081026'
        assert request.headers['X-YaTaxi-User'] == 'personal_email_id=1026518'
        assert 'X-YaTaxi-Bound-Uids' not in request.headers

        return mockserver.make_response('{"text": "smth"}', status=201)

    blackbox_service.set_token_info(
        'test_token', uid='1081026', user_ticket='USER_TICKET',
    )

    response = await taxi_passenger_authorizer.post(
        '4.0/personal_ids/email/test',
        data=json.dumps({}),
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '123481026'},
    )
    assert stats['call-test'] == 1
    assert response.status_code == 201
    assert response.json() == {'text': 'smth'}


# test_route_personal_ids_email_by_bound_phonishes_yandex_uids2
# check users.yandex_uid prefer to phones_confirmations.uid's
async def test_route_personal_ids_eml4(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/personal_ids/email/test')
    def _test(request):
        stats['call-test'] += 1

        assert request.headers['X-Yandex-UID'] == '1091026'
        assert request.headers['X-YaTaxi-User'] == 'personal_email_id=1026509'
        assert 'X-YaTaxi-Bound-Uids' not in request.headers

        return mockserver.make_response('{"text": "smth"}', status=201)

    blackbox_service.set_token_info(
        'test_token', uid='1091026', user_ticket='USER_TICKET',
    )

    response = await taxi_passenger_authorizer.post(
        '4.0/personal_ids/email/test',
        data=json.dumps({}),
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '123491026'},
    )
    assert stats['call-test'] == 1
    assert response.status_code == 201
    assert response.json() == {'text': 'smth'}


# test_route_personal_ids_phone_and_email
async def test_route_personal_ids_pe(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/personal_ids/phone_and_email/test')
    def _test(request):
        stats['call-test'] += 1

        assert request.headers['X-Yandex-UID'] == '1001026'
        expected_res = 'personal_phone_id=1026001, personal_email_id=1026501'
        assert request.headers['X-YaTaxi-User'] == expected_res
        assert 'X-YaTaxi-Bound-Uids' not in request.headers

        return mockserver.make_response('{"text": "smth"}', status=201)

    blackbox_service.set_token_info(
        'test_token', uid='1001026', user_ticket='USER_TICKET',
    )

    response = await taxi_passenger_authorizer.post(
        '4.0/personal_ids/phone_and_email/test',
        data=json.dumps({}),
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '123451026'},
    )
    assert stats['call-test'] == 1
    assert response.status_code == 201
    assert response.json() == {'text': 'smth'}


async def test_route_bounded_uids(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/personal_ids/bounded_uids/test')
    def _test(request):
        stats['call-test'] += 1

        assert request.headers['X-Yandex-UID'] == '1081026'
        assert request.headers['X-YaTaxi-Bound-Uids'] == '1181026,1281026'

        return mockserver.make_response('{"text": "smth"}', status=201)

    blackbox_service.set_token_info(
        'test_token', uid='1081026', user_ticket='USER_TICKET',
    )

    response = await taxi_passenger_authorizer.post(
        '4.0/personal_ids/bounded_uids/test',
        data=json.dumps({}),
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '123481026'},
    )
    assert stats['call-test'] == 1
    assert response.status_code == 201
    assert response.json() == {'text': 'smth'}


# test_route_bounded_uids_not_portal_account
async def test_route_bounded_uids_np(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/personal_ids/bounded_uids/test')
    def _test(request):
        stats['call-test'] += 1

        assert request.headers['X-Yandex-UID'] == '1071026'
        assert 'X-YaTaxi-Bound-Uids' not in request.headers

        return mockserver.make_response('{"text": "smth"}', status=201)

    blackbox_service.set_token_info(
        'test_token', uid='1071026', user_ticket='USER_TICKET',
    )

    response = await taxi_passenger_authorizer.post(
        '4.0/personal_ids/bounded_uids/test',
        data=json.dumps({}),
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '123471026'},
    )
    assert stats['call-test'] == 1
    assert response.status_code == 201
    assert response.json() == {'text': 'smth'}


async def test_route_bounded_uids_empty(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/personal_ids/bounded_uids/test')
    def _test(request):
        stats['call-test'] += 1

        assert request.headers['X-Yandex-UID'] == '1101026'
        assert request.headers['X-YaTaxi-Bound-Uids'] == ''

        return mockserver.make_response('{"text": "smth"}', status=201)

    blackbox_service.set_token_info(
        'test_token', uid='1101026', user_ticket='USER_TICKET',
    )

    response = await taxi_passenger_authorizer.post(
        '4.0/personal_ids/bounded_uids/test',
        data=json.dumps({}),
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '123501026'},
    )
    assert stats['call-test'] == 1
    assert response.status_code == 201
    assert response.json() == {'text': 'smth'}
