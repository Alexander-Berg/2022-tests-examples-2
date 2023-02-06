def execute_query(query, pgsql, *args):
    cursor = pgsql['dbridermetrics'].conn.cursor()
    cursor.execute(query, tuple(*args))
    cursor.close()


def select_named(query, pgsql, *args):
    cursor = pgsql['dbridermetrics'].conn.cursor()
    cursor.execute(query, tuple(*args))
    res = []
    for row in cursor.fetchall():
        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]
    cursor.close()
    return res


def to_map(items, key, transform=None):
    result = {}
    for item in items:
        result[item[key]] = item if transform is None else transform(item)
    assert len(items) == len(result)
    return result


def hide_ticket(item):
    assert 'ticket_id' in item
    assert isinstance(item['ticket_id'], int)
    assert item['ticket_id'] > 0
    item['ticket_id'] = '*'
    return item
