# coding: utf8
import datetime
import json
import logging
import os
import re
from typing import Optional

import asyncpg
import requests

from vault_client.vault_client.instances import (  # noqa  # pylint: disable=E0401
    Production as VaultClient,
)

logger = logging.getLogger(__name__)


class PgSampler:
    def __init__(
            self,
            sample_name: str,
            file_name: str,
            date: datetime.date,
            token_path: str,
            options: Optional[dict] = None,
    ):
        assert options
        logger.info(options)
        self.__db_name = sample_name
        self.__file_name = os.path.abspath(os.path.join(options['file_name']))
        self.__secret = options['secret']
        self.__table_schema = options['table_schema']
        self.__parameters = options.get('parameters', {})
        self.__tables = options.get('tables', {})

    async def sample_data(self) -> bool:
        try:
            client = VaultClient(decode_files=True, check_status=False)
            secret = client.get_version(self.__secret)
            host = secret['value']['shards.0.host']
            port = secret['value']['shards.0.port']
            user = secret['value']['shards.0.user']
            password = secret['value']['shards.0.password']
            return await dump_database_filtered(
                host=host,
                port=port,
                db_name=self.__db_name,
                user=user,
                password=password,
                table_schema=self.__table_schema,
                tables=self.__tables,
                parameters=self.__parameters,
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


async def dump_database_filtered(
        host: str,
        port: str,
        db_name: str,
        user: str,
        password: str,
        table_schema: str,
        tables: list,
        parameters: dict,
        out: str,
) -> bool:
    generated_list_file_name = os.path.join(out, 'generated')
    if os.path.isfile(generated_list_file_name):
        backup_dir_name = os.path.join(out, 'bak')
        logger.info(f'backup previous to {backup_dir_name}')
        with open(generated_list_file_name, 'r') as file:
            previous_files = file.readlines()
            file.close()
        if previous_files:
            if os.path.isdir(backup_dir_name):
                for old_file in os.listdir(backup_dir_name):
                    os.remove(os.path.join(backup_dir_name, old_file))
            else:
                os.makedirs(backup_dir_name)
            for previous_file in previous_files:
                file_name = previous_file.rstrip()
                old_file_name = os.path.join(out, file_name)
                backup_file_name = os.path.join(backup_dir_name, file_name)
                if os.path.isfile(old_file_name):
                    os.rename(old_file_name, backup_file_name)
        os.remove(generated_list_file_name)

    logger.info(f'host={host}, port={port}, db_name={db_name}, out={out}')
    conn = await asyncpg.connect(
        host=host.split(',')[0],
        port=port,
        database=db_name,
        user=user,
        password=password,
    )
    files: list = []
    try:
        if not os.path.isdir(out):
            os.makedirs(out)
        order_number = 0
        for table_name in tables:
            logger.info(f'dump table: {table_name}')
            filters = tables[table_name]['filters']
            replaces = tables[table_name]['replaces']
            if table_name != '$all':
                order_number = order_number + 1
                await dump_table(
                    conn,
                    order_number,
                    table_schema,
                    table_name,
                    out,
                    filters,
                    replaces,
                    parameters,
                    files,
                )
            else:
                all_tables = await get_all_table(
                    conn=conn,
                    table_schema=table_schema,
                    dumped_tables=tables,
                    skip_patterns=tables[table_name]['skip'],
                )
                for a_table_name in all_tables:
                    order_number = order_number + 1
                    await dump_table(
                        conn,
                        order_number,
                        table_schema,
                        a_table_name,
                        out,
                        filters,
                        replaces,
                        parameters,
                        files,
                    )
    finally:
        await conn.close()
        output = open(generated_list_file_name, 'w+')
        logger.info(f'saved: {files}')
        output.writelines('\n'.join(files))
        output.close()
    return True


async def get_all_table(
        conn: asyncpg.Connection,
        table_schema: str,
        dumped_tables: list,
        skip_patterns: list,
) -> list:
    logger.info(f'get all tables, skip: {skip_patterns}')
    patterns = []
    for skip_pattern in skip_patterns:
        patterns.append(re.compile(skip_pattern))
    statement = await conn.prepare(
        f'SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES '
        f'WHERE TABLE_SCHEMA = \'{table_schema}\'',
    )
    all_tables = await statement.fetch()
    tables = []
    for table in all_tables:
        table_name = table['table_name']
        logger.info(f'check {table_name}')
        if table_name in dumped_tables:
            logger.info(f'skip {table_name} (already dumped)')
            continue
        skip = False
        for pattern in patterns:
            if pattern.match(table_name):
                logger.info(f'skip {table_name} (matched skip regexp)')
                skip = True
                break
        if not skip:
            tables.append(table_name)
    return tables


async def dump_table(
        conn: asyncpg.Connection,
        order_number: int,
        table_schema: str,
        table_name: str,
        out: str,
        filters: dict,
        replaces: dict,
        parameters: dict,
        files: list,
):
    full_table_name = f'{table_schema}.{table_name}'
    logger.info('-------------------------------------------')
    logger.info(f'dumping {full_table_name}')
    statement = await conn.prepare(
        f'SELECT * FROM {table_schema}.{table_name} LIMIT 0;',
    )
    columns = [x.name for x in statement.get_attributes()]
    column_info = {x.name: x for x in statement.get_attributes()}

    columns_to_save = {}
    if parameters:
        for parameter_name in parameters:
            parameter = parameters[parameter_name]
            if isinstance(parameter, str) and parameter.startswith(
                    f'{full_table_name}.',
            ):
                logger.info(f'saving {parameter} to {parameter_name}')
                columns_to_save[parameter.split('.')[2]] = parameter_name
                parameters[parameter_name] = []

    table_insert_sql_file = os.path.join(
        out, f'{order_number:03d}_{table_schema}_{table_name}.sql',
    )
    table_data_file = os.path.join(
        out, f'{order_number:03d}_{table_schema}_{table_name}.jsonl',
    )
    files.append(os.path.basename(table_insert_sql_file))
    files.append(os.path.basename(table_data_file))
    output = open(table_insert_sql_file, 'w+')
    output.write(build_insert(table_schema, table_name, columns, column_info))
    output.close()

    where = build_where(filters, parameters, columns, column_info)
    logger.info(
        f'SELECT * FROM {table_schema}.{table_name}'
        f'{" WHERE <filter>" if where else ""}',
    )
    statement = await conn.prepare(
        f'SELECT * FROM {table_schema}.{table_name} {where};',
    )
    data = await statement.fetch()
    output = open(table_data_file, 'w+')
    for row in data:
        row_data = []
        for column in columns:
            if column in replaces:
                row_data.append(replaces[column])
            elif (row[column] is not None) and (
                column_info[column].type.name == 'uuid'
                or column_info[column].type.name == 'numeric'
                or column_info[column].type.name == 'timestamptz'
            ):
                row_data.append(str(row[column]))
            elif (row[column] is not None) and (
                column_info[column].type.name == 'int4range'
            ):
                range_str = str(row[column])
                # remove <Range and >
                row_data.append(range_str[7 : len(range_str) - 1])
            else:
                row_data.append(row[column])
            if column in columns_to_save:
                parameters[columns_to_save[column]].append(row[column])
        try:
            output.write(json.dumps(row_data) + '\n')
        except Exception as exception:
            logger.error(f'error: {exception}')
            logger.error(column_info)
            logger.info(row_data)
            raise exception

    logger.info(f'rows saved: {len(data)} to {table_data_file}')
    if columns_to_save:
        for column in columns_to_save:
            logger.info(
                f'{column} for {columns_to_save[column]}'
                f' saved: {len(parameters[columns_to_save[column]])}',
            )
    output.close()
    logger.info('-------------------------------------------')


def build_where(
        filters: dict, parameters: dict, columns: list, column_info: dict,
) -> str:
    if not filters:
        return ''
    filter_expressions = []
    for filter_column in filters:
        if filter_column in columns:
            filter_value = filters[filter_column]
            logger.info(f'filter {filter_column}')
            if filter_value.startswith('$'):
                filter_value = parameters[filter_value.replace('$', '')]
                if isinstance(filter_value, list):
                    if column_info[filter_column].type.name == 'uuid':
                        values = [f'uuid(\'{v}\')' for v in filter_value]
                    else:
                        values = [f'\'{v}\'' for v in filter_value]
                    if not values:
                        raise Exception(
                            f'empty filter for {filter_column}'
                            f' ({filter_value})',
                        )
                    filter_expression = (
                        f'{filter_column} in ({", ".join(values)})'
                    )
                else:
                    filter_expression = f'{filter_column} = {filter_value}'
                filter_expressions.append(filter_expression)

    if filter_expressions:
        return ' WHERE ' + ' AND '.join(filter_expressions)
    return ''


def build_insert(
        table_schema: str, table_name: str, columns: list, column_info: dict,
) -> str:
    values = []
    for num, column in enumerate(columns):
        value = f'${num + 1}'
        if column_info[column].type.name == 'uuid':
            value = f'uuid({value}::varchar)'
        elif column_info[column].type.name == 'numeric':
            value = f'CAST({value}::varchar AS numeric)'
        elif column_info[column].type.name == 'int4range':
            value = f'CAST({value}::varchar AS int4range)'
        elif column_info[column].type.name == 'timestamptz':
            value = (
                f'to_timestamp({value}::varchar, \'YYYY-MM-DD HH24:MI:SS\')'
            )
        values.append(value)
    return (
        f'INSERT INTO {table_schema}.{table_name} ({",".join(columns)})'
        f' VALUES({",".join(values)}) ON CONFLICT DO NOTHING'
    )
