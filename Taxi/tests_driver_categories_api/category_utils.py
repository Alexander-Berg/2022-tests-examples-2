import collections

ALL_FLAGS = (
    'robot',
    'chain',
    'portman',
    'search_by_address',
    'want_home',
    'econom',
    'business',
    'vip',
    'common_settings_enabled',
    'robot_comfort_disable',
    'minivan',
    'robot_disable_yandex',
    'business2',
    'universal',
    'express',
    'EMPTY_RESTRICTION',
    'start',
    'standart',
    'child_tariff',
    'ultimate',
    'maybach',
    'promo',
    'premium_van',
    'premium_suv',
    'suv',
    'personal_driver',
    'cargo',
    'night',
    'courier',
    'eda',
    'lavka',
    'scooters',
)

LEGACY_FLAGS = (
    'robot',
    'chain',
    'portman',
    'search_by_address',
    'want_home',
    'common_settings_enabled',
    'robot_comfort_disable',
    'robot_disable_yandex',
    'EMPTY_RESTRICTION',
)

RESTRICTION_MAP = {key: 1 << idx for idx, key in enumerate(ALL_FLAGS)}


def get_category_code(category):
    checked_category = 'business2' if category == 'comfortplus' else category
    assert checked_category in RESTRICTION_MAP
    return RESTRICTION_MAP[checked_category]


def get_all_restrictions():
    return [item for item in ALL_FLAGS if item not in LEGACY_FLAGS] + [
        'comfortplus',
    ]


def filter_legacy_flags(categories):
    return [item for item in categories if item not in LEGACY_FLAGS]


def convert_flag_to_restrictions(flag):
    restrictions = []
    flag_bits = bin(flag)[:1:-1]
    for bit, restriction in zip(flag_bits, ALL_FLAGS):
        if bit == '1' and restriction != 'EMPTY_RESTRICTION':
            restrictions.append(restriction)
        if bit == '1' and restriction == 'business2':
            restrictions.append('comfortplus')

    return restrictions


def set_redis_restrictions(redis_store, park_id, driver_id, restrictions):
    general_code = 0
    for restriction in restrictions:
        restriction_code = get_category_code(restriction)
        general_code |= restriction_code
        redis_store.sadd(
            f'RobotSettings:{park_id}:Settings_{restriction_code}', driver_id,
        )
    redis_store.hset(
        f'RobotSettings:{park_id}:Settings', driver_id, general_code,
    )


def check_redis_restrictions(
        redis_store, park_id, driver_id, expected_restrictions,
):
    expected_codes = [
        get_category_code(c)
        for c in expected_restrictions
        if c != 'comfortplus'
    ]
    for code in RESTRICTION_MAP.values():
        if code in expected_codes:
            assert driver_id.encode() in redis_store.smembers(
                f'RobotSettings:{park_id}:Settings_{code}',
            )
        else:
            assert driver_id.encode() not in redis_store.smembers(
                f'RobotSettings:{park_id}:Settings_{code}',
            )
    assert f'{sum(expected_codes)}'.encode() == redis_store.hget(
        f'RobotSettings:{park_id}:Settings', driver_id,
    )


def select_categories(pgsql):
    cursor = pgsql['driver-categories-api'].cursor()
    cursor.execute(
        'SELECT name, type, jdoc FROM categories.categories ORDER BY name',
    )
    result = []
    for row in cursor:
        result.append(row)
    return result


def select_driver_restrictions(pgsql, park_id, driver_id):
    cursor = pgsql['driver-categories-api'].cursor()
    cursor.execute(
        'SELECT categories FROM '
        'categories.driver_restrictions '
        'WHERE park_id = %s AND driver_id = %s;',
        (park_id, driver_id),
    )
    for row in cursor:
        return row[0]


def upsert_driver_restrictions(pgsql, park_id, driver_id, restrictions):
    cursor = pgsql['driver-categories-api'].cursor()
    cursor.execute(
        'INSERT INTO categories.driver_restrictions AS dr '
        '(park_id, driver_id, categories) VALUES '
        '(%s, %s, %s) ON CONFLICT (park_id, driver_id) DO UPDATE '
        'SET categories = %s WHERE dr.park_id = %s AND dr.driver_id = %s;',
        (park_id, driver_id, restrictions, restrictions, park_id, driver_id),
    )


def check_pg_restrictions(pgsql, park_id, driver_id, expected_restrictions):
    check_unordered_collections(
        expected_restrictions,
        select_driver_restrictions(pgsql, park_id, driver_id),
    )


def check_unordered_collections(left, right):
    left_counter = collections.Counter(left)
    right_couner = collections.Counter(right)
    assert left_counter == right_couner


def get_bulk_metrics_config(use_optimized_bulk, use_metrics):
    return {
        'DRIVER_CATEGORIES_API_USE_OPTIMIZED_BULK_QUERIES': use_optimized_bulk,
        'DRIVER_CATEGORIES_API_PG_METRICS_SETTINGS': {
            '__default__': {'allow_all': use_metrics, 'allowed_services': []},
        },
    }


def config_use_locked_queries(use_locked_queries):
    return {'DRIVER_CATEGORIES_API_USE_LOCKED_QUERIES': use_locked_queries}
