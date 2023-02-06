import http

import psycopg2.extras
import pytest

from taxi.stq import async_worker_ng as async_worker
from testsuite.utils import callinfo

from eats_integration_offline_orders.internal import constants
from eats_integration_offline_orders.stq import ei_offline_orders_generate_posm
from test_eats_integration_offline_orders import conftest


@pytest.mark.parametrize(
    (
        'generation_id',
        'reschedule_counter',
        'status',
        'is_rescheduled',
        'comment',
        'raise_error',
        'template_code',
    ),
    (
        pytest.param(
            1, 1, 'done', False, '', False, http.HTTPStatus.OK, id='OK',
        ),
        pytest.param(
            2,
            1,
            'done',
            False,
            'good comment',
            False,
            http.HTTPStatus.OK,
            id='already-done',
        ),
        pytest.param(
            1,
            1,
            'created',
            True,
            'rescheduled because of error (2 try), details: s3 upload failed',
            True,
            http.HTTPStatus.OK,
            id='reschedule',
        ),
        pytest.param(
            1,
            5,
            'error',
            False,
            'retry limit reached, details: s3 upload failed',
            True,
            http.HTTPStatus.OK,
            id='retry-limit',
        ),
        pytest.param(
            1,
            1,
            'error',
            False,
            'can\'t download template 1 - mds returned 404',
            False,
            http.HTTPStatus.NOT_FOUND,
            id='template-not-found',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=[
        'restaurants.sql',
        'tables.sql',
        'posm_templates.sql',
        'restaurants_posm_templates.sql',
        'posm_generations.sql',
        'posm_generations_templates.sql',
    ],
)
async def test_ei_offline_orders_generate_posm(
        stq3_context,
        mockserver,
        patch,
        stq,
        pgsql,
        generation_id,
        reschedule_counter,
        status,
        is_rescheduled,
        comment,
        raise_error,
        template_code,
):
    data = conftest.load_pdf_template('template.pdf')
    mds_called = []

    @patch(
        'eats_integration_offline_orders.stq.ei_offline_orders_generate_posm.'
        '_upload_to_s3',
    )
    async def _upload_to_s3(context, body, mds_key, metadata):
        if raise_error and len(mds_called) == 1:
            raise ValueError('s3 upload failed')
        mds_called.append(mds_key)
        return

    @mockserver.handler(
        rf'/mds_s3/{conftest.MDS_S3_BUCKET_NAME}/'
        rf'{constants.MDS_TEMPLATES_PREFIX}/(?P<file_id>\d+)',
        regex=True,
    )
    async def _mds_s3_mock(request, **kwargs):
        assert request.method == 'GET'
        if template_code is http.HTTPStatus.OK:
            return mockserver.make_response(data, headers={'ETag': 'asdf'})
        return mockserver.make_response(status=template_code)

    @patch(
        'eats_integration_offline_orders.stq.ei_offline_orders_generate_posm.'
        '_undo_mds_upload',
    )
    async def _undo_mds_upload(context, mds_keys):
        for key in mds_called:
            assert key in mds_keys
        return

    task_info = async_worker.TaskInfo(
        id=f'{generation_id}',
        exec_tries=1,
        reschedule_counter=reschedule_counter,
        queue='ei_offline_orders_generate_posm',
    )

    await ei_offline_orders_generate_posm.task(
        context=stq3_context, task_info=task_info,
    )

    cursor = pgsql['eats_integration_offline_orders'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    cursor.execute(f'select * from posm_generations where id={generation_id}')
    row = cursor.fetchone()
    assert row['status'] == status
    assert row['comment'] == comment
    try:
        stq_info = stq.ei_offline_orders_generate_posm.next_call()
    except callinfo.CallQueueEmptyError:
        assert not is_rescheduled
        return
    assert is_rescheduled
    assert stq_info['id'] == str(generation_id)
