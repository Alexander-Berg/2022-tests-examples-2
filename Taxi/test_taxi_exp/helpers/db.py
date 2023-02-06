import uuid

from taxi_exp.util import pg_helpers

DEFAULT_NAMESPACE = None

INIT_QUERY = """
INSERT INTO clients_schema.consumers (name) VALUES ('test_consumer');
INSERT INTO clients_schema.applications (name) VALUES ('android'), ('ios');
"""
ADD_CONSUMER = 'INSERT INTO clients_schema.consumers (name) VALUES (\'{}\');'
ADD_KWARGS = """
INSERT INTO clients_schema.consumer_kwargs
    (consumer, kwargs, metadata, library_version)
VALUES
    (
        \'{consumer}\'::text,
        \'{kwargs}\'::jsonb,
        \'{metadata}\'::jsonb,
        \'{library_version}\'::text);
"""
ADD_APPLICATION = (
    'INSERT INTO clients_schema.applications (name) VALUES (\'{}\');'
)
ADD_SALT = """
INSERT INTO clients_schema.salts (salt, segmentation_method)
VALUES (\'{}\', \'{}\');
"""
LINK_EXP_AND_CONS = """INSERT INTO clients_schema.experiments_consumers
    (experiment_id, consumer_id) VALUES ({}, {});"""

EXISTED_EXPERIMENT = """INSERT INTO clients_schema.experiments
    (
        name,
        date_from, date_to,
        rev, clauses, predicate, description, enabled, schema, closed
    )
        VALUES
            (
                'existed_experiment',
                CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Moscow',
                CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Moscow',
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                'DESCRIPTION',
                TRUE,
                'additionalProperties: false',
                FALSE);
"""


async def get_salts(app):
    pool = app['pool']
    query = """
    SELECT id, salt, segmentation_method FROM clients_schema.salts
    ORDER BY id;"""
    return await pg_helpers.fetch(pool, query)


async def get_rolling_stats(app):
    query = """SELECT *
    FROM clients_schema.rollout_stats ORDER BY rollout_stable_time;"""
    return await pg_helpers.fetch(app['pool'], query)


async def get_kwargs_history(app):
    query = (
        'SELECT * FROM clients_schema.consumer_kwargs_history '
        'ORDER BY updation_time;'
    )
    return await pg_helpers.fetch(app['pool'], query)


async def get_prestable_events(app):
    query = 'SELECT * FROM clients_schema.rollout_stats;'
    return await pg_helpers.fetch(app['pool'], query)


async def update_experiment_field(app, experiment_name, **kwargs):
    assert len(kwargs) == 1
    key, value = list(kwargs.items()).pop()
    query = f"""
        WITH t AS (
            UPDATE clients_schema.experiments
                SET
                    rev = nextval('clients_schema.clients_rev'),
                    {key}=$1
                WHERE name = '{experiment_name}' AND is_config IS FALSE
            RETURNING *
        )
        SELECT pg_temp.add_experiments_history_item(rev, 'direct') FROM t
        ;
        """
    await pg_helpers.execute_sql_function(app['pool'], query, str(value))


async def update_experiment_bool_field(app, experiment_name, **kwargs):
    assert len(kwargs) == 1
    key, value = list(kwargs.items()).pop()
    query = f"""
        WITH t AS (
            UPDATE clients_schema.experiments
                SET
                    rev = nextval('clients_schema.clients_rev'),
                    {key}=$1
                WHERE name = '{experiment_name}' AND is_config IS FALSE
            RETURNING *
        )
        SELECT pg_temp.add_experiments_history_item(rev) FROM t
        ;
        """
    await pg_helpers.execute_sql_function(app['pool'], query, bool(value))


async def close_experiment(app, experiment_name):
    query = f"""
        UPDATE clients_schema.experiments
            SET
                rev = nextval('clients_schema.clients_rev'),
                closed = TRUE
            WHERE name = '{experiment_name}' AND is_config IS FALSE;
        """
    await pg_helpers.execute_sql_function(app['pool'], query)


async def get_experiments_history(app, name=None):
    if not name:
        return await pg_helpers.fetch(
            app['pool'],
            'SELECT rev, name, body FROM clients_schema.experiments_history;',
        )
    return await pg_helpers.fetch(
        app['pool'],
        """
        SELECT exp.name as name, rh.rev as rev, rh.change_type as change_type
        FROM clients_schema.revision_history as rh
        INNER JOIN clients_schema.experiments as exp
            ON exp.id=rh.experiment_id
        WHERE exp.name=$1::text;""",
        name,
    )


async def get_all_experiments(app):
    return await pg_helpers.fetch(
        app['pool'], 'SELECT * FROM clients_schema.experiments;',
    )


