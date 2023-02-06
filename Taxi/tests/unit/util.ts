import {seed} from 'casual';
import type {Connection} from 'typeorm';

seed(3);

export async function madeJsonError(callback: () => unknown) {
    try {
        await callback();
    } catch (e) {
        return JSON.parse((e as Error).message);
    }
}

export async function remakePublicSchema(connection: Connection) {
    for (const sql of [
        'DROP SCHEMA IF EXISTS public CASCADE',
        'CREATE SCHEMA public',
        'CREATE EXTENSION LTREE',
        'CREATE EXTENSION HSTORE',
        'CREATE EXTENSION PG_TRGM',
        'CREATE EXTENSION POSTGIS',
        'CREATE EXTENSION POSTGIS_TOPOLOGY'
    ]) {
        await connection.query(sql);
    }
}
