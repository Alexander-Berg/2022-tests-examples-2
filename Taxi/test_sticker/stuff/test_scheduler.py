# pylint: disable=unused-variable
import asyncio
import os
import random

import pytest

from taxi.clients import personal

from sticker import dump_manager
from sticker.generated.cron import run_cron
from sticker.stuff import scheduler


@pytest.mark.config(
    STICKER_SCHEDULER_CHUNK_DELAY=0.0,
    STICKER_SCHEDULER_CHUNK_SETTINGS={'chunks_per_run': 1, 'chunk_size': 10},
)
@pytest.mark.parametrize(
    'personal_email, decoded_email',
    [
        ('some@yandex.ru', 'some@yandex.ru'),
        ('some@почта.ру', 'some@xn--80a1acny.xn--p1ag'),
        ('aaaa@почта.ру', 'aaaa@xn--80a1acny.xn--p1ag'),
    ],
)
async def test_do_stuff(patch, cron_context, personal_email, decoded_email):
    @patch('sticker.stuff.scheduler._personals_tvm_auth_cache_refresh')
    async def _personals_tvm_auth_cache_refresh(*args, **kwargs):
        return

    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(*args, **kwargs):
        return {'email': personal_email}

    emails = []

    @patch('sticker.mail.smailik.send_email')
    def _send_email(email, *args, **kwargs):
        emails.append(email)

    await run_cron.main(['sticker.stuff.scheduler', '-t', '0', '-d'])

    async with cron_context.pg.master.acquire() as connection:
        rows = await connection.fetch(
            'SELECT id, status FROM sticker.mail_queue',
        )

    assert len(rows) == 2
    assert {x['id'] for x in rows} == {1, 2}
    assert {x['status'] for x in rows} == {'SCHEDULED'}
    assert emails == [decoded_email, 'ya@ya.ru']


@pytest.mark.config(
    STICKER_SCHEDULER_CHUNK_DELAY=0.0,
    STICKER_SCHEDULER_CHUNK_SETTINGS={'chunks_per_run': 1, 'chunk_size': 10},
)
async def test_tvm_fail(patch, cron_context):
    @patch('taxi.clients.tvm.TVMClient.get_auth_headers')
    async def _tvm_auth_cache_refresh(*args, **kwargs):
        return

    await run_cron.main(['sticker.stuff.scheduler', '-t', '0', '-d'])

    async with cron_context.pg.master.acquire() as connection:
        rows = await connection.fetch(
            'SELECT id, status FROM sticker.mail_queue',
        )

    assert len(rows) == 2
    assert {x['id'] for x in rows} == {1, 2}
    assert {x['status'] for x in rows} == {'PENDING'}


@pytest.mark.config(
    STICKER_SCHEDULER_CHUNK_DELAY=0.0,
    STICKER_SCHEDULER_CHUNK_SETTINGS={'chunks_per_run': 1, 'chunk_size': 10},
)
@pytest.mark.parametrize(
    'personal_exc, db_status, db_reason',
    [
        (personal.BadRequestError, 'FAILED', 'BadRequestError()'),
        (personal.PersonalTimeoutError, 'TO_RETRY', 'PersonalTimeoutError()'),
    ],
)
async def test_fail_reason(
        patch, cron_context, personal_exc, db_reason, db_status,
):
    @patch('sticker.stuff.scheduler._personals_tvm_auth_cache_refresh')
    async def _personals_tvm_auth_cache_refresh(*args, **kwargs):
        return

    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(*args, **kwargs):
        raise personal_exc

    await run_cron.main(['sticker.stuff.scheduler', '-t', '0', '-d'])

    async with cron_context.pg.master.acquire() as connection:
        rows = await connection.fetch(
            'SELECT id, status, reason FROM sticker.mail_queue',
        )

    assert len(rows) == 2
    assert {x['id'] for x in rows} == {1, 2}
    assert rows[0]['status'] == db_status
    assert rows[0]['reason'] == db_reason


@pytest.mark.config(
    STICKER_SCHEDULER_CHUNK_DELAY=0.0,
    STICKER_SCHEDULER_CHUNK_SETTINGS={'chunks_per_run': 1, 'chunk_size': 10},
)
async def test_attachments(patch):
    @patch('sticker.stuff.scheduler._personals_tvm_auth_cache_refresh')
    async def _personals_tvm_auth_cache_refresh(*args, **kwargs):
        return

    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(*args, **kwargs):
        return {'email': random.choice(['some@yandex.ru', 'more@yandex.ru'])}

    @patch('sticker.mail.smailik.send_email')
    def _send_email(*args, **kwargs):
        pass

    @patch('sticker.mail.smailik.path.write_attachment')
    def _write_attachment(attachment):
        assert attachment.idempotence_token == '1'
        assert attachment.recipient == 'id1'
        assert attachment.file_name in ('some.pdf', 'more.pdf')

    await run_cron.main(['sticker.stuff.scheduler', '-t', '0', '-d'])

    assert len(_send_email.calls) == 2
    assert len(_write_attachment.calls) == 2


