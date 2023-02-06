import pytest


@pytest.fixture(name='passport_internal')
def _passport_internal(mockserver):
    class Context:
        def __init__(self):
            self.body = '{"status":"ok"}'
            self.code = 200
            self.expected_args = {'consumer': 'taxi-zalogin'}
            self.expected_form = {
                'admin_name': 'login',
                'comment': 'DARIA-5006',
                'is_changing_required': 'yes',
                'max_change_frequency_in_days': '1',
            }

        def verify(self, request):
            assert self.expected_args == request.args
            assert self.expected_form == request.form

    context = Context()

    @mockserver.handler('/passport-internal/2/account/1111/password_options/')
    def _unbind_phonish_by_uid(request):
        context.verify(request)
        return mockserver.make_response(context.body, context.code)

    return context


@pytest.fixture(name='tracker_internal')
def _tracker_internal(mockserver):
    class Context:
        def __init__(self):
            self.body = None
            self.code = 201

    context = Context()

    @mockserver.handler('/api-tracker-uservices/v2/issues/DARIA-5005')
    def _get_tracker_ticket_200(request):
        return mockserver.make_response(context.body, 200)

    @mockserver.handler('/api-tracker-uservices/v2/issues/DARIA-5006')
    def _get_tracker_ticket_201(request):
        return mockserver.make_response(context.body, context.code)

    @mockserver.handler('/api-tracker-uservices/v2/issues/DARIA-5007')
    def _get_tracker_ticket_incorrect_data(request):
        return mockserver.make_response(
            '{"statusCode": 404, "errorMessages": []}', 400,
        )

    @mockserver.handler('/api-tracker-uservices/v2/issues/DARIA-5008')
    def _get_tracker_ticket_not_authorized(request):
        return mockserver.make_response(
            '{"statusCode": 404, "errorMessages": []}', 401,
        )

    @mockserver.handler('/api-tracker-uservices/v2/issues/DARIA-5009')
    def _get_tracker_ticket_not_found(request):
        return mockserver.make_response(
            '{"statusCode": 404, "errorMessages": []}', 404,
        )

    @mockserver.handler('/api-tracker-uservices/v2/issues/DARIA-5010')
    def _get_tracker_ticket_server_error(request):
        return mockserver.make_response(
            '{"statusCode": 500, "errorMessages": []}', 500,
        )

    return context


@pytest.fixture(name='chatterbox_internal')
def _chatterbox_internal(mockserver):
    class Context:
        def __init__(self):
            self.body = None
            self.code = 200

    context = Context()

    @mockserver.handler('/chatterbox-uservices/v1/tasks/DARIA5006')
    def _get_chatterbox_ticket_200(request):
        return mockserver.make_response(context.body, context.code)

    @mockserver.handler('/chatterbox-uservices/v1/tasks/DARIA5007')
    def _get_chatterbox_ticket_incorrect_data(request):
        return mockserver.make_response(None, 400)

    @mockserver.handler('/chatterbox-uservices/v1/tasks/DARIA5008')
    def _get_chatterbox_ticket_not_authorized(request):
        return mockserver.make_response(None, 401)

    @mockserver.handler('/chatterbox-uservices/v1/tasks/DARIA5009')
    def _get_chatterbox_ticket_not_found(request):
        return mockserver.make_response(None, 404)

    @mockserver.handler('/chatterbox-uservices/v1/tasks/DARIA5010')
    def _get_chatterbox_ticket_server_error(request):
        return mockserver.make_response(None, 500)

    return context


