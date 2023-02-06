import datetime

import pytest

from taxi.maintenance import run

from sticker.mail import types
from sticker.mail.smailik import path
from sticker.stuff import expirer


ALL_SEND_REQUEST_IDS = set(range(11, 22))
ALL_ATTACHMENT_IDS = set(range(1, 2))


@pytest.mark.parametrize(
    'expire_max_ages, not_expired_ids',
    [
        ([{'status': 'SCHEDULED', 'max_age': 2}], ALL_SEND_REQUEST_IDS - {12}),
        (
            [
                {'status': 'SCHEDULED', 'max_age': 1},
                {'status': 'FAILED', 'max_age': 2},
            ],
            ALL_SEND_REQUEST_IDS - {12, 13, 20},
        ),
        (
            [
                {'status': 'PROCESSING', 'max_age': 3},
                {'status': 'PENDING', 'max_age': 2},
                {'status': 'FAILED', 'max_age': 1},
            ],
            ALL_SEND_REQUEST_IDS - {14, 20, 21},
        ),
        ([{'status': 'TO_RETRY', 'max_age': 2}], ALL_SEND_REQUEST_IDS - {16}),
    ],
)
@pytest.mark.now(datetime.datetime(2019, 1, 2, 9, 0, 0).isoformat())
async def test_expirer(
        monkeypatch,
        tmpdir,
        patch,
        cron_context,
        expire_max_ages,
        not_expired_ids,
):
    monkeypatch.setattr(path, 'TEMPORARY_FILES_DIR', tmpdir.mkdir('tmp_xml'))
    async with cron_context.pg.master.acquire() as connection:
        attachments = await connection.fetch(
            'SELECT * FROM sticker.attachment;',
        )
    for attach in attachments:
        path.write_attachment(types.MailAttachment.from_dict(attach))

    @patch('sticker.mail.smailik.path.remove_attachment')
    def _remove_file(attachment):
        assert attachment.file_name == 'attachment.pdf'
        return True

    monkeypatch.setattr(
        cron_context.config, 'STICKER_EXPIRE_MAX_AGES', expire_max_ages,
    )
    context = run.StuffContext(
        lock=None,
        task_id='1',
        start_time=datetime.datetime.utcnow(),
        data=cron_context,
    )

    await expirer.do_stuff(task_context=context, loop=None)

    async with cron_context.pg.master.acquire() as connection:
        remaining_id_rows = await connection.fetch(
            'SELECT id FROM sticker.mail_queue ORDER BY id ASC;',
        )

    assert {row['id'] for row in remaining_id_rows} == not_expired_ids
