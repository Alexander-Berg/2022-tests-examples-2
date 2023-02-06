# pylint: disable=too-many-lines

import pytest

EATER_TEMPLATE = {
    'id': 'some_eater',
    'uuid': 'some_uuid',
    'created_at': '2021-11-09T22:11:00+03:00',
    'updated_at': '2021-11-09T22:13:00+03:00',
}

EATERS = {
    'eater_1': dict(EATER_TEMPLATE, id='eater_1', personal_phone_id='phone_1'),
    'eater_2': dict(EATER_TEMPLATE, id='eater_2', personal_email_id='email_1'),
    'eater_3': dict(
        EATER_TEMPLATE, id='eater_3', passport_uid='123456789', name='stepan',
    ),
    'eater_4': dict(EATER_TEMPLATE, id='eater_4', personal_phone_id='phone_2'),
    'eater_5': dict(EATER_TEMPLATE, id='eater_5', personal_phone_id='phone_2'),
    'eater_6': dict(
        EATER_TEMPLATE,
        id='eater_6',
        personal_phone_id='phone_3',
        personal_email_id='email_2',
        type='native',
    ),
    'eater_7': dict(
        EATER_TEMPLATE,
        id='eater_7',
        personal_phone_id='phone_3',
        type='magnit',
    ),
    'eater_8': dict(EATER_TEMPLATE, id='eater_8', personal_phone_id='phone_4'),
    'eater_9': dict(EATER_TEMPLATE, id='eater_9', personal_phone_id='phone_4'),
    'eater_10': dict(
        EATER_TEMPLATE, id='eater_10', personal_phone_id='phone_4',
    ),
}

TRANSLATIONS = {
    'search_eaters_by_phone_error': {
        'ru': (
            'При поиске пользователя Яндекс.Еды с номером телефона '
            '{personal_data_value} произошла ошибка'
        ),
        'en': (
            'When searching for a Yandex.Eats user with '
            'the phone number {personal_data_value} an error occurred'
        ),
    },
    'search_eaters_by_email_error': {
        'ru': (
            'При поиске пользователя Яндекс.Еды с адресом электронной почты '
            '{personal_data_value} произошла ошибка'
        ),
        'en': (
            'When searching for a Yandex.Eats user with '
            'the email {personal_data_value} an error occurred'
        ),
    },
    'search_eaters_by_passport_uid_error': {
        'ru': (
            'При поиске пользователя Яндекс.Еды с passport_uid={passport_uid} '
            'произошла ошибка'
        ),
        'en': (
            'When searching for a Yandex.Eats user with '
            'the passport_uid={passport_uid} an error occurred'
        ),
    },
    'get_phone_id_by_phone_number_error': {
        'ru': (
            'При поиске пользователя сервисов Яндекс с номером телефона '
            '{personal_data_value} произошла ошибка'
        ),
        'en': (
            'An error occurred when searching for a Yandex services user '
            'with the phone number {personal_data_value}'
        ),
    },
    'get_email_id_by_email_error': {
        'ru': (
            'При поиске пользователя сервисов Яндекс с адресом '
            'электронной почты {personal_data_value} произошла ошибка'
        ),
        'en': (
            'An error occurred when searching for a Yandex services user '
            'with the email {personal_data_value}'
        ),
    },
    'exceeded_maximum_number_of_eaters_in_search_result': {
        'ru': (
            'Певышен предел ({max_count}) по количеству пользователей '
            'Яндекс.Еды в поисковой выдаче'
        ),
        'en': (
            'The limit on the number of Yandex.Eats users '
            'in the search results has been exceeded (limit is {max_count})'
        ),
    },
}


