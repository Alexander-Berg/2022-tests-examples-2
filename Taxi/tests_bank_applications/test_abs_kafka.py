import json


DEFAULT_PHONE = '+79991234567'
DEFAULT_BUID = 'buid_1'
DEFAULT_PHONE_ID = 'phone_id_1'
DEFAULT_APPLICATON_ID = '7948e3a9-623c-4524-a390-9e4264d27a09'


def get_message() -> str:
    return json.dumps(
        {
            'phone_number': '+79991234567',
            'id_record_abs': '64414288',
            'first_name': 'Сергей',
            'last_name': 'Панин',
            'patronymic': 'Александрович',
            'birthday': '2000-01-01',
            'inn': '0123456789',
            'snils': '9876543210',
            'sex': 'M',
            'birth_place': 'Москва',
            'is_resident': '1',
            'sitizenship': '643',
            'id_doc_type': '021',
            'id_doc_number': '8916891600',
            'id_doc_issued': '2000-01-01',
            'id_doc_issued_by': 'ОВД',
            'id_doc_department_code': '000-000',
            'addresses': [
                {
                    'type': 'REGISTRATION',
                    'country': 'Россия',
                    'region': 'Московская',
                    'house': '1',
                    'postalcode': '143989',
                    'area': 'Краснознаменный',
                    'city': 'Реутов',
                    'street': 'Неизвестного героя',
                    'build': '1',
                    'struct': '1',
                    'flat': '1',
                },
                {
                    'type': 'REAL_LIVE',
                    'country': 'Россия',
                    'region': 'Московская',
                    'house': '1',
                    'postalcode': '143989',
                    'area': 'Краснознаменный',
                    'city': 'Реутов',
                    'street': 'Неизвестного героя',
                    'build': '1',
                    'struct': '1',
                    'flat': '1',
                },
            ],
        },
    )


async def test_kafka_abs(
        taxi_bank_applications, pgsql, mockserver, stq_runner, testpoint,
):
    await taxi_bank_applications.enable_testpoints()

    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_phone_id',
    )
    def _phone_id_handler(request):
        assert request.method == 'POST'
        phone = request.json.get('phone')
        assert phone == DEFAULT_PHONE
        return mockserver.make_response(
            status=200, json={'phone_id': DEFAULT_PHONE_ID},
        )

    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_buid_info',
    )
    def _get_buid_info_handler(request):
        assert request.json['phone_id'] == DEFAULT_PHONE_ID
        return mockserver.make_response(
            status=200, json={'buid_info': {'buid': DEFAULT_BUID}},
        )

    @mockserver.json_handler(
        '/bank-applications/applications-internal/v1/kyc/create_application',
    )
    def _kyc_create_application(request):
        return mockserver.make_response(
            json={
                'application_id': DEFAULT_APPLICATON_ID,
                'status': 'CREATED',
            },
            status=200,
        )

    @mockserver.json_handler(
        '/bank-applications/applications-internal/v1/kyc/submit_form',
    )
    def _kyc_submit_form(request):
        form = json.loads(get_message())
        form['birth_place_info'] = {'country_code': 'RU', 'place': 'Москва'}

        # have to do it because of difference in kyc form and abs form
        form['address_registration'] = form['addresses'][0]
        form['address_registration']['postal_code'] = form[
            'address_registration'
        ]['postalcode']
        form['address_registration']['building'] = form[
            'address_registration'
        ]['build']
        form['address_registration']['structure'] = form[
            'address_registration'
        ]['struct']

        form['address_actual'] = form['addresses'][1]
        form['address_actual']['postal_code'] = form['address_actual'][
            'postalcode'
        ]
        form['address_actual']['building'] = form['address_actual']['build']
        form['address_actual']['structure'] = form['address_actual']['struct']
        del form['addresses']
        del form['birth_place']
        return mockserver.make_response(
            json={
                'application_id': DEFAULT_APPLICATON_ID,
                'buid': DEFAULT_BUID,
                'form': form,
            },
            status=200,
        )

    @testpoint('tp_kafka-consumer-kyc-form')
    def received_messages_func(data):
        pass

    response = await taxi_bank_applications.post(
        'tests/kafka/messages/kafka-consumer-kyc-form',
        data=json.dumps({'data': get_message(), 'topic': 'cft_send_kyc'}),
    )
    assert response.status_code == 200

    await received_messages_func.wait_call()
    assert _kyc_create_application.times_called == 1
    assert _kyc_submit_form.times_called == 1


async def test_kafka_abs_error(
        taxi_bank_applications, pgsql, stq_runner, mockserver, testpoint,
):
    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_phone_id',
    )
    def _phone_id_handler(request):
        return mockserver.make_response(json={}, status=500)

    @testpoint('tp_error_kafka-consumer-kyc-form')
    def received_messages_func_error(data):
        pass

    await taxi_bank_applications.enable_testpoints()

    response = await taxi_bank_applications.post(
        'tests/kafka/messages/kafka-consumer-kyc-form',
        data=json.dumps({'data': get_message(), 'topic': 'cft_send_kyc'}),
    )
    assert response.status_code == 200

    await received_messages_func_error.wait_call()
    assert _phone_id_handler.times_called == 1


async def test_kafka_abs_error_bad_message(
        taxi_bank_applications, pgsql, stq_runner, mockserver, testpoint,
):
    @testpoint('tp_error_kafka-consumer-kyc-form')
    def received_messages_func_error(data):
        pass

    await taxi_bank_applications.enable_testpoints()

    response = await taxi_bank_applications.post(
        'tests/kafka/messages/kafka-consumer-kyc-form',
        data=json.dumps({'data': json.dumps({}), 'topic': 'cft_send_kyc'}),
    )
    assert response.status_code == 200

    await received_messages_func_error.wait_call()
