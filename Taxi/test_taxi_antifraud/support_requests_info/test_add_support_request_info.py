import pytest

from test_taxi_antifraud.utils import utils


@pytest.mark.now('2020-03-10T11:20:00')
async def test_add_support_request_few_requests(web_app_client, db, now):
    order_id = 'some_order'
    pre_state = await db.antifraud_support_requests_info_mdb.find(
        {'order_id': order_id},
    ).to_list(None)

    assert len(pre_state) == 1

    request_info = {
        'order_id': order_id,
        'request_id': 'some_id_1',
        'request_type': 'unknown_transaction',
    }
    login = 'login'
    response = await web_app_client.post(
        '/v1/add_support_request_info',
        json=request_info,
        headers={'X-Yandex-Login': login},
    )
    assert response.status == 200
    request_info['last_updater_login'] = login
    request_info['creator_login'] = login
    request_info['created'] = now
    request_info['updated'] = now
    state = utils.del_fields(
        utils.convert_datetimes(
            [*pre_state, request_info], ['created', 'updated'],
        ),
        ['_id', 'order_id'],
    )

    response_data = utils.del_fields(
        utils.convert_datetimes(await response.json(), ['created', 'updated']),
        ['_id', 'order_id'],
    )

    assert response_data == state

    rows = utils.del_fields(
        await db.antifraud_support_requests_info_mdb.find(
            {'order_id': order_id},
        ).to_list(None),
        ['_id', 'order_id'],
    )

    assert rows == state


@pytest.mark.now('2020-03-10T11:20:00')
async def test_add_support_request_first_request(web_app_client, db, now):
    order_id = 'some_other_order'

    assert (
        await db.antifraud_support_requests_info_mdb.find_one(
            {'order_id': order_id},
        )
        is None
    )

    request_info = {
        'order_id': order_id,
        'request_id': 'some_other_id',
        'request_type': 'unknown_transaction',
    }
    login = 'login1'
    response = await web_app_client.post(
        '/v1/add_support_request_info',
        json=request_info,
        headers={'X-Yandex-Login': login},
    )
    assert response.status == 200
    request_info['last_updater_login'] = login
    request_info['creator_login'] = login
    request_info['created'] = now
    request_info['updated'] = now
    expected = utils.del_fields(
        utils.convert_datetimes([request_info], ['created', 'updated']),
        ['order_id'],
    )

    response_data = utils.del_fields(
        utils.convert_datetimes(await response.json(), ['created', 'updated']),
        ['_id', 'order_id'],
    )

    assert response_data == expected

    rows = utils.del_fields(
        utils.convert_datetimes(
            await db.antifraud_support_requests_info_mdb.find(
                {'order_id': order_id},
            ).to_list(None),
            ['created', 'updated'],
        ),
        ['_id', 'order_id'],
    )

    assert rows == expected


@pytest.mark.now('2020-03-10T11:20:00')
async def test_add_support_request_update_requests(web_app_client, db, now):
    order_id = 'some_order'
    request_id = 'some_id_1'
    pre_state = await db.antifraud_support_requests_info_mdb.find(
        {'order_id': order_id},
    ).to_list(None)

    assert len(pre_state) == 2

    unchanged_row, row_to_change = (
        pre_state.reverse()
        if pre_state[0]['request_id'] == request_id
        else pre_state
    )

    request_info = {
        'order_id': order_id,
        'request_id': request_id,
        'request_type': 'unknown_transaction',
        'additional_info': 'some str',
    }
    login = 'login'
    response = await web_app_client.post(
        '/v1/add_support_request_info',
        json=request_info,
        headers={'X-Yandex-Login': login},
    )
    assert response.status == 200
    row_to_change['last_updater_login'] = login
    row_to_change['updated'] = now
    row_to_change['additional_info'] = 'some str'
    expected = utils.del_fields(
        utils.convert_datetimes(
            [unchanged_row, row_to_change], ['created', 'updated'],
        ),
        ['_id', 'order_id'],
    )

    response_data = utils.del_fields(
        utils.convert_datetimes(await response.json(), ['created', 'updated']),
        ['_id', 'order_id'],
    )

    assert response_data == expected

    rows = utils.del_fields(
        await db.antifraud_support_requests_info_mdb.find(
            {'order_id': order_id},
        ).to_list(None),
        ['_id', 'order_id'],
    )

    assert rows == expected
