# pylint: disable=unused-variable
import pytest

from test_chatterbox import plugins as conftest


@pytest.mark.config(
    TVM_RULES=[{'src': 'chatterbox', 'dst': 'ivr-dispatcher'}],
    TVM_ENABLED=True,
)
@pytest.mark.parametrize(
    ('task_id', 'call_id', 'record_id', 'expected_response'),
    [
        (
            '5b2cae5cb2682a976914c2a1',
            'my_call_id',
            0,
            '/telphin_record/asd_sad',
        ),
        (
            '5b2cae5cb2682a976914c2a3',
            'my_call_id',
            0,
            '/v1/ivr-framework/get-call-record?'
            'ivr_flow_id=market_support_flow&call_record_id=123',
        ),
    ],
)
async def test_sip_record(
        cbox: conftest.CboxWrap,
        patch,
        task_id: str,
        call_id: str,
        record_id: int,
        expected_response: str,
):
    @patch('taxi.clients.tvm.TVMClient.get_ticket')
    async def get_ticket(*args, **kwargs):
        return 'Ticket 123'

    await cbox.query(
        '/v1/tasks/{}/sip_record/{}/{}'.format(task_id, call_id, record_id),
    )

    assert cbox.status == 200
    assert cbox.headers['X-Accel-Redirect'] == expected_response


@pytest.mark.parametrize(
    ('task_id', 'call_id', 'record_id', 'expected_response'),
    (
        (
            '5b2cae5cb2682a976914c2a1',
            'my_call_id',
            1,
            {
                'status': 'error',
                'message': (
                    'record_id: 1 not found in call_id: my_call_id, '
                    'task: 5b2cae5cb2682a976914c2a1'
                ),
                'code': 'not_found',
            },
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            'my_error_call_id',
            0,
            {
                'code': 'not_found',
                'message': (
                    'call_id: my_error_call_id not found in task: '
                    '5b2cae5cb2682a976914c2a1'
                ),
                'status': 'error',
            },
        ),
        (
            '5b2cae5cb2682a976914c2a2',
            'my_call_id',
            0,
            {
                'code': 'not_found',
                'message': (
                    'task 5b2cae5cb2682a976914c2a2 not found in ' 'archive'
                ),
                'status': 'error',
            },
        ),
    ),
)
async def test_sip_record_error(
        cbox: conftest.CboxWrap,
        patch_archive_yt_lookup_rows,
        task_id: str,
        call_id: str,
        record_id: int,
        expected_response: dict,
):
    patch_archive_yt_lookup_rows()

    await cbox.query(
        '/v1/tasks/{}/sip_record/{}/{}'.format(task_id, call_id, record_id),
    )

    assert cbox.status == 404
    assert cbox.body_data == expected_response
