# pylint: disable=unused-variable
import datetime

import pytest


def create_result(cursor):
    result = {}
    for item in cursor:
        result[item[0]] = {
            'status': item[1],
            'send_time': item[2],
            'next_request_time': item[3],
        }
    return result


def create_date(delta=None):
    if delta:
        return datetime.datetime.utcnow() + delta
    return datetime.datetime.utcnow()


EXPECTED_RESULT = create_result(
    [
        [
            1,
            'zero_balance',
            create_date(datetime.timedelta(days=0)),
            create_date(datetime.timedelta(days=1)),
        ],
        [2, 'zero_balance', None, create_date(datetime.timedelta(days=1))],
        [
            3,
            'zero_balance',
            create_date(datetime.timedelta(days=1)),
            create_date(datetime.timedelta(days=1)),
        ],
        [4, 'high_balance', None, create_date(datetime.timedelta(days=1))],
        [5, 'high_balance', None, create_date(datetime.timedelta(days=1))],
        [
            6,
            'zero_balance',
            create_date(datetime.timedelta(days=0)),
            create_date(datetime.timedelta(days=1)),
        ],
        [
            7,
            'zero_balance',
            create_date(datetime.timedelta(days=0)),
            create_date(datetime.timedelta(days=-2)),
        ],
    ],
)


def check_result(result, expected_result):
    assert len(result) == len(expected_result)
    for advert_id in result:
        assert (
            result[advert_id]['status'] == expected_result[advert_id]['status']
        )
        assert (
            result[advert_id]['send_time'] is None
            and expected_result[advert_id]['send_time'] is None
            or result[advert_id]['send_time']
            - expected_result[advert_id]['send_time']
            < datetime.timedelta(minutes=5)
        )
        assert result[advert_id]['next_request_time'] - expected_result[
            advert_id
        ]['next_request_time'] < datetime.timedelta(minutes=5)


def fetch_result(cursor):
    cursor.execute(
        """
            SELECT advert_id,
                    status, sending_time AT TIME ZONE 'UTC',
                    next_request_time AT TIME ZONE 'UTC'
            FROM eats_restapp_marketing.balance as balance
        """,
    )
    return cursor.fetchall()


async def test_update_balance_for_advert_not_in_balance(
        pgsql, taxi_eats_restapp_marketing, testpoint, mock_direct_internal,
):
    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        """
            INSERT INTO eats_restapp_marketing.advert
            (id, updated_at, place_id, averagecpc, campaign_id, group_id,
              ad_id, banner_id, content_id, is_active, passport_id,
              strategy_type)
            VALUES (1, '2021-07-01 03:00+03:00'::timestamptz, 1, 10000000, 1,
              1, 1, 1, 1, true, 1, 'average_cpc');
        """,
    )

    @testpoint('update-advertrs-balances-finished')
    def handle_finished(arg):
        expected_result = create_result(
            [
                [
                    1,
                    'high_balance',
                    None,
                    create_date(datetime.timedelta(days=1)),
                ],
            ],
        )
        cursor = pgsql['eats_restapp_marketing'].cursor()
        check_result(create_result(fetch_result(cursor)), expected_result)

    async with taxi_eats_restapp_marketing.spawn_task(
            'update-adverts-balances',
    ):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'


async def test_dont_updadte_balance_if_advert_is_not_active(
        pgsql, taxi_eats_restapp_marketing, testpoint, mock_direct_internal,
):
    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        """
            INSERT INTO eats_restapp_marketing.advert
            (id, updated_at, place_id, averagecpc, campaign_id, group_id,
              ad_id, banner_id, content_id, is_active, passport_id,
              strategy_type)
            VALUES (1, '2021-07-01 03:00+03:00'::timestamptz, 1, 10000000, 1,
              1, 1, 1, 1, false, 1, 'average_cpc');

            INSERT INTO eats_restapp_marketing.balance
            (advert_id, status, sending_time, next_request_time)
            VALUES (1,'zero_balance', NOW() + interval '1 day',
              NOW() - interval '1 day');
        """,
    )

    @testpoint('update-advertrs-balances-finished')
    def handle_finished(arg):
        expected_result = create_result(
            [
                [
                    1,
                    'zero_balance',
                    create_date(datetime.timedelta(days=1)),
                    create_date(datetime.timedelta(days=-1)),
                ],
            ],
        )
        cursor = pgsql['eats_restapp_marketing'].cursor()
        check_result(create_result(fetch_result(cursor)), expected_result)

    async with taxi_eats_restapp_marketing.spawn_task(
            'update-adverts-balances',
    ):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'


