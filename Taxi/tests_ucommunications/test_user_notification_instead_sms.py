import pytest

from testsuite.utils import http


@pytest.fixture(name='mock_xiva')
def _mock_xiva(mockserver):
    class Service:
        @staticmethod
        @mockserver.json_handler('/xiva/v2/send')
        def send(request):
            assert request.args['user'] == 'my_user_id'
            assert request.json == {'payload': 'Вам SMS: Добрый день!'}
            return mockserver.make_response(
                'OK', 200, headers={'TransitID': 'id'},
            )

    return Service()


@pytest.fixture(name='mock_xiva_bad')
def _mock_xiva_bad(mockserver):
    class Service:
        @staticmethod
        @mockserver.json_handler('/xiva/v2/send')
        def send(request):
            raise mockserver.TimeoutError()

    return Service()


@pytest.fixture(name='mock_yasms')
def _mock_yasms(mockserver):
    class Service:
        @staticmethod
        @mockserver.json_handler('/yasms/sendsms')
        def send(request):
            return mockserver.make_response(
                '<doc><message-sent id="127000000003456" /></doc>', 200,
            )

    return Service()


@pytest.fixture(name='mock_yasms_limit_exceed')
def _mock_yasms_limit_exceed(mockserver):
    class Service:
        @staticmethod
        @mockserver.json_handler('/yasms/sendsms')
        def send(request):
            return (
                mockserver.make_response(
                    """<doc>
                       <error>SMS limit for this phone is exceeded</error>
                       <errorcode>LIMITEXCEEDED</errorcode>
                    </doc>""",
                    200,
                ),
            )

    return Service()


@pytest.fixture(name='mock_personal')
def _mock_personal(mockserver):
    @mockserver.json_handler('/personal/v1/phones/find')
    def _personal_phones_find(request):
        return {'id': 'personal_phone_id', 'value': '+70001112233'}

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _phones_retrieve(request):
        return {'id': 'personal_phone_id', 'value': '+70001112233'}


@pytest.fixture(name='mock_user_api')
def _mock_user_api(mockserver):
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

    @mockserver.json_handler('/user-api/user_phones/by_personal/retrieve')
    def _user_phones_by_personal_retrieve(request):
        return {
            'id': 'phone_id',
            'phone': '+70001112233',
            'type': 'yandex',
            'created': '2019-02-01T13:00:00+0000',
            'updated': '2019-02-01T13:00:00+0000',
            'stat': {
                'total': 0,
                'big_first_discounts': 0,
                'complete': 0,
                'complete_card': 0,
                'complete_apple': 0,
                'complete_google': 0,
                'fake': 0,
            },
            'is_loyal': False,
            'is_yandex_staff': False,
            'is_taxi_staff': False,
        }

    @mockserver.json_handler('/user-api/user_phones/by-natural-id')
    def _user_phones_by_natural_id(request):
        return {
            'id': 'phone_id',
            'phone': '+70001112233',
            'personal_phone_id': 'personal_phone_id',
            'type': 'yandex',
            'created': '2019-02-01T13:00:00+0000',
            'updated': '2019-02-01T13:00:00+0000',
            'stat': {
                'big_first_discounts': 0,
                'complete': 0,
                'complete_card': 0,
                'complete_apple': 0,
                'complete_google': 0,
                'fake': 0,
                'total': 0,
            },
            'is_loyal': True,
            'is_yandex_staff': True,
            'is_taxi_staff': True,
        }

    @mockserver.json_handler('/user-api/user_phones/by_personal/retrieve_bulk')
    def _phones_retrieve_bulk(request):
        return {'items': [{}]}


@pytest.fixture(name='sms_intents_admin')
def _mock_sms_intents_admin(mockserver):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(load_json):
        return load_json('sms_intents.json')


async def _send_push_or_sms(taxi_ucommunications):
    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'user_id': 'my_user_id',
            'text': 'Добрый день!',
            'intent': 'notification_instead_sms',
        },
    )
    return response


