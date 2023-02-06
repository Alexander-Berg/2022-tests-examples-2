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


def driver_status(taximeter_status):
    return {
        'drivers': [
            {
                'position': [0, 0],
                'id': 'dbid_uuid',
                'dbid': 'dbid',
                'uuid': 'uuid',
                'status': {
                    'driver': 'verybusy',
                    'taximeter': taximeter_status,
                },
            },
        ],
    }


def driver_statuses(driver_ids, taximeter_status):
    result = []

    for driver_id in driver_ids:
        dbid_uuid = driver_id.split('_')

        result.append(
            {
                'position': [0, 0],
                'id': driver_id,
                'dbid': dbid_uuid[0],
                'uuid': dbid_uuid[1],
                'status': {
                    'driver': 'verybusy',
                    'taximeter': taximeter_status,
                },
            },
        )

    return {'drivers': result}


def get_task_name(task_name='reposition-watcher'):
    return f'{task_name}@{HOST}'
