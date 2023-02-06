def select_named(query, pgsql, *args):
    cursor = pgsql['workforce_metrics_storage'].conn.cursor()
    cursor.execute(query, tuple(*args))
    res = []
    for row in cursor.fetchall():
        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]
    cursor.close()
    return res
