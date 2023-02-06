# pylint: disable=redefined-outer-name
# pylint: disable=too-many-lines

import datetime
import json
import typing

from aiohttp import web
import pytest

from taxi.util import itertools_ext

from taxi_qc_exams.generated.cron import run_cron
from test_taxi_qc_exams import utils

RUN_ARGS = [
    'taxi_qc_exams.crontasks.communications.prenotify_drivers',
    '-t',
    '0',
]

DATA_TEMPLATE = """
{{
    "action": {{
        "key": "exams.default.primary",
        "keyset": "taximeter_backend_driver_messages"
    }},
    "action_link": "taximeter://qc_pass_route?exam_code={exam}",
    "action_link_need_auth": false,
    "id": "{id}",
    "need_notification": false,
    "text": {{
        "key": "{key}",
        "keyset": "taximeter_backend_driver_messages",
        "params": {{
            "time_to_deadline": "{time_to_deadline}"
        }}
    }}
}}
"""

PARK_ID = '6fefc330ceea40358924705a6990724b'


async def _check_notification(
        db, entity_id: str, data: typing.List[dict],
) -> typing.List[str]:
    docs = await db.qc_notifications.find(
        dict(entity_id=entity_id), dict(entity_id=0),
    ).to_list(length=None)

    ids = [str(x.pop('_id')) for x in docs]
    assert not utils.symmetric_lists_diff(docs, data)
    return ids


@pytest.mark.now('2018-11-10T21:00:00.000Z')
@pytest.mark.config(
    QC_EXAMS_PRENOTIFICATIONS_ENABLED=True,
    QC_EXAMS_PRENOTIFICATIONS_LOGS_WITHOUT_PUSHES=False,
    QC_EXAMS_PRENOTIFICATIONS_SETTINGS=[
        {
            'applicable_exam_codes': ['dkk'],
            'entity_type': 'driver',
            'time_to_deadline_seconds': 60 * 60 * 24,
            'ttl_seconds': 60 * 60 * 1,
            'msg_key': 'exams.prenotification.dkk.12.text',
            'experiment': 'prenotify_dkk',
            'chunk_size': 1000,
        },
    ],
)
@pytest.mark.filldb(qc_notifications='empty')
async def test_base(simple_secdist, driver_profiles, db, mock_communications):
    @mock_communications('/driver/notification/push')
    def push(request):
        return web.json_response(data={})

    # check db before crontask
    assert await db.qc_notifications.count() == 0

    # crontask
    await run_cron.main(RUN_ARGS)

    assert push.times_called == 2
    assert await db.qc_notifications.count() == 2
    db_notification_data = dict(
        created=datetime.datetime.utcnow(),
        code='dkk',
        reason='sent',
        type='exam_prenotification_push',
    )

    for i in [0, 1]:
        uuid = f'7d7a94a3fee84eda95de736b5e00000{i}'
        notification_id = itertools_ext.first(
            await _check_notification(
                db, f'{PARK_ID}_{uuid}', [db_notification_data],
            ),
        )

        assert push.next_call()['request'].json == dict(
            action='PrenotifyExam',
            code=1300,
            dbid=PARK_ID,
            uuid=uuid,
            data=json.loads(
                DATA_TEMPLATE.format(
                    exam='dkk',
                    id=notification_id,
                    key='exams.prenotification.dkk.12.text',
                    time_to_deadline=23 + i,
                ),
            ),
        )


