# coding: utf8
import asyncio
import datetime
import logging
import os
from typing import Optional

import requests

from vault_client.vault_client.instances import (  # noqa  # pylint: disable=E0401
    Production as VaultClient,
)

logger = logging.getLogger(__name__)


class PgDumpSampler:
    def __init__(
            self,
            sample_name: str,
            file_name: str,
            date: datetime.date,
            token_path: str,
            options: Optional[dict] = None,
    ):
        assert options
        self.__db_name = sample_name
        self.__file_name = os.path.abspath(os.path.join(options['file_name']))
        self.__secret = options['secret']
        self.__table = options.get('table')
        self.__exclude_table = options.get('exclude_table')

    async def sample_data(self) -> bool:
        try:
            client = VaultClient(decode_files=True, check_status=False)
            secret = client.get_version(self.__secret)
            host = secret['value']['shards.0.host']
            port = secret['value']['shards.0.port']
            user = secret['value']['shards.0.user']
            password = secret['value']['shards.0.password']
            connection_string = (
                f'host={host} port={port} dbname={self.__db_name} '
                f'user={user} password={password} '
                f'sslmode=verify-full target_session_attrs=any'
            )
            logger.info(f'host={host} port={port} dbname={self.__db_name}')
            if os.path.exists(self.__file_name):
                logger.info(f'backup {self.__file_name}')
                os.rename(self.__file_name, self.__file_name + '.bak')
            return await dump_database(
                connection_string=connection_string,
                table=self.__table,
                exclude_table=self.__exclude_table,
                out=self.__file_name,
            )
        except requests.exceptions.ConnectionError as error:
            logger.error(f'Error: {str(error)}')
            if 'CERTIFICATE_VERIFY_FAILED' in str(error):
                logger.error(
                    'To fix visit: https://wiki.yandex-team.ru'
                    '/security/ssl/sslclientfix/#vpython',
                )
        except Exception as error:  # pylint: disable=broad-except
            logger.error(f'Error: {str(error)}')
        return False


async def dump_database(
        connection_string: str,
        table: Optional[list],
        exclude_table: Optional[list],
        out: str,
) -> bool:
    args = [
        'pg_dump',
        '--data-only',
        '--inserts',
        '--attribute-inserts',
        f'{connection_string}',
        f'--file={out}',
    ]
    if table:
        args = args + [f'--table={t}' for t in table]
    if exclude_table:
        args = args + [f'--exclude-table={t}' for t in exclude_table]
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    logger.info(f'Started: pg_dump to {out} (pid = {process.pid})')
    stdout, stderr = await process.communicate()
    if stdout:
        logger.info(f'pg_dump stdout: {stdout.decode()}')
    if stderr:
        logger.info(f'pg_dump stderr: {stderr.decode()}')
    return process.returncode == 0
