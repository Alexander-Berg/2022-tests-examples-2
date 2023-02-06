import datetime

import freezegun
import pytest

from cashback.api import restore_cashback

ORDER_RATES_TABLE = (
    '//testsuite/unittests/private/postgres/cashback/cashback_order_rates'
)

ORDER_CLEARS_TABLE = (
    '//testsuite/unittests/private/postgres/cashback/cashback_order_clears'
)

# pylint: disable=invalid-name
pytestmark = pytest.mark.config(
    TVM_RULES=[{'dst': 'archive-api', 'src': 'cashback'}],
)
# pylint: enable=invalid-name


@pytest.fixture(name='mock_archive_api')
def _mock_archive_api(mockserver, load_json):
    @mockserver.json_handler('/archive-api/v1/yt/select_rows')
    def _mock(request):
        request_query = request.json['query']['query_string']
        result = _mock.result_by_query[request_query]
        return {'items': result, 'source': 'hahn'}

    _mock.result_by_query = {}
    return _mock


@pytest.mark.parametrize(
    'order_id, order_created_at, service, version',
    [
        # Fresh order with no rate → return default
        pytest.param(
            'order_id_5',
            '2020-07-18T15:10:00',
            'yataxi',
            0,
            id='yataxi-no-rate',
        ),
        # Fresh order with a rate but without a clear → return default
        pytest.param(
            'order_id_3',
            '2020-07-18T15:10:00',
            'yataxi',
            0,
            id='yataxi-rate-exists-no-clear',
        ),
        # Fresh order with a rate and a clear
        pytest.param(
            'order_id_2',
            '2020-07-18T15:10:00',
            'yataxi',
            2,
            id='yataxi-rate-clear exist',
        ),
        pytest.param(
            'order_id_6', None, 'lavka', 6, id='lavka-rate-clear-exist',
        ),
    ],
)
@pytest.mark.config(CASHBACK_ORDERS_RESTORE_TTL=86400)
@pytest.mark.now('2020-07-18T15:26:00')
@pytest.mark.pgsql('cashback', files=['basic_cashback.sql'])
async def test_restore_fresh(
        web_cashback,
        web_context,
        pg_cashback,
        order_id,
        order_created_at,
        service,
        version,
):
    params = {'order_id': order_id}
    if order_created_at:
        params['order_created_at'] = order_created_at
    if service:
        params['service'] = service
    response = await web_cashback.restore_cashback.make_request(
        override_params=params,
    )
    assert response.status == 200

    response_data = await response.json()
    assert response_data['version'] == version


@pytest.mark.now('2019-11-08T01:10:00+0300')
@pytest.mark.config(CASHBACK_ORDERS_RESTORE_TTL=86400)
@pytest.mark.parametrize(
    'use_archive_api',
    [
        pytest.param(
            True, marks=pytest.mark.config(CASHBACK_YT_USE_ARCHIVE_API=True),
        ),
        pytest.param(
            False, marks=pytest.mark.config(CASHBACK_YT_USE_ARCHIVE_API=False),
        ),
    ],
)
@pytest.mark.parametrize(
    'order_created_at',
    [
        pytest.param(None, id='order-created-none'),
        pytest.param('2019-10-08T01:00:00', id='order-created-stale'),
    ],
)
async def test_restore_from_yt(
        web_cashback,
        web_context,
        pg_cashback,
        mock_yt,
        mock_archive_api,
        load_json,
        order_created_at,
        use_archive_api,
):
    order_id = 'order_id'
    service = 'yataxi'
    version = 2

    rates_query = web_context.yt_queries.make_query(
        'get_order_rates.sql',
        order_id=order_id,
        order_rates_table=ORDER_RATES_TABLE,
    )

    clear_query = web_context.yt_queries.make_query(
        'get_order_clears.sql',
        order_id=order_id,
        service=service,
        order_clears_table=ORDER_CLEARS_TABLE,
    )

    if use_archive_api:
        mock_archive_api.result_by_query.update(
            {
                rates_query: [load_json('response_select_rows_rates.json')],
                clear_query: [load_json('response_select_rows_clears.json')],
            },
        )

    else:
        mock_yt.add_select_rows_response(
            rates_query, 'response_select_rows_rates.json',
        )
        mock_yt.add_select_rows_response(
            clear_query, 'response_select_rows_clears.json',
        )

    params = {'order_id': order_id, 'service': service}
    if order_created_at:
        params['order_created_at'] = order_created_at
    response = await web_cashback.restore_cashback.make_request(
        override_params=params,
    )
    assert response.status == 200

    response_data = await response.json()
    assert response_data['version'] == version

    rates = await pg_cashback.order_rates.all()
    assert len(rates) == 1
    assert rates[0]['order_id'] == order_id

    clears = await pg_cashback.order_clears.all()
    assert len(clears) == 1
    assert clears[0]['order_id'] == order_id

    if use_archive_api:
        assert mock_archive_api.has_calls
        assert mock_archive_api.times_called == 2

        calls = (mock_archive_api.next_call(), mock_archive_api.next_call())
        request_bodies = [call['request'].json for call in calls]

        assert request_bodies == [
            {
                'query': {'query_string': rates_query},
                'replication_rules': [{'name': 'cashback_order_rates'}],
                'bson': False,
            },
            {
                'query': {'query_string': clear_query},
                'replication_rules': [{'name': 'cashback_order_clears'}],
                'bson': False,
            },
        ]

    else:
        assert not mock_archive_api.has_calls


@pytest.mark.parametrize(
    'now, ttl, order_created_at, expected',
    [
        pytest.param(
            '2020-07-18T11:35:07',
            datetime.timedelta(days=2),
            None,
            True,
            id='order-created-is-none',
        ),
        pytest.param(
            '2020-07-18T11:35:07',
            datetime.timedelta(days=2),
            '2020-07-18T11:20:07',
            False,
            id='fresh-order',
        ),
        pytest.param(
            '2020-07-18T11:35:07',
            datetime.timedelta(days=2),
            '2020-06-18T11:20:07',
            True,
            id='stale-order',
        ),
        pytest.param(
            '2020-07-18T11:35:07',
            datetime.timedelta(minutes=1),
            '2020-07-18T11:34:07',
            True,
            id='just-archived',
        ),
        pytest.param(
            '2020-07-18T11:35:07',
            datetime.timedelta(minutes=1),
            '2020-07-18T11:34:08',
            False,
            id='almost-archived',
        ),
    ],
)
def test_should_lookup_archive(now, ttl, order_created_at, expected):
    if order_created_at is not None:
        order_created_at = datetime.datetime.fromisoformat(order_created_at)
    with freezegun.freeze_time(now):
        result = restore_cashback.should_lookup_archive(
            order_ttl=ttl, order_created_at=order_created_at,
        )

    assert result == expected
