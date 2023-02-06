import datetime as dt

import pytest
import pytz


@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.parametrize(
    'check_enabled',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                RIDEHISTORY_CHECK_REMOVE_PERMISSIONS=True,
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                RIDEHISTORY_CHECK_REMOVE_PERMISSIONS=False,
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'url, request_json',
    [
        ('v2/remove/?order_id=first', None),
        (
            '4.0/ridehistory/v2/remove',
            {'order_id': 'first', 'created_at': 777},
        ),
    ],
)
@pytest.mark.config(
    RIDEHISTORY_ROUTEHISTORY_FORGET={'enabled': True, 'fail_otherwise': True},
)
@pytest.mark.now('2017-09-09T00:00:00+0300')
async def test_simple(
        taxi_ridehistory,
        mock_yt_queries,
        get_hidden_data,
        check_enabled,
        url,
        request_json,
        mockserver,
):
    if check_enabled:
        yt_mock = mock_yt_queries('expected_yt_request_simple')

    @mockserver.json_handler('/routehistory/routehistory/forget')
    def _mock_routehistory_forget(request):
        assert request.json['order_id'] == 'first'
        return {}

    response = await taxi_ridehistory.delete(
        url,
        json=request_json,
        headers={
            'X-Yandex-UID': '12345',
            'X-YaTaxi-PhoneId': 'aaaaaaaaaaaaaaaaaaaaaaaa',
            'X-YaTaxi-Bound-Uids': '1,2',
        },
    )

    assert response.status == 204

    data = get_hidden_data()
    assert data['user_index'] == {'first': True, 'second': False}

    assert len(data['hidden_orders']) == 1
    hidden_order = data['hidden_orders']['first']
    assert hidden_order['order_id'] == 'first'
    assert hidden_order['user_uid'] == '12345'

    if check_enabled:  # insert data from db
        assert hidden_order['phone_id'] == '777777777777777777777777'
    else:  # insert data from request
        assert hidden_order['phone_id'] == 'aaaaaaaaaaaaaaaaaaaaaaaa'

    assert hidden_order['created_at'].astimezone(pytz.UTC) == dt.datetime(
        2017, 9, 8, 21, tzinfo=pytz.UTC,
    )

    if url.startswith('4.0'):
        assert hidden_order['order_created_at'].astimezone(
            pytz.UTC,
        ) == dt.datetime(1970, 1, 1, 0, 12, 57, tzinfo=pytz.UTC)
    else:
        assert hidden_order['order_created_at'] is None

    if check_enabled:
        assert yt_mock.times_called == 2


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.parametrize(
    'url, request_json',
    [
        ('v2/remove/?order_id=test', None),
        ('4.0/ridehistory/v2/remove', {'order_id': 'test', 'created_at': 777}),
    ],
)
async def test_archived(taxi_ridehistory, get_hidden_data, url, request_json):
    response = await taxi_ridehistory.delete(
        url,
        json=request_json,
        headers={
            'X-Yandex-UID': '12345',
            'X-YaTaxi-PhoneId': 'aaaaaaaaaaaaaaaaaaaaaaaa',
        },
    )

    assert response.status == 204

    data = get_hidden_data()
    assert data['user_index'] == {}

    assert len(data['hidden_orders']) == 1
    hidden_order = data['hidden_orders']['test']
    assert hidden_order['order_id'] == 'test'
    assert hidden_order['phone_id'] == 'aaaaaaaaaaaaaaaaaaaaaaaa'
    assert hidden_order['user_uid'] == '12345'
    assert hidden_order['created_at'].astimezone(pytz.UTC) == dt.datetime(
        2017, 9, 8, 21, tzinfo=pytz.UTC,
    )


@pytest.mark.pgsql('ridehistory', files=['ridehistory_idempotency.sql'])
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                RIDEHISTORY_CHECK_REMOVE_PERMISSIONS=True,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                RIDEHISTORY_CHECK_REMOVE_PERMISSIONS=False,
            ),
        ),
    ],
)
@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.parametrize(
    'url, request_json',
    [
        ('v2/remove/?order_id=first', None),
        (
            '4.0/ridehistory/v2/remove',
            {'order_id': 'first', 'created_at': 777},
        ),
    ],
)
async def test_idempotency(
        taxi_ridehistory,
        mock_yt_queries_empty,
        get_hidden_data,
        url,
        request_json,
):
    response = await taxi_ridehistory.delete(
        url,
        json=request_json,
        headers={
            'X-Yandex-UID': '12345',
            'X-YaTaxi-PhoneId': 'aaaaaaaaaaaaaaaaaaaaaaaa',
        },
    )

    assert response.status == 204

    data = get_hidden_data()
    assert data['user_index'] == {'first': True}

    assert len(data['hidden_orders']) == 1
    hidden_order = data['hidden_orders']['first']
    assert hidden_order['order_id'] == 'first'
    assert (
        hidden_order['phone_id'] == '777777777777777777777777'
    )  # on conflict do nothing
    assert hidden_order['user_uid'] == '12345'


