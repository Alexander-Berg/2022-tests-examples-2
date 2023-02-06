# pylint: disable=import-only-modules

from dateutil.parser import parse  # noqa
import pytest


DIGEST_SENDER_CONFIG = {
    'enabled': True,
    'period': 10,
    'chunk_size': 5,
    'send_cooldown': 120,
    'default_send_time': '10:00',
}


def make_digest_sender_config(**kwargs):
    res = DIGEST_SENDER_CONFIG.copy()
    res.update(dict(**kwargs))
    return res


def check_sent_at(pgsql, place_ids, dttm):
    cursor = pgsql['eats_restapp_communications'].cursor()
    cursor.execute(
        'SELECT distinct(sent_at) '
        'FROM eats_restapp_communications.place_digest_send_schedule '
        'WHERE place_id = ANY(%s)',
        (place_ids,),
    )
    rows = list(cursor)
    assert len(rows) == 1
    assert rows[0] == (dttm,)


@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_DIGEST_SENDER=make_digest_sender_config(
        enabled=False,
    ),
)
async def test_digest_sender_disabled(
        taxi_eats_restapp_communications, testpoint,
):
    @testpoint('digest-sender-finished')
    async def handle_finished(arg):
        pass

    async with taxi_eats_restapp_communications.spawn_task('digest-sender'):
        await handle_finished.wait_call()


@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_DIGEST_SENDER=make_digest_sender_config(),
)
async def test_digest_sender_empty_schedule(
        taxi_eats_restapp_communications, testpoint,
):
    @testpoint('digest-sender-finished')
    async def handle_finished(arg):
        pass

    async with taxi_eats_restapp_communications.spawn_task('digest-sender'):
        await handle_finished.wait_call()


@pytest.mark.now('2022-05-01T10:00:00+0300')
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_DIGEST_SENDER=make_digest_sender_config(),
)
@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_already_sent.sql',),
)
async def test_digest_sender_skip_already_sent(
        pgsql, taxi_eats_restapp_communications, testpoint,
):
    @testpoint('digest-sender-finished')
    async def handle_finished(arg):
        check_sent_at(pgsql, [11, 22, 33], parse('2022-05-01 09:00:00+03:00'))

    async with taxi_eats_restapp_communications.spawn_task('digest-sender'):
        await handle_finished.wait_call()


@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_DIGEST_SENDER=make_digest_sender_config(),
)
@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_inactive_schedule.sql',),
)
async def test_digest_sender_skip_inactive(
        pgsql, taxi_eats_restapp_communications, testpoint,
):
    @testpoint('digest-sender-finished')
    async def handle_finished(arg):
        check_sent_at(pgsql, [11, 22, 33], None)

    async with taxi_eats_restapp_communications.spawn_task('digest-sender'):
        await handle_finished.wait_call()


@pytest.mark.now('2022-05-01T09:00:00+0300')
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_DIGEST_SENDER=make_digest_sender_config(),
)
@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_active_schedule.sql',),
)
async def test_digest_sender_skip_places_to_send_later(
        pgsql, taxi_eats_restapp_communications, testpoint,
):
    @testpoint('digest-sender-finished')
    async def handle_finished(arg):
        check_sent_at(pgsql, [11, 22, 33], None)

    async with taxi_eats_restapp_communications.spawn_task('digest-sender'):
        await handle_finished.wait_call()


@pytest.mark.now('2022-05-01T11:00:00+0300')
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_DIGEST_SENDER=make_digest_sender_config(
        send_window=30,
    ),
)
@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_active_schedule.sql',),
)
async def test_digest_sender_skip_places_not_in_window(
        pgsql, taxi_eats_restapp_communications, testpoint,
):
    @testpoint('digest-sender-finished')
    async def handle_finished(arg):
        check_sent_at(pgsql, [11, 22, 33], None)

    async with taxi_eats_restapp_communications.spawn_task('digest-sender'):
        await handle_finished.wait_call()


@pytest.mark.now('2022-05-01T10:00:00+0300')
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_DIGEST_SENDER=make_digest_sender_config(),
)
@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_active_schedule.sql',),
)
async def test_digest_sender_skip_unsubscribed(
        pgsql,
        taxi_eats_restapp_communications,
        testpoint,
        mockserver,
        mocked_time,
):
    @mockserver.json_handler(
        '/eats-place-subscriptions/internal/'
        'eats-place-subscriptions/v1/feature/enabled-for-places',
    )
    def _mock_subscriptions(request):
        req = request.json
        assert req['feature'] == 'boss_bot'
        assert sorted(req['place_ids']) == [11, 22, 33]
        resp = {
            'feature': 'boss_bot',
            'places': {
                'with_enabled_feature': [],
                'with_disabled_feature': [11, 22, 33],
            },
        }
        return mockserver.make_response(status=200, json=resp)

    @testpoint('digest-sender-finished')
    async def handle_finished(arg):
        check_sent_at(pgsql, [11, 22, 33], parse('2022-05-01 10:00:00+03:00'))

    async with taxi_eats_restapp_communications.spawn_task('digest-sender'):
        await handle_finished.wait_call()

    assert _mock_subscriptions.times_called == 1


