import pytest

from taxi_billing_subventions.personal_uploads import actions
from taxi_billing_subventions.personal_uploads import db as upload_db
from taxi_billing_subventions.personal_uploads import stq_task


class StqAgentClientMock:
    def __init__(self, *args, **kwargs):
        self.calls = []

    async def put_task(
            self, queue, eta=None, task_id=None, args=None, kwargs=None,
    ):
        self.calls.append((queue, task_id))


@pytest.mark.subventions_config(TVM_ENABLED=True)
@pytest.mark.nofilldb()
async def test_not_authorized_response(
        billing_subventions_client, request_headers,
):
    response = await billing_subventions_client.post(
        '/v1/rules/approve_upload', headers={}, json={},
    )
    assert response.status == 403


@pytest.mark.parametrize(
    'ticket, login, expected_status',
    [
        (None, None, 400),
        (None, 'testuser', 400),
        ('TAXIRATE-44', None, 400),
        ('TAXIRATE-44', 'testuser', 404),
    ],
)
@pytest.mark.subventions_config(TVM_ENABLED=True)
@pytest.mark.filldb()
async def test_headers(
        patched_tvm_ticket_check,
        billing_subventions_client,
        request_headers,
        ticket,
        login,
        expected_status,
):
    headers = request_headers
    if ticket:
        headers.update({'X-YaTaxi-Draft-Tickets': ticket})
    if login:
        headers.update({'X-Yandex-Login': login})
    request = {'request_id': 'missing_id_001'}
    response = await billing_subventions_client.post(
        '/v1/rules/approve_upload', headers=headers, json=request,
    )
    assert bool(patched_tvm_ticket_check.calls)
    assert response.status == expected_status


@pytest.mark.subventions_config(TVM_ENABLED=True)
async def test_malformed_request(
        patched_tvm_ticket_check, billing_subventions_client, request_headers,
):
    headers = request_headers
    headers.update(
        {
            'X-YaTaxi-Draft-Tickets': 'RUPRICING-55',
            'X-Yandex-Login': 'testuser',
        },
    )
    request = {}
    response = await billing_subventions_client.post(
        '/v1/rules/approve_upload', headers=headers, json=request,
    )
    assert response.status == 400


async def _get_approved_doc_ids(db):
    query = {'status': {'$in': ['approved', None]}}
    rules = await db.personal_subvention_rules.find(query).to_list(None)
    return sorted([rule['_id'] for rule in rules])


async def _count_locks(db):
    return await db.distlock.count()


@pytest.mark.now('2019-11-25T10:00:00')
@pytest.mark.filldb(
    personal_subvention_rules='stub', personal_subvention_uploads='stub',
)
@pytest.mark.subventions_config(TVM_ENABLED=True)
async def test_handle_missing_upload(
        db,
        billing_subventions_client,
        patched_tvm_ticket_check,
        request_headers,
):
    headers = request_headers
    headers.update(
        {
            'X-YaTaxi-Draft-Tickets': 'RUPRICING-55',
            'X-Yandex-Login': 'testuser',
        },
    )
    request = {'request_id': 'missing_id'}
    response = await billing_subventions_client.post(
        '/v1/rules/approve_upload', headers=headers, json=request,
    )
    assert response.status == 404


@pytest.mark.now('2019-11-25T10:00:00')
@pytest.mark.filldb(
    personal_subvention_rules='bigmix', personal_subvention_uploads='bigmix',
)
@pytest.mark.subventions_config(TVM_ENABLED=True)
async def test_handle_unfinished_upload(
        db,
        billing_subventions_client,
        patched_tvm_ticket_check,
        request_headers,
):
    headers = request_headers
    headers.update(
        {
            'X-YaTaxi-Draft-Tickets': 'RUPRICING-55',
            'X-Yandex-Login': 'testuser',
        },
    )
    request = {'request_id': 'currently_uploading'}
    response = await billing_subventions_client.post(
        '/v1/rules/approve_upload', headers=headers, json=request,
    )
    assert response.status == 400


@pytest.mark.now('2019-11-25T10:00:00')
@pytest.mark.filldb(
    personal_subvention_rules='bigmix', personal_subvention_uploads='bigmix',
)
@pytest.mark.subventions_config(TVM_ENABLED=True)
async def test_handle_already_approved(
        db,
        billing_subventions_client,
        patched_tvm_ticket_check,
        request_headers,
):
    headers = request_headers
    headers.update(
        {
            'X-YaTaxi-Draft-Tickets': 'RUPRICING-55',
            'X-Yandex-Login': 'testuser',
        },
    )
    request = {'request_id': 'completely_finished'}
    response = await billing_subventions_client.post(
        '/v1/rules/approve_upload', headers=headers, json=request,
    )
    assert response.status == 200
    actual = await response.json()
    assert actual == {}


@pytest.mark.now('2019-11-25T10:00:00')
@pytest.mark.filldb(
    personal_subvention_rules='bigmix', personal_subvention_uploads='bigmix',
)
@pytest.mark.subventions_config(TVM_ENABLED=True)
async def test_handle_currently_approving(
        db,
        patch,
        billing_subventions_client,
        patched_tvm_ticket_check,
        request_headers,
):
    stq = []

    @patch('taxi.clients.stq_agent.StqAgentClient.put_task')
    async def put(  # pylint: disable=unused-variable
            queue, eta=None, task_id=None, args=None, kwargs=None,
    ):
        stq.append((task_id, eta, args))

    headers = request_headers
    headers.update(
        {
            'X-YaTaxi-Draft-Tickets': 'RUPRICING-55',
            'X-Yandex-Login': 'testuser',
        },
    )
    request = {'request_id': 'currently_approving'}
    response = await billing_subventions_client.post(
        '/v1/rules/approve_upload', headers=headers, json=request,
    )
    assert response.status == 200
    actual = await response.json()
    assert actual == {'status': 'applying'}
    assert stq == [
        (
            'currently_approving',
            0,
            ('currently_approving', 'testuser', 'RUPRICING-55'),
        ),
    ]


