import pytest

from client_github import components as github

ARCADIA_URL = 'https://a.yandex-team.ru'
GITHUB_ORG_URL = 'https://github.yandex-team.ru/taxi'


@pytest.mark.parametrize(
    'service_yaml_link, service_yaml, database, expected_status,'
    ' expected_json, expected_error_content',
    [
        pytest.param(
            (
                f'{GITHUB_ORG_URL}/uservices/blob/develop/'
                f'services/eats-couriers-equipment/service.yaml'
            ),
            'uservice.yaml',
            {
                'flavor': 's2.micro',
                'type': 'pgaas',
                'disk_size_gb': 4,
                'testing_disk_size_gb': 2,
            },
            200,
            'single_uservice.json',
            None,
            id='uservice',
        ),
        pytest.param(
            (
                f'{GITHUB_ORG_URL}/uservices/blob/develop/'
                f'services/eats-couriers-equipment/service.yaml'
            ),
            'uservices_new_multi.yaml',
            {
                'flavor': 's2.micro',
                'type': 'pgaas',
                'disk_size_gb': 4,
                'testing_disk_size_gb': 2,
            },
            200,
            'uservices_new_multi.json',
            None,
            id='uservices_new_multi',
        ),
        pytest.param(
            (
                f'{GITHUB_ORG_URL}/uservices/blob/develop/'
                f'services/eats-couriers-equipment/service.yaml'
            ),
            'exist_main_uservices.yaml',
            {
                'flavor': 's2.micro',
                'type': 'pgaas',
                'disk_size_gb': 4,
                'testing_disk_size_gb': 2,
            },
            400,
            None,
            {
                'code': 'DB_REQUEST_ERROR',
                'message': 'Cant create database, cause main_alias is exists',
            },
            id='exist_main_uservices',
        ),
        pytest.param(
            (
                f'{GITHUB_ORG_URL}/uservices/blob/develop/'
                f'services/eats-couriers-equipment/service.yaml'
            ),
            'exist_main_uservices.yaml',
            {},
            200,
            'exist_main_uservices.json',
            None,
            id='exist_main_uservices',
        ),
        pytest.param(
            (
                f'{GITHUB_ORG_URL}/uservices/blob/develop/'
                f'services/eats-couriers-equipment/service.yaml'
            ),
            'exist_main_and_alias_uservices.yaml',
            {
                'flavor': 's2.micro',
                'type': 'pgaas',
                'disk_size_gb': 4,
                'testing_disk_size_gb': 2,
            },
            400,
            None,
            {
                'code': 'DB_REQUEST_ERROR',
                'message': 'Cant create database, cause main_alias is exists',
            },
            id='exist_main_and_alias_uservices',
        ),
        pytest.param(
            (
                f'{GITHUB_ORG_URL}/uservices/blob/develop/'
                f'services/eats-couriers-equipment/service.yaml'
            ),
            'exist_main_and_alias_uservices.yaml',
            {},
            200,
            'exist_main_and_alias_uservices.json',
            None,
            id='exist_main_and_alias_uservices',
        ),
        pytest.param(
            (
                f'{GITHUB_ORG_URL}/backend-py3/blob/develop/'
                f'services/eats-couriers-equipment/service.yaml'
            ),
            'py3_multi.yaml',
            {
                'flavor': 's2.micro',
                'type': 'pgaas',
                'disk_size_gb': 4,
                'testing_disk_size_gb': 2,
            },
            200,
            'py3_multi.json',
            None,
            id='py3_multi',
        ),
        pytest.param(
            (
                f'{GITHUB_ORG_URL}/backend-py3/blob/develop/'
                f'services/eats-couriers-equipment/service.yaml'
            ),
            'all_exists.yaml',
            {
                'flavor': 's2.micro',
                'type': 'pgaas',
                'disk_size_gb': 4,
                'testing_disk_size_gb': 2,
            },
            400,
            None,
            {
                'code': 'NOT_FOUND_NEW_ALIASES',
                'message': (
                    'No new aliases in yaml were found, existing aliases '
                    'in service.yaml:\ntaxi-devops:service-exist'
                ),
            },
            id='all_exists',
        ),
    ],
)
@pytest.mark.features_on(
    'disk_profiles',
    'yaml_duty_is_required',
    'yaml_new_duty_enabled',
    'service_draft_ticket',
    'design_review_relates',
)
@pytest.mark.pgsql('clownductor', files=['add_data.sql'])
@pytest.mark.config(
    CLOWNDUCTOR_CREATE_UNSTABLE={
        'creation_possible': True,
        'exclude_services': [],
    },
    CLOWNDUCTOR_PRESET_RANGES={
        'cpu': {'high': 10, 'low': 0},
        'datacenters_count': {'high': 3, 'low': 2},
        'ram': {'high': 16, 'low': 0},
        'root_size': {'high': 50, 'low': 0},
        'stable_instances': {'high': 3, 'low': 1},
    },
    CLOWNDUCTOR_PROFILE_DEFAULT={'__default__': 'ssd-default'},
    CLOWNDUCTOR_BANNED_PROJECTS=[
        {
            'project_name': 'taxi',
            'description_error': (
                'project name taxi was banned, '
                'please choice correct project name from '
                f'https://wiki.yandex-team.ru/taxi-ito/'
                f'cloudhowto/#spisokproektov'
            ),
        },
    ],
    CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS={
        'components': ['duty'],
        'description_template': {
            'service': (
                'В этом тикете робот будет описывать прогресс создания '
                'нового сервиса.\nОбычно все получается сделать за '
                '1-2 часа.\n\nПараметры сервиса:\n{params}\n\n'
                'FAQ: https://wiki.yandex-team.ru/taxi-tech/rtchelp/\n'
                'Manual: https://wiki.yandex-team.ru/taxi-ito/cloudhowto/'
                '\nLink: https://t.me/joinchat/AggzAFkove-smhuNqGiH_g'
            ),
            'create_multiunit_service': (
                'В этом тикете робот будет описывать прогресс создания '
                'алиасов.\nНа каждый новый алиас будет сформирован тикет.'
                '\nОбычно все получается сделать за 1-2 часа.\n\n'
                'Параметры алиасов:\n{params}\n\n'
                'FAQ: https://wiki.yandex-team.ru/taxi-tech/rtchelp/\n'
                'Manual: https://wiki.yandex-team.ru/taxi-ito/cloudhowto/'
                '\nLink: https://t.me/joinchat/AggzAFkove-smhuNqGiH_g'
            ),
        },
        'summary_template': {
            'create_multiunit_service': (
                'New aliases for service: {project_name}-{service_name}'
            ),
        },
    },
)
async def test_create_multiunit_service(
        web_app_client,
        login_mockserver,
        patch,
        load,
        load_json,
        service_yaml_link,
        service_yaml,
        database,
        expected_status,
        expected_json,
        expected_error_content,
):
    @patch('client_github.components.GithubClient.get_single_file')
    async def _get_single_file(**kwargs):
        try:
            yaml_data = load(service_yaml)
        except FileNotFoundError:
            raise github.BaseError('Client error')
        return yaml_data.encode()

    login_mockserver()
    handle = '/v1/requests/service_from_yaml/validate/'
    data = {'service_yaml_link': service_yaml_link}
    if database:
        data['database'] = database
    response = await web_app_client.post(
        handle,
        json=data,
        headers={
            'X-Yandex-Login': 'deoevgen',
            'X-YaTaxi-Ticket': 'TAXIADMIN-1234',
        },
    )
    content = await response.json()

    assert response.status == expected_status, content
    if response.status == 200:
        expected_response = load_json(f'expected_responses/{expected_json}')
        assert content == expected_response
    else:
        assert content == expected_error_content