async def test_updadte_zero_balance_to_high_balance(
        pgsql, taxi_eats_restapp_marketing, testpoint, mock_direct_internal,
):
    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        """
            INSERT INTO eats_restapp_marketing.advert
            (id, updated_at, place_id, averagecpc, campaign_id, group_id,
              ad_id, banner_id, content_id, is_active, passport_id,
              strategy_type)
            VALUES (1, '2021-07-01 03:00+03:00'::timestamptz, 1, 10000000, 1,
              1, 1, 1, 1, true, 1, 'average_cpc');

            INSERT INTO eats_restapp_marketing.balance
            (advert_id, status, sending_time, next_request_time)
            VALUES (1,'zero_balance', NOW() + interval '1 day',
              NOW() - interval '1 day');
        """,
    )

    @testpoint('update-advertrs-balances-finished')
    def handle_finished(arg):
        expected_result = create_result(
            [
                [
                    1,
                    'high_balance',
                    None,
                    create_date(datetime.timedelta(days=1)),
                ],
            ],
        )
        cursor = pgsql['eats_restapp_marketing'].cursor()
        check_result(create_result(fetch_result(cursor)), expected_result)

    async with taxi_eats_restapp_marketing.spawn_task(
            'update-adverts-balances',
    ):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'


async def test_updadte_high_balance_to_zero_balance(
        pgsql, taxi_eats_restapp_marketing, testpoint, mock_direct_internal,
):
    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        """
            INSERT INTO eats_restapp_marketing.advert
            (id, updated_at, place_id, averagecpc, campaign_id, group_id,
              ad_id, banner_id, content_id, is_active, passport_id,
              strategy_type)
            VALUES (2, '2021-07-01 03:00+03:00'::timestamptz, 1, 10000000, 1,
              1, 1, 1, 1, true, 2, 'average_cpc');

            INSERT INTO eats_restapp_marketing.balance
            (advert_id, status, sending_time, next_request_time)
            VALUES (2,'high_balance', NULL, NOW() - interval '1 day');
        """,
    )

    @testpoint('update-advertrs-balances-finished')
    def handle_finished(arg):
        expected_result = create_result(
            [
                [
                    2,
                    'zero_balance',
                    create_date(datetime.timedelta(days=0)),
                    create_date(datetime.timedelta(days=1)),
                ],
            ],
        )
        cursor = pgsql['eats_restapp_marketing'].cursor()
        check_result(create_result(fetch_result(cursor)), expected_result)

    async with taxi_eats_restapp_marketing.spawn_task(
            'update-adverts-balances',
    ):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'


async def test_dont_update_sending_time_if_its_null(
        pgsql, taxi_eats_restapp_marketing, testpoint, mock_direct_internal,
):
    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        """
            INSERT INTO eats_restapp_marketing.advert
            (id, updated_at, place_id, averagecpc, campaign_id, group_id,
              ad_id, banner_id, content_id, is_active, passport_id,
              strategy_type)
            VALUES (2, '2021-07-01 03:00+03:00'::timestamptz, 1, 10000000, 1,
              1, 1, 1, 1, true, 2, 'average_cpc');

            INSERT INTO eats_restapp_marketing.balance
            (advert_id, status, sending_time, next_request_time)
            VALUES (2,'zero_balance', NULL, NOW() - interval '1 day');
        """,
    )

    @testpoint('update-advertrs-balances-finished')
    def handle_finished(arg):
        expected_result = create_result(
            [
                [
                    2,
                    'zero_balance',
                    None,
                    create_date(datetime.timedelta(days=1)),
                ],
            ],
        )
        cursor = pgsql['eats_restapp_marketing'].cursor()
        check_result(create_result(fetch_result(cursor)), expected_result)

    async with taxi_eats_restapp_marketing.spawn_task(
            'update-adverts-balances',
    ):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'


async def test_dont_update_balance_if_next_request_time_greater_now(
        pgsql, taxi_eats_restapp_marketing, testpoint, mock_direct_internal,
):
    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        """
            INSERT INTO eats_restapp_marketing.advert
            (id, updated_at, place_id, averagecpc, campaign_id, group_id,
              ad_id, banner_id, content_id, is_active, passport_id,
              strategy_type)
            VALUES (1, '2021-07-01 03:00+03:00'::timestamptz, 1, 10000000, 1,
              1, 1, 1, 1, true, 1, 'average_cpc');

            INSERT INTO eats_restapp_marketing.balance
            (advert_id, status, sending_time, next_request_time)
            VALUES (1,'zero_balance', NOW(), NOW() + interval '1 day');
        """,
    )

    @testpoint('update-advertrs-balances-finished')
    def handle_finished(arg):
        expected_result = create_result(
            [
                [
                    1,
                    'zero_balance',
                    create_date(datetime.timedelta(days=0)),
                    create_date(datetime.timedelta(days=1)),
                ],
            ],
        )
        cursor = pgsql['eats_restapp_marketing'].cursor()
        check_result(create_result(fetch_result(cursor)), expected_result)

    async with taxi_eats_restapp_marketing.spawn_task(
            'update-adverts-balances',
    ):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'


