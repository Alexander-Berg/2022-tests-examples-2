import datetime
from typing import Any
from typing import Dict

import pytest

import generated.clients.voximplant as voximplant_client

from supportai_calls.generated.stq3 import stq_context


@pytest.mark.parametrize('error_response', [True, False])
@pytest.mark.parametrize('extra_field', [True, False])
@pytest.mark.parametrize('no_required_field', [True, False])
async def test_create_call_list(
        stq3_context: stq_context.Context,
        mockserver,
        error_response,
        extra_field,
        no_required_field,
):
    json_ok: Dict[Any, Any] = {'result': True, 'list_id': 12345}
    json_error: Dict[Any, Any] = {'error': {'msg': 'some error message'}}
    if extra_field:
        json_ok['extra_field'] = 'extra_value'
        json_error['extra_field'] = 'extra_value'
        json_error['error']['extra_field'] = 'extra_value'
    if not no_required_field:
        json_error['error']['code'] = 123

    @mockserver.json_handler('voximplant/platform_api/CreateCallList')
    # pylint: disable=unused-variable
    async def handle(request):
        if error_response:
            return json_error
        return json_ok

    exception_case = no_required_field and error_response

    try:
        response = await stq3_context.clients.voximplant.post_create_call_list(
            account_id=0,
            api_key='api key',
            max_simultaneous=2,
            name='file_name',
            num_attempts=2,
            priority=0,
            rule_id=0,
            body=b'some file data',
        )
        if exception_case:
            assert False
    except voximplant_client.PostCreateCallListInvalidResponse:
        if not exception_case:
            assert False

    if exception_case:
        return

    assert response.status == 200
    body = response.body

    if error_response:
        assert body.error is not None
        assert body.result is None
        assert body.count is None
        assert body.error.code is not None
        assert body.error.msg is not None
        if extra_field:
            assert body.extra
            assert body.error.extra
            assert 'extra_field' in body.extra
            assert 'extra_field' in body.error.extra
    else:
        assert body.result is not None
        assert body.list_id is not None
        assert body.error is None
        if extra_field:
            assert body.extra
            assert 'extra_field' in body.extra


@pytest.mark.parametrize('extra_field', [True, False])
async def test_get_call_list_details(
        stq3_context: stq_context.Context, mockserver, extra_field,
) -> None:
    json_ok: Dict[Any, Any] = {
        'result': [
            {
                'list_id': 123,
                'status': 'New',
                'status_id': 0,
                'start_execution_time': '',
                'finish_execution_time': '2020-10-10 00:00:00',
                'start_at': '',
                'attempts_left': 2,
                'last_attempt': '2020-10-10 00:00:00',
                'custom_data': '{}',
            },
        ],
        'count': 1,
    }

    if extra_field:
        json_ok['extra_field'] = 'extra_value'
        json_ok['result'][0]['extra_field'] = 'extra_value'

    @mockserver.json_handler('voximplant/platform_api/GetCallListDetails')
    # pylint: disable=unused-variable
    async def handle(request):
        return json_ok

    response = await stq3_context.clients.voximplant.get_call_list_details(
        account_id=0, api_key='', list_id=0, output='json',
    )

    assert response.status == 200
    body = response.body
    assert body.result is not None
    assert body.count is not None
    assert body.result[0].start_execution_time == ''
    assert body.result[0].finish_execution_time == datetime.datetime(
        2020, 10, 10, 0, 0, 0,
    )
    if extra_field:
        assert body.extra
        assert 'extra_field' in body.extra
        assert body.result[0].extra
        assert 'extra_field' in body.result[0].extra


@pytest.mark.parametrize('extra_field', [True, False])
async def test_stop_call_list(
        stq3_context: stq_context.Context, mockserver, extra_field,
) -> None:
    json_ok = {'result': True, 'msg': 'Tasks cancelled.'}

    @mockserver.json_handler('voximplant/platform_api/StopCallListProcessing')
    # pylint: disable=unused-variable
    async def handle(request):
        return json_ok

    if extra_field:
        json_ok['extra_field'] = 'extra_value'

    response = (
        await stq3_context.clients.voximplant.post_stop_call_list_processing(  # noqa
            account_id=0, api_key='', list_id=0,
        )
    )

    assert response.status == 200
    body = response.body

    assert body.result is not None
    assert body.msg is not None
    assert body.error is None
    if extra_field:
        assert body.extra
        assert 'extra_field' in body.extra
