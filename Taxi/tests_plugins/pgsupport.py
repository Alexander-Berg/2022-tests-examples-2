import pathlib
import typing

from testsuite.databases.pgsql import discover


class BaseError(Exception):
    """Base class for exceptions of this module."""


class PgConfigurationError(BaseError):
    pass


def find_databases(
        service_name: str,
        get_source_path,
        source_dir: pathlib.Path,
        service_yaml: dict,
) -> typing.Dict[str, discover.PgShardedDatabase]:
    service_databases = service_yaml.get('postgresql', {}).get('databases', [])
    if not service_databases:
        return {}

    common_schemas_dir = get_source_path('../schemas/schemas/postgresql')
    shared_schemas = discover.find_schemas(
        service_name,
        schema_dirs=[
            common_schemas_dir / dbname for dbname in service_databases
        ],
    )
    schemas = discover.find_schemas(
        service_name,
        schema_dirs=[
            source_dir / 'testsuite/schemas/postgresql',
            source_dir / 'postgresql',
        ],
    )
    discovered = {**shared_schemas, **schemas}

    databases = {}
    for dbname in service_databases:
        if dbname in discovered:
            databases[dbname] = discovered[dbname]
        else:
            databases[dbname] = discover.PgShardedDatabase(
                service_name, dbname, shards=[],
            )
    return databases