@pytest.mark.parametrize(
    'phone_id, status', [('phone_id', 204), ('nonexistent', 404)],
)
@pytest.mark.parametrize(
    'yt_mock_name',
    [
        pytest.param(
            'expected_yt_request_yt_no_content',
            marks=pytest.mark.pgsql('ridehistory'),
        ),
        pytest.param(
            'expected_yt_request_hidden_orders_no_content',
            marks=pytest.mark.pgsql(
                'ridehistory',
                files=['ridehistory_hidden_orders_no_content.sql'],
            ),
        ),
        pytest.param(
            'expected_yt_request_user_index_no_content',
            marks=pytest.mark.pgsql(
                'ridehistory', files=['ridehistory_user_index_no_content.sql'],
            ),
        ),
    ],
)
@pytest.mark.config(RIDEHISTORY_CHECK_REMOVE_PERMISSIONS=True)
@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.parametrize(
    'url, request_json',
    [
        ('v2/remove/?order_id=first', None),
        (
            '4.0/ridehistory/v2/remove',
            {'order_id': 'first', 'created_at': 123},
        ),
    ],
)
async def test_no_content(
        taxi_ridehistory,
        mock_yt_queries,
        phone_id,
        status,
        yt_mock_name,
        url,
        request_json,
):
    yt_mock = mock_yt_queries(yt_mock_name)

    response = await taxi_ridehistory.delete(
        url,
        json=request_json,
        headers={'X-Yandex-UID': 'nonexistent', 'X-YaTaxi-PhoneId': phone_id},
    )

    assert response.status == status
    assert yt_mock.times_called == 2


@pytest.mark.pgsql('ridehistory')
@pytest.mark.parametrize(
    'request_user_uid, request_phone_id, request_tag',
    [
        ('nonexistent', 'phone_id', 'phone_id'),
        ('user_uid', 'nonexistent', 'user_uid'),
    ],
)
@pytest.mark.parametrize('response_id_prefix', ['yt', 'pg'])
@pytest.mark.config(RIDEHISTORY_CHECK_REMOVE_PERMISSIONS=True)
@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.parametrize(
    'url, request_json',
    [
        ('v2/remove/?order_id=first', None),
        (
            '4.0/ridehistory/v2/remove',
            {'order_id': 'first', 'created_at': 123},
        ),
    ],
)
async def test_pg_data_preferred(
        taxi_ridehistory,
        pgsql,
        load,
        mock_yt_queries,
        get_hidden_data,
        request_phone_id,
        request_user_uid,
        request_tag,
        response_id_prefix,
        url,
        request_json,
):
    if response_id_prefix == 'pg':
        pgsql['ridehistory'].cursor().execute(
            load(f'ridehistory_pg_data_preferred_{request_tag}.sql'),
        )

    mock_yt_queries('expected_yt_request_pg_data_preferred')

    response = await taxi_ridehistory.delete(
        url,
        json=request_json,
        headers={
            'X-Yandex-UID': request_user_uid,
            'X-YaTaxi-PhoneId': request_phone_id,
        },
    )

    assert response.status == 204

    data = get_hidden_data()

    if response_id_prefix == 'pg':
        assert data['user_index'] == {'first': True}
    else:
        assert data['user_index'] == {}

    assert len(data['hidden_orders']) == 1
    hidden_order = data['hidden_orders']['first']

    assert hidden_order['order_id'] == 'first'
    if response_id_prefix == 'pg':
        if request_tag == 'phone_id':
            assert hidden_order['phone_id'] == 'phone_id'
            assert hidden_order['user_uid'] == 'pg_user_uid'
        else:
            assert hidden_order['phone_id'] == 'pg_phone_id'
            assert hidden_order['user_uid'] == 'user_uid'

        assert hidden_order['payment_tech_type'] == 'pg_payment_tech_type'
        assert hidden_order['payment_method_id'] == 'pg_payment_method_id'
    else:
        if request_tag == 'phone_id':
            assert hidden_order['phone_id'] == 'yt_phone_id'
            assert hidden_order['user_uid'] == 'nonexistent'
        else:
            assert hidden_order['phone_id'] == 'yt_phone_id'
            assert hidden_order['user_uid'] == 'yt_user_uid'

        assert hidden_order['payment_tech_type'] == 'yt_payment_tech_type'
        assert hidden_order['payment_method_id'] == 'yt_payment_method_id'

    assert hidden_order['created_at'].astimezone(pytz.UTC) == dt.datetime(
        2017, 9, 8, 21, tzinfo=pytz.UTC,
    )


