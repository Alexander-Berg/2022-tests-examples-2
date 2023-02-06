import collections
import os
import os.path

from . import exceptions
from . import utils


class SingleShard:
    pass


class PgShard:
    def __init__(
            self,
            dbname,
            service_name=None,
            shard_id=SingleShard,
            files=(),
            migrations=None,
    ):
        if shard_id is SingleShard:
            self.shard_id = 0
            self.pretty_name = dbname
            sharded_dbname = dbname
        else:
            self.shard_id = shard_id
            self.pretty_name = '%s@%d' % (dbname, shard_id)
            sharded_dbname = '%s_%d' % (dbname, shard_id)
        if service_name is not None:
            sharded_dbname = '%s_%s' % (
                _normalize_name(service_name),
                sharded_dbname,
            )
        self.dbname = sharded_dbname
        self.files = files
        self.migrations = migrations


class PgShardedDatabase:
    def __init__(self, service_name, dbname, shards):
        self.service_name = service_name
        self.dbname = dbname
        self.shards = shards

    def initialize(self, pg_control):
        print(
            'Initializing database %s for service %s...'
            % (self.dbname, self.service_name),
        )
        connections = {}
        for shard in self.shards:
            print('Creating database %s' % (shard.dbname,))
            pg_control.create_database(shard.dbname)
            for path in shard.files:
                print(
                    'Running sql script %s against database %s'
                    % (path, shard.dbname),
                )
                pg_control.run_script(shard.dbname, path)

            if shard.migrations:
                for path in shard.migrations:
                    print(
                        'Running migrations from %s against database %s'
                        % (path, shard.dbname),
                    )
                    pg_control.run_migrations(shard.dbname, path)

            connections[shard.pretty_name] = pg_control.get_connection_cached(
                shard.dbname,
            )
        return connections


def find_databases(service_name, schema_path, migrations_path=None):
    schemas = {}
    migrations = {}

    if os.path.isdir(schema_path):
        schemas = _find_databases_schemas(service_name, schema_path)

    if migrations_path and os.path.isdir(migrations_path):
        migrations = _find_databases_migrations(service_name, migrations_path)

    for conflict in schemas.keys() & migrations.keys():
        raise exceptions.PostgresqlError(
            'Database %s has both migrations and schemas' % (conflict,),
        )

    return {**schemas, **migrations}


def _find_databases_schemas(service_name, schema_path):
    fixtures = collections.defaultdict(lambda: collections.defaultdict(list))
    result = {}

    for child in os.listdir(schema_path):
        fullpath = os.path.join(schema_path, child)
        basename, suffix = os.path.splitext(child)
        dbname, shard = _split_shard(basename)
        if suffix == '.sql':
            fixtures[dbname][shard].append(fullpath)
        elif os.path.isdir(fullpath):
            files = utils.scan_sql_directory(fullpath)
            if not files:
                continue
            fixtures[dbname][shard].extend(files)

    for dbname, shards in fixtures.items():
        if SingleShard in shards:
            if len(shards) != 1:
                raise exceptions.PostgresqlError(
                    'Postgresql database %s has single shard configuration '
                    'while defined as multishard' % (dbname,),
                )
        else:
            if set(shards.keys()) != set(range(len(shards))):
                raise exceptions.PostgresqlError(
                    'Postgresql database %s is missing fixtures '
                    'for some shards' % (dbname,),
                )

        pg_shards = []
        for shard_id, shard_files in sorted(shards.items()):
            pg_shards.append(
                PgShard(
                    dbname,
                    service_name=service_name,
                    shard_id=shard_id,
                    files=sorted(shard_files),
                ),
            )
        result[dbname] = PgShardedDatabase(
            service_name=service_name, dbname=dbname, shards=pg_shards,
        )
    return result


def _find_databases_migrations(service_name, migrations_path):
    migrations = collections.defaultdict(lambda: collections.defaultdict(list))
    result = {}

    for basename in os.listdir(migrations_path):
        fullpath = os.path.join(migrations_path, basename)
        dbname, shard = _split_shard(basename)
        if os.path.isdir(fullpath):
            migrations[dbname][shard].append(fullpath)

    for dbname, shards in migrations.items():
        if SingleShard in shards:
            if len(shards) != 1:
                raise exceptions.PostgresqlError(
                    'Postgresql database %s has single shard configuration '
                    'while defined as multishard' % (dbname,),
                )
        else:
            if set(shards.keys()) != set(range(len(shards))):
                raise exceptions.PostgresqlError(
                    'Postgresql database %s is missing fixtures '
                    'for some shards' % (dbname,),
                )

        pg_shards = []

        for shard_id, shard_directory in sorted(shards.items()):
            pg_shards.append(
                PgShard(
                    dbname,
                    service_name=service_name,
                    shard_id=shard_id,
                    migrations=shard_directory,
                ),
            )
        result[dbname] = PgShardedDatabase(
            service_name=service_name, dbname=dbname, shards=pg_shards,
        )

    return result


def _split_shard(name):
    parts = name.rsplit('@', 1)
    if len(parts) == 2:
        try:
            shard_id = int(parts[1])
        except (ValueError, TypeError):
            pass
        else:
            return parts[0], shard_id
    return name, SingleShard


def _normalize_name(name):
    return name.replace('.', '_').replace('-', '_')
