import asyncio
import dataclasses
import datetime
import logging
from typing import Any
from typing import Dict
from typing import Optional

import pytest

from taxi.logs import log
from taxi.maintenance import run

from rida.crontasks import import_php_request_logs
from rida.generated.cron import run_cron
from rida.models import request_log as request_log_models


DATETIME = datetime.datetime(2021, 8, 17)


@pytest.mark.parametrize(
    ['record', 'expected_request_log'],
    [
        pytest.param(
            {
                'id': 40739936,
                'path': 'https://api.rida.app/v1/setPushToken?applicationId=3',
                'ip': '105.112.115.5',
                'request': (
                    '{"push_token":"PUSH_TOKEN"}\n'
                    'method: POST\n'
                    'Language: en\n'
                    'headers: {"Accept-Language":"en"}\n'
                    'userGUID: ad14c94a-a801-4675-9c68-ee7c36fac9c5\n'
                ),
                'data_server': (
                    'Response status: 200\n'
                    '{"status":"OK"}\n'
                    'duration: 0.277'
                ),
                'data': '',
                'created_at': DATETIME,
                'updated_at': DATETIME,
                'user_guid': 'ad14c94a-a801-4675-9c68-ee7c36fac9c5',
            },
            request_log_models.RequestLog(
                id=40739936,
                path='/v1/setPushToken',
                created_at=DATETIME,
                updated_at=DATETIME,
                request={'push_token': 'PUSH_TOKEN'},
                response={'status': 'OK'},
                response_status=200,
                duration=0.277,
                user_guid='ad14c94a-a801-4675-9c68-ee7c36fac9c5',
            ),
            id='full',
        ),
        pytest.param(
            {
                'id': 40739936,
                'path': 'https://api.rida.app/v1/setPushToken?applicationId=3',
                'request': (
                    '{"push_token":"PUSH_TOKEN"}\n'
                    'method: POST\n'
                    'Language: en\n'
                    'headers: {"Accept-Language":"en"}\n'
                    'userGUID: ad14c94a-a801-4675-9c68-ee7c36fac9c5\n'
                ),
                'data_server': None,
                'created_at': DATETIME,
                'updated_at': DATETIME,
                'user_guid': 'ad14c94a-a801-4675-9c68-ee7c36fac9c5',
            },
            request_log_models.RequestLog(
                id=40739936,
                path='/v1/setPushToken',
                created_at=DATETIME,
                updated_at=DATETIME,
                request={'push_token': 'PUSH_TOKEN'},
                response=None,
                response_status=None,
                duration=None,
                user_guid='ad14c94a-a801-4675-9c68-ee7c36fac9c5',
            ),
            id='no_response',
        ),
        pytest.param(
            {
                'id': 40739936,
                'path': 'https://api.rida.app/v1/setPushToken?applicationId=3',
                'request': (
                    '{"push_token":"PUSH_TOKEN"}\n'
                    'method: POST\n'
                    'Language: en\n'
                    'headers: {"Accept-Language":"en"}\n'
                    'userGUID: ad14c94a-a801-4675-9c68-ee7c36fac9c5\n'
                ),
                'data_server': (
                    'Response status: 200\n'
                    '{"status":"OK"}\n'
                    'duration: 0.277'
                ),
                'created_at': DATETIME,
                'updated_at': DATETIME,
                'user_guid': None,
            },
            request_log_models.RequestLog(
                id=40739936,
                path='/v1/setPushToken',
                created_at=DATETIME,
                updated_at=DATETIME,
                request={'push_token': 'PUSH_TOKEN'},
                response={'status': 'OK'},
                response_status=200,
                duration=0.277,
                user_guid=None,
            ),
            id='no_user_guid',
        ),
        pytest.param(
            {
                'id': 40739936,
                'path': 'https://api.rida.app/v1/setPushToken?applicationId=3',
                'request': '{"push_token":"PUSH_TOKE',
                'data_server': (
                    'Response status: 200\n'
                    '{"status":"OK\n'
                    'duration: 0.277'
                ),
                'created_at': DATETIME,
                'updated_at': DATETIME,
                'user_guid': 'ad14c94a-a801-4675-9c68-ee7c36fac9c5',
            },
            request_log_models.RequestLog(
                id=40739936,
                path='/v1/setPushToken',
                created_at=DATETIME,
                updated_at=DATETIME,
                request=None,
                response=None,
                response_status=200,
                duration=0.277,
                user_guid='ad14c94a-a801-4675-9c68-ee7c36fac9c5',
            ),
            id='invalid_request_and_response_json',
        ),
    ],
)
def test_model_parsing(
        record: Dict[str, Any],
        expected_request_log: request_log_models.RequestLog,
):
    request_log = request_log_models.RequestLog.from_record(record)
    assert request_log == expected_request_log