# This test illustrates why should we write user_uid/phone_id fetched from
# ridehistory dbs and not from user_uid/order_id from request
# users:
#   user1(user_uid='1', bound_uids=['2'], phone_id='1')
#   user2(user_uid='2', bound_uids=[], phone_id='2')
# user_uid='1' is portal and user_uid='2' is phonish
# order:
#   order1(order_id='1', user_uid='1', phone_id='2')
# Setup:
#   1) user2 makes order1 with portal account
#   2) user2 logs out from portal account
#   3) Time passes, order is archived
#   4) user1 deletes order1, which he finds by user_uid, resulting in
#      hidden_orders entry (user_uid='1', phone_id='1') -- user_uid/phone_id
#      are taken from request
#   5) user2 still thinks order is not deleted as he can't find it in
#      hidden_orders
#   6) After a minute order is replicated from hidden_orders to yt and user2
#      recovers that order is deleted
# This situation is impossible when one writes user_uid/phone_id fetched from
# ridehistory. Worth mentioning, one can come up with some other setups.
@pytest.mark.pgsql('ridehistory')
@pytest.mark.parametrize(
    'check_enabled, check_suffix',
    [
        pytest.param(
            True,
            'check',
            marks=pytest.mark.config(
                RIDEHISTORY_CHECK_REMOVE_PERMISSIONS=True,
            ),
        ),
        pytest.param(
            False,
            'no_check',
            marks=pytest.mark.config(
                RIDEHISTORY_CHECK_REMOVE_PERMISSIONS=False,
            ),
        ),
    ],
)
@pytest.mark.config(
    APPLICATION_MAP_BRAND={'android': 'yataxi'},
    RIDEHISTORY_YANDEX_UID_SEARCH_ENABLED=True,
)
@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.parametrize(
    'url, request_json',
    [
        ('v2/remove/?order_id=1', None),
        ('4.0/ridehistory/v2/remove', {'order_id': '1', 'created_at': 123}),
    ],
)
async def test_list_remove(
        taxi_ridehistory,
        mock_zones_v2_empty,
        mock_yamaps_default,
        get_hidden_data,
        mock_yt_queries,
        mock_taxi_tariffs_query,
        check_enabled,
        check_suffix,
        url,
        request_json,
):
    yt_mock = mock_yt_queries(
        f'expected_yt_request_list_remove_{check_suffix}',
    )
    mock_taxi_tariffs_query(['saratov'])

    # user1 deletes order
    response = await taxi_ridehistory.delete(
        url,
        json=request_json,
        headers={
            'X-Yandex-UID': '1',
            'X-YaTaxi-PhoneId': '1',
            'X-YaTaxi-Bound-Uids': '2',
        },
    )

    assert response.status == 204

    data = get_hidden_data()

    assert data['user_index'] == {}
    assert len(data['hidden_orders']) == 1

    hidden_order = data['hidden_orders']['1']
    assert hidden_order['order_id'] == '1'
    assert hidden_order['user_uid'] == '1'
    if check_enabled:
        assert hidden_order['phone_id'] == '2'
    else:
        assert hidden_order['phone_id'] == '1'

    # user2 gets ridehistory
    response = await taxi_ridehistory.post(
        'v2/list',
        json={},
        headers={
            'X-Yandex-UID': '2',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '2',
        },
    )

    assert response.status == 200

    order_ids = {o['order_id'] for o in response.json()['orders']}
    if check_enabled:
        assert order_ids == set()
    else:
        assert order_ids == {'1'}

    if check_enabled:
        assert yt_mock.times_called == 4
    else:
        assert yt_mock.times_called == 2


@pytest.mark.pgsql('ridehistory', files=['ridehistory_user_uid_null.sql'])
@pytest.mark.config(RIDEHISTORY_CHECK_REMOVE_PERMISSIONS=True)
@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.parametrize(
    'url, request_json',
    [
        ('v2/remove/?order_id=first', None),
        (
            '4.0/ridehistory/v2/remove',
            {'order_id': 'first', 'created_at': 777},
        ),
    ],
)
async def test_user_uid_null(
        taxi_ridehistory, mock_yt_queries, get_hidden_data, url, request_json,
):
    mock_yt_queries('expected_yt_request_simple')

    response = await taxi_ridehistory.delete(
        url,
        json=request_json,
        headers={
            'X-Yandex-UID': '12345',
            'X-YaTaxi-PhoneId': 'aaaaaaaaaaaaaaaaaaaaaaaa',
            'X-YaTaxi-Bound-Uids': '1,2',
        },
    )

    assert response.status == 204

    assert get_hidden_data()['hidden_orders']['first']['user_uid'] is None


@pytest.mark.config(RIDEHISTORY_CHECK_REMOVE_PERMISSIONS=True)
@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.parametrize(
    'url, request_json',
    [
        ('v2/remove/?order_id=first', None),
        (
            '4.0/ridehistory/v2/remove',
            {'order_id': 'first', 'created_at': 777},
        ),
    ],
)
async def test_order_phone_id_null(
        taxi_ridehistory, mock_yt_queries, get_hidden_data, url, request_json,
):
    mock_yt_queries('expected_yt_request_semi_empty')

    response = await taxi_ridehistory.delete(
        url,
        json=request_json,
        headers={
            'X-Yandex-UID': '12345',
            'X-YaTaxi-PhoneId': 'aaaaaaaaaaaaaaaaaaaaaaaa',
            'X-YaTaxi-Bound-Uids': '1,2',
        },
    )

    assert response.status == 204

    data = get_hidden_data()['hidden_orders']['first']
    assert data['phone_id'] == '2'
    assert data['user_uid'] == 'yt_user_uid'
    assert data['payment_tech_type'] is None
    assert data['payment_method_id'] is None
