import pytest


@pytest.mark.parametrize('failed', [True, False])
async def test_set_card_label(stq_runner, mockserver, failed):
    @mockserver.json_handler('/trust/card-id/labels')
    def _handle_label(request):
        assert request.headers['X-Uid'] == 'owner-uid'
        assert (
            request.headers['X-Service-Token']
            == 'taxifee_8c7078d6b3334e03c1b4005b02da30f4'
        )
        assert request.json == {'label': 'card-label'}

        if failed:
            response = mockserver.make_response(status=500)
        else:
            response = {'status': 'success'}
        return response

    await stq_runner.cardstorage_set_card_label.call(
        task_id='task-id',
        args=[],
        kwargs={
            'card_id': 'card-id',
            'owner_uid': 'owner-uid',
            'service_type': 'card',
            'label': 'card-label',
        },
        expect_fail=failed,
    )
    assert _handle_label.times_called >= 1


async def test_set_card_label__should_not_retry_unbound_cards(
        stq_runner, mockserver,
):
    @mockserver.json_handler('/trust/card-id/labels')
    def _handle_label(request):
        assert request.headers['X-Uid'] == 'owner-uid'
        assert (
            request.headers['X-Service-Token']
            == 'taxifee_8c7078d6b3334e03c1b4005b02da30f4'
        )
        assert request.json == {'label': 'card-label'}
        response = mockserver.make_response(
            status=400, json={'status_code': 'invalid_card_id'},
        )
        return response

    await stq_runner.cardstorage_set_card_label.call(
        task_id='task-id',
        args=[],
        kwargs={
            'card_id': 'card-id',
            'owner_uid': 'owner-uid',
            'service_type': 'card',
            'label': 'card-label',
        },
        expect_fail=False,
    )
    assert _handle_label.times_called == 1