@pytest.mark.now('2022-05-01T10:00:00+0300')
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_DIGEST_SENDER=make_digest_sender_config(
        chunk_size=1,
    ),
)
@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_active_schedule.sql',),
)
async def test_digest_sender_multiple_chunk(
        pgsql,
        taxi_eats_restapp_communications,
        testpoint,
        mockserver,
        mocked_time,
):
    @mockserver.json_handler(
        '/eats-place-subscriptions/internal/'
        'eats-place-subscriptions/v1/feature/enabled-for-places',
    )
    def _mock_subscriptions(request):
        resp = {
            'feature': 'boss_bot',
            'places': {
                'with_enabled_feature': [],
                'with_disabled_feature': [],
            },
        }
        return mockserver.make_response(status=200, json=resp)

    @testpoint('digest-sender-finished')
    async def handle_finished(arg):
        check_sent_at(pgsql, [11, 22, 33], parse('2022-05-01 10:00:00+03:00'))

    async with taxi_eats_restapp_communications.spawn_task('digest-sender'):
        await handle_finished.wait_call()

    assert _mock_subscriptions.times_called == 3


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_different_timezones.sql',),
)
@pytest.mark.parametrize(
    'mock_now, place_ids',
    [
        pytest.param(
            parse('2022-05-01T10:00:00+0300'),
            [11, 22, 33],
            marks=pytest.mark.config(
                EATS_RESTAPP_COMMUNICATIONS_DIGEST_SENDER=(
                    make_digest_sender_config()
                ),
            ),
            id='all places, large window',
        ),
        pytest.param(
            parse('2022-05-01T10:00:00+0400'),
            [22, 33],
            marks=pytest.mark.config(
                EATS_RESTAPP_COMMUNICATIONS_DIGEST_SENDER=(
                    make_digest_sender_config()
                ),
            ),
            id='some places, large window',
        ),
        pytest.param(
            parse('2022-05-01T10:00:00+0500'),
            [33],
            marks=pytest.mark.config(
                EATS_RESTAPP_COMMUNICATIONS_DIGEST_SENDER=(
                    make_digest_sender_config()
                ),
            ),
            id='one place, large window',
        ),
        pytest.param(
            parse('2022-05-01T10:00:00+0300'),
            [11],
            marks=pytest.mark.config(
                EATS_RESTAPP_COMMUNICATIONS_DIGEST_SENDER=(
                    make_digest_sender_config(send_window=30)
                ),
            ),
            id='all places, smaill window',
        ),
        pytest.param(
            parse('2022-05-01T10:00:00+0400'),
            [22],
            marks=pytest.mark.config(
                EATS_RESTAPP_COMMUNICATIONS_DIGEST_SENDER=(
                    make_digest_sender_config(send_window=30)
                ),
            ),
            id='some places, small window',
        ),
        pytest.param(
            parse('2022-05-01T10:00:00+0500'),
            [33],
            marks=pytest.mark.config(
                EATS_RESTAPP_COMMUNICATIONS_DIGEST_SENDER=(
                    make_digest_sender_config(send_window=30)
                ),
            ),
            id='one place, small window',
        ),
    ],
)
async def test_digest_sender_different_timezones(
        pgsql,
        taxi_eats_restapp_communications,
        testpoint,
        mockserver,
        mocked_time,
        mock_now,
        place_ids,
):
    mocked_time.set(mock_now)
    await taxi_eats_restapp_communications.invalidate_caches()

    @mockserver.json_handler(
        '/eats-place-subscriptions/internal/'
        'eats-place-subscriptions/v1/feature/enabled-for-places',
    )
    def _mock_subscriptions(request):
        req = request.json
        assert req['feature'] == 'boss_bot'
        assert sorted(req['place_ids']) == place_ids
        resp = {
            'feature': 'boss_bot',
            'places': {
                'with_enabled_feature': [],
                'with_disabled_feature': [],
            },
        }
        return mockserver.make_response(status=200, json=resp)

    @testpoint('digest-sender-finished')
    async def handle_finished(arg):
        check_sent_at(pgsql, place_ids, mock_now)

    async with taxi_eats_restapp_communications.spawn_task('digest-sender'):
        await handle_finished.wait_call()

    assert _mock_subscriptions.times_called == 1