@pytest.mark.config(
    STICKER_SCHEDULER_CHUNK_DELAY=0.0,
    STICKER_SCHEDULER_CHUNK_SETTINGS={'chunks_per_run': 1, 'chunk_size': 10},
)
async def test_several_requests_for_one_email(patch):
    @patch('sticker.stuff.scheduler._personals_tvm_auth_cache_refresh')
    async def _personals_tvm_auth_cache_refresh(*args, **kwargs):
        return

    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(*args, **kwargs):
        return {'email': 'some@yandex.ru'}

    @patch('sticker.mail.smailik.send_email')
    def _send_email(*args, **kwargs):
        pass

    await run_cron.main(['sticker.stuff.scheduler', '-t', '0', '-d'])

    assert len(_send_email.calls) == 2


@pytest.mark.config(
    STICKER_SCHEDULER_CHUNK_DELAY=0.0,
    STICKER_SCHEDULER_CHUNK_SETTINGS={'chunks_per_run': 1, 'chunk_size': 10},
)
@pytest.mark.parametrize(
    'problem_mail_id, expected_send_calls, expected_dump, fail_load_attach',
    [
        (1, 1, {'SCHEDULED': '1\n', 'PENDING': '2\n3\n'}, False),
        (2, 2, {'SCHEDULED': '2\n', 'PENDING': '3\n'}, False),
        (3, 3, {'SCHEDULED': '3\n'}, False),
        (None, 0, {'PENDING': '1\n2\n3\n'}, True),
    ],
)
async def test_create_dump(
        patch,
        tmpdir,
        monkeypatch,
        problem_mail_id,
        expected_send_calls,
        expected_dump,
        fail_load_attach,
        mockserver,
):
    class ExpectedError(Exception):
        pass

    @mockserver.handler('/solomon/', json_response=True)
    def _solomon(request):
        return mockserver.make_response()

    @patch('sticker.stuff.scheduler._personals_tvm_auth_cache_refresh')
    async def _personals_tvm_auth_cache_refresh(*args, **kwargs):
        return

    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(*args, **kwargs):
        return {'email': 'some@yandex.ru'}

    @patch('sticker.mail.smailik.send_email')
    def _send_email(*args, **kwargs):
        pass

    monkeypatch.setattr(dump_manager, 'DUMPS_DIR', tmpdir)

    original_set_status = scheduler.set_status

    @patch('sticker.stuff.scheduler.set_status')
    async def set_status(connection, query, mail_request_ids):
        if 'SCHEDULED' in query and problem_mail_id in mail_request_ids:
            raise ExpectedError
        return await original_set_status(connection, query, mail_request_ids)

    @patch('sticker.stuff.scheduler.load_attachments')
    async def load_attachments(*args, **kwargs):
        if not fail_load_attach:
            return {}
        raise ExpectedError

    with pytest.raises(ExpectedError):
        await run_cron.main(['sticker.stuff.scheduler', '-t', '0', '-d'])

    assert len(_send_email.calls) == expected_send_calls

    dir_names = os.listdir(tmpdir)
    assert len(dir_names) == 1
    dump_dir = os.path.join(tmpdir, dir_names[0])
    file_names = os.listdir(dump_dir)
    assert file_names
    dump = {}
    for file_name in file_names:
        with open(os.path.join(dump_dir, file_name), 'r') as fp:
            dump[file_name] = fp.read()
    assert dump == expected_dump


@pytest.mark.config(
    STICKER_SCHEDULER_CHUNK_DELAY=0.0,
    STICKER_SCHEDULER_CHUNK_SETTINGS={'chunks_per_run': 1, 'chunk_size': 2},
)
async def test_parallel_run(patch, cron_context):
    @patch('sticker.stuff.scheduler._personals_tvm_auth_cache_refresh')
    async def _personals_tvm_auth_cache_refresh(*args, **kwargs):
        return

    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(*args, **kwargs):
        return {'email': 'some@yandex.ru'}

    @patch('sticker.mail.smailik.send_email')
    def _send_email(*args, **kwargs):
        pass

    await asyncio.gather(
        run_cron.main(['sticker.stuff.scheduler', '-t', '0', '-d']),
        run_cron.main(['sticker.stuff.scheduler', '-t', '0', '-d']),
    )

    async with cron_context.pg.master.acquire() as connection:
        query = (
            'SELECT * FROM sticker.mail_queue '
            'WHERE status = \'SCHEDULED\' '
            'ORDER BY id;'
        )
        rows = await connection.fetch(query)
    assert len(rows) == 4