@pytest.mark.now('2018-11-10T21:00:00.000Z')
@pytest.mark.config(
    QC_EXAMS_PRENOTIFICATIONS_ENABLED=True,
    QC_EXAMS_PRENOTIFICATIONS_LOGS_WITHOUT_PUSHES=False,
    QC_EXAMS_PRENOTIFICATIONS_SETTINGS=[
        {
            'applicable_exam_codes': ['branding'],
            'entity_type': 'car',
            'time_to_deadline_seconds': 60 * 60 * 24,
            'ttl_seconds': 60 * 60 * 1,
            'msg_key': 'exams.prenotification.branding.1.text',
            'experiment': 'prenotify_branding',
            'chunk_size': 1000,
        },
    ],
)
@pytest.mark.filldb(qc_notifications='branding_notified')
async def test_branding(
        simple_secdist, driver_profiles, db, mock_communications,
):
    @mock_communications('/driver/notification/push')
    def push(request):
        return web.json_response(data={})

    # check db before crontask
    assert await db.qc_notifications.count() == 1

    # crontask
    await run_cron.main(RUN_ARGS)

    # check calls
    assert push.times_called == 2
    # check db after crontask
    assert await db.qc_notifications.count() == 3

    db_notification_data = dict(
        created=datetime.datetime.utcnow(),
        code='branding',
        reason='sent',
        type='exam_prenotification_push',
    )

    for i in [0, 1]:
        uuid = f'7d7a94a3fee84eda95de736b5e00000{i}'
        notification_id = itertools_ext.first(
            await _check_notification(
                db, f'{PARK_ID}_{uuid}', [db_notification_data],
            ),
        )

        assert push.next_call()['request'].json == dict(
            action='PrenotifyExam',
            code=1300,
            dbid=PARK_ID,
            uuid=uuid,
            data=json.loads(
                DATA_TEMPLATE.format(
                    exam='branding',
                    id=notification_id,
                    key='exams.prenotification.branding.1.text',
                    time_to_deadline=23,
                ),
            ),
        )


@pytest.mark.now('2018-11-10T21:00:00.000Z')
@pytest.mark.config(
    QC_EXAMS_PRENOTIFICATIONS_ENABLED=True,
    QC_EXAMS_PRENOTIFICATIONS_LOGS_WITHOUT_PUSHES=False,
    QC_EXAMS_PRENOTIFICATIONS_SETTINGS=[
        {
            'applicable_exam_codes': ['dkk'],
            'entity_type': 'driver',
            'time_to_deadline_seconds': 60 * 60 * 24,
            'ttl_seconds': 60 * 60 * 1,
            'msg_key': 'exams.prenotification.dkk.12.text',
            'experiment': 'prenotify_dkk',
            'chunk_size': 1000,
        },
    ],
)
async def test_already_has_sent_push(
        simple_secdist, db, driver_profiles, mock_communications,
):
    @mock_communications('/driver/notification/push')
    def push(request):
        return web.json_response(data={})

    # check db before crontask
    assert await db.qc_notifications.count() == 1

    # crontask
    await run_cron.main(RUN_ARGS)

    # checks after crontask
    assert push.times_called == 1
    assert await db.qc_notifications.count() == 2

    db_notification_data = dict(
        created=datetime.datetime.utcnow(),
        code='dkk',
        reason='sent',
        type='exam_prenotification_push',
    )

    uuid = '7d7a94a3fee84eda95de736b5e000001'
    notification_id = itertools_ext.first(
        await _check_notification(
            db, f'{PARK_ID}_{uuid}', [db_notification_data],
        ),
    )
    assert push.next_call()['request'].json == dict(
        action='PrenotifyExam',
        code=1300,
        dbid=PARK_ID,
        uuid=uuid,
        data=json.loads(
            DATA_TEMPLATE.format(
                exam='dkk',
                id=notification_id,
                key='exams.prenotification.dkk.12.text',
                time_to_deadline=24,
            ),
        ),
    )


@pytest.mark.now('2018-11-10T21:00:00.000Z')
@pytest.mark.config(
    QC_EXAMS_PRENOTIFICATIONS_ENABLED=True,
    QC_EXAMS_PRENOTIFICATIONS_LOGS_WITHOUT_PUSHES=False,
    QC_EXAMS_PRENOTIFICATIONS_SETTINGS=[
        {
            'applicable_exam_codes': ['dkk'],
            'entity_type': 'driver',
            'time_to_deadline_seconds': 60 * 60 * 24,
            'ttl_seconds': 60 * 60 * 1,
            'msg_key': 'exams.prenotification.dkk.12.text',
            'experiment': 'prenotify_dkk',
            'chunk_size': 1000,
        },
    ],
)
@pytest.mark.filldb(qc_notifications='too_old')
async def test_sent_push_is_too_old(
        simple_secdist, db, driver_profiles, mock_communications,
):
    @mock_communications('/driver/notification/push')
    def push(request):
        return web.json_response(data={})

    # check db before crontask
    assert await db.qc_notifications.count() == 1

    # crontask
    await run_cron.main(RUN_ARGS)

    # checks after crontask
    assert push.times_called == 2
    assert await db.qc_notifications.count() == 3

    db_notification_data = dict(
        created=datetime.datetime.utcnow(),
        code='dkk',
        reason='sent',
        type='exam_prenotification_push',
    )

    await _check_notification(
        db,
        f'{PARK_ID}_7d7a94a3fee84eda95de736b5e000000',
        [
            dict(
                created=datetime.datetime(2018, 11, 10, 20, 0, 0, 0),
                code='dkk',
                reason='sent',
                type='exam_prenotification_push',
            ),
            db_notification_data,
        ],
    )

    await _check_notification(
        db,
        f'{PARK_ID}_7d7a94a3fee84eda95de736b5e000001',
        [db_notification_data],
    )