@pytest.mark.now('2019-11-25T10:00:00')
@pytest.mark.filldb(
    personal_subvention_rules='stq_test',
    personal_subvention_uploads='stq_test',
)
async def test_approve_action(loop, db, taxi_config):

    stq_client_mock = StqAgentClientMock()

    upload_id = 'ready_to_approve'
    login = 'testuser'
    ticket = 'TAXIPRICING-99'
    upload = await upload_db.fetch_upload(db, upload_id)
    assert upload.is_finished
    assert upload.is_succeeded
    assert not upload.is_approved
    await actions.do_approve(
        stq_client_mock,
        upload_id=upload_id,
        login=login,
        ticket=ticket,
        database=db,
        log_extra=None,
    )
    approved_docs = await _get_approved_doc_ids(db)
    expected_docs = ['id_to_approve_1', 'id_to_approve_2']
    assert sorted(approved_docs) == sorted(expected_docs)
    upload = await upload_db.fetch_upload(db, upload_id)
    assert upload.is_finished
    assert upload.is_succeeded
    assert upload.is_approved
    assert stq_client_mock.calls == [
        ('personal_subventions_notify', 'personal_subventions_notify'),
    ]


@pytest.mark.parametrize(
    'upload_id, reason, called, notify_called',
    [
        ('ready_to_approve', 'approve rules', True, True),
        ('completely_finished', 'already approved', False, False),
    ],
)
@pytest.mark.now('2019-11-25T10:00:00')
@pytest.mark.filldb(
    personal_subvention_rules='stub', personal_subvention_uploads='bigmix',
)
async def test_approve_calls(
        patch, loop, db, caplog, upload_id, reason, called, notify_called,
):
    stq_client_mock = StqAgentClientMock()

    calls = []

    @patch(
        'taxi_billing_subventions.common.db.rule.'
        'approve_uploaded_personal_rules',
    )
    async def approve_uploaded_personal_rules(
            # pylint: disable=unused-variable
            database,
            upload_id,
            ticket,
            batch_size,
            delay,
    ):
        calls.append(upload_id)

    login = 'testuser'
    ticket = 'TAXIPRICING-99'
    await actions.do_approve(
        stq_client_mock,
        upload_id=upload_id,
        login=login,
        ticket=ticket,
        database=db,
        log_extra=None,
    )
    assert called == bool(calls)
    assert any(reason in x for x in caplog.messages)
    stq_calls = stq_client_mock.calls
    if notify_called:
        assert stq_calls == [
            ('personal_subventions_notify', 'personal_subventions_notify'),
        ]
    else:
        assert not stq_calls


@pytest.mark.parametrize(
    'upload_id, exception_cls',
    [
        ('failed_to_upload', actions.UnexpectedUploadState),
        ('currently_uploading', actions.UnexpectedUploadState),
        ('ready_to_upload', actions.UnexpectedUploadState),
        ('nonexistent', upload_db.NotFound),
    ],
)
@pytest.mark.now('2019-11-25T10:00:00')
@pytest.mark.filldb(
    personal_subvention_rules='stub', personal_subvention_uploads='bigmix',
)
async def test_approve_failure(patch, loop, db, upload_id, exception_cls):
    stq_client_mock = StqAgentClientMock()

    calls = []

    @patch(
        'taxi_billing_subventions.common.db.rule.'
        'approve_uploaded_personal_rules',
    )
    async def approve_uploaded_personal_rules(
            # pylint: disable=unused-variable
            database,
            upload_id,
            ticket,
            batch_size,
            delay,
    ):
        calls.append(upload_id)

    with pytest.raises(exception_cls):
        await actions.do_approve(
            stq_client_mock,
            upload_id=upload_id,
            login='testuser',
            ticket='TAXIPRICING-99',
            database=db,
            log_extra=None,
        )
    assert not calls
    assert not stq_client_mock.calls


class _Data:
    def __init__(self, db, loop, config):
        self._db = db
        self._loop = loop
        self._config = config
        self.stq_agent = StqAgentClientMock()

    @property
    def db(self):
        return self._db

    @property
    def loop(self):
        return self._loop

    @property
    def config(self):
        return self._config


@pytest.mark.now('2019-11-25T10:00:00')
@pytest.mark.filldb(
    personal_subvention_rules='stq_test',
    personal_subvention_uploads='stq_test',
)
@pytest.mark.subventions_config(TVM_ENABLED=True)
async def test_stq_task_approve_uploads(loop, db, patch, taxi_config):
    data = _Data(db, loop, taxi_config)
    await stq_task.task_approve_uploads(
        data=data,
        upload_id='ready_to_approve',
        login='testuser',
        ticket='TAXIPRICING-99',
        log_extra=None,
    )
    approved_docs = await _get_approved_doc_ids(db)
    expected_docs = ['id_to_approve_1', 'id_to_approve_2']
    assert sorted(approved_docs) == sorted(expected_docs)
    assert data.stq_agent.calls == [
        ('personal_subventions_notify', 'personal_subventions_notify'),
    ]
