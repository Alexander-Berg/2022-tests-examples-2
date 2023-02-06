import decimal
import enum
from typing import Optional

import pytest

from generated.clients import check as check_module
from taxi.clients import mds_s3
from taxi.stq import async_worker_ng

from iiko_integration import const
from iiko_integration.stq import render_receipt


@pytest.fixture
def mock_receipt_services(mock_check, mockserver, patch):
    def _mock(
            service_problem: Optional[ProblemType] = None,
            expected_pdf_request: Optional[dict] = None,
            document_id: Optional[str] = None,
    ):
        @mock_check('/pdf')
        def _mock_check(request):
            if service_problem == ProblemType.CHECK_SERVICE:
                return mockserver.make_response(status=500)
            if expected_pdf_request:
                assert request.json == expected_pdf_request
            return mockserver.make_response(
                response=b'pdf receipt', content_type='application/pdf',
            )

        @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
        async def _mds_upload(
                key, body: bytes, content_type: str, *args, **kwargs,
        ):
            if service_problem == ProblemType.MDS_PROBLEM:
                raise MdsExeption
            if document_id:
                assert key == document_id
            assert body == b'pdf receipt'
            assert content_type == 'application/pdf'
            return mds_s3.S3Object(Key='', ETag=None)

        return {'check_mock': _mock_check, 'mds_mock': _mds_upload}

    return _mock


class ProblemType(enum.Enum):
    CHECK_SERVICE = 'check_service_problem'
    MDS_PROBLEM = 'mds_problem'


class MdsExeption(Exception):
    pass


def _get_receipt_from_pg(pgsql, document_id: str) -> dict:
    with pgsql['iiko_integration'].cursor() as cursor:
        cursor.execute(
            f'SELECT document_id, order_version, order_id, type, sum, url '
            f'FROM iiko_integration.receipts '
            f'WHERE document_id=\'{document_id}\'',
        )
        assert cursor.rowcount == 1
        fields = cursor.fetchone()
        return {
            'document_id': fields[0],
            'order_version': fields[1],
            'order_id': fields[2],
            'type': fields[3],
            'sum': fields[4],
            'url': fields[5],
        }


@pytest.mark.config(
    IIKO_INTEGRATION_SEND_RECEIPT_NOTIFICATION={
        'enabled': True,
        'intent': 'go_qr_send_receipt',
        'tanker_key': 'go.qr.send_receipt',
        'deeplink': 'yandextaxi://cashback',
    },
)
@pytest.mark.parametrize(
    'document_id',
    (
        pytest.param('document_1', id='Not receipt in db'),
        pytest.param('document_2', id='Receipt already exists'),
    ),
)
async def test_successful(
        stq3_context,
        mock_receipt_services,  # pylint: disable=redefined-outer-name
        load_json,
        pgsql,
        mockserver,
        mock_stats,
        document_id: str,
):
    @mockserver.json_handler('/ucommunications/user/sms/send')
    def _ucommunications_mock(req):
        assert 'X-Idempotency-Token' in req.headers
        assert req.json == {
            'intent': 'go_qr_send_receipt',
            'locale': const.DEFAULT_LOCALE,
            'text': {'key': 'go.qr.send_receipt', 'keyset': 'notify'},
            'user_id': 'user1',
            'notification': {'deeplink': 'yandextaxi://cashback'},
        }
        return {'code': 'code', 'message': 'message'}

    expected_pdf_request = load_json('check_expected_request.json')
    mocks = mock_receipt_services(
        expected_pdf_request=expected_pdf_request, document_id=document_id,
    )
    metric_counter = mock_stats('order.events.successful_render_receipt')

    await render_receipt.task(
        context=stq3_context,
        task_info=async_worker_ng.TaskInfo('000', 0, 0, 'render_receipt'),
        document_id=document_id,
        order_id='000',
        receipt_type='payment',
        order_version=0,
    )
    assert metric_counter.count == 1
    assert mocks['check_mock'].times_called == 1
    mds_calls_count = len(mocks['mds_mock'].calls)
    assert mds_calls_count == 1

    if document_id == 'document_2':
        return

    receipt = _get_receipt_from_pg(pgsql, document_id)
    assert receipt['document_id'] == document_id
    assert receipt['order_version'] == 0
    assert receipt['order_id'] == '000'
    assert receipt['type'] == 'payment'
    assert receipt['sum'] == decimal.Decimal(219)
    assert (
        receipt['url']
        == f'https://taxi-iiko-integration.s3.yandex.net/{document_id}'
    )
    assert _ucommunications_mock.times_called == 1


@pytest.mark.parametrize(
    'problem_type', (ProblemType.CHECK_SERVICE, ProblemType.MDS_PROBLEM),
)
async def test_failes(
        stq3_context,
        mock_receipt_services,  # pylint: disable=redefined-outer-name
        mock_stats,
        problem_type: ProblemType,
):
    mocks = mock_receipt_services(service_problem=problem_type)
    metric_counter = mock_stats('order.events.successful_render_receipt')

    try:
        await render_receipt.task(
            context=stq3_context,
            task_info=async_worker_ng.TaskInfo('000', 0, 0, 'render_receipt'),
            document_id='document_id',
            order_id='000',
            receipt_type='payment',
            order_version=0,
        )
    except check_module.ClientException:
        mds_calls_count = len(mocks['mds_mock'].calls)
        assert mds_calls_count == 0
        assert problem_type == ProblemType.CHECK_SERVICE
        assert metric_counter.count == 0
        return
    except MdsExeption:
        assert problem_type == ProblemType.MDS_PROBLEM
        assert metric_counter.count == 0
        return
    assert False  # Task must have failed
