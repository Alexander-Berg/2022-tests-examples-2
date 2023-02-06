import datetime
import json
import sys

import dateutil.parser
import psycopg2.extensions as ext

RPS_LIMITER_CONFIG = {
    'rules_select_limiter': {
        'common_settings': {
            'execution_rate': 25,
            'max_queue_size': 10000,
            'wait_for_timeous_ms': 1000,
        },
    },
    'rules_match_limiter': {
        'common_settings': {'execution_rate': 25, 'max_queue_size': 10000},
        'batch_push_settings': {'timeout_ms': 500, 'soft_max_queue_size': 100},
    },
    'bulk_rules_match_limiter': {
        'common_settings': {'execution_rate': 5, 'max_queue_size': 2000},
        'batch_push_settings': {'timeout_ms': 1000, 'soft_max_queue_size': 20},
    },
}


def myconverter(data):
    if isinstance(data, datetime.datetime):
        if data == datetime.datetime.max:
            return 'infinity'
        if data == datetime.datetime.min:
            return '-infinity'

        return data.__str__()

    return None


class InfDateAdapter:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def getquoted(self):
        if self.wrapped == datetime.date.max:
            return b'\'infinity\'::date'
        if self.wrapped == datetime.date.min:
            return b'\'-infinity\'::date'

        return ext.DateFromPy(self.wrapped).getquoted()


ext.register_adapter(datetime.date, InfDateAdapter)


def execute_query(query, pgsql, args=None):
    pg_cursor = pgsql['subvention_schedule'].cursor()
    pg_cursor.execute(query, args)

    return list(pg_cursor)


def execute(query, pgsql, args=None):
    print(f'exec: {query}', file=sys.stderr)
    ext.register_adapter(datetime.date, InfDateAdapter)

    pg_cursor = pgsql['subvention_schedule'].cursor()
    pg_cursor.execute(query, args)


def get_schedules(pgsql):
    result = {
        'descriptors': execute_query(
            """SELECT
                zones.zone,
                tariff_classes.tariff_class,
                descriptiors.rule_type,
                lower(descriptiors.activity_range),
                upper(descriptiors.activity_range) - 1,
                restrictions.restrictions,
                (descriptiors.branding::int::bit(1) & B'1') = B'1',
                (descriptiors.branding::int::bit(2) & B'10') = B'10',
                tags.tags,
                lower(descriptiors.active_range),
                upper(descriptiors.active_range),
                descriptiors.last_rule_updated_at
            FROM sch.schedule_descriptiors as descriptiors
            LEFT JOIN sch.zones as zones
                ON zones.idx = descriptiors.zone_idx
            LEFT JOIN sch.tariff_classes as tariff_classes
                ON tariff_classes.idx = descriptiors.tariff_class_idx
            LEFT JOIN sch.restriction_variants as restrictions
                ON restrictions.idx = descriptiors.restrictions_idx
            LEFT JOIN sch.tags_variants as tags
                ON tags.idx = descriptiors.tags_idx
            order by zone, tariff_class, rule_type,
                active_range, descriptiors.idx;""",
            pgsql,
        ),
        'items': execute_query(
            """SELECT
                schedules.schedule_idx,
                rule_id.rule_id,
                draft_id.draft_id,
                lower(schedules.offset_range),
                upper(schedules.offset_range),
                schedules.rate::int,
                geoarea.geoarea,
                schedules.branding_value,
                schedules.activity_value,
                schedules.is_branding_satisfied,
                schedules.is_activity_satisfied
            FROM sch.schedule_items as schedules
            LEFT JOIN sch.rule_ids as rule_id
                ON rule_id.idx = schedules.rule_idx
            LEFT JOIN sch.draft_ids as draft_id
                ON draft_id.idx = schedules.draft_idx
            LEFT JOIN sch.geoareas as geoarea
                ON geoarea.idx = schedules.geoarea_idx
            ORDER BY schedules.schedule_idx, offset_range;""",
            pgsql,
        ),
    }

    tags_masks = []
    tags_masks = execute_query(
        """SELECT
                lower(active_range),
                upper(active_range),
                rule_type,
                zone_idx,
                tariff_class_idx,
                mask,
                is_active
            FROM sch.tags_masks;""",
        pgsql,
    )
    if tags_masks:
        result['tags_masks'] = tags_masks

    prostponed_user_requests = get_prostponed_user_requests(pgsql)
    if prostponed_user_requests:
        result['postponed_user_requests'] = prostponed_user_requests

    return json.loads(json.dumps(result, default=myconverter))


