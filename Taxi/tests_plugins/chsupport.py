import pathlib
import typing

from testsuite.databases.clickhouse import classes
from testsuite.databases.clickhouse import discover


class BaseError(Exception):
    """Base class for exceptions of this module."""


class ChConfigurationError(BaseError):
    pass


def find_databases(
        get_source_path,
        source_dir: pathlib.Path,
        service_databases: typing.List[str],
) -> typing.Dict[str, classes.DatabaseConfig]:
    common_schemas_dir = get_source_path('../schemas/schemas/clickhouse')
    shared_schemas = discover.find_schemas(
        schema_dirs=[
            common_schemas_dir / dbname for dbname in service_databases
        ],
        dbprefix='',
    )
    schemas = discover.find_schemas(
        schema_dirs=[
            source_dir / 'testsuite' / 'schemas' / 'clickhouse',
            source_dir / 'clickhouse',
        ],
        dbprefix='',
    )

    discovered = {**shared_schemas, **schemas}
    databases = {}
    for dbname in service_databases:
        if dbname in discovered:
            databases[dbname] = discovered[dbname]
        else:
            databases[dbname] = classes.DatabaseConfig(
                dbname=dbname, migrations=[],
            )
    return databases