@pytest.mark.pgsql('eats_restapp_marketing', files=['update_balance.sql'])
async def test_update_balance(
        pgsql, taxi_eats_restapp_marketing, testpoint, mockserver,
):
    @mockserver.json_handler('/direct-internal/clients/checkClientState')
    def mock_direct_internal(request):
        assert request.json['with_balance'] is True
        balances = {1: 0.1, 2: 11}
        return mockserver.make_response(
            status=200,
            json={
                'success': True,
                'client_state': 'API_ENABLED',
                'balance': balances[request.json['uid']],
            },
        )

    @testpoint('update-advertrs-balances-finished')
    def handle_finished(arg):
        cursor = pgsql['eats_restapp_marketing'].cursor()
        check_result(create_result(fetch_result(cursor)), EXPECTED_RESULT)
        assert mock_direct_internal.times_called == 4

    async with taxi_eats_restapp_marketing.spawn_task(
            'update-adverts-balances',
    ):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_UPDATE_ADVERTS_BALANCES={
        'chunk': 2,
        'enabled': True,
        'task_period': 3,
        'need_sending_mails': True,
    },
)
@pytest.mark.experiments3(filename='advert_send_balance_mail.json')
async def test_send_mails_if_time_less_now(
        pgsql,
        stq_runner,
        testpoint,
        taxi_eats_restapp_marketing,
        mock_communications,
        experiments3,
        mock_retrieve_ids,
):
    exp3_recorder = experiments3.record_match_tries(
        'eats_restapp_marketing_advert_send_balance_mail',
    )

    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        """
            INSERT INTO eats_restapp_marketing.advert
            (id, updated_at, place_id, averagecpc, campaign_id, group_id,
              ad_id, banner_id, content_id, is_active, passport_id,
              strategy_type)
            VALUES (1, '2021-07-01 03:00+03:00'::timestamptz, 1, 10000000, 1,
              1, 1, 1, 1, true, 1, 'average_cpc');

            INSERT INTO eats_restapp_marketing.balance
            (advert_id, status, sending_time, next_request_time)
            VALUES (1,'zero_balance', NOW() - interval '1 day',
              NOW() + interval '1 day');
        """,
    )

    @testpoint('sending-mails-about-zero-balance-finished')
    def handle_finished(arg):
        cursor = pgsql['eats_restapp_marketing'].cursor()
        cursor.execute(
            """
                SELECT advert_id
                FROM eats_restapp_marketing.balance as balance
                WHERE sending_time is NULL
            """,
        )

        assert sorted(cursor.fetchall()) == [(1,)]

    async with taxi_eats_restapp_marketing.spawn_task(
            'update-adverts-balances',
    ):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'

    await exp3_recorder.get_match_tries(ensure_ntries=1)


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_UPDATE_ADVERTS_BALANCES={
        'chunk': 2,
        'enabled': True,
        'task_period': 3,
        'need_sending_mails': True,
    },
)
async def test_dont_send_if_advert_is_not_active(
        pgsql,
        stq_runner,
        testpoint,
        taxi_eats_restapp_marketing,
        mock_communications,
):
    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        """
            INSERT INTO eats_restapp_marketing.advert
            (id, updated_at, place_id, averagecpc, campaign_id, group_id,
              ad_id, banner_id, content_id, is_active, passport_id,
              strategy_type)
            VALUES (1, '2021-07-01 03:00+03:00'::timestamptz, 1, 10000000, 1,
              1, 1, 1, 1, false, 1, 'average_cpc');

            INSERT INTO eats_restapp_marketing.balance
            (advert_id, status, sending_time, next_request_time)
            VALUES (1,'zero_balance', NOW() - interval '1 day',
              NOW() + interval '1 day');
        """,
    )

    @testpoint('sending-mails-about-zero-balance-finished')
    def handle_finished(arg):
        cursor = pgsql['eats_restapp_marketing'].cursor()
        cursor.execute(
            """
                SELECT advert_id
                FROM eats_restapp_marketing.balance as balance
                WHERE sending_time is NULL
            """,
        )

        assert sorted(cursor.fetchall()) == []

    async with taxi_eats_restapp_marketing.spawn_task(
            'update-adverts-balances',
    ):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_UPDATE_ADVERTS_BALANCES={
        'chunk': 2,
        'enabled': True,
        'task_period': 3,
        'need_sending_mails': True,
    },
)
async def test_send_mails_if_sending_time_greater_now(
        pgsql,
        stq_runner,
        testpoint,
        taxi_eats_restapp_marketing,
        mock_communications,
):
    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        """
            INSERT INTO eats_restapp_marketing.advert
            (id, updated_at, place_id, averagecpc, campaign_id, group_id,
              ad_id, banner_id, content_id, is_active, passport_id,
              strategy_type)
            VALUES (1, '2021-07-01 03:00+03:00'::timestamptz, 1, 10000000, 1,
              1, 1, 1, 1, true, 1, 'average_cpc');

            INSERT INTO eats_restapp_marketing.balance
            (advert_id, status, sending_time, next_request_time)
            VALUES (1,'zero_balance', NOW() + interval '1 day',
              NOW() + interval '1 day');
        """,
    )

    @testpoint('sending-mails-about-zero-balance-finished')
    def handle_finished(arg):
        cursor = pgsql['eats_restapp_marketing'].cursor()
        cursor.execute(
            """
                SELECT advert_id
                FROM eats_restapp_marketing.balance as balance
                WHERE sending_time is NULL
            """,
        )

        assert sorted(cursor.fetchall()) == []

    async with taxi_eats_restapp_marketing.spawn_task(
            'update-adverts-balances',
    ):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_UPDATE_ADVERTS_BALANCES={
        'chunk': 2,
        'enabled': True,
        'task_period': 3,
        'need_sending_mails': True,
    },
)
@pytest.mark.pgsql(
    'eats_restapp_marketing', files=['send_mails_with_zero_balance.sql'],
)
@pytest.mark.experiments3(filename='advert_send_balance_mail.json')
async def test_send_mails_and_update_sending_time(
        pgsql,
        stq_runner,
        mockserver,
        testpoint,
        taxi_eats_restapp_marketing,
        mock_retrieve_ids,
):
    @mockserver.json_handler(
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def mock_communications_sender(request):
        return mockserver.make_response(status=204)

    @testpoint('sending-mails-about-zero-balance-finished')
    def handle_finished(arg):
        cursor = pgsql['eats_restapp_marketing'].cursor()
        cursor.execute(
            """
                SELECT advert_id
                FROM eats_restapp_marketing.balance as balance
                WHERE sending_time is NULL
            """,
        )

        assert sorted(cursor.fetchall()) == [(1,), (2,), (7,)]
        assert mock_communications_sender.times_called == 2

    async with taxi_eats_restapp_marketing.spawn_task(
            'update-adverts-balances',
    ):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_UPDATE_ADVERTS_BALANCES={
        'chunk': 2,
        'enabled': True,
        'task_period': 3,
        'need_sending_mails': True,
    },
)
@pytest.mark.pgsql(
    'eats_restapp_marketing', files=['send_mails_with_zero_balance.sql'],
)
@pytest.mark.experiments3(filename='advert_send_balance_mail.json')
async def test_skip_sending_some_mails_if_communication_return_error(
        pgsql,
        stq_runner,
        mockserver,
        testpoint,
        taxi_eats_restapp_marketing,
        mock_retrieve_ids,
):
    @mockserver.json_handler(
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def mock_communications_sender(request):
        if sorted(request.json['recipients']['place_ids']) == [1]:
            return mockserver.make_response(status=204)
        return mockserver.make_response(status=500)

    @testpoint('sending-mails-about-zero-balance-finished')
    def handle_finished(arg):
        cursor = pgsql['eats_restapp_marketing'].cursor()
        cursor.execute(
            """
                SELECT advert_id
                FROM eats_restapp_marketing.balance as balance
                WHERE sending_time is NULL
            """,
        )

        assert sorted(cursor.fetchall()) == [(1,), (2,)]
        assert mock_communications_sender.times_called == 2

    async with taxi_eats_restapp_marketing.spawn_task(
            'update-adverts-balances',
    ):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_UPDATE_ADVERTS_BALANCES={
        'chunk': 2,
        'enabled': True,
        'task_period': 3,
        'need_sending_mails': True,
    },
)
@pytest.mark.pgsql(
    'eats_restapp_marketing', files=['all_balances_are_high.sql'],
)
async def test_skip_sending_mails_if_all_balances_are_high(
        pgsql, stq_runner, mockserver, testpoint, taxi_eats_restapp_marketing,
):
    @mockserver.json_handler(
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def mock_communications_sender(request):
        return mockserver.make_response(status=204)

    @testpoint('sending-mails-about-zero-balance-finished')
    def handle_finished(arg):
        cursor = pgsql['eats_restapp_marketing'].cursor()
        cursor.execute(
            """
                SELECT advert_id
                FROM eats_restapp_marketing.balance as balance
                WHERE sending_time is NULL
            """,
        )
        assert mock_communications_sender.times_called == 0

    async with taxi_eats_restapp_marketing.spawn_task(
            'update-adverts-balances',
    ):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'
