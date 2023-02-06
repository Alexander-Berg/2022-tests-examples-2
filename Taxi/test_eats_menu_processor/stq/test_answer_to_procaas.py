from integration_procaas.internal import (  # noqa: IS001, pylint: disable=C5521
    ErrorCodes,
    Phases,
)

from eats_menu_processor import utils
from eats_menu_processor.stq import answer_to_procaas


async def test_answer_to_procaas_success(
        stq3_context, mock_processing, mockserver,
):

    item_id = '123456789'
    s3_link = '/s3/bucket/file.json'
    log_uuid = 'log_uuid__1'

    @mock_processing(f'/v1/eda/integration_menu_processing/create-event')
    def _procaas_create_event(request):
        assert request.json == {
            's3_link': s3_link,
            'phase': Phases.PROCESSED.value,
            'log_uuid': log_uuid,
        }
        assert request.headers[
            'X-Idempotency-Token'
        ] == utils.get_idempotency_token_success(item_id)
        assert request.query['item_id'] == item_id
        return {'event_id': 'event_id__1'}

    await answer_to_procaas.task(
        stq3_context,
        data={'s3_link': s3_link, 'log_uuid': log_uuid},
        phase=Phases.PROCESSED.value,
        item_id=item_id,
    )


async def test_answer_to_procaas_fallback(
        stq3_context, mock_processing, mockserver,
):

    item_id = '123456789'
    error_text = 'error text'
    log_uuid = 'log_uuid__1'
    exception_message = 'exception_message'

    @mock_processing(f'/v1/eda/integration_menu_processing/create-event')
    def _procaas_create_event(request):
        assert request.json == {
            'error_code': ErrorCodes.SERVICE_ERROR.value,
            'error_text': error_text,
            'phase': Phases.FALLBACK.value,
            'log_uuid': log_uuid,
            'exception_message': exception_message,
        }
        assert request.headers[
            'X-Idempotency-Token'
        ] == utils.get_idempotency_token_fallback(item_id)
        assert request.query['item_id'] == item_id
        return {'event_id': 'event_id__1'}

    await answer_to_procaas.task(
        stq3_context,
        data={
            'error_code': ErrorCodes.SERVICE_ERROR.value,
            'error_text': error_text,
            'log_uuid': log_uuid,
            'exception_message': exception_message,
        },
        phase=Phases.FALLBACK.value,
        item_id=item_id,
    )
