def select_named(query, db):
    cursor = db.conn.cursor()
    cursor.execute(query)
    res = []
    for row in cursor.fetchall():
        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]
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
        + 'FROM information_schema.tables '
        + 'WHERE table_name = \''
        + str(table)
        + '\';',
        db,
    )