async def get_experiments_by_tag(app, tag_name):
    return await pg_helpers.fetch(
        app['pool'],
        """
SELECT exp.name as name FROM clients_schema.experiments as exp
    INNER JOIN clients_schema.experiments_tags as ext
        ON exp.id=ext.experiment_id
            WHERE ext.file_tag=$1;""",
        tag_name,
    )


async def get_current_timestamp(app):
    query = """SELECT CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Moscow' as ct;"""
    return (await pg_helpers.fetchrow(app['pool'], query))['ct']


async def get_experiment(app, experiment_name, namespace=DEFAULT_NAMESPACE):
    query, args = app.sqlt(
        'experiments/get_one.sqlt',
        dict(
            experiment_name=experiment_name,
            namespace=namespace,
            is_config=False,
            show_removed=True,
        ),
    )
    return await pg_helpers.fetchrow(app['pool'], query, *args)


async def get_config(app, config_name, namespace=DEFAULT_NAMESPACE):
    query, args = app.sqlt(
        'experiments/get_one.sqlt',
        dict(
            experiment_name=config_name,
            is_config=True,
            show_removed=True,
            namespace=namespace,
        ),
    )
    return await pg_helpers.fetchrow(app['pool'], query, *args)


async def get_applications(app, experiment_name, namespace=DEFAULT_NAMESPACE):
    experiment = await get_experiment(
        app, experiment_name, namespace=namespace,
    )
    experiment_id = experiment['exp_id']

    return await pg_helpers.fetch(
        app['pool'],
        app.postgres_queries['applications/get_applications_by_exp_id.sql'],
        [experiment_id],
    )


async def get_all_consumers(app):
    query = 'SELECT name FROM clients_schema.consumers;'
    return await pg_helpers.fetch(app['pool'], query)


async def add_or_update_file(
        app,
        name,
        namespace=DEFAULT_NAMESPACE,
        experiment_name=None,
        file_type='string',
        mds_id=None,
        transform=None,
        file_size=None,
        file_format=None,
        lines=None,
        sha256=None,
):
    if mds_id is None:
        mds_id = uuid.uuid4().hex
    if file_format is None:
        file_format = file_type
    old_metadata = await pg_helpers.fetchrow(
        app['pool'],
        app.postgres_queries['files/get_file_metadata.sql'],
        name,
        namespace,
    )
    if old_metadata is None:
        query = 'files/add_file.sql'
    else:
        query = 'files/update_file.sql'
    await pg_helpers.execute_sql_function(
        app['pool'],
        app.postgres_queries[query],
        mds_id,
        name,
        namespace,
        experiment_name,
        file_type,
        transform,
        file_size,
        file_format,
        lines,
        sha256,
    )
    return mds_id


async def delete_file(app, mds_id, version):
    await pg_helpers.execute_sql_function(
        app['pool'], app.postgres_queries['files/delete.sql'], mds_id,
    )


async def get_file(app, mds_id, has_removed=False):
    query = """
        SELECT name, version, file_type, updated, sha256, file_size
        FROM clients_schema.files
        WHERE mds_id = $1::text AND removed = $2::boolean;
    """

    return await pg_helpers.fetchrow(app['pool'], query, mds_id, has_removed)


async def get_history(app, namespace=DEFAULT_NAMESPACE, **kwargs):
    kwargs['namespace_'] = namespace
    query, args = app.sqlt('files/search_files_history.sqlt', kwargs)
    return await pg_helpers.fetch(app['pool'], query, *args)


async def transform_file_to_trusted(app, file_id, tag):
    check_query = """
        SELECT COUNT(exp_fls.experiment_id) as experiments_count
        FROM clients_schema.experiments_files as exp_fls
            WHERE exp_fls.file_id = $1;
        """
    response = await pg_helpers.fetchrow(app['pool'], check_query, file_id)
    assert response['experiments_count'] == 0

    transform_query = """
        UPDATE clients_schema.files
            SET is_trusted=TRUE,
                file_tag=$2,
                name=''
            WHERE mds_id = $1;
        """
    await pg_helpers.execute_sql_function(
        app['pool'], transform_query, file_id, tag,
    )


async def activate_trusted_file(app, tag, file_type='string'):
    activate_query = """
        INSERT INTO clients_schema.files
            (name, mds_id, is_trusted, file_tag, version, updated, file_type)
            VALUES ($1::text,
                    $2::text,
                    TRUE,
                    $3::text,
                    0,
                    CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
                    $4::text);
        """
    await pg_helpers.execute_sql_function(
        app['pool'],
        activate_query,
        uuid.uuid4().hex,
        uuid.uuid4().hex,
        tag,
        file_type,
    )