def sort_response(response):
    if 'schedules' not in response:
        pass

    for i in range(0, len(response['schedules'])):
        if (
                'items' not in response['schedules'][i]
                or not response['schedules'][i]['items']
        ):
            pass

        response['schedules'][0]['items'].sort(
            key=lambda x: dateutil.parser.parse(x['time_range']['from']),
        )

    return response


def load_db(pgsql, db_json, mocked_time=None):
    if 'descriptors' in db_json:
        for descr in db_json['descriptors']:

            zone_idx = execute_query(
                f"""
                INSERT INTO
                    sch.zones(zone)
                VALUES('{descr[0]}')
                ON CONFLICT(zone) DO UPDATE SET zone=EXCLUDED.zone
                RETURNING idx;
                """,
                pgsql,
            )[0][0]

            tariff_class_idx = execute_query(
                f"""
                INSERT INTO
                    sch.tariff_classes(tariff_class)
                VALUES('{descr[1]}')
                ON CONFLICT(tariff_class)
                DO UPDATE SET tariff_class=EXCLUDED.tariff_class
                RETURNING idx;
                """,
                pgsql,
            )[0][0]

            restrictions_idx = execute_query(
                f"""
                INSERT INTO
                    sch.restriction_variants(restrictions)
                VALUES(ARRAY['activity']::sch.ignored_restriction[])
                ON CONFLICT(restrictions)
                DO UPDATE SET restrictions=EXCLUDED.restrictions
                RETURNING idx;
                """,
                pgsql,
            )[0][0]

            tags_idx = execute_query(
                f"""
                INSERT INTO
                    sch.tags_variants(tags)
                VALUES(ARRAY{descr[8]}::TEXT[])
                ON CONFLICT(tags) DO UPDATE SET tags=EXCLUDED.tags
                RETURNING idx;
                """,
                pgsql,
            )[0][0]

            updated_at = (
                mocked_time.now() if mocked_time else datetime.datetime.now()
            )
            execute(
                f"""
            INSERT INTO sch.schedule_descriptiors (
                zone_idx,
                tariff_class_idx,
                rule_type,
                activity_range,
                restrictions_idx,
                branding,
                tags_idx,
                active_range,
                last_rule_updated_at,
                update_time,
                update_at
            )
            VALUES (
                {zone_idx},
                {tariff_class_idx},
                '{descr[2]}',
                int4range({descr[3]}, {descr[4]}, '[]'),
                {restrictions_idx},
                {descr[6]}::int + ({descr[7]}::int * 2),
                {tags_idx},
                tsrange('{descr[9]}', '{descr[10]}'),
                '{descr[11]}',
                '00:00:01',
                '{updated_at.isoformat()}'
            )""",
                pgsql,
            )

    if 'items' in db_json:
        for item in db_json['items']:
            rule_idx = execute_query(
                f"""
                    INSERT INTO
                        sch.rule_ids(rule_id)
                    VALUES ('{item[1]}')
                    ON CONFLICT(rule_id)
                        DO UPDATE SET rule_id=EXCLUDED.rule_id
                    RETURNING idx;
                """,
                pgsql,
            )[0][0]

            draft_idx = execute_query(
                f"""
                    INSERT INTO
                        sch.draft_ids(draft_id)
                    VALUES ('{item[2]}')
                    ON CONFLICT(draft_id)
                        DO UPDATE SET draft_id=EXCLUDED.draft_id
                    RETURNING idx;
                """,
                pgsql,
            )[0][0]

            geoarea_idx = (
                None
                if not item[7]
                else execute_query(
                    f"""
                    INSERT INTO
                        sch.geoareas(geoarea)
                    VALUES ('{item[6]}')
                    ON CONFLICT(geoarea)
                        DO UPDATE SET geoarea=EXCLUDED.geoarea
                    RETURNING idx;
                """,
                    pgsql,
                )[0][0]
            )

            execute(
                f"""
            INSERT INTO
                sch.schedule_items (
                    schedule_idx,
                    rule_idx,
                    draft_idx,
                    offset_range,
                    rate,
                    geoarea_idx,
                    branding_value,
                    activity_value,
                    is_branding_satisfied,
                    is_activity_satisfied
                )
                VALUES (
                %s,
                %s,
                %s,
                int4range(%s, %s, '[)'),
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )""",
                pgsql,
                (
                    item[0],
                    rule_idx,
                    draft_idx,
                    item[3],
                    item[4],
                    item[5],
                    geoarea_idx,
                    item[7],
                    item[8],
                    item[9],
                    item[10],
                ),
            )

    if 'affected_schedules' in db_json:
        for affected_schedule in db_json['affected_schedules']:
            execute(
                f"""
            INSERT INTO
                sch.affected_schedules (
                    rule_type,
                    zone_idx,
                    tariff_class_idx,
                    restrictions_idx,
                    tags_idx,
                    branding,
                    updated_at,
                    invalidate_from
                )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                pgsql,
                (
                    affected_schedule[0],
                    affected_schedule[1],
                    affected_schedule[2],
                    affected_schedule[3],
                    affected_schedule[4],
                    affected_schedule[5],
                    affected_schedule[6],
                    affected_schedule[7],
                ),
            )

    if 'tags_masks' in db_json:
        execute(
            f"""
        INSERT INTO
            sch.tags_masks (
                active_range,
                rule_type,
                zone_idx,
                tariff_class_idx,
                mask,
                is_active
            )
        SELECT r, t, z, c, m, a
        FROM UNNEST(ARRAY[%s])
            s(
                r tsrange,
                t sch.rule_type,
                z BIGINT,
                c BIGINT,
                m TEXT[],
                a BOOLEAN
        );"""
            % ', '.join(
                map(
                    str,
                    [
                        f'(\'[{m[0]}, {m[1]})\'::tsrange'
                        f', \'{m[2]}\'::sch.rule_type, {m[3]}::BIGINT'
                        f', {m[4]}::BIGINT, ARRAY{m[5]}::TEXT[]'
                        f', {m[6]})'
                        for m in db_json['tags_masks']
                    ],
                ),
            ),
            pgsql,
        )

    if 'postponed_user_requests' in db_json:
        postponed = db_json['postponed_user_requests']
        for data in postponed:
            preinsert_normalized_data(
                pgsql, zones=[data[1]], tariff_classes=[data[2]], tags=data[4],
            )

        for postponed_request in postponed:
            execute(
                f"""
            INSERT INTO
                sch.postponed_user_requests (
                    rule_type,
                    zone_idx,
                    tariff_class_idx,
                    restrictions_idx,
                    tags_idx,
                    branding,
                    min_activity_inc,
                    max_activity_inc,
                    request_from,
                    request_to,
                    processed,
                    deadline
                )
            SELECT
                \'{postponed_request[0]}\',
                zones.idx,
                tariff_classes.idx,
                restrictions.idx,
                tags.idx,
                {postponed_request[5]},
                {postponed_request[6]},
                {postponed_request[7]},
                \'{postponed_request[8]}\',
                \'{postponed_request[9]}\',
                {postponed_request[10]},
                \'{postponed_request[11]}\'
            FROM sch.zones AS zones
                JOIN sch.tariff_classes AS tariff_classes
                    ON tariff_classes.tariff_class = \'{postponed_request[2]}\'
                JOIN sch.restriction_variants AS restrictions
                    ON restrictions.restrictions =
                    \'{postponed_request[3]}\'::sch.ignored_restriction[]
                JOIN sch.tags_variants AS tags
                    ON tags.tags = ARRAY{postponed_request[4]}::text[]
                WHERE zones.zone = \'{postponed_request[1]}\';
                """,
                pgsql,
            )


def set_last_updated(pgsql, updated_at):
    execute(
        f"""INSERT INTO sch.last_update (updated_at)
                VALUES ('{updated_at}') ON CONFLICT (onerow_id) DO
                UPDATE SET updated_at = EXCLUDED.updated_at;""",
        pgsql,
    )


def insert_use_statistics(pgsql, idx, count, used_at):
    execute(
        f"""INSERT INTO sch.schedule_use_statistic (schedule_idx, use_count, last_used)
                VALUES ({idx}, {count}, '{used_at}');""",
        pgsql,
    )


def get_use_statistics(pgsql):
    return execute_query(
        """SELECT schedule_idx, use_count, last_used
             FROM sch.schedule_use_statistic ORDER BY schedule_idx""",
        pgsql,
    )


def get_last_updated(pgsql):
    return execute_query('SELECT updated_at::TEXT FROM sch.last_update', pgsql)


def get_affected_schedules(pgsql):
    result = {
        'affected': execute_query(
            """
            SELECT
                affected.rule_type,
                zones.zone,
                tariff_classes.tariff_class,
                restrictions.restrictions,
                tags.tags,
                affected.branding,
                affected.updated_at,
                affected.invalidate_from
            FROM sch.affected_schedules as affected
            LEFT JOIN sch.zones as zones
                ON zones.idx = affected.zone_idx
            LEFT JOIN sch.tariff_classes as tariff_classes
                ON tariff_classes.idx = affected.tariff_class_idx
            LEFT JOIN sch.restriction_variants as restrictions
                ON restrictions.idx = affected.restrictions_idx
            LEFT JOIN sch.tags_variants as tags
                ON tags.idx = affected.tags_idx
            ORDER BY zone, tariff_class, rule_type,
                tags, affected.idx
            """,
            pgsql,
        ),
    }
    return json.loads(json.dumps(result, default=myconverter))


def get_tags_variants(pgsql):
    return execute_query(
        """
        SELECT * FROM sch.tags_variants
        """,
        pgsql,
    )


def check_update_time_valid(pgsql):
    data = execute_query(
        """
        SELECT FALSE
        FROM sch.schedule_descriptiors
        WHERE update_time is NULL
        """,
        pgsql,
    )

    if not data:
        return True
    return False


def clean_db(pgsql):
    execute('TRUNCATE TABLE sch.affected_schedules;', pgsql)
    execute('TRUNCATE TABLE sch.tags_masks;', pgsql)


def preinsert_normalized_data(pgsql, zones, tariff_classes, tags):
    print(
        f'preinsert_normalized_data {zones}, {tariff_classes}, {tags}',
        file=sys.stderr,
    )
    execute(
        """
        INSERT INTO
            sch.zones(zone)
        VALUES(%s)
        ON CONFLICT DO NOTHING;
        """,
        pgsql,
        zones,
    )

    execute(
        """
        INSERT INTO
            sch.tariff_classes(tariff_class)
        VALUES(%s)
        ON CONFLICT DO NOTHING;
        """,
        pgsql,
        tariff_classes,
    )

    execute(
        f"""
        INSERT INTO
            sch.restriction_variants(restrictions)
        VALUES(ARRAY['activity']::sch.ignored_restriction[])
        ON CONFLICT DO NOTHING;
        """,
        pgsql,
    )

    execute(
        f"""
        INSERT INTO
            sch.tags_variants(tags)
        VALUES(ARRAY{tags}::TEXT[])
        ON CONFLICT DO NOTHING;
        """,
        pgsql,
    )


def get_prostponed_user_requests(pgsql):
    result = execute_query(
        """
            SELECT
                postponed.rule_type,
                zones.zone,
                tariff_classes.tariff_class,
                restrictions.restrictions,
                tags.tags,
                postponed.branding,
                min_activity_inc,
                max_activity_inc,
                request_from,
                request_to,
                processed,
                deadline
            FROM sch.postponed_user_requests as postponed
            LEFT JOIN sch.zones as zones
                ON zones.idx = postponed.zone_idx
            LEFT JOIN sch.tariff_classes as tariff_classes
                ON tariff_classes.idx = postponed.tariff_class_idx
            LEFT JOIN sch.restriction_variants as restrictions
                ON restrictions.idx = postponed.restrictions_idx
            LEFT JOIN sch.tags_variants as tags
                ON tags.idx = postponed.tags_idx
            ORDER BY zone, tariff_class, rule_type,
                tags, postponed.idx
            """,
        pgsql,
    )

    return json.loads(json.dumps(result, default=myconverter))
