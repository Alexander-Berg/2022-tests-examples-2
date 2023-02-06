# pylint: disable=wrong-import-order, import-error, import-only-modules
import datetime

import pytz


def clear_face_signatures_table(pgsql):
    cursor = pgsql['cctv_workers'].cursor()
    cursor.execute('DELETE FROM cctv_workers.face_signatures;')


def upsert_face_signatures(pgsql, data):
    if not data:
        return

    query = """
            INSERT INTO cctv_workers.face_signatures(id,signature,updated_ts)
            VALUES
            """
    records = str()
    first = True
    for face_id, item in data.items():
        if not item['signature']:
            continue

        updated_ts_str = str(
            item.get(
                'updated_ts',
                datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=pytz.utc),
            ),
        )

        if not first:
            records += ','
        else:
            first = False

        records += '(\'{}\',ARRAY{},\'{}\')'.format(
            face_id, item['signature'], updated_ts_str,
        )

    if not records:
        return

    query += (
        records
        + """
              ON CONFLICT (id) DO UPDATE SET
              signature = excluded.signature,
              updated_ts = excluded.updated_ts;
             """
    )
    cursor = pgsql['cctv_workers'].cursor()
    cursor.execute(query)


def get_face_signatures(pgsql):
    cursor = pgsql['cctv_workers'].cursor()
    cursor.execute(
        'SELECT id, signature, updated_ts'
        ' FROM cctv_workers.face_signatures;',
    )
    result = dict()
    for row in cursor:
        result[row[0]] = {'signature': row[1], 'updated_ts': row[2]}
    return result
