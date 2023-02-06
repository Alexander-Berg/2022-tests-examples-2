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
