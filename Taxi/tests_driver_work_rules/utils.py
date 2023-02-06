import copy
import datetime
import json

from tests_driver_work_rules import defaults


def build_calc_table_redis_key(park_id, rule_id):
    return defaults.RULE_WORK_CALC_TABLE_ITEMS_PREFIX + park_id + ':' + rule_id


def modify_base_dict(base, tested_fields):
    request_body = copy.deepcopy(base)
    if tested_fields:
        for key, value in tested_fields.items():
            if value is not None:
                request_body[key] = value
            else:
                request_body.pop(key)
    return request_body


def get_redis_all_park_work_rules(redis_store, park_id):
    return redis_store.hgetall(defaults.RULE_WORK_ITEMS_PREFIX + park_id)


def get_redis_work_rule(redis_store, park_id, rule_id):
    redis_work_rules = get_redis_all_park_work_rules(redis_store, park_id)

    if rule_id.encode('ascii') in redis_work_rules:
        return json.loads(redis_work_rules[rule_id.encode('ascii')])
    return None


def select_by_query(pgsql, query):
    cursor = pgsql['driver-work-rules'].conn.cursor()
    cursor.execute(query)
    res = []
    for row in cursor.fetchall():
        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]
    return res


def get_postgres_work_rule(pgsql, park_id, rule_id):
    query = (
        'SELECT * '
        'FROM driver_work_rules.work_rules '
        'WHERE park_id = \'{}\' AND id = \'{}\''.format(park_id, rule_id)
    )
    work_rules = select_by_query(pgsql, query)

    if work_rules:
        return work_rules[0]
    return None


def get_redis_calc_table(redis_store, part_id, rule_id):
    real_redis_value = redis_store.hgetall(
        build_calc_table_redis_key(part_id, rule_id),
    )
    return {
        key.decode('ascii'): json.loads(value)
        for key, value in real_redis_value.items()
    }


def get_redis_order_types(redis_store):
    real_redis_value = redis_store.hgetall(
        defaults.RULE_TYPE_ITEMS_KEY,
    ).items()
    return {
        key.decode('ascii'): json.loads(value)
        for key, value in real_redis_value
    }


def get_order_types_names_to_ids(redis_store):
    real_redis_value = redis_store.hgetall(
        defaults.RULE_TYPE_NAMES_TO_IDS,
    ).items()
    return {
        key.decode('utf-8'): value.decode('ascii')
        for key, value in real_redis_value
    }


def check_updated_at(updated_at):
    delta = datetime.datetime.now(datetime.timezone.utc) - updated_at
    assert datetime.timedelta() <= delta < datetime.timedelta(minutes=1), delta