@pytest.mark.parametrize(
    (
        'request_data',
        'personal_phone_id',
        'personal_email_id',
        'eaters_found_by_phone_number',
        'eaters_found_by_email',
        'eater_found_by_passport_uid',
        'expected_response',
    ),
    [
        (
            {'phone_number': '+70000000000'},
            'phone_1',
            None,
            [EATERS['eater_1']],
            [],
            {},
            {
                'eaters': [
                    {
                        'eater_id': 'eater_1',
                        'personal_phone_id': 'phone_1',
                        'personal_email_id': '',
                        'name': '',
                        'passport_uid': '',
                        'type': 'native',
                    },
                ],
            },
        ),
        (
            {'email': 'best_eater@yandex.ru'},
            None,
            'email_1',
            [],
            [EATERS['eater_2']],
            {},
            {
                'eaters': [
                    {
                        'eater_id': 'eater_2',
                        'personal_phone_id': '',
                        'personal_email_id': 'email_1',
                        'name': '',
                        'passport_uid': '',
                        'type': 'native',
                    },
                ],
            },
        ),
        (
            {'passport_uid': '123456789'},
            None,
            None,
            [],
            [],
            EATERS['eater_3'],
            {
                'eaters': [
                    {
                        'eater_id': 'eater_3',
                        'personal_phone_id': '',
                        'personal_email_id': '',
                        'name': 'stepan',
                        'passport_uid': '123456789',
                        'type': 'native',
                    },
                ],
            },
        ),
        (
            {'phone_number': '+70000000001'},
            'phone_2',
            None,
            [EATERS['eater_4'], EATERS['eater_5']],
            [],
            {},
            {
                'eaters': [
                    {
                        'eater_id': 'eater_4',
                        'personal_phone_id': 'phone_2',
                        'personal_email_id': '',
                        'name': '',
                        'passport_uid': '',
                        'type': 'native',
                    },
                    {
                        'eater_id': 'eater_5',
                        'personal_phone_id': 'phone_2',
                        'personal_email_id': '',
                        'name': '',
                        'passport_uid': '',
                        'type': 'native',
                    },
                ],
            },
        ),
        (
            {
                'phone_number': '+70000000000',
                'email': 'best_eater@yandex.ru',
                'passport_uid': '123456789',
            },
            'phone_1',
            'email_1',
            [EATERS['eater_1']],
            [EATERS['eater_2']],
            EATERS['eater_3'],
            {
                'eaters': [
                    {
                        'eater_id': 'eater_1',
                        'personal_phone_id': 'phone_1',
                        'personal_email_id': '',
                        'name': '',
                        'passport_uid': '',
                        'type': 'native',
                    },
                    {
                        'eater_id': 'eater_2',
                        'personal_phone_id': '',
                        'personal_email_id': 'email_1',
                        'name': '',
                        'passport_uid': '',
                        'type': 'native',
                    },
                    {
                        'eater_id': 'eater_3',
                        'personal_phone_id': '',
                        'personal_email_id': '',
                        'name': 'stepan',
                        'passport_uid': '123456789',
                        'type': 'native',
                    },
                ],
            },
        ),
        (
            {'phone_number': '+70000000002', 'email': 'worse_eater@yandex.ru'},
            'phone_3',
            'email_2',
            [EATERS['eater_6'], EATERS['eater_7']],
            [EATERS['eater_6']],
            None,
            {
                'eaters': [
                    {
                        'eater_id': 'eater_6',
                        'personal_phone_id': 'phone_3',
                        'personal_email_id': 'email_2',
                        'name': '',
                        'passport_uid': '',
                        'type': 'native',
                    },
                    {
                        'eater_id': 'eater_7',
                        'personal_phone_id': 'phone_3',
                        'personal_email_id': '',
                        'name': '',
                        'passport_uid': '',
                        'type': 'magnit',
                    },
                ],
            },
        ),
    ],
)
async def test_green_flow(
        # ---- fixtures ----
        mock_personal,
        mock_eats_eaters,
        taxi_eats_eater_meta_web,
        # ---- parameters ----
        request_data,
        personal_phone_id,
        personal_email_id,
        eaters_found_by_phone_number,
        eaters_found_by_email,
        eater_found_by_passport_uid,
        expected_response,
):
    @mock_personal('/v1/phones/find')
    def _mock_get_phone_id_by_phone_number(request):
        assert request.json['value'] == request_data['phone_number']
        return {'id': personal_phone_id, 'value': request.json['value']}

    @mock_personal('/v1/emails/find')
    def _mock_get_email_id_by_email(request):
        assert request.json['value'] == request_data['email']
        return {'id': personal_email_id, 'value': request.json['value']}

    @mock_eats_eaters('/v1/eaters/find-by-personal-phone-id')
    def _mock_find_eaters_by_phone_id(request):
        assert request.json['personal_phone_id'] == personal_phone_id
        return {
            'eaters': eaters_found_by_phone_number,
            'pagination': {'limit': 1000, 'has_more': False},
        }

    @mock_eats_eaters('/v1/eaters/find-by-personal-email-id')
    def _mock_find_eaters_by_email_id(request):
        assert request.json['personal_email_id'] == personal_email_id
        return {
            'eaters': eaters_found_by_email,
            'pagination': {'limit': 1000, 'has_more': False},
        }

    @mock_eats_eaters('/v1/eaters/find-by-passport-uid')
    def _mock_find_eaters_by_passport_uid(request):
        return {'eater': eater_found_by_passport_uid}

    response = await taxi_eats_eater_meta_web.post(
        '/v1/eaters/search/', json=request_data,
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_response


@pytest.mark.parametrize(
    (
        'request_data',
        'personal_phone_id',
        'personal_email_id',
        'eaters_found_by_phone_number',
        'eaters_found_by_email',
        'expected_response',
    ),
    [
        ({'phone_number': '00000000000'}, None, None, [], [], {'eaters': []}),
        (
            {'phone_number': '00000000000', 'email': 'best_eater@yandex.ru'},
            None,
            'email_1',
            [],
            [EATERS['eater_2']],
            {
                'eaters': [
                    {
                        'eater_id': 'eater_2',
                        'personal_phone_id': '',
                        'personal_email_id': 'email_1',
                        'name': '',
                        'passport_uid': '',
                        'type': 'native',
                    },
                ],
            },
        ),
    ],
)
async def test_personal_data_id_not_found(
        # ---- fixtures ----
        mockserver,
        mock_personal,
        taxi_eats_eater_meta_web,
        mock_eats_eaters,
        # ---- parameters ----
        request_data,
        personal_phone_id,
        personal_email_id,
        eaters_found_by_phone_number,
        eaters_found_by_email,
        expected_response,
):
    @mock_personal('/v1/phones/find')
    def _mock_get_phone_id_by_phone_number(request):
        return mockserver.make_response(
            status=404, json={'code': '404', 'message': 'Phone id not found'},
        )

    @mock_personal('/v1/emails/find')
    def _mock_get_email_id_by_email(request):
        return {'id': personal_email_id, 'value': request.json['value']}

    @mock_eats_eaters('/v1/eaters/find-by-personal-phone-id')
    def _mock_find_eaters_by_phone_id(request):
        return {
            'eaters': eaters_found_by_phone_number,
            'pagination': {'limit': 1000, 'has_more': False},
        }

    @mock_eats_eaters('/v1/eaters/find-by-personal-email-id')
    def _mock_find_eaters_by_email_id(request):
        return {
            'eaters': eaters_found_by_email,
            'pagination': {'limit': 1000, 'has_more': False},
        }

    response = await taxi_eats_eater_meta_web.post(
        '/v1/eaters/search/', json=request_data,
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_response


@pytest.mark.translations(eats_eater_meta=TRANSLATIONS)
@pytest.mark.parametrize(
    (
        'request_data',
        'personal_phone_id',
        'personal_email_id',
        'eaters_found_by_phone_number',
        'eaters_found_by_email',
        'expected_response',
    ),
    [
        (
            {'email': 'best_eater@yandex.ru'},
            None,
            None,
            [],
            [],
            {
                'eaters': [],
                'errors': [
                    {
                        'error_message': (
                            'При поиске пользователя сервисов Яндекс '
                            'с адресом электронной почты '
                            'best_eater@yandex.ru произошла ошибка'
                        ),
                    },
                ],
            },
        ),
        (
            {'phone_number': '+70000000000', 'email': 'best_eater@yandex.ru'},
            'phone_1',
            None,
            [EATERS['eater_1']],
            [],
            {
                'eaters': [
                    {
                        'eater_id': 'eater_1',
                        'personal_phone_id': 'phone_1',
                        'personal_email_id': '',
                        'name': '',
                        'passport_uid': '',
                        'type': 'native',
                    },
                ],
                'errors': [
                    {
                        'error_message': (
                            'При поиске пользователя сервисов Яндекс '
                            'с адресом электронной почты '
                            'best_eater@yandex.ru произошла ошибка'
                        ),
                    },
                ],
            },
        ),
    ],
)
async def test_error_of_service_personal(
        # ---- fixtures ----
        mockserver,
        mock_personal,
        taxi_eats_eater_meta_web,
        mock_eats_eaters,
        # ---- parameters ----
        request_data,
        personal_phone_id,
        personal_email_id,
        eaters_found_by_phone_number,
        eaters_found_by_email,
        expected_response,
):
    @mock_personal('/v1/phones/find')
    def _mock_get_phone_id_by_phone_number(request):
        return {'id': personal_phone_id, 'value': request.json['value']}

    @mock_personal('/v1/emails/find')
    def _mock_get_email_id_by_email(request):
        return mockserver.make_response(
            status=500, response='Internal personal service error',
        )

    @mock_eats_eaters('/v1/eaters/find-by-personal-phone-id')
    def _mock_find_eaters_by_phone_id(request):
        return {
            'eaters': eaters_found_by_phone_number,
            'pagination': {'limit': 1000, 'has_more': False},
        }

    @mock_eats_eaters('/v1/eaters/find-by-personal-email-id')
    def _mock_find_eaters_by_email_id(request):
        return {
            'eaters': eaters_found_by_email,
            'pagination': {'limit': 1000, 'has_more': False},
        }

    response = await taxi_eats_eater_meta_web.post(
        '/v1/eaters/search/', json=request_data,
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_response


@pytest.mark.parametrize(
    ('request_data', 'eaters_found_by_phone_number', 'expected_response'),
    [
        ({'passport_uid': '00000000'}, [], {'eaters': []}),
        (
            {'phone_number': '+70000000000', 'passport_uid': '00000000'},
            [EATERS['eater_1']],
            {
                'eaters': [
                    {
                        'eater_id': 'eater_1',
                        'personal_phone_id': 'phone_1',
                        'personal_email_id': '',
                        'name': '',
                        'passport_uid': '',
                        'type': 'native',
                    },
                ],
            },
        ),
    ],
)
async def test_eater_not_found_by_passport_uid(
        # ---- fixtures ----
        mockserver,
        mock_personal,
        mock_eats_eaters,
        taxi_eats_eater_meta_web,
        # ---- parameters ----
        request_data,
        eaters_found_by_phone_number,
        expected_response,
):
    @mock_personal('/v1/phones/find')
    def _mock_get_phone_id_by_phone_number(request):
        return {'id': 'some_phone_id', 'value': request.json['value']}

    @mock_eats_eaters('/v1/eaters/find-by-personal-phone-id')
    def _mock_find_eaters_by_phone_id(request):
        return {
            'eaters': eaters_found_by_phone_number,
            'pagination': {'limit': 1000, 'has_more': False},
        }

    @mock_eats_eaters('/v1/eaters/find-by-passport-uid')
    def _mock_find_eaters_by_passport_uid(request):
        return mockserver.make_response(
            status=404,
            json={'code': 'eater_not_found', 'message': 'Итер не найден.'},
            headers={'X-YaTaxi-Error-Code': '404'},
        )

    response = await taxi_eats_eater_meta_web.post(
        '/v1/eaters/search/', json=request_data,
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_response


@pytest.mark.translations(eats_eater_meta=TRANSLATIONS)
@pytest.mark.parametrize(
    ('request_data', 'eaters_found_by_email', 'expected_response'),
    [
        (
            {'passport_uid': '00000000'},
            [],
            {
                'eaters': [],
                'errors': [
                    {
                        'error_message': (
                            'При поиске пользователя Яндекс.Еды '
                            'с passport_uid=00000000 произошла ошибка'
                        ),
                    },
                ],
            },
        ),
        (
            {'email': 'best_eater@yandex.ru', 'passport_uid': '00000000'},
            [EATERS['eater_2']],
            {
                'eaters': [
                    {
                        'eater_id': 'eater_2',
                        'personal_phone_id': '',
                        'personal_email_id': 'email_1',
                        'name': '',
                        'passport_uid': '',
                        'type': 'native',
                    },
                ],
                'errors': [
                    {
                        'error_message': (
                            'При поиске пользователя Яндекс.Еды '
                            'с passport_uid=00000000 произошла ошибка'
                        ),
                    },
                ],
            },
        ),
    ],
)
async def test_error_while_finding_eater_by_passport_uid(
        # ---- fixtures ----
        mockserver,
        mock_personal,
        mock_eats_eaters,
        taxi_eats_eater_meta_web,
        # ---- parameters ----
        request_data,
        eaters_found_by_email,
        expected_response,
):
    @mock_personal('/v1/emails/find')
    def _mock_get_email_id_by_email(request):
        return {'id': 'some_email_id', 'value': request.json['value']}

    @mock_eats_eaters('/v1/eaters/find-by-personal-email-id')
    def _mock_find_eaters_by_email_id(request):
        return {
            'eaters': eaters_found_by_email,
            'pagination': {'limit': 1000, 'has_more': False},
        }

    @mock_eats_eaters('/v1/eaters/find-by-passport-uid')
    def _mock_find_eaters_by_passport_uid(request):
        return mockserver.make_response(
            status=500, response='Internal eats-eaters service error',
        )

    response = await taxi_eats_eater_meta_web.post(
        '/v1/eaters/search/', json=request_data,
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_response


@pytest.mark.translations(eats_eater_meta=TRANSLATIONS)
@pytest.mark.parametrize(
    (
        'request_data',
        'eaters_found_by_phone_number',
        'eaters_found_by_email',
        'expected_response',
    ),
    [
        (
            {'phone_number': '+70000000000'},
            [],
            [],
            {
                'eaters': [],
                'errors': [
                    {
                        'error_message': (
                            'При поиске пользователя Яндекс.Еды с номером '
                            'телефона +70000000000 произошла ошибка'
                        ),
                    },
                ],
            },
        ),
        (
            {'phone_number': '+70000000001', 'email': 'best_eater@yandex.ru'},
            [],
            [EATERS['eater_2']],
            {
                'eaters': [
                    {
                        'eater_id': 'eater_2',
                        'personal_phone_id': '',
                        'personal_email_id': 'email_1',
                        'name': '',
                        'passport_uid': '',
                        'type': 'native',
                    },
                ],
                'errors': [
                    {
                        'error_message': (
                            'При поиске пользователя Яндекс.Еды с номером '
                            'телефона +70000000001 произошла ошибка'
                        ),
                    },
                ],
            },
        ),
    ],
)
async def test_error_while_finding_eater_by_personal_data(
        # ---- fixtures ----
        mockserver,
        mock_personal,
        mock_eats_eaters,
        taxi_eats_eater_meta_web,
        # ---- parameters ----
        request_data,
        eaters_found_by_phone_number,
        eaters_found_by_email,
        expected_response,
):
    @mock_personal('/v1/phones/find')
    def _mock_get_phone_id_by_phone_number(request):
        return {'id': 'some_phone_id', 'value': request.json['value']}

    @mock_personal('/v1/emails/find')
    def _mock_get_email_id_by_email(request):
        return {'id': 'some_email_id', 'value': request.json['value']}

    @mock_eats_eaters('/v1/eaters/find-by-personal-phone-id')
    def _mock_find_eaters_by_phone_id(request):
        return mockserver.make_response(
            status=500, response='Internal eats-eaters service error',
        )

    @mock_eats_eaters('/v1/eaters/find-by-personal-email-id')
    def _mock_find_eaters_by_email_id(request):
        return {
            'eaters': eaters_found_by_email,
            'pagination': {'limit': 1000, 'has_more': False},
        }

    response = await taxi_eats_eater_meta_web.post(
        '/v1/eaters/search/', json=request_data,
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_response


@pytest.mark.translations(eats_eater_meta=TRANSLATIONS)
@pytest.mark.config(EATS_EATER_META_MAX_EATER_COUNT_IN_SEARCH_RESULT=2)
@pytest.mark.parametrize(
    (
        'request_data',
        'eaters_found_by_phone_number',
        'eaters_found_by_email',
        'expected_response',
    ),
    [
        (
            {'phone_number': '+70000000000', 'email': 'best_eater@yandex.ru'},
            [EATERS['eater_1']],
            [EATERS['eater_2']],
            {
                'eaters': [
                    {
                        'eater_id': 'eater_1',
                        'personal_phone_id': 'phone_1',
                        'personal_email_id': '',
                        'name': '',
                        'passport_uid': '',
                        'type': 'native',
                    },
                    {
                        'eater_id': 'eater_2',
                        'personal_phone_id': '',
                        'personal_email_id': 'email_1',
                        'name': '',
                        'passport_uid': '',
                        'type': 'native',
                    },
                ],
            },
        ),
        (
            {'phone_number': '+70000000002', 'email': 'worse_eater@yandex.ru'},
            [EATERS['eater_6'], EATERS['eater_7']],
            [EATERS['eater_6']],
            {
                'eaters': [
                    {
                        'eater_id': 'eater_6',
                        'personal_phone_id': 'phone_3',
                        'personal_email_id': 'email_2',
                        'name': '',
                        'passport_uid': '',
                        'type': 'native',
                    },
                    {
                        'eater_id': 'eater_7',
                        'personal_phone_id': 'phone_3',
                        'personal_email_id': '',
                        'name': '',
                        'passport_uid': '',
                        'type': 'magnit',
                    },
                ],
            },
        ),
        (
            {'phone_number': '+70000000001', 'email': 'best_eater@yandex.ru'},
            [EATERS['eater_4'], EATERS['eater_5']],
            [EATERS['eater_2']],
            {
                'eaters': [
                    {
                        'eater_id': 'eater_4',
                        'personal_phone_id': 'phone_2',
                        'personal_email_id': '',
                        'name': '',
                        'passport_uid': '',
                        'type': 'native',
                    },
                    {
                        'eater_id': 'eater_5',
                        'personal_phone_id': 'phone_2',
                        'personal_email_id': '',
                        'name': '',
                        'passport_uid': '',
                        'type': 'native',
                    },
                ],
                'errors': [
                    {
                        'error_message': (
                            'Певышен предел (2) по количеству пользователей '
                            'Яндекс.Еды в поисковой выдаче'
                        ),
                    },
                ],
            },
        ),
    ],
)
async def test_max_eater_count(
        # ---- fixtures ----
        mockserver,
        mock_personal,
        mock_eats_eaters,
        taxi_eats_eater_meta_web,
        # ---- parameters ----
        request_data,
        eaters_found_by_phone_number,
        eaters_found_by_email,
        expected_response,
):
    @mock_personal('/v1/phones/find')
    def _mock_get_phone_id_by_phone_number(request):
        return {'id': 'some_phone_id', 'value': request.json['value']}

    @mock_personal('/v1/emails/find')
    def _mock_get_email_id_by_email(request):
        return {'id': 'some_email_id', 'value': request.json['value']}

    @mock_eats_eaters('/v1/eaters/find-by-personal-phone-id')
    def _mock_find_eaters_by_phone_id(request):
        return {
            'eaters': eaters_found_by_phone_number,
            'pagination': {'limit': 1, 'has_more': False},
        }

    @mock_eats_eaters('/v1/eaters/find-by-personal-email-id')
    def _mock_find_eaters_by_email_id(request):
        return {
            'eaters': eaters_found_by_email,
            'pagination': {'limit': 1, 'has_more': False},
        }

    response = await taxi_eats_eater_meta_web.post(
        '/v1/eaters/search/', json=request_data,
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_response


@pytest.mark.config(
    EATS_EATER_META_EATERS_BUNDLE_SIZE=2,
    EATS_EATER_META_MAX_EATER_COUNT_IN_SEARCH_RESULT=3,
)
@pytest.mark.parametrize(
    (
        'request_data',
        'eaters_found_by_phone_number_1',
        'eaters_found_by_phone_number_2',
        'expected_response',
    ),
    [
        (
            {'phone_number': '+70000000002'},
            [EATERS['eater_8'], EATERS['eater_9']],
            [EATERS['eater_10']],
            {
                'eaters': [
                    {
                        'eater_id': 'eater_8',
                        'personal_phone_id': 'phone_4',
                        'personal_email_id': '',
                        'name': '',
                        'passport_uid': '',
                        'type': 'native',
                    },
                    {
                        'eater_id': 'eater_9',
                        'personal_phone_id': 'phone_4',
                        'personal_email_id': '',
                        'name': '',
                        'passport_uid': '',
                        'type': 'native',
                    },
                    {
                        'eater_id': 'eater_10',
                        'personal_phone_id': 'phone_4',
                        'personal_email_id': '',
                        'name': '',
                        'passport_uid': '',
                        'type': 'native',
                    },
                ],
            },
        ),
    ],
)
async def test_multiple_requests_to_eats_eaters(
        # ---- fixtures ----
        mockserver,
        mock_personal,
        mock_eats_eaters,
        taxi_eats_eater_meta_web,
        # ---- parameters ----
        request_data,
        eaters_found_by_phone_number_1,
        eaters_found_by_phone_number_2,
        expected_response,
):
    @mock_personal('/v1/phones/find')
    def _mock_get_phone_id_by_phone_number(request):
        return {'id': 'some_phone_id', 'value': request.json['value']}

    @mock_eats_eaters('/v1/eaters/find-by-personal-phone-id')
    def _mock_find_eaters_by_phone_id(request):
        pagination = request.json['pagination']
        after = pagination.get('after')
        limit = pagination.get('limit')
        if after is None:
            assert limit == 2
            return {
                'eaters': eaters_found_by_phone_number_1,
                'pagination': {
                    'limit': len(eaters_found_by_phone_number_1),
                    'has_more': True,
                },
            }

        assert after == eaters_found_by_phone_number_1[-1]['id']
        assert limit == 3 - len(eaters_found_by_phone_number_1)
        return {
            'eaters': eaters_found_by_phone_number_2,
            'pagination': {
                'limit': len(eaters_found_by_phone_number_2),
                'has_more': False,
            },
        }

    response = await taxi_eats_eater_meta_web.post(
        '/v1/eaters/search/', json=request_data,
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_response


@pytest.mark.translations(eats_eater_meta=TRANSLATIONS)
@pytest.mark.parametrize(
    ('request_data', 'language', 'expected_response'),
    [
        (
            {'passport_uid': '00000000'},
            'ru',
            {
                'eaters': [],
                'errors': [
                    {
                        'error_message': (
                            'При поиске пользователя Яндекс.Еды '
                            'с passport_uid=00000000 произошла ошибка'
                        ),
                    },
                ],
            },
        ),
        (
            {'passport_uid': '00000000'},
            'en',
            {
                'eaters': [],
                'errors': [
                    {
                        'error_message': (
                            'When searching for a Yandex.Eats user with '
                            'the passport_uid=00000000 an error occurred'
                        ),
                    },
                ],
            },
        ),
    ],
)
async def test_translations(
        # ---- fixtures ----
        mockserver,
        mock_personal,
        mock_eats_eaters,
        taxi_eats_eater_meta_web,
        # ---- parameters ----
        request_data,
        language,
        expected_response,
):
    @mock_personal('/v1/emails/find')
    def _mock_get_phone_id_by_phone_number(request):
        return {'id': 'some_phone_id', 'value': request.json['value']}

    @mock_eats_eaters('/v1/eaters/find-by-personal-email-id')
    def _mock_find_eaters_by_email_id(request):
        return {'id': 'some_email_id', 'value': request.json['value']}

    @mock_eats_eaters('/v1/eaters/find-by-passport-uid')
    def _mock_find_eaters_by_passport_uid(request):
        return mockserver.make_response(
            status=500, response='Internal eats-eaters service error',
        )

    response = await taxi_eats_eater_meta_web.post(
        '/v1/eaters/search/',
        json=request_data,
        headers={'Accept-Language': language},
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_response
