import collections
import pathlib
from typing import DefaultDict
from typing import Dict
from typing import List

from . import classes
from . import utils


def find_schemas(
        schema_dirs: List[pathlib.Path], dbprefix: str = 'testsuite-',
) -> Dict[str, classes.DatabaseConfig]:
    """Retrieve database schemas from filesystem.

    :param schema_dirs: list of schema pathes
    :param dbprefix: database name internal prefix
    :returns: Dictionary where key is dbname and value is
        ``classes.DatabaseConfig`` instance.
    """
    result = {}
    for path in schema_dirs:
        if not path.is_dir():
            continue
        for dbname, migrations in _scan_path(path).items():
            result[dbname] = classes.DatabaseConfig(
                dbname=dbprefix + dbname, migrations=migrations,
            )
    return result


def _scan_path(
        schema_path: pathlib.Path,
) -> DefaultDict[str, List[pathlib.Path]]:
    result = collections.defaultdict(list)
    for entry in schema_path.iterdir():
        if entry.suffix == '.sql' and entry.is_file():
            result[entry.stem].append(entry)
        elif entry.is_dir():
            result[entry.stem].extend(utils.scan_sql_directory(entry))
    return result
