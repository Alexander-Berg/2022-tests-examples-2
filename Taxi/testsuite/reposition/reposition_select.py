def select_named(query, db):
    cursor = db.conn.cursor()
    cursor.execute(query)
    res = []
    for row in cursor.fetchall():
        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]
    return res


def select_table_named(table, order, db):
    return select_named(
        'SELECT * FROM ' + table + ' ORDER BY ' + order + ';', db,
    )


def select_table(table, order, db):
    query = 'SELECT * FROM ' + table + ' ORDER BY ' + order + ';'
    cursor = db.conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


def usages_count(db):
    usage_query = 'SELECT COUNT(1) FROM state.sessions WHERE is_usage;'
    usage_cursor = db.conn.cursor()
    usage_cursor.execute(usage_query)
    usage_rows = usage_cursor.fetchall()
    assert len(usage_rows) == 1
    return usage_rows[0][0]