async def test_simple(taxi_zalogin, passport_internal, tracker_internal):
    body = {'yandex_uid': '1111', 'comment': 'DARIA-5006'}
    headers = {'X-Yandex-Login': 'login'}

    response = await taxi_zalogin.post(
        'admin/password-reset', body, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


async def test_error_200(taxi_zalogin, passport_internal, tracker_internal):
    passport_internal.body = '{"status":"error","errors":["error1","error2"]}'

    body = {'yandex_uid': '1111', 'comment': 'DARIA-5006'}
    headers = {'X-Yandex-Login': 'login'}

    response = await taxi_zalogin.post(
        'admin/password-reset', body, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {
        'status': 'error',
        'errors': ['error1', 'error2'],
    }


async def test_error(taxi_zalogin, passport_internal, tracker_internal):
    passport_internal.code = 404

    body = {'yandex_uid': '1111', 'comment': 'DARIA-5006'}
    headers = {'X-Yandex-Login': 'login'}

    response = await taxi_zalogin.post(
        'admin/password-reset', body, headers=headers,
    )
    assert response.status_code == 500


@pytest.mark.config(ZALOGIN_MAX_PASSWORD_CHANGE_FREQUENCY_IN_DAYS=777)
async def test_max_change_frequency_in_days_config(
        taxi_zalogin, passport_internal, tracker_internal,
):
    passport_internal.expected_form['max_change_frequency_in_days'] = '777'

    body = {'yandex_uid': '1111', 'comment': 'DARIA-5006'}
    headers = {'X-Yandex-Login': 'login'}

    response = await taxi_zalogin.post(
        'admin/password-reset', body, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


@pytest.mark.parametrize(
    ['ticket', 'expected_status_json', 'expected_status_code'],
    [
        ('DARIA-5005', {'status': 'ok'}, 200),
        ('DARIA-5006', {'status': 'ok'}, 200),
        (
            'DARIA-5007',
            {
                'status': 'error',
                'errors': ['Некорректный запрос в тикет-сервис'],
            },
            400,
        ),
        (
            'DARIA-5008',
            {
                'status': 'error',
                'errors': ['Ошибка авторизации в тикет-сервисе'],
            },
            400,
        ),
        (
            'DARIA-5009',
            {'status': 'error', 'errors': ['Тикет не существует']},
            400,
        ),
        (
            'DARIA-5010',
            {'status': 'error', 'errors': ['Серверная ошибка тикет-сервиса']},
            400,
        ),
        ('DARIA5006', {'status': 'ok'}, 200),
        (
            'DARIA5007',
            {
                'status': 'error',
                'errors': ['Некорректный запрос в тикет-сервис'],
            },
            400,
        ),
        (
            'DARIA5008',
            {
                'status': 'error',
                'errors': ['Ошибка авторизации в тикет-сервисе'],
            },
            400,
        ),
        (
            'DARIA5009',
            {'status': 'error', 'errors': ['Тикет не существует']},
            400,
        ),
        (
            'DARIA5010',
            {'status': 'error', 'errors': ['Серверная ошибка тикет-сервиса']},
            400,
        ),
        (
            'BLABLA-1-1',
            {'status': 'error', 'errors': ['Тикет не существует']},
            400,
        ),
    ],
)
@pytest.mark.translations(
    tariff_editor={
        'zalogin.ticket.errors.not_exists': {
            'ru': 'Тикет не существует',
            'en': '',
        },
        'zalogin.ticket.errors.unauthorized': {
            'ru': 'Ошибка авторизации в тикет-сервисе',
            'en': '',
        },
        'zalogin.ticket.errors.server_error': {
            'ru': 'Серверная ошибка тикет-сервиса',
            'en': '',
        },
        'zalogin.ticket.errors.incorrect_data_format': {
            'ru': 'Некорректный запрос в тикет-сервис',
            'en': '',
        },
    },
)
async def test_check_ticket(
        taxi_zalogin,
        mockserver,
        tracker_internal,
        chatterbox_internal,
        ticket,
        expected_status_json,
        expected_status_code,
):
    body = {'yandex_uid': '1111', 'comment': ticket}
    headers = {'X-Yandex-Login': 'login'}

    @mockserver.handler('/passport-internal/2/account/1111/password_options/')
    def _unbind_phonish_by_uid():
        return mockserver.make_response('{"status":"ok"}', 200)

    response = await taxi_zalogin.post(
        'admin/password-reset', body, headers=headers,
    )

    assert response.status_code == expected_status_code
    assert response.json() == expected_status_json
