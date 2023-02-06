# pylint: disable=protected-access
import asyncio
import datetime

import pytest

from replication.common import cron_distribution


@pytest.mark.parametrize(
    'input_hosts, ordered_hosts',
    [
        (
            [
                'abc-01.sas.yp.net',
                'abc-01.vla.yp.net',
                'abc-01.man.yp.net',
                'abc-02.sas.yp.net',
                'abc-02.vla.yp.net',
                'abc-02.man.yp.net',
            ],
            [
                'abc-01.man.yp.net',
                'abc-01.sas.yp.net',
                'abc-01.vla.yp.net',
                'abc-02.man.yp.net',
                'abc-02.sas.yp.net',
                'abc-02.vla.yp.net',
            ],
        ),
        (
            [
                'abc-01.sas.yp.net',
                'abc-01.vla.yp.net',
                'abc-01.man.yp.net',
                'abc-02.sas.yp.net',
                'abc-02.vla.yp.net',
            ],
            [
                'abc-01.man.yp.net',
                'abc-01.sas.yp.net',
                'abc-01.vla.yp.net',
                'abc-02.sas.yp.net',
                'abc-02.vla.yp.net',
            ],
        ),
        (
            ['abc-01.sas.yp.net', 'abc-01.vla.yp.net', 'abc-02.vla.yp.net'],
            ['abc-01.sas.yp.net', 'abc-01.vla.yp.net', 'abc-02.vla.yp.net'],
        ),
        (['abc-01.sas.yp.net'], ['abc-01.sas.yp.net']),
        (
            ['abc-01.sas.yp.net', 'fail_no_dc', 'xxx-02.vla'],
            ['fail_no_dc', 'abc-01.sas.yp.net', 'xxx-02.vla'],
        ),
    ],
)
def test_rtc_dc_host_sort(input_hosts, ordered_hosts):
    assert ordered_hosts == cron_distribution._rtc_dc_host_sort(input_hosts)


@pytest.mark.parametrize(
    'cron_task_use_start_second, start_datetime',
    [
        pytest.param(
            None,
            datetime.datetime(2022, 6, 6, 12, 57, 36),
            marks=pytest.mark.now(
                datetime.datetime(2022, 6, 6, 12, 57, 36).isoformat(),
            ),
        ),
        pytest.param(
            15,
            datetime.datetime(2022, 6, 6, 12, 58, 15),
            marks=pytest.mark.now(
                datetime.datetime(2022, 6, 6, 12, 57, 36).isoformat(),
            ),
        ),
        pytest.param(
            15,
            datetime.datetime(2022, 6, 6, 12, 57, 15),
            marks=pytest.mark.now(
                datetime.datetime(2022, 6, 6, 12, 57, 15).isoformat(),
            ),
        ),
        pytest.param(
            15,
            datetime.datetime(2022, 6, 6, 12, 57, 15),
            marks=pytest.mark.now(
                datetime.datetime(2022, 6, 6, 12, 57, 13).isoformat(),
            ),
        ),
    ],
)
async def test_wait_ready_for(
        monkeypatch, cron_task_use_start_second, start_datetime,
):
    monkeypatch.setattr(asyncio, 'sleep', _mocked_sleep)
    delay = await cron_distribution.wait_ready_for(
        cron_task_use_start_second=cron_task_use_start_second,
    )
    assert start_datetime == datetime.datetime.now() + datetime.timedelta(
        seconds=delay,
    )


async def _mocked_sleep(*args, **kwargs):
    pass
