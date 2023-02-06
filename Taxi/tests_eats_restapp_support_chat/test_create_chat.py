import pytest

SECRET_KEY_FROM_SECDIST = 'NdRgUkXp2s5v8y/A?D(G+KbPeShVmYq3'


CORE_FULL_INFO_RESP = {
    'is_success': True,
    'payload': {
        'info': {
            'name': 'test1',
            'type': 'native',
            'address': {
                'country': 'test1',
                'city': 'test°',
                'street': 'test',
                'building': '20/1',
                'full': 'test',
            },
            'phones': [
                {'number': '+79999999998', 'type': 'auto_call'},
                {'number': '+79999999998', 'type': 'lpr'},
                {'number': '+79999999998', 'type': 'place'},
                {'number': '+79999999999', 'type': 'official'},
            ],
            'email': 'storm@yandex-team.ru',
            'payments': ['Безналичный расчет'],
            'address_comment': 'test',
            'client_comment': 'test',
        },
        'billing': {
            'inn': '0007201970',
            'kpp': '000701001',
            'bik': '000525411',
            'account': '40702810500000143829',
            'name': 'test',
            'address': {'postcode': '103051', 'full': 'test'},
            'post_address': {'postcode': '103051', 'full': 'test'},
            'accountancy_phone': {
                'number': '+74956252892',
                'type': 'accountancy',
                'description': '',
            },
            'accountancy_email': 'tochka35@yandex.ru',
            'signer': {
                'name': 'test',
                'position': 'test',
                'authority_doc': 'test',
            },
            'balance_external_id': '180406-32',
            'balance_date_start': '2019-07-01',
        },
        'commission': [
            {'value': 25, 'acquiring': 3, 'type': 'delivery'},
            {'value': 1.55, 'acquiring': 0, 'type': 'pickup'},
        ],
    },
}


@pytest.fixture(autouse=True)
def _mock_core(mockserver):
    @mockserver.json_handler('/eats-core/v1/places/12/full-info')
    def _mock_place_12(request):
        return CORE_FULL_INFO_RESP

    @mockserver.json_handler('/eats-core/v1/places/11/full-info')
    def _mock_place_11(request):
        return CORE_FULL_INFO_RESP

    @mockserver.json_handler('/eats-core/v1/places/10/full-info')
    def _mock_place_10(request):
        return CORE_FULL_INFO_RESP


@pytest.mark.parametrize('partner_id,place_id', [(1, 10), (2, 11), (3, 12)])
@pytest.mark.parametrize('ticket_line', [None, 'some_line'])
@pytest.mark.parametrize(
    'title', ['Title form', 'Title form ', ' Title form', '  Title form   '],
)
@pytest.mark.experiments3(filename='places_settings.json')
async def test_create_chat(
        taxi_eats_restapp_support_chat,
        partner_id,
        place_id,
        ticket_line,
        title,
        pgsql,
        testpoint,
):
    @testpoint('create_chat::ivalid_nonce')
    def ivalid_nonce(data):
        pass

    # генерируем зашифрованный json
    response = await taxi_eats_restapp_support_chat.post(
        '/4.0/restapp-front/support_chat/v1/generate_key_data?'
        'place_id={}'.format(place_id),
        headers={'X-YaEda-PartnerId': str(partner_id)},
    )
    assert response.status == 200
    assert response.json()['data']
    secret_data = response.json()['data']

    # проверка на создание записи в базе
    cursor = pgsql['eats_restapp_support_chat'].cursor()
    cursor.execute(
        'SELECT nonce,expire_at FROM'
        ' eats_restapp_support_chat.applied_keys',
    )
    res = list(cursor)
    assert len(res) == 1

    # отправляем секретный json
    json = {'title': title, 'data': 'DATA FROM FORMS', 'data-key': secret_data}
    if ticket_line:
        json['ticket_line'] = ticket_line
    response = await taxi_eats_restapp_support_chat.post(
        '/4.0/restapp-front/support_chat/v1/create_chat', json=json,
    )
    assert response.status == 200
    data_res = response.json()
    chat_data = data_res['chat_data']
    chat_query = data_res['chat_query']
    message_metadata = chat_data['message_metadata']
    assert len(chat_data['message_id']) == 36  # длинна uuid
    assert data_res['partner_id'] == partner_id
    assert message_metadata['restapp_place_id'] == str(place_id)
    assert message_metadata['ticket_subject'] == 'Title form'

    assert message_metadata['user_email'] == 'storm@yandex-team.ru'
    assert message_metadata['restapp_rest'] == 'test1'
    assert message_metadata['restapp_inn'] == '0007201970'
    assert message_metadata['restapp_company'] == 'test'

    if ticket_line:
        assert message_metadata['ticket_line'] == ticket_line
    else:
        assert 'ticket_line' not in message_metadata

    # проверка данных, необходимых для чатов
    assert chat_data['type'] == 'text'
    assert chat_query['handler_type'] == 'realtime'
    assert chat_query['service'] == 'restapp'

    # проверка на удаление nonce из базы
    cursor = pgsql['eats_restapp_support_chat'].cursor()
    cursor.execute(
        'SELECT nonce,expire_at FROM'
        ' eats_restapp_support_chat.applied_keys',
    )
    res = list(cursor)
    assert res == []
    assert ivalid_nonce.times_called == 0

    # попробуем отправить его еще раз - должен сработать testpoint
    response = await taxi_eats_restapp_support_chat.post(
        '/4.0/restapp-front/support_chat/v1/create_chat',
        json={
            'title': 'Title form',
            'data': 'DATA FROM FORMS',
            'data-key': secret_data,
        },
    )
    assert response.status == 400

    # проверка на удаление nonce из базы
    cursor = pgsql['eats_restapp_support_chat'].cursor()
    cursor.execute(
        'SELECT nonce,expire_at FROM'
        ' eats_restapp_support_chat.applied_keys',
    )
    res = list(cursor)
    assert res == []
    assert ivalid_nonce.times_called == 1


@pytest.mark.parametrize('data_key', ['', 'invalid'])
@pytest.mark.experiments3(filename='places_settings.json')
async def test_create_chat_with_invalid_or_data_key(
        taxi_eats_restapp_support_chat, data_key,
):
    # отправляем данные
    json = {'title': 'Title', 'data': 'DATA FROM FORMS', 'data-key': data_key}
    response = await taxi_eats_restapp_support_chat.post(
        '/4.0/restapp-front/support_chat/v1/create_chat', json=json,
    )
    assert response.status == 200
    data_res = response.json()
    chat_data = data_res['chat_data']
    chat_query = data_res['chat_query']
    message_metadata = chat_data['message_metadata']
    assert len(chat_data['message_id']) == 36  # длинна uuid
    assert data_res['partner_id'] == 0
    assert message_metadata.get('restapp_place_id') is None

    assert message_metadata.get('user_email') is None
    assert message_metadata.get('restapp_rest') is None
    assert message_metadata.get('restapp_inn') is None
    assert message_metadata.get('restapp_company') is None

    # проверка данных, необходимых для чатов
    assert chat_data['type'] == 'text'
    assert chat_query['handler_type'] == 'realtime'
    assert chat_query['service'] == 'restapp'