@pytest.mark.now('2022-05-01T10:00:00+0300')
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_DIGEST_SENDER=make_digest_sender_config(),
)
@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_custom_schedule.sql',),
)
async def test_digest_sender_custom_schedule(
        pgsql,
        taxi_eats_restapp_communications,
        testpoint,
        mockserver,
        mocked_time,
):
    @mockserver.json_handler(
        '/eats-place-subscriptions/internal/'
        'eats-place-subscriptions/v1/feature/enabled-for-places',
    )
    def _mock_subscriptions(request):
        req = request.json
        assert req['feature'] == 'boss_bot'
        assert sorted(req['place_ids']) == [11, 22, 33]
        resp = {
            'feature': 'boss_bot',
            'places': {
                'with_enabled_feature': [],
                'with_disabled_feature': [11, 22, 33],
            },
        }
        return mockserver.make_response(status=200, json=resp)

    @testpoint('digest-sender-finished')
    async def handle_finished(arg):
        check_sent_at(pgsql, [11, 22, 33], parse('2022-05-01 10:00:00+03:00'))

    async with taxi_eats_restapp_communications.spawn_task('digest-sender'):
        await handle_finished.wait_call()

    assert _mock_subscriptions.times_called == 1


@pytest.mark.now('2022-05-01T10:00:00+0300')
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_DIGEST_SENDER=make_digest_sender_config(),
)
@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_active_schedule.sql',),
)
async def test_digest_sender_success(
        pgsql,
        taxi_eats_restapp_communications,
        stq,
        testpoint,
        mockserver,
        mocked_time,
        load_json,
):
    @mockserver.json_handler(
        '/eats-place-subscriptions/internal/'
        'eats-place-subscriptions/v1/feature/enabled-for-places',
    )
    def _mock_subscriptions(request):
        req = request.json
        assert req['feature'] == 'boss_bot'
        assert sorted(req['place_ids']) == [11, 22, 33]
        resp = {
            'feature': 'boss_bot',
            'places': {
                'with_enabled_feature': [11, 22, 33],
                'with_disabled_feature': [],
            },
        }
        return mockserver.make_response(status=200, json=resp)

    expected_reports_response = load_json('eats_report_storage_response.json')

    @mockserver.json_handler(
        '/eats-report-storage/internal' '/place-metrics/v1/digests',
    )
    def _mock_reports(request):
        req = request.json
        assert req == {
            'digests': [
                {'place_id': 11, 'period_date': '2022-04-30'},
                {'place_id': 22, 'period_date': '2022-04-30'},
                {'place_id': 33, 'period_date': '2022-04-30'},
            ],
        }
        return mockserver.make_response(
            status=200, json=expected_reports_response,
        )

    @testpoint('digest-sender-finished')
    async def handle_finished(arg):
        check_sent_at(pgsql, [11, 22, 33], parse('2022-05-01 10:00:00+03:00'))

    async with taxi_eats_restapp_communications.spawn_task('digest-sender'):
        await handle_finished.wait_call()

    assert _mock_subscriptions.times_called == 1
    assert _mock_reports.times_called == 1

    assert stq.eats_restapp_communications_event_sender.times_called == 2
    cursor = pgsql['eats_restapp_communications'].cursor()

    arg = stq.eats_restapp_communications_event_sender.next_call()
    assert arg['queue'] == 'eats_restapp_communications_event_sender'
    cursor.execute(
        """
        SELECT event_type, event_mode, recipients, data
        FROM eats_restapp_communications.send_event_data
        WHERE event_id = %s
        """,
        (arg['id'],),
    )
    res = cursor.fetchall()
    assert len(res) == 1
    assert res[0][0] == 'daily-digests'
    assert res[0][1] == 'asap'
    assert res[0][2]['recipients'] == {'place_ids': [11]}
    assert res[0][3]['place_name'] == 'place 1'

    arg = stq.eats_restapp_communications_event_sender.next_call()
    assert arg['queue'] == 'eats_restapp_communications_event_sender'
    cursor.execute(
        """
        SELECT event_type, event_mode, recipients, data
        FROM eats_restapp_communications.send_event_data
        WHERE event_id = %s
        """,
        (arg['id'],),
    )
    res = cursor.fetchall()
    assert len(res) == 1
    assert res[0][0] == 'daily-digests-inactive'
    assert res[0][1] == 'asap'
    assert res[0][2]['recipients'] == {'place_ids': [33]}
    assert res[0][3]['place_name'] == 'place 3'
