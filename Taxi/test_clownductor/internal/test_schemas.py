import asyncio
import difflib
import pathlib

from testsuite.databases.pgsql import discover


async def _call_command(args):
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode:
        raise Exception(stderr.decode())

    return stdout, stderr


async def get_schemas(params):
    row_schemas, errors = await _call_command(
        ['pg_dump', '--no-owner', '--schema-only', f'{params}'],
    )
    return row_schemas.decode().lower().splitlines(), errors


async def test_validate_schemas(web_context, pgsql_local, pgsql_control):
    psql_discover_info = discover.find_schemas(
        service_name='clownductor',
        schema_dirs=[
            pathlib.Path(__file__).parent.parent.joinpath(
                'internal/static/test_schemas',
            ),
        ],
    )
    pgsql_control.initialize_sharded_db(
        psql_discover_info['actual_clownductor'],
    )
    actual_conn_wrapper = pgsql_control.get_connection_cached(
        'clownductor_actual_clownductor',
    )

    connection_info = pgsql_local['clownductor']
    connection_params = connection_info.get_dsn()
    schemas_by_migrations, errors = await get_schemas(connection_params)
    assert not errors

    actual_schemas, errors = await get_schemas(
        f'host={connection_info.host} port={connection_info.port}'
        f' user={connection_info.user} dbname=clownductor_actual_clownductor',
    )
    assert not errors

    with actual_conn_wrapper.conn as conn:
        with conn.cursor() as cursor:
            cursor.execute('DROP SCHEMA clownductor CASCADE;')

    differ = difflib.Differ()
    result = '\n'.join(differ.compare(schemas_by_migrations, actual_schemas))
    schemas_by_migrations.sort()
    actual_schemas.sort()
    assert schemas_by_migrations == actual_schemas, result