@pytest.mark.experiments3(
    filename='user_notification_instead_sms_experiment.json',
)
async def test_send_by_phone(
        taxi_ucommunications,
        mock_user_api,
        mock_personal,
        mock_xiva,
        mock_yasms,
        mongodb,
        mockserver,
        load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'notification_instead_sms',
        },
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'forwarded'
    assert mock_xiva.send.times_called == 1
    assert mock_yasms.send.times_called == 0

    # Ensure fallback info added to notification acknowledge
    acks = list(
        mongodb.user_notification_ack_queue.find(
            {'fallback.request.intent': 'notification_instead_sms'},
            {'_id': False},
        ),
    )
    assert len(acks) == 1
    fallback = acks[0]['fallback']
    assert fallback['request'].pop('id') is not None
    assert fallback['request'].pop('meta') is not None
    assert fallback == {
        'channel': 'sms',
        'request': {
            'intent': 'notification_instead_sms',
            'mask_text': False,
            'phone': '+70001112233',
            'phone_id': 'personal_phone_id',
            'provider': '',
            'recipient_id': {'user_id': ''},
            'recipient_type': 'user',
            'text': 'Добрый день!',
            'sender': '',
        },
    }


@pytest.mark.experiments3(
    filename='user_notification_instead_sms_experiment.json',
)
async def test_send_by_user_id(
        taxi_ucommunications,
        mock_user_api,
        mock_personal,
        mock_xiva,
        mock_yasms,
        mockserver,
        load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'user_id': 'my_user_id',
            'text': 'Добрый день!',
            'intent': 'notification_instead_sms',
        },
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'forwarded'
    assert mock_xiva.send.times_called == 1
    assert mock_yasms.send.times_called == 0


@pytest.mark.experiments3(
    filename='user_notification_instead_sms_experiment.json',
)
async def test_fallback_to_sms_on_error(
        taxi_ucommunications,
        mock_user_api,
        mock_personal,
        mock_xiva_bad,
        mock_yasms,
        mockserver,
        load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'user_id': 'my_user_id',
            'text': 'Добрый день!',
            'intent': 'notification_instead_sms',
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    response_json.pop('message_id')
    assert response_json == {
        'code': '200',
        'message': 'OK',
        'content': 'Добрый день!',
        'status': 'sent',
    }
    assert mock_xiva_bad.send.times_called == 3
    assert mock_yasms.send.times_called == 1


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_EXPIRE_ACKNOWLEDGE_WORKER_ENABLED=True,
)
@pytest.mark.experiments3(
    filename='user_notification_instead_sms_experiment.json',
)
async def test_fallback_to_sms_on_ack_expired(
        taxi_ucommunications,
        taxi_config,
        mocked_time,
        testpoint,
        mock_user_api,
        mock_personal,
        mock_xiva,
        mock_yasms,
        mongodb,
        mockserver,
        load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    @testpoint('user-notification-expire-acknowledge-worker-finish')
    def worker_finished(data):
        assert data == {'fetched': 1, 'sent': 1, 'error': 0, 'skip': 0}

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'user_id': 'my_user_id',
            'text': 'Добрый день!',
            'intent': 'notification_instead_sms',
        },
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'forwarded'
    assert mock_xiva.send.times_called == 1
    assert mock_yasms.send.times_called == 0

    mocked_time.sleep(60 * 60)
    await taxi_ucommunications.invalidate_caches(clean_update=False)

    await taxi_ucommunications.run_task(
        'user-notification-expire-acknowledge-worker',
    )
    await worker_finished.wait_call()
    assert mock_yasms.send.times_called == 1


