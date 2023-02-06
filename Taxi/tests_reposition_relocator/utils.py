import datetime
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


def select_table_named(table, order, db):
    return select_named(
        'SELECT * FROM ' + table + ' ORDER BY ' + order + ';', db,
    )


def format_execution_timestamp(now, step=0):
    now += datetime.timedelta(milliseconds=step)
    string = now.strftime('%Y-%m-%dT%H:%M:%S.%f')
    return string[:-3] + 'Z'


def get_task_name(task_name):
    return f'{task_name}@{HOST}'
