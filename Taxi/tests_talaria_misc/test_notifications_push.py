import pytest


async def post_notification_push(taxi_talaria_misc, ntf_id='ntf_id_1'):
    request = {'wind_user_id': 'wind_user_id', 'notification': {'id': ntf_id}}
    return await taxi_talaria_misc.post(
        '/talaria/v1/notifications/push',
        headers={'X-Idempotency-Token': 'some-idempotency-token'},
        json=request,
    )


async def test_notification_push_404_user_not_found(
        taxi_talaria_misc, get_users_form_db,
):
    response = await post_notification_push(taxi_talaria_misc)
    assert response.status_code == 404


@pytest.mark.pgsql('talaria_misc', files=['users.sql'])
async def test_notification_push_500_no_config(
        taxi_talaria_misc, get_users_form_db,
):
    response = await post_notification_push(taxi_talaria_misc)
    assert response.status_code == 500


@pytest.mark.pgsql('talaria_misc', files=['users.sql'])
@pytest.mark.experiments3(
    filename='config3_wind_yango_push_notifications.json',
)
async def test_notification_push_200_ntf_not_supported(
        taxi_talaria_misc, mockserver, get_users_form_db,
):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    def _mock_ucommunications(request):
        return {}

    response = await post_notification_push(
        taxi_talaria_misc, ntf_id='not_exist',
    )
    assert response.status_code == 200
    assert _mock_ucommunications.times_called == 0


@pytest.mark.pgsql('talaria_misc', files=['users.sql'])
@pytest.mark.experiments3(
    filename='config3_wind_yango_push_notifications.json',
)
@pytest.mark.parametrize(
    'ntf_id, expected_ntf_payload',
    [
        (
            'text_ntf_id_1',
            {
                'notification_title': {
                    'key': 'text_ntf_id_1_title_tanker_key',
                    'keyset': 'notify',
                },
                'notification_body': {
                    'key': 'text_ntf_id_1_subtitle_tanker_key',
                    'keyset': 'notify',
                },
            },
        ),
        (
            'deeplink_ntf_id_1',
            {
                'msg': {
                    'key': 'deeplink_ntf_id_1_subtitle_tanker_key',
                    'keyset': 'notify',
                },
                'deeplink': 'deeplink_ntf_id_1_deeplink',
            },
        ),
    ],
)
async def test_notification_push_200_ok(
        taxi_talaria_misc,
        mockserver,
        get_users_form_db,
        ntf_id,
        expected_ntf_payload,
):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    def _mock_ucommunications(request):
        assert (
            request.headers['X-Idempotency-Token'] == 'some-idempotency-token'
        )
        assert request.json == {
            'data': {'payload': expected_ntf_payload},
            'intent': (
                'text_ntf_id_1'
                if ntf_id == 'text_ntf_id_1'
                else 'deeplink_ntf_id_1'
            ),
            'user': 'yandex_user_id',
            'locale': 'en',
        }
        return {}

    response = await post_notification_push(taxi_talaria_misc, ntf_id=ntf_id)
    assert response.status_code == 200
    assert _mock_ucommunications.times_called == 1
