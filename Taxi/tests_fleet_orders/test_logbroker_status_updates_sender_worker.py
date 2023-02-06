import dateutil.parser
import pytest

from tests_fleet_orders import utils


JOB_NAME = 'logbroker-status-updates-sender'

LOGBROKER_MESSAGES = (
    '{"park_id":"7f74df331eb04ad78bc2ff25ff88a8f2",'
    '"order_id":"f7cf24e6b13dde30b3b272f7a2c8478f",'
    '"order_created_at":"2022-02-24T10:09:06.852+00:00",'
    '"status":"completed_others",'
    '"tariff_class":"econom",'
    '"event_index":9.0,'
    '"event_time":"2022-02-25T09:56:31.191+00:00"}',
    '{"park_id":"c5cdea22ad6b4e4da8f3fdbd4bddc2e7",'
    '"order_id":"1ba9a26ae45c2fcabfa11aee9dfd3813",'
    '"order_created_at":"2022-02-25T13:28:38.458+00:00",'
    '"status":"completed_own",'
    '"tariff_class":"econom",'
    '"event_index":8.0,'
    '"event_time":"2022-02-25T13:45:20.359+00:00"}',
    '{"park_id":"c5cdea22ad6b4e4da8f3fdbd4bddc2e7",'
    '"order_id":"10eada445af2288c9d75742fee1c50c8",'
    '"order_created_at":"2022-02-25T14:07:40.961+00:00",'
    '"status":"completed_own",'
    '"tariff_class":"econom",'
    '"event_index":8.0,'
    '"event_time":"2022-02-25T14:11:52.884+00:00"}',
    '{"park_id":"c5cdea22ad6b4e4da8f3fdbd4bddc2e7",'
    '"order_id":"4972987590a9c7dc9ae6de57f81c79d3",'
    '"order_created_at":"2022-02-25T16:05:34.647+00:00",'
    '"status":"canceled_by_platform",'
    '"tariff_class":"econom",'
    '"event_index":8.0,'
    '"event_time":"2022-02-25T17:11:09.088+00:00"}',
    '{"park_id":"c5cdea22ad6b4e4da8f3fdbd4bddc2e7",'
    '"order_id":"6d78eb5520d6cc01b5eae78c4d238243",'
    '"order_created_at":"2022-02-25T14:45:35.018+00:00",'
    '"status":"completed_own",'
    '"tariff_class":"business",'
    '"event_index":9.0,'
    '"event_time":"2022-02-26T14:39:33.404+00:00"}',
    '{"park_id":"c5cdea22ad6b4e4da8f3fdbd4bddc2e7",'
    '"order_id":"5c4d8a5bf62bcaa58b0d03de8e2c7bb3",'
    '"order_created_at":"2022-02-25T17:10:47.61+00:00",'
    '"status":"completed_own",'
    '"tariff_class":"econom",'
    '"event_index":9.0,'
    '"event_time":"2022-02-26T15:30:03.487+00:00"}',
    '{"park_id":"c5cdea22ad6b4e4da8f3fdbd4bddc2e7",'
    '"order_id":"3998d7c8ed411d49bf1d19f35b1735d4",'
    '"order_created_at":"2022-02-25T17:08:55.68+00:00",'
    '"status":"completed_own",'
    '"tariff_class":"econom",'
    '"event_index":9.0,'
    '"event_time":"2022-02-26T15:32:09.684+00:00"}',
    '{"park_id":"c5cdea22ad6b4e4da8f3fdbd4bddc2e7",'
    '"order_id":"82ced154f4ed113cb45b79c9258a7f74",'
    '"order_created_at":"2022-02-25T15:29:30.31+00:00",'
    '"status":"completed_own",'
    '"tariff_class":"econom",'
    '"event_index":9.0,'
    '"event_time":"2022-02-26T15:33:38.424+00:00"}',
    '{"park_id":"c5cdea22ad6b4e4da8f3fdbd4bddc2e7",'
    '"order_id":"7bc879bda461259b8e9a50449bf14fca",'
    '"order_created_at":"2022-02-25T15:26:46.093+00:00",'
    '"status":"completed_own",'
    '"tariff_class":"econom",'
    '"event_index":9.0,'
    '"event_time":"2022-02-26T15:34:14.925+00:00"}',
)


def get_job_state(cursor):
    cursor.execute(
        'SELECT last_sent_seq_no '
        'FROM fleet.logbroker_status_updates_sender_state;',
    )
    return utils.pg_response_to_dict(cursor)


@pytest.mark.config(
    FLEET_ORDERS_LOGBROKER_STATUS_SENDER_SETTINGS={
        'job_period_seconds': 60,
        'limit': 5,
        'batch_size': 2,
        'enabled': True,
    },
)
@pytest.mark.pgsql('fleet_orders', files=['orders.sql'])
async def test_job(testpoint, pgsql, taxi_fleet_orders, mocked_time):
    @testpoint('logbroker-status-updates-sender-finished')
    def handle_finished(arg):
        pass

    @testpoint('logbroker_publish')
    def logbroker_commit(data):
        assert (
            data['data'] == LOGBROKER_MESSAGES[logbroker_commit.times_called]
        )

    cursor = pgsql['fleet_orders'].cursor()

    assert get_job_state(cursor) == [{'last_sent_seq_no': 0}]

    mocked_time.set(dateutil.parser.parse('2022-02-26T00:00:00'))
    await taxi_fleet_orders.invalidate_caches()

    await taxi_fleet_orders.run_distlock_task(JOB_NAME)

    result = handle_finished.next_call()

    assert get_job_state(cursor) == [
        {
            # order with update_seq_no == 1 is in the assigned state
            'last_sent_seq_no': 6,
        },
    ]
    assert result == {
        'arg': [
            '7f74df331eb04ad78bc2ff25ff88a8f2_'
            'f7cf24e6b13dde30b3b272f7a2c8478f',
            'c5cdea22ad6b4e4da8f3fdbd4bddc2e7_'
            '1ba9a26ae45c2fcabfa11aee9dfd3813',
            'c5cdea22ad6b4e4da8f3fdbd4bddc2e7_'
            '10eada445af2288c9d75742fee1c50c8',
            'c5cdea22ad6b4e4da8f3fdbd4bddc2e7_'
            '4972987590a9c7dc9ae6de57f81c79d3',
            'c5cdea22ad6b4e4da8f3fdbd4bddc2e7_'
            '6d78eb5520d6cc01b5eae78c4d238243',
        ],
    }
    assert logbroker_commit.times_called == 5

    mocked_time.set(dateutil.parser.parse('2022-02-28T00:00:00'))
    await taxi_fleet_orders.invalidate_caches()

    await taxi_fleet_orders.run_distlock_task(JOB_NAME)

    result = handle_finished.next_call()

    assert get_job_state(cursor) == [{'last_sent_seq_no': 10}]
    assert result == {
        'arg': [
            'c5cdea22ad6b4e4da8f3fdbd4bddc2e7_'
            '5c4d8a5bf62bcaa58b0d03de8e2c7bb3',
            'c5cdea22ad6b4e4da8f3fdbd4bddc2e7_'
            '3998d7c8ed411d49bf1d19f35b1735d4',
            'c5cdea22ad6b4e4da8f3fdbd4bddc2e7_'
            '82ced154f4ed113cb45b79c9258a7f74',
            'c5cdea22ad6b4e4da8f3fdbd4bddc2e7_'
            '7bc879bda461259b8e9a50449bf14fca',
        ],
    }
    assert logbroker_commit.times_called == 9
