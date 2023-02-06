import datetime
import json
import uuid

import psycopg2

MSK_TIMEZONE = psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)


def make_msk_datetime(year, month, day, hour=0, minute=0, seconds=0):
    return datetime.datetime(
        year, month, day, hour, minute, seconds, tzinfo=MSK_TIMEZONE,
    )


def run_script(pgsql, query):
    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(query)
    return list(cursor)


def insert_feed_in_db(
        service,
        channels,
        payload,
        request_id,
        created,
        pgsql,
        publish_at=None,
):
    cursor = pgsql['feeds-pg'].cursor()
    query = f"""
        INSERT INTO services (name)
        VALUES ('{service}')
        ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
        RETURNING id;
        """
    cursor.execute(query)
    service_id = list(cursor)[0][0]

    for channel in channels:
        etag = uuid.uuid4()
        cursor.execute(
            f"""
            INSERT INTO channels (name, service_id, etag, updated)
            VALUES (
              '{channel}', {service_id}, '{etag}', current_timestamp
            )
            ON CONFLICT (name, service_id)
            DO UPDATE SET etag = '{etag}', updated = current_timestamp;
            """,
        )

        feed_id = uuid.uuid4()
        cursor.execute(
            f"""
            WITH
              channel AS
                (SELECT * FROM channels WHERE name = '{channel}'
                                          AND service_id = {service_id}),
              service AS
                (SELECT id FROM services WHERE name = '{service}'),
              feed AS (
                INSERT INTO feeds
                  (feed_id, service_id, package_id, request_id,
                   created, expire, payload, publish_at)
                VALUES (
                  '{feed_id}', '{service_id}', '{request_id}',
                  '{request_id}', '{created}',
                  CURRENT_TIMESTAMP + interval '3 hours',
                  '{json.dumps(payload)}',
                  '{publish_at if publish_at else created}')
                RETURNING feed_id)
            INSERT INTO feed_channel_status
              (feed_id, channel_id, created, status)
            VALUES (
              (SELECT feed_id FROM feed),
              (SELECT id FROM channel),
              '{created}',
              'published'
            );
            """,
        )
