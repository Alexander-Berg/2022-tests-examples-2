import datetime

from test_taxi_exp.helpers import db


FILE_NAME = 'file.txt'


async def test(taxi_exp_client):
    mds_id = await db.add_or_update_file(taxi_exp_client.app, FILE_NAME)
    first_timestamp = (await db.get_file(taxi_exp_client.app, mds_id))[
        'updated'
    ]
    await db.delete_file(taxi_exp_client.app, mds_id, 1)
    last_timestamp = (
        await db.get_file(taxi_exp_client.app, mds_id, has_removed=True)
    )['updated']

    dt1 = last_timestamp - first_timestamp
    dt2 = first_timestamp - last_timestamp
    excepted_delta = datetime.timedelta(minutes=5)
    assert dt1 < excepted_delta and dt2 < excepted_delta, f'{dt1}, {dt2}'
