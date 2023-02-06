import pytest

SERVICE_KEY_SET = 'eats-performer-subventions'


def create_driver_profiles_response(eats_id):
    return {
        'courier_by_eats_id': [
            {
                'eats_courier_id': eats_id,
                'profiles': [
                    {
                        'data': {
                            'work_status': 'working',
                            'created_date': '2020-08-25T17:17:07.543',
                        },
                        'park_driver_profile_id': 'parkid_driverid1',
                    },
                ],
            },
        ],
    }


async def get_notification_status(cursor, notification_id):
    cursor.execute(
        """
SELECT
    status
FROM eats_performer_subventions.performer_subvention_notifications psn
WHERE psn.id = '{}'
        """.format(
            notification_id,
        ),
    )

    return cursor.fetchone()['status']


@pytest.fixture(name='mock_driver_app_profile')
def _mock_driver_app_profile(mockserver):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_driver_app_profile_retrieve(request):
        return mockserver.make_response(
            status=200,
            json={
                'profiles': [
                    {
                        'park_driver_profile_id': 'parkid_driverid1',
                        'data': {'locale': 'ru'},
                    },
                ],
            },
        )

    return _mock_driver_app_profile_retrieve


@pytest.mark.translations()
@pytest.mark.pgsql(
    'eats_performer_subventions',
    files=['subvention_goals_chats_notifier.sql'],
)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize(
    'notification_id,retrieve_by_eats_id_response',
    [
        pytest.param(
            '999029c4-291b-4c5e-a88e-803bed1444ac',
            create_driver_profiles_response('42'),
            id='welcome message',
        ),
        pytest.param(
            '11111111-1111-1111-1111-111111111111',
            create_driver_profiles_response('42'),
            id='daily welcome message',
        ),
        pytest.param(
            'db7c792e-e842-4de8-8a17-c56d2f51f90a',
            create_driver_profiles_response('42'),
            id='check state message',
        ),
        pytest.param(
            '2acff7c1-f719-4130-bc5c-624499485ebc',
            create_driver_profiles_response('42'),
            id='finalize message',
        ),
        pytest.param(
            '22111111-1111-1111-1111-111111111122',
            create_driver_profiles_response('42'),
            id='daily finalize message',
        ),
    ],
)
async def test_send_pro_notifications(
        pgsql,
        testpoint,
        mockserver,
        mock_driver_app_profile,
        stq_runner,
        load_json,
        notification_id,
        retrieve_by_eats_id_response,
):
    @mockserver.json_handler(
        '/driver-profiles/v1/courier/profiles/retrieve_by_eats_id',
    )
    def _driver_profiles_retrieve_by_eats_id(request):
        return retrieve_by_eats_id_response

    @mockserver.json_handler('driver-wall/internal/driver-wall/v1/add')
    def _driver_wall_add(request):
        assert request.json == load_json(
            'driver_wall_request_{0}.json'.format(notification_id),
        )
        assert request.headers['X-Idempotency-Token'] == 'eatscour-{}'.format(
            notification_id,
        )
        return mockserver.make_response(status=200, json={'id': '1'})

    @mockserver.json_handler('/client-notify/v2/push')
    def _client_notify_push(request):
        assert request.json == load_json(
            'client_notify_request_{0}.json'.format(notification_id),
        )
        assert request.headers[
            'X-Idempotency-Token'
        ] == 'eatscoursubv-{}'.format(notification_id)
        return mockserver.make_response(
            json={'notification_id': '1221'}, status=200,
        )

    @testpoint('chats_notification_sent')
    def chats_notification_sent(data):
        pass

    await stq_runner.eats_performer_subventions_send_pro_notifications.call(
        task_id='dummy_task', kwargs={'notification_id': notification_id},
    )

    assert chats_notification_sent.times_called == 1

    cursor = pgsql['eats_performer_subventions'].dict_cursor()
    assert await get_notification_status(cursor, notification_id) == 'finished'


@pytest.mark.translations()
@pytest.mark.pgsql(
    'eats_performer_subventions',
    files=['subvention_goals_chats_notifier.sql'],
)
@pytest.mark.experiments3(filename='experiments3.json')
async def test_send_pro_notifications_too_many_reschedules(
        testpoint, stq_runner,
):
    @testpoint('chats_notification_sent')
    def chats_notification_sent(data):
        pass

    @testpoint('send_to_chats_too_many_reschedule_count')
    def too_many_reschedule_count(data):
        pass

    notification_id = '2acff7c1-f719-4130-bc5c-624499485eb1'
    await stq_runner.eats_performer_subventions_send_pro_notifications.call(
        task_id='dummy_task',
        kwargs={'notification_id': notification_id},
        reschedule_counter=100,
    )

    assert chats_notification_sent.times_called == 0
    assert too_many_reschedule_count.times_called == 1


@pytest.mark.translations()
@pytest.mark.pgsql(
    'eats_performer_subventions',
    files=['subvention_goals_chats_notifier.sql'],
)
@pytest.mark.experiments3(filename='experiments3.json')
async def test_send_cancelled_pro_notifications(testpoint, stq_runner, pgsql):
    @testpoint('chats_notification_sent')
    def chats_notification_sent(data):
        pass

    @testpoint('send_to_chats_too_many_reschedule_count')
    def too_many_reschedule_count(data):
        pass

    @testpoint('send_to_chats_rescheduled')
    def send_to_chats_rescheduled(data):
        pass

    notification_id = '88300a7d-bbbd-4c8d-a067-9e90d91d71ac'
    await stq_runner.eats_performer_subventions_send_pro_notifications.call(
        task_id='dummy_task', kwargs={'notification_id': notification_id},
    )

    assert chats_notification_sent.times_called == 0
    assert too_many_reschedule_count.times_called == 0
    assert send_to_chats_rescheduled.times_called == 0

    cursor = pgsql['eats_performer_subventions'].dict_cursor()
    assert (
        await get_notification_status(cursor, notification_id) == 'cancelled'
    )
