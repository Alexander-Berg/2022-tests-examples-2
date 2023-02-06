# pylint: disable=unused-variable,unused-argument,protected-access

import re

import pytest

from crm_admin import storage
from crm_admin.api import quicksegment_get_input_schema
from crm_admin.utils.segment import quicksegment
from test_crm_admin.utils import audience_cfg


def get_full_schema(audience, is_valid=True):
    schema = {
        'audience': audience,
        'version': '0.0',
        'schemas': [
            {
                'id': 'table_schema',
                'format': 'yaml',
                'text': """
                    tables:
                      - name: base
                        path:
                    root_table: base
                    graph: []
                """,
            },
            {
                'id': 'filter_schema',
                'format': 'yaml',
                'text': """
                    filters:
                      - id: 'filter1'
                        where: base.colubm is not null
                    'targets': ['filter1']
                """,
            },
            {'id': 'input_schema', 'format': 'json', 'text': '[]'},
        ],
    }

    if not is_valid:
        table_schema = schema['schemas'][0]
        assert table_schema['id'] == 'table_schema'
        table_schema[
            'text'
        ] = """
                tables:
                  - name: base
                    path:
                graph: []
            """
    return schema


@pytest.mark.parametrize(
    'audience, ver, expected_ver, status',
    [
        ('User', '1.123', '1.123', 200),
        ('User', '1', '1.345', 200),
        ('Driver', '1', '1.456', 200),
        ('Unknown', '0', None, 404),
        ('User', '0.100', None, 404),
        ('User', '100', None, 404),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_get_full_schema(
        web_app_client, audience, ver, expected_ver, status,
):
    response = await web_app_client.get(
        '/v1/quicksegment/full-schema',
        params={'audience': audience, 'version': ver},
    )
    assert response.status == status
    if status != 200:
        return

    response = await response.json()
    assert response['version'] == expected_ver
    assert response['audience'] == audience
    schemas = {item['id'] for item in response['schemas']}
    assert schemas == {'table_schema', 'filter_schema', 'input_schema'}


@pytest.mark.parametrize(
    'audience, is_valid, status, base_ver, expected_ver',
    [
        ('User', True, 200, '1.345', '1.346'),
        ('User', True, 200, '2', '2.1'),
        ('Driver', True, 200, '1.456', '1.457'),
        ('User', False, 422, '1.345', None),
        ('User', True, 422, '1', None),
        ('User', True, 409, '1.344', '1.345'),
        ('uknown', True, 404, '1.0', None),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.config(CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS)
async def test_post_full_schema(
        web_app_client,
        web_context,
        audience,
        is_valid,
        status,
        base_ver,
        expected_ver,
):
    params = get_full_schema(audience, is_valid)
    params['version'] = base_ver

    response = await web_app_client.post(
        '/v1/quicksegment/full-schema', json=params,
    )
    assert response.status == status

    if status == 409:
        response = await response.json()
        latest_version = response['data']
        assert latest_version == expected_ver

    if status == 200:
        response = await response.json()
        new_version = response['data']
        assert new_version == expected_ver

        expected = params.copy()
        expected['version'] = new_version
        expected['schemas'] = sorted(
            expected['schemas'], key=lambda item: item['id'],
        )

        db_quicksegment = storage.DbQuicksegment(web_context)
        new_schema = await db_quicksegment.fetch_full_schema(
            audience, new_version,
        )
        assert new_schema.serialize() == expected


@pytest.mark.parametrize(
    'audience, base_ver, expected_ver',
    [
        ('User', '1', '1.345'),
        ('User', '0', '0.123'),
        ('Driver', '1', '1.456'),
        ('User', '100', '100.0'),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_latest_version(web_context, audience, base_ver, expected_ver):
    db_quicksegment = storage.DbQuicksegment(web_context)
    latest_version = await db_quicksegment.latest_version(audience, base_ver)
    assert latest_version == expected_ver


@pytest.mark.parametrize(
    'audience, expected',
    [
        ('User', ['0.123', '1.345']),
        ('Driver', ['0.12', '1.456']),
        ('unknown', ['0.0']),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_list_latest_versions(
        web_app_client, web_context, audience, expected,
):
    response = await web_app_client.get(
        '/v1/quicksegment/versions', params={'audience': audience},
    )
    assert response.status == 200

    latest_versions = await response.json()
    assert latest_versions == expected


@pytest.mark.config(CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS)
async def test_post_new_full_schema(web_app_client, web_context):
    audience = 'User'
    params = get_full_schema(audience)
    params['version'] = '1'

    response = await web_app_client.post(
        '/v1/quicksegment/full-schema', json=params,
    )
    assert response.status == 200
    response = await response.json()
    new_version = response['data']
    assert new_version == '1.1'

    expected = params.copy()
    expected['version'] = new_version
    expected['schemas'] = sorted(
        expected['schemas'], key=lambda item: item['id'],
    )

    db_quicksegment = storage.DbQuicksegment(web_context)
    new_schema = await db_quicksegment.fetch_full_schema(audience, '1')

    assert new_schema.serialize() == expected


@pytest.mark.config(CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS)
async def test_post_empty_schemas(web_app_client, web_context):
    audience = 'User'
    params = {
        'audience': audience,
        'version': '1.345',
        'schemas': [
            {'id': 'table_schema', 'format': 'yaml', 'text': ''},
            {'id': 'filter_schema', 'format': 'yaml', 'text': ''},
            {'id': 'input_schema', 'format': 'json', 'text': '{}'},
        ],
    }

    response = await web_app_client.post(
        '/v1/quicksegment/full-schema', json=params,
    )
    assert response.status == 422


@pytest.mark.parametrize(
    'audience, is_valid, status',
    [('User', True, 200), ('Driver', True, 200), ('User', False, 422)],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_validate(
        web_app_client, web_context, audience, is_valid, status,
):
    params = get_full_schema(audience, is_valid)
    response = await web_app_client.post(
        '/v1/quicksegment/validate', json=params,
    )
    assert response.status == status


@pytest.mark.parametrize(
    'name, is_valid',
    [('valid', True), ('unknown environ', False), ('missing environ', False)],
)
async def test_validate_table_environs(load_json, name, is_valid):
    schemas = dict(table_schema=load_json('table_schemas.json')[name])
    if is_valid:
        assert quicksegment.validate_table_environs(schemas)
    else:
        with pytest.raises(quicksegment.qs.error.ValidationError):
            quicksegment.validate_table_environs(schemas)


@pytest.mark.parametrize('is_valid, status', [(True, 200), (False, 422)])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_render_sql(web_app_client, web_context, is_valid, status):
    params = get_full_schema('User', is_valid)
    response = await web_app_client.post(
        '/v1/quicksegment/render-sql', json=params,
    )
    assert response.status == status

    if status == 200:
        sql = (await response.json())['data']
        assert re.match(r'SELECT.*FROM.*WHERE', sql, re.DOTALL)


async def test_invalid_yaml(web_app_client):
    params = get_full_schema('User')
    table_schema = params['schemas'][0]
    assert table_schema['id'] == 'table_schema'

    table_schema[
        'text'
    ] = """
        tables:
          - name: base
                path:
        root_table: base
        graph: []
    """

    response = await web_app_client.post(
        '/v1/quicksegment/render-sql', json=params,
    )
    assert response.status == 422
    assert 'invalid format' in (await response.json())['message']


async def test_invalid_json(web_app_client):
    params = get_full_schema('User')
    input_schema = params['schemas'][2]
    assert input_schema['id'] == 'input_schema'
    input_schema['text'] = '{{}'

    response = await web_app_client.post(
        '/v1/quicksegment/render-sql', json=params,
    )
    assert response.status == 422
    assert 'invalid format' in (await response.json())['message']


@pytest.mark.parametrize(
    'campaign_id, status', [(1, 200), (2, 200), (3, 200), (100, 404)],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_get_input_schema(
        web_app_client, campaign_id, status, load_json,
):
    response = await web_app_client.get(
        '/v1/quicksegment/input-schema', params={'campaign_id': campaign_id},
    )
    assert response.status == status

    if status == 200:
        response = await response.json()
        expected = load_json('input_schemas.json')[str(campaign_id)]
        assert response == expected


def test_filter_regular_schema():
    input_schema = [
        {'id': 'oneshot_filters'},
        {
            'id': 'oneshot_filters/1',
            'groupId': 'oneshot_filters',
            'campaign_type': 'oneshot',
        },
        {
            'id': 'oneshot_filters/2',
            'groupId': 'oneshot_filters',
            'campaign_type': 'oneshot',
        },
        {'id': 'oneshot_group', 'campaign_type': 'oneshot'},
        {'id': 'oneshot_group/1', 'groupId': 'oneshot_group'},
        {'id': 'oneshot_group/2', 'groupId': 'oneshot_group'},
        {'id': 'mixed_group'},
        {
            'id': 'mixed_group/1',
            'groupId': 'mixed_group',
            'campaign_type': 'oneshot',
        },
        {
            'id': 'mixed_group/2',
            'groupId': 'mixed_group',
            'campaign_type': 'regular',
        },
        {'id': 'mixed_group/3', 'groupId': 'mixed_group'},
    ]

    oneshot_expected = [
        'oneshot_filters',
        'oneshot_filters/1',
        'oneshot_filters/2',
        'oneshot_group',
        'oneshot_group/1',
        'oneshot_group/2',
        'mixed_group',
        'mixed_group/1',
        'mixed_group/3',
    ]
    oneshot_actual = [
        item['id']
        for item in quicksegment_get_input_schema._remove_non_regular_items(
            input_schema, 'oneshot',
        )
    ]
    assert oneshot_expected == oneshot_actual

    regular_expected = ['mixed_group', 'mixed_group/2', 'mixed_group/3']
    regular_actual = [
        item['id']
        for item in quicksegment_get_input_schema._remove_non_regular_items(
            input_schema, 'regular',
        )
    ]
    assert regular_expected == regular_actual


@pytest.mark.parametrize(
    'audience, version, status', [('Driver', '1', 200), ('Driver', '2', 404)],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_render_final_sql(
        web_context, web_app_client, audience, version, status,
):
    params = {
        'audience': audience,
        'version': version,
        'variables': {'var': 1},
    }

    response = await web_app_client.post(
        '/v1/quicksegment/render-final-sql', json=params,
    )
    assert response.status == status