@dataclasses.dataclass
class ExpectedLog:
    log_level: int
    path: str
    status_code: int
    request_body: dict
    response_body: dict
    total_time: float
    user_guid: Optional[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime

    def is_equal(self, record) -> bool:
        extdict = record.extdict
        is_equal = all(
            [
                record.msg
                == (
                    f'PHP request to handle {self.path} '
                    f'finished with code {self.status_code}'
                ),
                extdict.get('uri') == self.path,
                extdict.get('request_body') == self.request_body,
                extdict.get('response_body') == self.response_body,
                extdict.get('total_time') == self.total_time,
                extdict.get('user_guid') == self.user_guid,
                extdict.get('created_at') == self.created_at,
                extdict.get('updated_at') == self.updated_at,
                extdict.get('meta_code') == self.status_code,
            ],
        )
        return is_equal


async def test_import_php_request_logs(caplog, cron_context):
    module_name = 'rida.crontasks.import_php_request_logs'
    log.init_logger(logger_names=[module_name])
    caplog.set_level(logging.INFO, logger=module_name)
    await run_cron.main(['rida.crontasks.import_php_request_logs', '-t', '0'])
    expected_logs = [
        ExpectedLog(
            log_level=logging.INFO,
            path='/v1/logDriverPosition',
            status_code=304,
            request_body={
                'lat': 6.5154855,
                'long': 3.2890172,
                'heading': 90,
                'user_guid': '5c339935-722b-4986-bdb7-1400a7efa284',
            },
            response_body=[],
            total_time=0.203,
            user_guid='5c339935-722b-4986-bdb7-1400a7efa284',
            created_at=datetime.datetime(2021, 8, 17, 14, 00),
            updated_at=datetime.datetime(2021, 8, 17, 14, 00),
        ),
        ExpectedLog(
            log_level=logging.INFO,
            path='/v1/logDriverPosition',
            status_code=304,
            request_body={
                'lat': 6.5154855,
                'long': 3.2890172,
                'heading': 90,
                'user_guid': '5c339935-722b-4986-bdb7-1400a7efa284',
            },
            response_body=[],
            total_time=0.200,
            user_guid='5c339935-722b-4986-bdb7-1400a7efa284',
            created_at=datetime.datetime(2021, 8, 17, 14, 15),
            updated_at=datetime.datetime(2021, 8, 17, 14, 15),
        ),
        ExpectedLog(
            log_level=logging.INFO,
            path='/v1/getPointInfo',
            status_code=200,
            request_body={'lat': 6.5154855, 'long': 3.2890172},
            response_body={'status': 'INVALID_DATA', 'errors': {}},
            total_time=0.200,
            user_guid='5c339935-722b-4986-bdb7-1400a7efa284',
            created_at=datetime.datetime(2021, 8, 17, 15, 10),
            updated_at=datetime.datetime(2021, 8, 17, 15, 10),
        ),
    ]
    log_records = list()
    for record in caplog.records:
        if record.name != module_name:
            continue
        if not record.msg.startswith('PHP request'):
            continue
        log_records.append(record)

    assert len(log_records) == len(expected_logs)
    for record, expected_log in zip(log_records, expected_logs):
        assert expected_log.is_equal(record)
    # test cursor update
    query = (
        'SELECT last_id, last_updated_at '
        'FROM cursors '
        'WHERE name = \'requests\''
    )
    async with cron_context.pg.ro_pool.acquire() as conn:
        record = await conn.fetchrow(query)
        assert record['last_id'] == 5
        assert record['last_updated_at'] == datetime.datetime(
            2021, 8, 17, 15, 10,
        )


async def test_metrics(cron_context, get_stats_by_label_values):
    stuff_context = run.StuffContext(
        lock=None,
        task_id='some-id',
        start_time=datetime.datetime.utcnow(),
        data=cron_context,
    )

    loop = asyncio.get_event_loop()
    await import_php_request_logs.do_stuff(stuff_context, loop)

    stats = get_stats_by_label_values(
        cron_context, {'sensor': 'php_status_codes'},
    )
    assert stats == [
        {
            'value': 2,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'sensor': 'php_status_codes',
                'response_status': 'OK',
                'path': '/v1/logDriverPosition',
                'status_code': '304',
            },
        },
        {
            'value': 1,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'path': '/v1/getPointInfo',
                'response_status': 'INVALID_DATA',
                'sensor': 'php_status_codes',
                'status_code': '200',
            },
        },
    ]
