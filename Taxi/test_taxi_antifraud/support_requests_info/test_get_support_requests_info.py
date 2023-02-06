from test_taxi_antifraud.utils import utils


async def test_get_support_requests_one_request(web_app_client, db):
    order_id = 'some_order_1'

    request_info = {
        'request_id': 'some_id_2',
        'request_type': 'unknown_transaction',
        'creator_login': 'creator1',
        'last_updater_login': 'updater1',
        'additional_info': 'some_special_info',
        'created': utils.dates_utils.parse_timestring(
            '2020-12-20T11:05:39', timezone='UTC',
        ),
        'updated': utils.dates_utils.parse_timestring(
            '2021-12-20T11:05:39', timezone='UTC',
        ),
    }
    response = await web_app_client.get(
        '/v1/get_support_requests_info', params={'order_id': order_id},
    )
    assert response.status == 200

    response = utils.del_fields(
        utils.convert_datetimes(await response.json(), ['created', 'updated']),
        ['_id', 'order_id'],
    )

    assert response == [request_info]


async def test_get_support_requests_few_requests(web_app_client, db):
    order_id = 'some_order'

    requests_info = [
        {
            'request_id': 'some_id',
            'request_type': 'unknown_transaction',
            'creator_login': 'creator',
            'last_updater_login': 'login',
            'created': utils.dates_utils.parse_timestring(
                '2018-12-20T11:05:39', timezone='UTC',
            ),
            'updated': utils.dates_utils.parse_timestring(
                '2019-12-20T11:05:39', timezone='UTC',
            ),
        },
        {
            'request_id': 'some_id_1',
            'request_type': 'unknown_transaction',
            'creator_login': 'creator',
            'last_updater_login': 'updater',
            'created': utils.dates_utils.parse_timestring(
                '2019-12-20T11:05:39', timezone='UTC',
            ),
            'updated': utils.dates_utils.parse_timestring(
                '2019-12-20T11:05:39', timezone='UTC',
            ),
        },
    ]
    response = await web_app_client.get(
        '/v1/get_support_requests_info', params={'order_id': order_id},
    )
    assert response.status == 200

    response = utils.del_fields(
        utils.convert_datetimes(await response.json(), ['created', 'updated']),
        ['_id', 'order_id'],
    )

    assert response == requests_info
