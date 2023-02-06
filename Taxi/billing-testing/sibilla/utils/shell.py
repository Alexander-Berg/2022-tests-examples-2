import asyncio
import logging
import os

import asyncpg

from sibilla import loader
from sibilla.test import context as ctx
from taxi.pg import dsn_parser

logger = logging.getLogger(__name__)


async def restore_psql(context: ctx.ContextData, config: dict) -> None:
    if 'file' not in config:
        logger.info('Skip restore db from raw sql-file')
        return
    logger.warning('Restore raw sql for database was deprecated')
    dump_path = os.path.join(context.suite_path, 'dump', config['file'])
    if not os.path.exists(dump_path):
        return
    args = [
        'psql',
        context.pgaas_connections(config['conn'], config['shard']),
        '-f',
        dump_path,
    ]
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE,
    )
    logger.info('Started: %s (pid = %d)', str(args), process.pid)
    await process.communicate()
    if process.returncode != 0:
        msg = 'Restore failed: %s (pid = %d)' % (str(args), process.pid)
        raise RuntimeError(msg)
    logger.info('Restore complete: %s (pid = %d)', str(args), process.pid)


async def restore_mongo(
        context: ctx.ContextData, dbname: str, config: dict,
) -> None:
    dump_path = os.path.join(context.suite_path, 'dump')
    if not os.path.exists(dump_path):
        return
    args = [
        'mongorestore',
        '--uri',
        context.mongo_conn(config['conn'])['uri'],
        '--nsInclude',
        f'{dbname}.*',
        '--drop',
        dump_path,
    ]
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE,
    )
    logger.info('Started: %s (pid = %d)', str(args), process.pid)
    await process.communicate()
    if process.returncode != 0:
        msg = 'Restore failed: %s (pid = %d)' % (str(args), process.pid)
        raise RuntimeError(msg)
    logger.info('Restore complete: %s (pid = %d)', str(args), process.pid)


async def restore_mongocollections(
        context: ctx.ContextData, dbname: str, config: dict,
) -> None:
    dump_path = os.path.join(
        context.suite_path, 'database', 'mongo', 'collections', dbname,
    )
    if not os.path.exists(dump_path):
        return
    if not config.get('import', False):
        return
    dumps = [
        file
        for file in os.listdir(dump_path)
        if os.path.isfile(os.path.join(dump_path, file))
        and file.endswith('.jsonl')
    ]
    for file in dumps:
        args = [
            'mongoimport',
            '--uri',
            context.mongo_conn(config['conn'])['uri'],
            '-c',
            os.path.splitext(file)[0],
            '--drop',
            '--file',
            os.path.join(dump_path, file),
        ]
        process = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE,
        )
        logger.info('Started: %s (pid = %d)', str(args), process.pid)
        await process.communicate()
        if process.returncode != 0:
            msg = 'Restore failed: %s (pid = %d)' % (str(args), process.pid)
            raise RuntimeError(msg)
        logger.info('Restore complete: %s (pid = %d)', str(args), process.pid)


async def restore_psql_tables(
        context: ctx.ContextData, dbname: str, config: dict,
) -> None:
    dump_path = os.path.join(
        context.suite_path, 'database', 'postgresql', dbname,
    )
    if not os.path.exists(dump_path):
        return
    if not config.get('import', False):
        return
    dumps = [
        file
        for file in os.listdir(os.path.join(dump_path))
        if os.path.isfile(os.path.join(dump_path, file))
        and file.endswith('.sql')
    ]
    conn = await asyncpg.connect(
        **dsn_parser.parse_conn_settings(
            context.pgaas_connections(config['conn'], config['shard']),
        )[0].get_connect_kwargs(),
    )
    try:
        for file in dumps:
            sql_file_path = os.path.join(dump_path, file)
            sql_dump_path = os.path.join(
                dump_path, os.path.splitext(file)[0] + '.jsonl',
            )
            with open(sql_file_path) as sql_file:
                query = ''.join(sql_file.readlines())
                logger.info('Executer query %s', query)
                if os.path.exists(sql_dump_path) and os.path.isfile(
                        sql_dump_path,
                ):
                    stmt = await conn.prepare(query)
                    with open(sql_dump_path) as dump_file:
                        while True:
                            line = dump_file.readline()
                            if not line:
                                break
                            await stmt.fetch(
                                *loader.load_py_json(line.strip()),
                            )
                else:
                    await conn.execute(query)
            logger.info('Done restore sql tables from %s', file)
    finally:
        await conn.close()
