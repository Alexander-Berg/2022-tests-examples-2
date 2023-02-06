# pylint: disable=redefined-outer-name
from dateutil import parser as date_parser
import pytest

import infra_drills.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['infra_drills.generated.service.pytest_plugins']

HEADERS = {'X-Forwarded-For-Y': '192.168.0.1'}

TANKER = {
    'announce_disclaimer': {
        'ru': (
            'Важно!\n'
            '➤ Мы просим дежурных от групп критичных сервисов, '
            'влияющих на цикл заказа, подключиться к ЗУМУ УЧЕНИЙ '
            '(сделать ссылкой), дежурные некритичных сервисов '
            'подключаются по желанию\n'
            '➤ Подробная информация о том, что будет происходить '
            'во время учений добавлена в описание тикета учений\n'
            '➤ Базы и разработческие виртуалки выключать не будем\n'
            'Подписаться на канал '
            '[I LIKE TECHNO](https://t.me/+TkyY_A8Jt5pB5nJD)'
        ),
    },
    'announce_email_planned': {
        'ru': (
            '🌶 #учения ДЦ {datacenter}\n'
            '{drill_date}: {drill_type} ДЦ {datacenter} в '
            '{business_units} c {drill_date}\n'
            '{comment}\n'
            '{event_entities}'
            '- - -\n'
            '{disclamer}'
        ),
    },
    'announce_event_entity': {
        'ru': (
            '- {business_unit}: c {drill_time} // [ticket]({st_ticket}); '
            '[событие в календаре]({calendar_event}))\n'
        ),
    },
    'announce_telegram_planned': {
        'ru': (
            '🌶 #учения ДЦ {datacenter}\n'
            '{drill_date}: {drill_type} ДЦ {datacenter}\n'
            '{comment}\n'
            '{event_entities}'
            '- - -\n'
            '{disclamer}'
        ),
    },
    'calendar_event_description': {
        'ru': 'Тикет: {st_ticket} Zoom: https://zoom/link',
    },
    'calendar_event_summary_external': {
        'ru': 'Общеяндексовые учения с закрытием {datacenter}',
    },
    'calendar_event_summary_internal': {
        'ru': 'Учения {business_unit} с закрытием {datacenter}',
    },
    'calendar_event_summary_maintenance': {
        'ru': 'Регламентные работы {business_unit} с закрытием {datacenter}',
    },
    'st_ticket_description': {
        'ru': (
            '===={drill_type} в ДЦ **{datacenter}**\n'
            '%%`(wacko wrapper=shade`)\n'
            'Дата и время: {date} **{time_interval}**\n'
            'Цель: {comment}\n'
            'Способ закрытия: **[net]** с предварительным снятием нагрузки\n'
            '\n'
            '====Для справки:\n'
            '- ((https://wiki.yandex-team.ru/taxi-ito/drillsreq/ '
            '#osobennostiotkljuchenijadatacentrov '
            'Особенности отключения ДЦ))\n'
            '- ((https://wiki.yandex-team.ru/taxi-ito/drillsreq '
            'Регламент учений))\n'
            '====Что затрагиваем в {datacenter}:\n'
            '{description_info}\n'
            '====**Координатор:** {coordinator}\n'
        ),
    },
    'st_ticket_description_info_external_VLA': {
        'ru': (
            '- **LXC-сервисы**: закрытие iptables, закрытие через HBF\n'
            '- **LXC-stq**: выключение, закрытие через HBF\n'
            '- **RTC-сервисы**: закрытие iptables, закрытие L7-балансеров, '
            'закрытие через HBF\n'
            '- **RTC-stq**: закрытие через HBF\n'
            '- **LXC-db**: mongo - уведение мастеров в другие ДЦ, '
            'уведение реплик в hidden; redis - уведение мастеров в другие ДЦ, '
            'выключение реплик, закрытие через HBF\n'
            '- **MDB-db**: закрытие HBF\n'
            '- Разработческие виртуалки: закрытие через HBF'
        ),
    },
    'st_ticket_description_info_internal_MAN': {
        'ru': (
            '- **LXC-сервисы**: закрытие iptables, закрытие через HBF\n'
            '- **LXC-stq**: выключение, закрытие через HBF\n'
            '- **RTC-сервисы**: закрытие iptables, закрытие L7-балансеров, '
            'закрытие через HBF\n'
            '- **RTC-stq**: закрытие через HBF\n'
            '- **LXC-db**: mongo - уведение мастеров в другие ДЦ, '
            'уведение реплик в hidden; redis - уведение мастеров в '
            'другие ДЦ, выключение реплик, закрытие через HBF\n'
            '- **MDB-db**: -\n'
            '- Разработческие виртуалки: -\n'
        ),
    },
    'st_ticket_summary': {
        'ru': (
            '[net] {business_name} {date} {time_interval} '
            '{drill_type} в ДЦ {datacenter}'
        ),
    },
}


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(
        {
            'STARTRACK_API_PROFILES': {
                'robot-taxi-prd-37274': {
                    'url': 'http://test-startrack-url/',
                    'org_id': 0,
                    'oauth_token': 'some_token',
                },
            },
        },
    )
    return simple_secdist


