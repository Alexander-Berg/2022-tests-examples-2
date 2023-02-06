DEBUG_PREFIX = None


def select_named(query, db):
    cursor = db.conn.cursor()
    cursor.execute(query)
    col_names = [col_description[0] for col_description in cursor.description]
    res = [dict(zip(col_names, row)) for row in cursor.fetchall()]
    return res


def insert_into_table(table, columns, values, db):
    return select_named(
        'insert into '
        + table
        + ' ('
        + ', '.join(columns)
        + ') VALUES ( '
        + ', '.join(values)
        + ');',
        db,
    )


def select_columns_from_table_order(table, columns, order, db, limit=1000):
    return select_named(
        'SELECT '
        + ', '.join(columns)
        + ' FROM '
        + table
        + ' ORDER BY '
        + order
        + ' limit '
        + str(limit)
        + ';',
        db,
    )


def select_columns_from_table(table, columns, db, limit=1000):
    return select_named(
        'SELECT '
        + ', '.join(columns)
        + ' FROM '
        + table
        + ' limit '
        + str(limit)
        + ';',
        db,
    )


def if_table_exists(table, db):
    return select_named(
        'SELECT True '
        'FROM information_schema.tables '
        'WHERE table_name = \'' + str(table) + '\';',
        db,
    )


def read_count(pgsql, table, where=None):
    select_from = 'crm_scheduler.' + table
    if where is not None:
        select_from += ' WHERE ' + where
    return select_columns_from_table(
        select_from, ['count(*)'], pgsql['crm_scheduler'], 1000,
    )[0]['count']


def select_helper(pgsql, table, columns=None):
    columns = columns or ['id']
    return select_columns_from_table(
        'crm_scheduler.' + table, columns, pgsql['crm_scheduler'], 1000,
    )


async def v1_get_task_list(taxi_crm_scheduler, prefix=DEBUG_PREFIX):
    response = await taxi_crm_scheduler.post('/v1/get_task_list', {})
    assert response.status == 200
    if not prefix:
        return
    ids = [task['id'] for task in response.json()['task_list']]
    if response.json()['task_type'] == 'idle':
        return
    print(
        prefix,
        'task_type=',
        response.json()['task_type'],
        'ids=',
        ', '.join(map(str, ids)),
    )


async def v2_get_task_list(taxi_crm_scheduler, prefix=DEBUG_PREFIX):
    response = await taxi_crm_scheduler.post('/v2/get_task_list', {})
    assert response.status == 200
    if not prefix:
        return
    ids = [task['id'] for task in response.json()['task_list']]
    if response.json()['task_type'] == 'idle':
        return
    print(
        prefix,
        'task_type=',
        response.json()['task_type'],
        'ids=',
        ', '.join(map(str, ids)),
    )


def print_pool(pgsql, prefix='marker'):
    def print_table_count(prefix, name):
        print(prefix, name, read_count(pgsql, name))

    print_table_count(prefix, 'task_pool_crm_policy')
    print_table_count(prefix, 'task_pool_crm_policy_in_process')
    print_table_count(prefix, 'task_pool_logs')
    print_table_count(prefix, 'task_pool_logs_in_process')
    print_table_count(prefix, 'task_pool_user_push')
    print_table_count(prefix, 'task_pool_user_push_in_process')
    print_table_count(prefix, 'task_pool_sending_finished')
    print_table_count(prefix, 'task_reported_default')
    print(prefix, '-----------------------------------------------------')
