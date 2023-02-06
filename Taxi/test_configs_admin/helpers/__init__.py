from typing import Any
from typing import Dict

from configs_admin.migration import config_models


def get_config_with_value(
        default_value: Dict[str, Any], schema: Dict[str, Any],
):
    base_config = config_models.BaseConfig(
        name='TEST_SETTINGS',
        description='description',
        full_description='',
        wiki='',
        group='graph',
        default=default_value,
        tags=[],
        validator_declarations=[],
        schema=schema,
        schema_definitions={},
        maintainers=['dvasiliev89', 'serg-novikov'],
        turn_off_immediately=False,
    )
    return config_models.ConfigWithValue.from_base_config(
        base_config,
        default_value,
        'test edition',
        'TAXIBACKEND-1',
        None,
        None,
    )


async def get_schema_field(context, name, field_name) -> Any:
    return (await context.mongo.uconfigs_schemas.find_one({'_id': name})).get(
        field_name,
    )


async def get_value_v1(
        app_client, name, params, ticket='good', need_verbose: bool = False,
):
    url = f'/v1/configs/{name}/'
    headers = {'X-Ya-Service-Ticket': ticket}
    query_params = {
        key: value for key, value in params.items() if key != 'name'
    }

    response = await app_client.get(url, headers=headers, params=query_params)

    if need_verbose:
        return response
    return await response.json()


async def get_value_v2(
        app_client, params, ticket='good', need_verbose: bool = False,
):
    assert 'name' in params, 'Config name must be filled in request'
    url = '/v2/configs/'
    headers = {'X-Ya-Service-Ticket': ticket}

    response = await app_client.get(url, headers=headers, params=params)
    if need_verbose:
        return response
    return await response.json()