@pytest.mark.now('2018-11-10T21:00:00.000Z')
@pytest.mark.config(
    QC_EXAMS_PRENOTIFICATIONS_ENABLED=True,
    QC_EXAMS_PRENOTIFICATIONS_LOGS_WITHOUT_PUSHES=True,
    QC_EXAMS_PRENOTIFICATIONS_SETTINGS=[
        {
            'applicable_exam_codes': ['dkk'],
            'entity_type': 'driver',
            'time_to_deadline_seconds': 60 * 60 * 24,
            'ttl_seconds': 60 * 60 * 1,
            'msg_key': 'exams.prenotification.dkk.12.text',
            'experiment': 'prenotify_dkk',
            'chunk_size': 1000,
        },
    ],
)
@pytest.mark.filldb(qc_notifications='empty')
async def test_only_logs(simple_secdist, db, driver_profiles):
    # check db before crontask
    assert await db.qc_notifications.count() == 0

    # crontask
    await run_cron.main(RUN_ARGS)

    db_notification_data = dict(
        created=datetime.datetime.utcnow(),
        code='dkk',
        reason='only_logged',
        type='exam_prenotification_push',
    )
    for i in [0, 1]:
        uuid = f'7d7a94a3fee84eda95de736b5e00000{i}'
        await _check_notification(
            db, f'{PARK_ID}_{uuid}', [db_notification_data],
        )


@pytest.mark.now('2018-11-10T21:00:00.000Z')
@pytest.mark.config(
    QC_EXAMS_PRENOTIFICATIONS_LOGS_WITHOUT_PUSHES=False,
    QC_EXAMS_PRENOTIFICATIONS_SETTINGS=[],
)
@pytest.mark.filldb(qc_notifications='empty')
async def test_disabled_config(simple_secdist, db):
    # check db before crontask
    assert await db.qc_notifications.count() == 0
    # crontask
    await run_cron.main(RUN_ARGS)
    # checks after crontask
    assert await db.qc_notifications.count() == 0


@pytest.mark.now('2018-11-10T21:00:00.000Z')
@pytest.mark.config(
    COMMUNICATIONS_CLIENT_QOS={
        '__default__': {'attempts': 3, 'timeout-ms': 1000},
    },
    QC_EXAMS_PRENOTIFICATIONS_ENABLED=True,
    QC_EXAMS_PRENOTIFICATIONS_LOGS_WITHOUT_PUSHES=False,
    QC_EXAMS_PRENOTIFICATIONS_SETTINGS=[
        {
            'applicable_exam_codes': ['dkk'],
            'entity_type': 'driver',
            'time_to_deadline_seconds': 60 * 60 * 24,
            'ttl_seconds': 60 * 60 * 1,
            'msg_key': 'exams.prenotification.dkk.12.text',
            'experiment': 'prenotify_dkk',
            'chunk_size': 1000,
        },
    ],
)
@pytest.mark.filldb(qc_notifications='empty')
async def test_communication_500(
        simple_secdist, db, driver_profiles, mock_communications,
):
    @mock_communications('/driver/notification/push')
    def push(request):
        return web.json_response(status=500, data={})

    # check db before crontask
    assert await db.qc_notifications.count() == 0
    await run_cron.main(RUN_ARGS)

    # check calls
    assert push.times_called == 6

    # check db after crontask
    assert await db.qc_notifications.count() == 2
    db_notification_data = dict(
        created=datetime.datetime.utcnow(),
        code='dkk',
        reason='error',
        type='exam_prenotification_push',
    )

    for i in [0, 1]:
        uuid = f'7d7a94a3fee84eda95de736b5e00000{i}'
        await _check_notification(
            db, f'{PARK_ID}_{uuid}', [db_notification_data],
        )
