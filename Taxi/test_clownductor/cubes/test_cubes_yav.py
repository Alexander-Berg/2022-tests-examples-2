import pytest

from clownductor.generated.service.mdb_api import plugin as mdb_plugin
from clownductor.internal.db import db_types
from clownductor.internal.tasks import cubes


def task_data(name):
    return {
        'id': 123,
        'job_id': 456,
        'name': name,
        'sleep_until': 0,
        'input_mapping': {},
        'output_mapping': {},
        'payload': {},
        'retries': 0,
        'status': 'in_progress',
        'error_message': None,
        'created_at': 0,
        'updated_at': 0,
    }


@pytest.mark.parametrize(
    'db_type, expected_password_id, service_type',
    [
        (None, 'sec-XXX', mdb_plugin.ServiceType.POSTGRES),
        (
            db_types.DbType.Postgres.value,
            'sec-XXX',
            mdb_plugin.ServiceType.POSTGRES,
        ),
        (db_types.DbType.Mongo.value, 'sec-XXX', mdb_plugin.ServiceType.MONGO),
        (db_types.DbType.Redis.value, '', mdb_plugin.ServiceType.REDIS),
    ],
)
async def test_yav_generate_db_readonly_secret(
        web_context,
        mdb_mockserver,
        yav_mockserver,
        db_type,
        expected_password_id,
        service_type,
):
    mdb_mockserver(slug='taxisomeservice', service_type=service_type)
    yav_mockserver()

    input_data = {
        'env': 'stable',
        'cluster_id': 'mdbq9iqofu9vus91r2j9',
        'db_name': 'some-db-name',
        'user': 'axolm',
        'ro_password_id': 'sec-XXX',
    }

    if db_type:
        input_data['db_type'] = db_type

    cube = cubes.CUBES['YavCubeGenerateDBReadonlySecret'](
        web_context,
        task_data('YavCubeGenerateDBReadonlySecret'),
        input_data,
        [],
        None,
    )

    await cube.update()

    assert cube.success
    assert cube.data['payload']['yav_ro_password_id'] == expected_password_id


@pytest.mark.usefixtures('mocks_for_service_creation')
@pytest.mark.parametrize(
    'success, create_service, empty_secret_id, vars_additions, payload',
    [
        pytest.param(
            True,
            True,
            True,
            {},
            {'ticket_comment': ''},
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES={
                    'give_secret_ro_access': True,
                    'give_secret_ro_url_for_ticket': True,
                },
            ),
        ),
        pytest.param(
            True,
            True,
            False,
            {},
            {
                'ticket_comment': (
                    'Created RO '
                    '((https://yav.yandex-team.ru/secret/sec-XXX secret)) '
                    'for you.'
                ),
            },
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES={
                    'give_secret_ro_access': True,
                    'give_secret_ro_url_for_ticket': True,
                },
            ),
        ),
        pytest.param(
            True,
            True,
            False,
            {},
            {'ticket_comment': ''},
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES={'give_secret_ro_access': True},
            ),
        ),
        pytest.param(
            True,
            True,
            False,
            {'env': 'stable'},
            {
                'ticket_comment': (
                    'Created RO '
                    '((https://yav.yandex-team.ru/secret/sec-XXX secret)) '
                    'for you. (stable)'
                ),
            },
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES={
                    'give_secret_ro_access': True,
                    'give_secret_ro_url_for_ticket': True,
                },
            ),
        ),
        pytest.param(
            True,
            True,
            False,
            {},
            {'ticket_comment': ''},
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES={'give_secret_ro_access': False},
            ),
        ),
        pytest.param(
            False,
            False,
            False,
            {},
            {'ticket_comment': ''},
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES={'give_secret_ro_access': True},
            ),
        ),
        pytest.param(
            True,
            False,
            False,
            {},
            {'ticket_comment': ''},
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES={'give_secret_ro_access': False},
            ),
        ),
    ],
)
async def test_yav_cube_give_ro_access(
        yav_mockserver,
        web_context,
        add_service,
        success,
        create_service,
        empty_secret_id,
        vars_additions,
        payload,
):
    yav_mockserver()

    if create_service:
        await add_service('test', 'test')

    secret_id = '' if empty_secret_id else 'sec-XXX'

    cube = cubes.CUBES['YavCubeGiveROAccessForRequester'](
        web_context,
        task_data('YavCubeGiveROAccessForRequester'),
        {'service_id': 1, 'secret_id': secret_id, **vars_additions},
        [],
        None,
    )

    await cube.update()
    assert cube.success == success
    assert cube.data['payload'] == payload
