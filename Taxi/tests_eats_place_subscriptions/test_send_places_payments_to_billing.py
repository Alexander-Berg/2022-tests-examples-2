import datetime as dt

import pytest

from tests_eats_place_subscriptions import utils


PERIODIC_NAME = 'send-places-payments-to-billing-periodic'


def make_billing_request(place_id, offset, event_at, amount):
    place_time = event_at.astimezone(
        dt.timezone(dt.timedelta(hours=offset)),
    ).strftime('%Y-%m-%d')
    order_nr = f'subscribe-{place_id}-{place_time}'
    event_at = event_at.astimezone(dt.timezone.utc).isoformat()
    return {
        'order_nr': order_nr,
        'external_id': order_nr,
        'event_at': event_at,
        'kind': 'monthly_payment',
        'data': {
            'order_nr': order_nr,
            'event_at': event_at,
            'place_id': place_id,
            'amount': amount,
            'currency': 'RUB',
        },
        'rule_name': 'default',
    }


@pytest.mark.config(
    EATS_PLACE_SUBSCRIPTIONS_PERIODICS={
        PERIODIC_NAME: {'is_enabled': True, 'period_in_sec': 3600},
    },
    EATS_PLACE_SUBSCRIPTIONS_SEND_PLACES_PAYMENTS_TO_BILLING={
        'db_lookup_batch_size': 1000,
        'catalog_lookup_batch_size': 100,
        'start_hour': 1,
        'end_hour': 2,
    },
)
@pytest.mark.experiments3(filename='tariffs.json')
@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
@pytest.mark.parametrize(
    'current_time, expected_billing_request',
    [
        pytest.param(
            dt.datetime(2020, 2, 29, 23, 0, tzinfo=utils.MSC_TIMEZONE),
            # в плейсе UTC+5
            make_billing_request(
                '124',
                5,
                dt.datetime(2020, 2, 29, 23, 0, tzinfo=utils.MSC_TIMEZONE),
                '41.9',
            ),
            id='has_appropriate_places',
        ),
        pytest.param(
            dt.datetime(2021, 5, 15, 15, 0, tzinfo=utils.MSC_TIMEZONE),
            None,
            id='no_appropriate_places',
        ),
    ],
)
async def test_send_places_payments_to_billing(
        mocked_time,
        mockserver,
        taxi_eats_place_subscriptions,
        testpoint,
        # parametrize params
        current_time,
        expected_billing_request,
):
    mocked_time.set(current_time)

    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    @mockserver.json_handler(utils.BILLING_PROCESSOR_URL)
    def mock_billing_processor(request):
        assert request.json == expected_billing_request
        return mockserver.make_response(json={'event_id': '1'}, status=200)

    await taxi_eats_place_subscriptions.run_distlock_task(PERIODIC_NAME)

    assert mock_billing_processor.has_calls == (
        expected_billing_request is not None
    )
    assert periodic_finished.times_called == 1


@pytest.mark.now('2020-02-29T23:00:00+0300')
@utils.set_tariffs_experiment({'tariffs': []})
@pytest.mark.config(
    EATS_PLACE_SUBSCRIPTIONS_PERIODICS={
        PERIODIC_NAME: {'is_enabled': True, 'period_in_sec': 3600},
    },
)
@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
async def test_tariff_errors_metrics(
        mockserver,
        taxi_eats_place_subscriptions,
        taxi_eats_place_subscriptions_monitor,
        testpoint,
):
    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    @mockserver.json_handler(utils.BILLING_PROCESSOR_URL)
    def mock_billing_processor(request):
        return mockserver.make_response(json={'event_id': '1'}, status=200)

    await taxi_eats_place_subscriptions.tests_control(reset_metrics=True)

    await taxi_eats_place_subscriptions.run_distlock_task(PERIODIC_NAME)

    assert not mock_billing_processor.has_calls
    assert periodic_finished.has_calls

    metrics = await taxi_eats_place_subscriptions_monitor.get_metrics()
    assert metrics[utils.TARIFF_ERRORS_METRICS] == {'not_found_in_config': 1}