@pytest.mark.parametrize(
    'is_sms_error_temporary,intent_name',
    [
        (True, 'notification_instead_sms_ignore_errors'),
        (False, 'notification_instead_sms_no_ignore_errors'),
    ],
)
@pytest.mark.now('2020-07-01T18:00:06+00:00')
@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_EXPIRE_ACKNOWLEDGE_WORKER_ENABLED=True,
)
@pytest.mark.experiments3(
    filename='user_notification_instead_sms_experiment.json',
)
async def test_fallback_to_sms_failed(
        taxi_ucommunications,
        taxi_config,
        testpoint,
        mockserver,
        mock_user_api,
        mock_personal,
        mock_xiva,
        mongodb,
        is_sms_error_temporary,
        intent_name,
        load_json,
        mocked_time,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    @mockserver.json_handler('/yasms/sendsms')
    def _mock_yasms(request):
        return http.make_response(
            """<doc>
                  <error>SMS limit for this phone is exceeded</error>
                  <errorcode>LIMITEXCEEDED</errorcode>
               </doc>""",
            200,
        )

    @testpoint('user-notification-expire-acknowledge-worker-finish')
    def worker_finished(data):
        if is_sms_error_temporary:
            assert data == {'fetched': 1, 'sent': 1, 'error': 0, 'skip': 0}
        else:
            assert data == {'fetched': 1, 'sent': 0, 'error': 1, 'skip': 0}

    @testpoint('sms_fallback_queue_too_late')
    def sms_fallback_queue_too_late(data):
        pass

    # Send push instead SMS
    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'user_id': 'my_user_id',
            'text': 'Добрый день!',
            'intent': intent_name,
        },
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'forwarded'
    assert mock_xiva.send.times_called == 1
    assert _mock_yasms.times_called == 0

    # Run ack expire worker
    mocked_time.sleep(60 * 60)
    await taxi_ucommunications.invalidate_caches(clean_update=False)

    await taxi_ucommunications.run_task(
        'user-notification-expire-acknowledge-worker',
    )
    await worker_finished.wait_call()
    assert _mock_yasms.times_called == 1

    # Ensure sms fallback properly failed
    n_acks = mongodb.user_notification_ack_queue.count()
    assert n_acks == 0

    n_sms_fallback = sms_fallback_queue_too_late.times_called
    if is_sms_error_temporary:
        assert n_sms_fallback == 1
    else:
        assert n_sms_fallback == 0


@pytest.mark.experiments3(
    filename='user_notification_instead_sms_experiment.json',
)
async def test_send_by_user_id_with_deeplink(
        taxi_ucommunications,
        mock_user_api,
        mock_personal,
        mock_yasms,
        mockserver,
        taxi_config,
        load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    @mockserver.json_handler('/xiva/v2/send')
    def send(request):
        assert request.args['user'] == 'my_user_id'
        assert request.json == {
            'payload': 'Вам SMS: hello!',
            'itsdeeplink': '"yandextaxi://addpromocode?code=CLOCKS',
            'alert': 'Ya-Taxi',
        }
        return mockserver.make_response('OK', 200, headers={'TransitID': 'id'})

    config = {
        'COMMUNICATIONS_USER_NOTIFICATION_TEMPLATES_PAYLOAD': {
            'simple_notification': {
                'payload': 'Вам SMS: {text}',
                'itsdeeplink': '{deeplink}',
                'alert': '{title}',
            },
        },
    }
    taxi_config.set_values(config)
    await taxi_ucommunications.invalidate_caches(clean_update=False)

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'user_id': 'my_user_id',
            'text': 'Добрый день!',
            'notification': {
                'text': 'hello!',
                'deeplink': '"yandextaxi://addpromocode?code=CLOCKS',
                'title': 'Ya-Taxi',
            },
            'intent': 'notification_instead_sms',
        },
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'forwarded'
    assert send.times_called == 1
    assert mock_yasms.send.times_called == 0


