from taxi_corp.stq import registration_notices_tmp


async def test_registration_notices(taxi_corp_app_stq, patch):
    @patch(
        'taxi_corp.clients.notices_client.'
        'NoticesClient.enqueue_client_poll_notices',
    )
    async def _enqueue_client_poll_notices(client_id, on_create):
        pass

    @patch(
        'taxi_corp.clients.notices_client.'
        'NoticesClient.enqueue_client_onboarding_notices',
    )
    async def _enqueue_client_onboarding_notices(client_id):
        pass

    client_id = 'test_client_id'

    await registration_notices_tmp(taxi_corp_app_stq, client_id)

    assert _enqueue_client_poll_notices.calls == [
        {'on_create': True, 'client_id': 'test_client_id'},
    ]
    assert _enqueue_client_onboarding_notices.calls == [
        {'client_id': 'test_client_id'},
    ]
