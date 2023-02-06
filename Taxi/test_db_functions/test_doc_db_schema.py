import asyncio
import os

import pytest

import taxi_exp


WRITE_DOCUMENTATION_PATH = os.path.join(
    os.path.dirname(taxi_exp.__file__), 'docs', 'clean_schema_and_tables.psql',
)


class NonZeroExitCodeError(Exception):
    def __init__(self, exit_code, *args, stderr=''):
        super().__init__(
            f'subprocess with args {args} returned non-zero exit code: '
            f'{exit_code} {stderr}',
        )


async def _call_command(*args):
    # pylint: disable=no-value-for-parameter
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise NonZeroExitCodeError(process.returncode, *args, stderr=stderr)

    return stdout, stderr


@pytest.mark.skip
@pytest.mark.pgsql('taxi_exp')
async def test_write_actual_doc_for_db_schema(taxi_exp_client, pgsql_local):
    exp_db_uri = pgsql_local['taxi_exp'].get_dsn()
    raw_text, fail = await _call_command(
        'pg_dump',
        '--no-owner',
        '--schema-only',
        '--schema=clients_schema',
        f'--dbname={exp_db_uri}',
    )
    assert not fail
    assert raw_text

    with open(WRITE_DOCUMENTATION_PATH, 'wb') as doc:
        doc.write(raw_text)