@pytest.mark.config(
    EATS_PLACE_SUBSCRIPTIONS_PERIODICS={
        PERIODIC_NAME: {
            'is_enabled': True,
            'period_in_sec': 3600,
            'db_chunk_size': 1,
            'sleep_time_after_iteration': 0,
        },
    },
    EATS_PLACE_SUBSCRIPTIONS_SEND_PLACES_PAYMENTS_TO_BILLING={
        'db_lookup_batch_size': 1000,
        'catalog_lookup_batch_size': 100,
        'start_hour': 1,
        'end_hour': 2,
    },
)
@pytest.mark.experiments3(filename='tariffs.json')
@pytest.mark.pgsql(
    'eats_place_subscriptions',
    files=['db_places_subscriptions_inn_groups.sql'],
)
@pytest.mark.parametrize(
    'place_id, current_time, amount',
    [
        pytest.param(
            '200',
            dt.datetime(2020, 3, 1, 1, 0, tzinfo=utils.MSC_TIMEZONE),
            '41.9',
            id='empty INN',
        ),
        pytest.param(
            '202',
            dt.datetime(2020, 3, 1, 1, 0, tzinfo=utils.MSC_TIMEZONE),
            '41.9',
            id='1 with INN',
        ),
        pytest.param(
            '203',
            dt.datetime(2020, 3, 1, 1, 0, tzinfo=utils.MSC_TIMEZONE),
            '20.95',
            id='2 with INN',
        ),
        pytest.param(
            '205',
            dt.datetime(2020, 3, 1, 1, 0, tzinfo=utils.MSC_TIMEZONE),
            '13.97',
            id='3 with INN',
        ),
        pytest.param(
            '208',
            dt.datetime(2020, 3, 1, 1, 0, tzinfo=utils.MSC_TIMEZONE),
            '14.51',
            id='4 with INN',
        ),
        pytest.param(
            '212',
            dt.datetime(2020, 3, 1, 1, 0, tzinfo=utils.MSC_TIMEZONE),
            '14.83',
            id='5 active with INN',
        ),
        pytest.param(
            '217',
            dt.datetime(2020, 3, 1, 1, 0, tzinfo=utils.MSC_TIMEZONE),
            '14.51',
            id='5 active with INN, 1 not business_plus',
        ),
        pytest.param(
            '222',
            dt.datetime(2020, 3, 1, 1, 0, tzinfo=utils.MSC_TIMEZONE),
            '14.51',
            id='5 active with INN, 1 not valid',
        ),
        pytest.param(
            '227',
            dt.datetime(2020, 3, 1, 1, 0, tzinfo=utils.MSC_TIMEZONE),
            '14.51',
            id='5 active with INN, 1 is trial',
        ),
    ],
)
async def test_send_places_payments_to_billing_with_inn_aggregation(
        mocked_time,
        mockserver,
        taxi_eats_place_subscriptions,
        testpoint,
        pgsql,
        # parametrize params
        place_id,
        current_time,
        amount,
):
    mocked_time.set(current_time)

    cursor = pgsql['eats_place_subscriptions'].cursor()
    cursor.execute(
        f"""
        UPDATE eats_place_subscriptions.places
        SET timezone = 'Europe/Moscow'
        WHERE place_id = '{place_id}';
    """,
    )

    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    @mockserver.json_handler(utils.BILLING_PROCESSOR_URL)
    def mock_billing_processor(request):
        assert request.json == make_billing_request(
            place_id, 3, current_time, amount,
        )
        return mockserver.make_response(json={'event_id': '1'}, status=200)

    await taxi_eats_place_subscriptions.run_distlock_task(PERIODIC_NAME)

    assert mock_billing_processor.times_called == 1
    assert periodic_finished.times_called == 1