@pytest.mark.translations(
    notify={
        'key1': {'ru': '%(cost)s руб.', 'en': '%(cost)s dollars.'},
        'key2': {'en': 'fixed'},
    },
    client_messages={
        'key2': {'ru': 'сообщение1', 'en': 'message1'},
        'key3': {'ru': 'сообщение2', 'en': 'message2'},
    },
)
@pytest.mark.parametrize(
    'text,payload',
    [
        ('Строка!', 'Строка!'),
        (
            {'key': 'key1', 'keyset': 'notify', 'params': {'cost': 100}},
            '100 руб.',
        ),
    ],
)
@pytest.mark.experiments3(
    filename='user_notification_instead_sms_experiment.json',
)
async def test_send_localizable(
        taxi_ucommunications,
        mock_user_api,
        mock_personal,
        mock_yasms,
        mockserver,
        taxi_config,
        text,
        payload,
        load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    @mockserver.json_handler('/xiva/v2/send')
    def send(request):
        assert request.args['user'] == 'my_user_id'
        assert request.json == {
            'payload': 'Вам SMS: {}'.format(payload),
            'itsdeeplink': '"yandextaxi://addpromocode?code=CLOCKS',
            'alert': payload,
        }
        return mockserver.make_response('OK', 200, headers={'TransitID': 'id'})

    config = {
        'COMMUNICATIONS_USER_NOTIFICATION_TEMPLATES_PAYLOAD': {
            'simple_notification': {
                'payload': 'Вам SMS: {text}',
                'itsdeeplink': '{deeplink}',
                'alert': '{title}',
            },
        },
    }
    taxi_config.set_values(config)
    await taxi_ucommunications.invalidate_caches(clean_update=False)

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'user_id': 'my_user_id',
            'text': 'not used',
            'notification': {
                'text': text,
                'deeplink': '"yandextaxi://addpromocode?code=CLOCKS',
                'title': text,
            },
            'locale': 'ru',
            'intent': 'notification_instead_sms',
        },
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'forwarded'
    assert send.times_called == 1
    assert mock_yasms.send.times_called == 0


@pytest.mark.experiments3(
    filename='user_notification_instead_sms_experiment.json',
)
async def test_send_only_if_has_notification(
        taxi_ucommunications,
        mock_user_api,
        mock_personal,
        mock_yasms,
        mockserver,
        taxi_config,
        load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    @mockserver.json_handler('/xiva/v2/send')
    def xiva_send(request):
        # because send_only_if_has_notification=True in intent config
        assert False

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'user_id': 'my_user_id',
            'text': 'Добрый день!',
            'intent': 'notification_instead_sms_send_only_if_has_notification',
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    response_json.pop('message_id')
    assert response_json == {
        'code': '200',
        'message': 'OK',
        'content': 'Добрый день!',
        'status': 'sent',
    }
    assert xiva_send.times_called == 0
    assert mock_yasms.send.times_called == 1


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_INSTEAD_SMS_CHECK_LIST_ENABLED=True,
)
@pytest.mark.experiments3(
    filename='user_notification_instead_sms_experiment.json',
)
@pytest.mark.parametrize(
    'list_response, push_sent',
    [('[]', False), ('[{"id": "1", "session": "session_abcde"}]', True)],
)
async def test_list(
        taxi_ucommunications,
        mock_user_api,
        mock_personal,
        mock_yasms,
        mockserver,
        taxi_config,
        list_response,
        push_sent,
        load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    @mockserver.json_handler('/xiva/v2/send')
    def xiva_send(request):
        return mockserver.make_response('OK', 200, headers={'TransitID': 'id'})

    @mockserver.json_handler('/xiva/v2/list')
    def xiva_list(request):
        return mockserver.make_response(
            list_response, 200, headers={'TransitID': 'id'},
        )

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'user_id': 'my_user_id',
            'text': 'Добрый день!',
            'intent': 'notification_instead_sms',
        },
    )
    assert response.status_code == 200
    assert xiva_list.times_called == 1
    assert xiva_send.times_called == int(push_sent)


