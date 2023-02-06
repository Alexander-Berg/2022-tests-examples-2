from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple

from configs_admin import storage

ANY_VALUE = '__any__'


class Case(NamedTuple):
    method_name: str
    args: List[Any] = []
    kwargs: Dict[str, Any] = {}
    ignore_fields: List[str] = []
    expected: Any = None
    post_processing: Any = lambda x: x

    @classmethod
    def get_args(cls) -> str:
        return ','.join(cls.__annotations__.keys())  # pylint: disable=E1101


def get_args(typename: Any) -> str:
    return ','.join(typename.__annotations__.keys())


async def get_values(web_context, name, service_name=None, stage_name=None):
    result = {'main': None, 'service': None, 'stage': None, 'schema': None}

    # schema
    schema = await web_context.mongo.uconfigs_schemas.find_one(
        {storage.SCHEMA_FIELDS.NAME: name},
    )
    if schema:
        result['schema'] = schema[storage.SCHEMA_FIELDS.SCHEMA]

    # main
    main_value = await web_context.mongo.config.find_one(
        {storage.CONFIG_FIELDS.NAME: name},
    )
    if main_value:
        result['main'] = main_value.get(storage.CONFIG_FIELDS.VALUE)

    # service
    service_query = {storage.SERVICE_VALUES_FIELDS.NAME: name}
    if service_name != ANY_VALUE:
        service_query[
            storage.SERVICE_VALUES_FIELDS.SERVICE_NAME
        ] = service_name
    service_value = await web_context.mongo.configs_by_service.find_one(
        service_query,
    )
    if service_value:
        result['service'] = service_value.get(
            storage.SERVICE_VALUES_FIELDS.VALUE,
        )

    # stage
    stage_query = {storage.STAGE_VALUE_FIELDS.NAME: name}
    if stage_name != ANY_VALUE:
        stage_query[storage.STAGE_VALUE_FIELDS.STAGE_NAME] = stage_name
    stage_value = await web_context.mongo.uconfigs.find_one(stage_query)
    if stage_value:
        result['stage'] = stage_value.get(storage.STAGE_VALUE_FIELDS.VALUE)

    return result