@pytest.fixture
def taxi_infra_drills_mocks(mockserver, load_json, pgsql):
    @mockserver.json_handler('/infra-bot-api/api/queue')
    def _infra_bot_api(request):
        subscrioption_type = request.query['subscription_type']
        assert subscrioption_type == 'subscription_drills'
        return {'result': {'ok': True, 'error': None, 'data': True}}

    @mockserver.json_handler('/sticker/send-internal/')
    def _sticker_internal(request):
        return {}

    @mockserver.json_handler('/clownductor/v1/services/duty_info/')
    def _clownductor_duty_info(request):
        service_id = request.json['service_id']
        services = load_json('clownductor_service_duty_info.json')
        if service_id == 123456:
            return mockserver.make_response(status=500)

        return services.get(
            str(str(service_id)),
            {'duty_group_id': '', 'duty_person_logins': []},
        )

    @mockserver.json_handler('/clownductor/v1/services/')
    def _clownductor_services(request):
        tplatform_namespace = request.query['tplatform_namespace']
        services = load_json('clownductor_services.json')
        return services.get(tplatform_namespace, [])

    @mockserver.json_handler('/duty-generator/api/duty_groups')
    def _duty_generator_duty_groups(request):
        return load_json('duty_generator-duty_groups.json')

    @mockserver.json_handler('/duty-generator/api/duty_group')
    def _duty_generator_duty_group(request):
        duty_groups = load_json('duty_generator-duty_group.json')
        group_id = request.query['group_id']
        return duty_groups.get(
            group_id, {'result': {'ok': True, 'error': None, 'data': []}},
        )

    @mockserver.json_handler('/abc/api/v4/duty/shifts/')
    def _abc_duty_shifts(request):
        services = load_json('abc_duty_shifts.json')
        schedule__slug = request.query.get('schedule__slug', None)
        if schedule__slug:
            return services.get(schedule__slug, {'results': []})

        return {'results': []}

    @mockserver.json_handler('/startrek/issues', prefix=True)
    async def _create_ticket_handler(request):
        def ticket_create(ticket_id):
            with pgsql['infra_drills'].cursor() as cursor:
                cursor.execute(
                    (
                        'INSERT INTO drills.tests("key", "value") '
                        f'VALUES(\'startrek\', \'{ticket_id}\')'
                    ),
                )

        def ticket_get(ticket_id):
            with pgsql['infra_drills'].cursor() as cursor:
                cursor.execute(
                    (
                        'SELECT "value" FROM drills.tests '
                        f'WHERE "value" = \'{ticket_id}\''
                    ),
                )
                return cursor.fetchall()

        method = request.method

        if method in ('PATCH', 'GET'):
            st_ticket = request.path.split('/')[-1]
            if ticket_get(st_ticket):
                return load_json(f'ticket_created_{st_ticket}.json')

            return load_json('st_no_issue.json')

        if method == 'POST':
            req_data = request.json

            if req_data['queue']['key'] == 'TAXIADMIN':
                ticket_create('TAXIADMIN-103')
                return load_json('ticket_created_TAXIADMIN-103.json')
            if req_data['queue']['key'] == 'EDAOPS':
                if 'Еда' in req_data['summary']:
                    ticket_create('EDAOPS-201')
                    return load_json('ticket_created_EDAOPS-201.json')
                if 'Лавка' in req_data['summary']:
                    ticket_create('EDAOPS-205')
                    return load_json('ticket_created_EDAOPS-205.json')

            if req_data['queue']['key'] == 'TESTQUEUE':
                return load_json('st_no_permissions_403.json')
            return load_json('st_no_queue_404.json')

    @mockserver.json_handler('/passport-yateam/blackbox')
    async def _passport_yateam(request):
        assert request.query['userip'] == '192.168.0.1'
        assert request.query['method'] == 'oauth'
        data = {
            'uid': {'value': 'azaz'},
            'status': {'value': 'VALID'},
            'user_ticket': 'BACBAC',
        }
        return data

    @mockserver.json_handler('/calendar-corp/internal/create-event')
    async def _calendar_corp_create(request):
        req_data = request.json
        drill_end_date = date_parser.parse(req_data['endTs'])
        if 'taxi' in req_data['name']:
            calendar_event = 1186911
        if 'eda' in req_data['name']:
            calendar_event = 2286922
        if 'lavka' in req_data['name']:
            calendar_event = 3386933
        return mockserver.make_response(
            json={
                'status': 'ok',
                'sequence': 0,
                'showEventId': calendar_event,
                'showDate': f'{drill_end_date.date()}',
                'endTs': f'{drill_end_date.date()}T00:00:00',
                'externalIds': ['KtLedhjPyandex.ru'],
            },
        )

    @mockserver.json_handler('/calendar-corp/internal/update-event')
    async def _calendar_corp_update(request):
        calendar_event = int(request.query['id'])
        return mockserver.make_response(
            json={
                'status': 'ok',
                'showEventId': calendar_event,
                'externalIds': ['KtLedhjPyandex.ru'],
            },
        )