async def update_trusted_file(app, **kwargs):
    mds_id = 'abcdef'
    args = [
        kwargs.get(arg_name) or default
        for arg_name, default in (
            ('mds_id', mds_id),
            ('file_tag', 'test_tag'),
            ('file_type', 'string'),
            ('file_format', None),
            ('file_size', 1),
            ('file_sha256', 'abc'),
            ('lines', 1),
            ('save_to_history', False),
        )
    ]
    await pg_helpers.execute_sql_function(
        app['pool'],
        app.postgres_queries['files/update_trusted_file.sql'],
        *args,
    )
    return mds_id


async def tags_by_experiment(app, experiment_name):
    return await _tags_by(app, experiment_name, is_config=False)


async def tags_by_config(app, config_name):
    return await _tags_by(app, config_name, is_config=True)


async def files_by_config(app, config_name):
    return await _files_by(app, config_name, is_config=True)


async def files_by_experiment(app, experiment_name):
    return await _files_by(app, experiment_name, is_config=False)


async def count(app, with_removed=False):
    query = 'SELECT COUNT(*) as ct FROM clients_schema.experiments ' + (
        ';' if with_removed else 'WHERE removed IS FALSE;'
    )

    response = await pg_helpers.fetchrow(app['pool'], query)
    return response['ct']


async def _tags_by(app, name, is_config):
    query = f"""
        SELECT et.file_tag as tag
        FROM clients_schema.experiments_tags as et
        INNER JOIN clients_schema.experiments as e ON e.name=$1::text
        WHERE e.is_config IS {is_config};
        """
    response = await pg_helpers.fetch(app['pool'], query, name)
    return [item['tag'] for item in response]


async def _files_by(app, name, is_config=False):
    query = f"""
        SELECT ef.file_id as file_id
        FROM clients_schema.experiments_files as ef
        INNER JOIN clients_schema.experiments as e ON e.name=$1::text
        WHERE e.is_config IS {is_config};
        """
    response = await pg_helpers.fetch(app['pool'], query, name)
    return [item['file_id'] for item in response]


async def inc_rev(app, name, namespace=DEFAULT_NAMESPACE):
    query = """
        UPDATE clients_schema.experiments
        SET rev = nextval('clients_schema.clients_rev')
        WHERE name = $1::text
            AND (namespace=$2::text OR namespace IS NULL and $2::text IS NULL);
        """
    await pg_helpers.execute_sql_function(app['pool'], query, name, namespace)


async def remove_exp(app, name, last_modified_at, namespace=DEFAULT_NAMESPACE):
    query = """
        DELETE FROM clients_schema.experiments
        WHERE name=$1::text
            AND (namespace=$2::text OR namespace IS NULL AND $2::text IS NULL)
            AND rev=$3::bigint;
        """
    return await pg_helpers.fetch(
        app['pool'], query, name, namespace, last_modified_at,
    )


async def get_owner_group(app, owner, exp_name, namespace=DEFAULT_NAMESPACE):
    query = """
        SELECT owner_login as owner, own.experiment_id as exp_id, owner_group
        FROM clients_schema.owners as own
        INNER JOIN clients_schema.experiments as exp
        ON own.experiment_id = exp.id
        WHERE own.owner_login = $1::TEXT AND exp.name=$2::text
            AND (exp.namespace=$3::text
                OR exp.namespace IS NULL AND $3::text IS NULL);
    """
    return await pg_helpers.fetch(
        app['pool'], query, owner, exp_name, namespace,
    )


async def set_owner_group(
        app, owner, owner_group, exp_name, namespace=DEFAULT_NAMESPACE,
):
    response = await get_owner_group(
        app, owner=owner, exp_name=exp_name, namespace=namespace,
    )
    exp_id = response[0]['exp_id']
    update_query = """
        UPDATE clients_schema.owners
        SET owner_group = $1::BIGINT
        WHERE owner_login = $2::TEXT AND experiment_id = $3::BIGINT;
    """
    return await pg_helpers.fetch(
        app['pool'], update_query, owner_group, owner, exp_id,
    )


async def get_all_schemas(app):
    query = """
        SELECT *
        FROM clients_schema.schemas;
    """

    return await pg_helpers.fetch(app['pool'], query)


async def get_all_schema_drafts(app):
    query = """
        SELECT *
        FROM clients_schema.schema_drafts;
    """

    return await pg_helpers.fetch(app['pool'], query)


async def set_change_type_in_rev(app, rev, change_type):
    return await pg_helpers.fetch(
        app['pool'],
        """
        UPDATE clients_schema.revision_history
        SET change_type=$2::TEXT
        WHERE rev=$1::BIGINT;
        """,
        rev,
        change_type,
    )