@pytest.mark.experiments3(
    filename='user_notification_instead_sms_experiment.json',
)
async def test_select_user(
        taxi_ucommunications,
        mock_personal,
        mock_yasms,
        mock_xiva,
        mockserver,
        taxi_config,
        testpoint,
        load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    @mockserver.json_handler('/user-api/users/search')
    def _users_search(request):
        return {
            'items': [
                {
                    'id': 'my_user_id',
                    'application': 'android',
                    'created': '2019-06-23T13:00:00+0000',
                    'updated': '2019-06-23T13:00:00+0000',
                },
                {
                    'id': 'user_id_2',
                    'application': 'mbro',
                    'created': '2019-07-23T13:00:00+0000',
                    'updated': '2019-07-23T13:00:00+0000',
                },
                {
                    'id': 'user_id_3',
                    'created': '2019-08-23T13:00:00+0000',
                    'updated': '2019-08-23T13:00:00+0000',
                },
            ],
        }

    @mockserver.json_handler('/user-api/user_phones/by_personal/retrieve')
    def _user_phones_by_personal_retrieve(request):
        return {
            'id': 'phone_id',
            'phone': '+70001112233',
            'type': 'yandex',
            'created': '2019-02-01T13:00:00+0000',
            'updated': '2019-02-01T13:00:00+0000',
            'stat': {
                'total': 0,
                'big_first_discounts': 0,
                'complete': 0,
                'complete_card': 0,
                'complete_apple': 0,
                'complete_google': 0,
                'fake': 0,
            },
            'is_loyal': False,
            'is_yandex_staff': False,
            'is_taxi_staff': False,
        }

    @testpoint('select_user')
    def select_user(data):
        assert data['user_id'] == 'my_user_id'

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'notification_instead_sms_applications',
        },
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'forwarded'
    await select_user.wait_call()
    assert mock_xiva.send.times_called == 1
    assert mock_yasms.send.times_called == 0


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_INSTEAD_SMS_USER_ID_UPDATED_LIMIT={
        'max_updated_hours': 5 * 24,
        'enabled': True,
    },
)
@pytest.mark.now('2020-10-10T00:00:00+00:00')
@pytest.mark.experiments3(
    filename='user_notification_instead_sms_experiment.json',
)
async def test_user_id_updated_limit(
        taxi_ucommunications,
        mock_personal,
        mock_yasms,
        mock_xiva,
        mockserver,
        taxi_config,
        testpoint,
        load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    @mockserver.json_handler('/user-api/users/search')
    def _users_search(request):
        return {
            'items': [
                {
                    'id': 'user_id_1',
                    'application': 'android',
                    'created': '2019-06-23T13:00:00+0000',
                    'updated': '2020-10-01T13:00:00+0000',
                },
                {
                    'id': 'my_user_id',
                    'application': 'android',
                    'created': '2019-07-23T13:00:00+0000',
                    'updated': '2020-10-10T13:00:00+0000',
                },
                {
                    'id': 'user_id_2',
                    'application': 'android',
                    'created': '2019-08-23T13:00:00+0000',
                    'updated': '2020-10-09T13:00:00+0000',
                },
                {
                    'id': 'user_id_3',
                    'application': 'android',
                    'created': '2019-08-23T13:00:00+0000',
                    'updated': '2020-10-02T13:00:00+0000',
                },
            ],
        }

    @mockserver.json_handler('/user-api/user_phones/by_personal/retrieve')
    def _user_phones_by_personal_retrieve(request):
        return {
            'id': 'phone_id',
            'phone': '+70001112233',
            'type': 'yandex',
            'created': '2019-02-01T13:00:00+0000',
            'updated': '2019-02-01T13:00:00+0000',
            'stat': {
                'total': 0,
                'big_first_discounts': 0,
                'complete': 0,
                'complete_card': 0,
                'complete_apple': 0,
                'complete_google': 0,
                'fake': 0,
            },
            'is_loyal': False,
            'is_yandex_staff': False,
            'is_taxi_staff': False,
        }

    @testpoint('select_user')
    def select_user(data):
        assert data['user_id'] == 'my_user_id'

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'notification_instead_sms',
        },
    )
    assert response.status_code == 200
    await select_user.wait_call()
    assert mock_xiva.send.times_called == 1
    assert mock_yasms.send.times_called == 0


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_INSTEAD_SMS_CHECK_PUSH_ENABLED=True,
)
@pytest.mark.experiments3(
    filename='user_notification_instead_sms_experiment.json',
)
@pytest.mark.filldb(user_notification_subscription='pushes_not_enabled')
async def test_enabled_by_system_flag_disabled(
        taxi_ucommunications,
        mock_user_api,
        mock_personal,
        mock_yasms,
        mock_xiva,
        mock_sms_intents_admin,
):
    response = await _send_push_or_sms(taxi_ucommunications)
    assert response.status_code == 200
    assert mock_xiva.send.times_called == 0


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_INSTEAD_SMS_CHECK_PUSH_ENABLED=True,
)
@pytest.mark.experiments3(
    filename='user_notification_instead_sms_experiment.json',
)
@pytest.mark.filldb(user_notification_subscription='pushes_enabled')
async def test_enabled_by_system_flag_enabled(
        taxi_ucommunications,
        mock_user_api,
        mock_personal,
        mock_yasms,
        mock_xiva,
        mock_sms_intents_admin,
):
    response = await _send_push_or_sms(taxi_ucommunications)
    assert response.status_code == 200
    assert mock_xiva.send.times_called == 1


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_INSTEAD_SMS_CHECK_PUSH_ENABLED=True,
)
@pytest.mark.experiments3(
    filename='user_notification_instead_sms_experiment.json',
)
@pytest.mark.filldb(user_notification_subscription='pushes_not_set')
async def test_enabled_by_system_flag_not_set(
        taxi_ucommunications,
        mock_user_api,
        mock_personal,
        mock_yasms,
        mock_xiva,
        mock_sms_intents_admin,
):
    response = await _send_push_or_sms(taxi_ucommunications)
    assert response.status_code == 200
    assert mock_xiva.send.times_called == 1


