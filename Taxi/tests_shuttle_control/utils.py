import socket

HOST = socket.gethostname()


def select_named(query, db):
    cursor = db.conn.cursor()
    cursor.execute(query)
    res = []
    for row in cursor.fetchall():
        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]
    return res


def get_task_name(task_name='shuttle-route-watcher'):
    return f'{task_name}@{HOST}'


def stringify_visit_stop(obj):
    res = '""(' + str(obj[0]) + ','
    if obj[1]:
        res += str(obj[1])
    res += ','
    if obj[2] is not None:
        if obj[2] is True:
            res += 't'
        else:
            res += 'f'
    return res + ')""'


def stringify_detailed_view(view):
    res = '("{'
    res += ','.join(map(stringify_visit_stop, view))
    return res + '}")'
