import asyncpg
import pytest

from taxi_exp.util import pg_helpers


async def test(taxi_exp_client):
    pool = taxi_exp_client.app['pool']

    query = """DO $$ BEGIN
        INSERT INTO clients_schema.consumers (name)
            VALUES ('test_consumer'), ('launch');
        INSERT INTO clients_schema.applications (name)
            VALUES ('android'), ('ios');
        INSERT INTO clients_schema.experiments (
            id, name, rev, is_config, date_from, date_to
        )
        VALUES
            (723, 'experiment_with_revisions', 254570, False,
                '2020-01-01'::timestamp, '2020-01-01'::timestamp)
        ;
    END $$"""
    await pg_helpers.fetch(pool, query)

    query = """
        INSERT INTO clients_schema.salts (segmentation_method, salt)
        VALUES ('mod_sha1', 'aaaaa');"""
    await pg_helpers.fetch(pool, query)

    query = """SELECT pg_temp.update_salts(723, $2::text, $1::text[]);"""
    await pg_helpers.fetch(pool, query, ['dddddd'], None)
    await pg_helpers.fetch(pool, query, [], 'mod_sha1')
    await pg_helpers.fetch(pool, query, ['aaaaa', 'bbbbb'], 'mod_sha1')
    with pytest.raises(asyncpg.exceptions.RaiseError):
        await pg_helpers.fetch(pool, query, ['aaaaa', 'cccc'], 'segmentation')

    query = """SELECT * FROM clients_schema.salts;"""
    response = await pg_helpers.fetch(pool, query)
    assert [
        (item['id'], item['salt'], item['segmentation_method'])
        for item in response
    ] == [(1, 'aaaaa', 'mod_sha1'), (3, 'bbbbb', 'mod_sha1')], (
        f'salts: {response}'
    )
    query = """SELECT * FROM clients_schema.experiments_salts;"""
    response = await pg_helpers.fetch(pool, query)
    assert [(item['experiment_id'], item['salt']) for item in response] == [
        (723, 'aaaaa'),
        (723, 'bbbbb'),
    ], f'experiments_salts: {response}'
    query = """SELECT pg_temp.update_salts(723, $2::text, $1::text[]);"""
    await pg_helpers.fetch(pool, query, ['ffff'], 'mod_sha1')

    query = """SELECT * FROM clients_schema.salts;"""
    response = await pg_helpers.fetch(pool, query)
    assert (
        [
            (item['id'], item['salt'], item['segmentation_method'])
            for item in response
        ]
        == [
            (1, 'aaaaa', 'mod_sha1'),
            (3, 'bbbbb', 'mod_sha1'),
            (4, 'ffff', 'mod_sha1'),
        ]
    ), (
        f'salts: {response}'
    )
    query = """SELECT * FROM clients_schema.experiments_salts;"""
    response = await pg_helpers.fetch(pool, query)
    assert [(item['experiment_id'], item['salt']) for item in response] == [
        (723, 'ffff'),
    ], f'experiments_salts: {response}'