@pytest.mark.parametrize('is_support_dlr', [True, False])
@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
    COMMUNICATIONS_USER_NOTIFICATION_APPLICATIONS_SUPPORT_ACK_MIN_VERSION={
        'lavka_iphone': [1, 2, 3],
    },
)
@pytest.mark.experiments3(
    filename='user_notification_instead_sms_experiment.json',
)
async def test_support_delivery_report(
        taxi_ucommunications,
        mock_user_api,
        mock_personal,
        mock_yasms,
        mock_xiva,
        mock_sms_intents_admin,
        mockserver,
        is_support_dlr,
):
    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        if is_support_dlr:
            return {
                'id': 'my_user_id',
                'application': 'lavka_iphone',
                'application_version': '1.2.3',
            }
        return {
            'id': 'my_user_id',
            'application': 'lavka_iphone',
            'application_version': '1.2.2',
        }

    response = await _send_push_or_sms(taxi_ucommunications)
    assert response.status_code == 200
    assert mock_xiva.send.times_called == int(is_support_dlr)


@pytest.mark.experiments3(
    filename='user_notification_instead_sms_experiment.json',
)
async def test_add_sender(
        taxi_ucommunications,
        mock_user_api,
        mock_personal,
        mock_xiva,
        mock_yasms,
        mongodb,
        mockserver,
        load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'notification_instead_sms',
            'sender': 'eda',
        },
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'forwarded'
    assert mock_xiva.send.times_called == 1
    assert mock_yasms.send.times_called == 0

    acks = list(
        mongodb.user_notification_ack_queue.find(
            {'fallback.request.intent': 'notification_instead_sms'},
            {'_id': False},
        ),
    )
    assert len(acks) == 1
    assert acks[0]['fallback']['request']['sender'] == 'eda'
