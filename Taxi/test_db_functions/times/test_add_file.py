import datetime

from test_taxi_exp.helpers import db


FILE_NAME = 'file.txt'


async def test(taxi_exp_client):
    now_timestamp = await db.get_current_timestamp(taxi_exp_client.app)
    mds_id = await db.add_or_update_file(taxi_exp_client.app, FILE_NAME)
    last_timestamp = (await db.get_file(taxi_exp_client.app, mds_id))[
        'updated'
    ]

    dt1 = last_timestamp - now_timestamp
    dt2 = now_timestamp - last_timestamp
    excepted_delta = datetime.timedelta(minutes=5)
    assert dt1 < excepted_delta and dt2 < excepted_delta, f'{dt1}, {dt2}'
