import dataclasses
import json
import typing as tp


@dataclasses.dataclass(init=True)
class Parameter:
    name: str
    value: tp.Any
    version: int = 0


@dataclasses.dataclass(init=True)
class ParameterDefinition:
    name: str
    schema: tp.Any
    actions: tp.Set[str]


@dataclasses.dataclass(init=True)
class Tariff:
    name: str
    group_name: tp.Optional[str] = None


def execute_query(query, pgsql):
    pg_cursor = pgsql['dispatch_settings'].cursor()
    pg_cursor.execute(query)


def mock_parameters(
        pgsql: tp.Any,
        parameters: tp.List[ParameterDefinition],
        settings: tp.Dict[str, tp.Dict[str, tp.List[Parameter]]],
        groups: tp.Set[str],
        zone_names: tp.Set[str],
        tariffs: tp.List[Tariff],
):
    default_actions = {
        'set',
        'remove',
        'add_kv',
        'edit_kv',
        'add_items',
        'remove_items',
        'update_dict',
        'remove_kvs',
    }

    insert_groups_query = (
        'INSERT INTO dispatch_settings.groups (name, description) '
        'VALUES {}'.format(
            ','.join(('(\'{}\', \'desc\')'.format(name) for name in groups)),
        )
    )

    insert_zones_query = (
        'INSERT INTO dispatch_settings.zones (zone_name) VALUES {}'
    ).format(','.join(('(\'{}\')'.format(name) for name in zone_names)))

    insert_tariffs_query = (
        (
            'INSERT INTO dispatch_settings.tariffs (tariff_name, group_id) '
            'VALUES {}'
        ).format(
            ','.join(
                (
                    '(\'{}\', (SELECT id FROM dispatch_settings.groups '
                    'WHERE name = \'{}\'))'.format(
                        tariff.name, tariff.group_name,
                    )
                    for tariff in tariffs
                ),
            ),
        )
    )

    insert_actions = (
        'INSERT INTO dispatch_settings.actions (name) ' 'VALUES {}'
    ).format(','.join(('(\'{}\')'.format(name) for name in default_actions)))

    insert_parameters = (
        (
            'INSERT INTO dispatch_settings.parameters (field_name, schema) '
            'VALUES {}'
        ).format(
            ','.join(
                (
                    '(\'{}\', \'{}\')'.format(
                        param.name, json.dumps(param.schema),
                    )
                    for param in parameters
                ),
            ),
        )
    )

    insert_allowed_parameters = (
        (
            'INSERT INTO dispatch_settings.allowed_actions '
            '    (param_id, action_id) '
            'VALUES {}'
        ).format(
            ','.join(
                (
                    (
                        '('
                        '(SELECT id FROM dispatch_settings.parameters '
                        ' WHERE field_name = \'{}\'),'
                        '(SELECT id FROM dispatch_settings.actions '
                        ' WHERE name = \'{}\')'
                        ')'
                    ).format(param.name, action)
                    for param in parameters
                    for action in param.actions
                ),
            ),
        )
    )

    insert_settings = (
        (
            'INSERT INTO dispatch_settings.settings '
            '    (zone_id, tariff_id, param_id, version, value) '
            'VALUES {}'
        ).format(
            ','.join(
                (
                    (
                        '('
                        '(SELECT id FROM dispatch_settings.zones '
                        ' WHERE zone_name = \'{}\'), '
                        '(SELECT id FROM dispatch_settings.tariffs '
                        ' WHERE tariff_name = \'{}\'), '
                        '(SELECT id FROM dispatch_settings.parameters '
                        ' WHERE field_name = \'{}\'), '
                        '{}, '
                        '{}'
                        ')'
                    ).format(
                        zone_name,
                        tariff_name,
                        param.name,
                        param.version,
                        'NULL'
                        if param.value is None
                        else '\'{}\''.format(json.dumps(param.value)),
                    )
                    for zone_name, level_1 in settings.items()
                    for tariff_name, params in level_1.items()
                    for param in params
                ),
            ),
        )
    )

    queries = (
        insert_groups_query,
        insert_zones_query,
        insert_tariffs_query,
        insert_actions,
        insert_parameters,
        insert_allowed_parameters,
        insert_settings,
    )

    for query in queries:
        execute_query(query, pgsql)


async def get_settings_for(client: tp.Any, zone_name: str, tariff_name: str):
    response = await client.get(
        '/v2/admin/fetch',
        params={'zone_name': zone_name, 'tariff_name': tariff_name},
    )
    assert response.status == 200
    content = await response.json()
    return content['settings']


def current_settings(cursor):
    cursor.execute(
        """
      SELECT tariff_name, zone_name, field_name, version, value
      FROM dispatch_settings.settings settings
      JOIN dispatch_settings.zones zones ON zones.id = zone_id
      JOIN dispatch_settings.tariffs tariffs ON tariffs.id = tariff_id
      JOIN dispatch_settings.parameters params ON params.id = param_id
      ORDER BY tariff_name, zone_name, field_name;
    """,
    )
    result = cursor.fetchall()
    return sorted(result)


async def get_categories(client: tp.Any):
    response = await client.get('/v1/admin/dispatch_settings_info')
    assert response.status == 200
    content = await response.json()
    content['categories'].sort(key=lambda cat: cat['zone_name'])
    for cat in content['categories']:
        cat['tariff_names'].sort()
    return content['categories']
