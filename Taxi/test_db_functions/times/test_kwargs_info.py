import datetime

from test_taxi_exp.helpers import db


async def test(taxi_exp_client):
    now_timestamp = await db.get_current_timestamp(taxi_exp_client.app)

    response = await taxi_exp_client.post(
        '/v1/consumers/kwargs/',
        headers={'X-Ya-Service-Ticket': '123'},
        json={'consumer': 'test_consumer', 'kwargs': [], 'metadata': {}},
    )
    assert response.status == 200, await response.text()
    last_timestamp = (await db.get_kwargs_history(taxi_exp_client.app))[0][
        'updation_time'
    ]

    dt1 = last_timestamp - now_timestamp
    dt2 = now_timestamp - last_timestamp
    excepted_delta = datetime.timedelta(minutes=5)
    assert dt1 < excepted_delta and dt2 < excepted_delta, f'{dt1}, {dt2}'
