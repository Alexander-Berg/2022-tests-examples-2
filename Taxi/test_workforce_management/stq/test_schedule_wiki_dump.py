import json
import typing as tp

import pandas as pd
import pytest
import pytz

from taxi.clients import mds_s3
from taxi.stq import async_worker_ng

from test_workforce_management.stq.static.test_schedule_wiki_dump import data
from workforce_management.common import constants
from workforce_management.common.jobs.setup import setup
from workforce_management.stq import setup_jobs


WFM_DOMAIN = 'taxi'
WIKI_PATH = f'/{WFM_DOMAIN}/workgraph'
S3_PREFIX = 'hr_schedule'
DOMAIN_CONFIG: tp.Dict[str, tp.Any] = {
    'domains': [WFM_DOMAIN],
    'timezone': 'Europe/Moscow',
    'wiki_title': 'Графики сотрудников',
    'wiki_path': WIKI_PATH,
    's3_prefix': S3_PREFIX,
}
TIMEZONE = pytz.timezone(DOMAIN_CONFIG['timezone'])

PAGE_BODY = (
    'Последнее обновление: 2020-19-07 17:10:47.075813\n'
    f'Графики на **01.08.2020** 01-08-2020.xls\n'
    f'Графики на **19.07.2020** 19-07-2020.xls'
)

EXPECTED_BODY = (
    f'Последнее обновление: 2020-07-20 03:00:00.000000\n'
    f'Графики на **01.08.2020** mds-uri:hr_schedule/01-08-2020.xls\n'
    f'Графики на **20.07.2020** mds-uri:{S3_PREFIX}/20-07-2020.xls\n'
    f'Графики на **19.07.2020** 19-07-2020.xls'
)
EXPECTED_BODY_2 = (
    'Последнее обновление: 2022-06-23 00:00:00.000000\n'
    'Графики на **01.07.2022** mds-uri:hr_schedule/01-07-2022.xls\n'
    'Графики на **23.06.2022** mds-uri:hr_schedule/23-06-2022.xls\n'
    'Графики на **01.08.2020** 01-08-2020.xls\n'
    'Графики на **19.07.2020** 19-07-2020.xls'
)


@pytest.mark.now('2020-07-20T00:00:00+00:00')
@pytest.mark.parametrize(
    [
        'page_body',
        'expected_data',
        'task_kwargs',
        'expected_body',
        'expected_status',
    ],
    [
        pytest.param(
            PAGE_BODY,
            data.EXPECTED_DATA_0,
            {
                'job_type': constants.JobTypes.wiki_schedule_dump.value,
                'extra': DOMAIN_CONFIG,
            },
            EXPECTED_BODY,
            constants.JobStatus.completed.value,
            marks=[
                pytest.mark.pgsql(
                    'workforce_management',
                    files=['data0.sql', 'simple_shifts.sql'],
                ),
            ],
            id='active_schedule_with_tz_offset',
        ),
        pytest.param(
            PAGE_BODY,
            data.EXPECTED_DATA_1,
            {
                'job_type': constants.JobTypes.wiki_schedule_dump.value,
                'extra': DOMAIN_CONFIG,
            },
            EXPECTED_BODY,
            constants.JobStatus.completed.value,
            marks=[
                pytest.mark.pgsql(
                    'workforce_management',
                    files=['data1.sql', 'simple_shifts.sql'],
                ),
            ],
            id='no_active_schedule_between_schedules_with_tz_offset',
        ),
    ],
)
async def test_base(
        page_body,
        expected_data,
        task_kwargs,
        expected_body,
        expected_status,
        stq3_context,
        patch,
        patch_aiohttp_session,
        response_mock,
):
    dataframes: tp.List[pd.DataFrame] = []

    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _mds_upload(
            key: str, body: bytes, metadata: tp.Dict, *args, **kwargs,
    ):
        assert body, key
        dataframes.append(pd.read_excel(body, index_col=0))
        return mds_s3.S3Object(Key='mds-id:' + key, ETag=None)

    @patch('taxi.clients.mds_s3.MdsS3Client.generate_download_url')
    async def _generate_download_url(key: str, *args, **kwargs):
        return 'mds-uri:' + key

    page = ''

    @patch_aiohttp_session(stq3_context.client_wiki.base_url + WIKI_PATH)
    def _wiki_page(method, *args, **kwargs):
        nonlocal page
        if method.upper() == 'POST':
            page = kwargs['json']['body']
        return response_mock(status=200, json={'data': {'body': page_body}})

    queue = constants.StqQueueNames.setup_jobs

    job_id = await setup.setup_job(
        stq3_context, queue_name=queue, **task_kwargs,
    )

    await setup_jobs.task(
        context=stq3_context,
        task_info=async_worker_ng.TaskInfo(
            id=job_id, exec_tries=0, reschedule_counter=0, queue=queue.value,
        ),
        args=(),
        **task_kwargs,
    )

    assert page == expected_body
    assert len(dataframes) == len(expected_data)
    templates = data.get_date_templates()

    for index, expected_dataframe in enumerate(expected_data):
        dataframe = json.loads(
            dataframes[index].to_json(orient='index', force_ascii=False),
        )
        assert len(dataframe) == len(expected_dataframe)

        for key in expected_dataframe:
            operator = dataframe[key]
            expected_operator = {**templates[index], **expected_dataframe[key]}
            assert operator == expected_operator, f'data_{index}_{key}'


@pytest.mark.now('2022-06-22T21:00:00+00:00')
@pytest.mark.parametrize(
    [
        'page_body',
        'cached_operator',
        'expected_data',
        'task_kwargs',
        'expected_body',
        'expected_status',
    ],
    [
        pytest.param(
            PAGE_BODY,
            {
                'yandex_uid': 'uid1',
                'login': 'abd-damir',
                'full_name': 'Abdullin Damir',
                'timezone': 'Europe/Samara',
                'domain': 'taxi',
            },
            [
                {
                    'Abdullin Damir abd-damir': {
                        'WFM график': '7/7 ',
                        'WFM смещение': 8,
                        'Кадровый график': '2/2/3-2 11Ч',
                        'Кадровая смена': 2,
                        'Часы': '23:00:00 - 11:00:00',
                        'Страна': 'ru',
                        'Юр.лицо': 'Яндекс.Такси',
                        'Часовой пояс': 'Europe/Samara',
                        '01.06.2022': '23:00:00 - 11:00:00',
                        '02.06.2022': '23:00:00 - 11:00:00',
                        '06.06.2022': '23:00:00 - 11:00:00',
                        '07.06.2022': '23:00:00 - 11:00:00',
                        '10.06.2022': '23:00:00 - 11:00:00',
                        '11.06.2022': '23:00:00 - 11:00:00',
                        '12.06.2022': '23:00:00 - 11:00:00',
                        '15.06.2022': '23:00:00 - 11:00:00',
                        '16.06.2022': '23:00:00 - 11:00:00',
                        '20.06.2022': '23:00:00 - 11:00:00',
                        '21.06.2022': '23:00:00 - 11:00:00',
                        '24.06.2022': '23:00:00 - 11:00:00',
                        '25.06.2022': '23:00:00 - 11:00:00',
                        '26.06.2022': '23:00:00 - 11:00:00',
                        '29.06.2022': '23:00:00 - 11:00:00',
                        '30.06.2022': '23:00:00 - 11:00:00',
                    },
                },
                {
                    'Abdullin Damir abd-damir': {
                        'Страна': 'ru',
                        'Часовой пояс': 'Europe/Samara',
                        'Юр.лицо': 'Яндекс.Такси',
                    },
                },
            ],
            {
                'job_type': constants.JobTypes.wiki_schedule_dump.value,
                'extra': DOMAIN_CONFIG,
            },
            EXPECTED_BODY_2,
            constants.JobStatus.completed.value,
            marks=[
                pytest.mark.pgsql('workforce_management', files=['data2.sql']),
            ],
            id='bounds_start_less_than_datetime_from',
        ),
        pytest.param(
            PAGE_BODY,
            {
                'yandex_uid': 'uid1',
                'login': 'abd-damir',
                'full_name': 'Abdullin Damir',
                'timezone': 'Asia/Krasnoyarsk',
                'domain': 'taxi',
            },
            [
                {
                    'Abdullin Damir abd-damir': {
                        '01.06.2022': '00:00:00 - 05:00:00',
                        '02.06.2022': '00:00:00 - 05:00:00',
                        '03.06.2022': '00:00:00 - 05:00:00',
                        '04.06.2022': '00:00:00 - 05:00:00',
                        '07.06.2022': '00:00:00 - 05:00:00',
                        '08.06.2022': '00:00:00 - 05:00:00',
                        '09.06.2022': '00:00:00 - 05:00:00',
                        '10.06.2022': '00:00:00 - 05:00:00',
                        '11.06.2022': '00:00:00 - 05:00:00',
                        '14.06.2022': '00:00:00 - 05:00:00',
                        '15.06.2022': '00:00:00 - 05:00:00',
                        '16.06.2022': '00:00:00 - 05:00:00',
                        '17.06.2022': '00:00:00 - 05:00:00',
                        '18.06.2022': '00:00:00 - 05:00:00',
                        '21.06.2022': '00:00:00 - 05:00:00',
                        '22.06.2022': '00:00:00 - 05:00:00',
                        '23.06.2022': '00:00:00 - 05:00:00',
                        '24.06.2022': '00:00:00 - 05:00:00',
                        '25.06.2022': '00:00:00 - 05:00:00',
                        '28.06.2022': '00:00:00 - 05:00:00',
                        '29.06.2022': '00:00:00 - 05:00:00',
                        '30.06.2022': '00:00:00 - 05:00:00',
                        'WFM график': '5/2 (вых. сб, вс) ',
                        'WFM смещение': 1,
                        'Кадровая смена': 1,
                        'Кадровый график': '5/2 (СБ,ВС) 4Ч',
                        'Страна': 'ru',
                        'Часовой пояс': 'Asia/Krasnoyarsk',
                        'Часы': '21:00:00 - 02:00:00',
                        'Юр.лицо': 'Яндекс.Такси',
                    },
                },
                {
                    'Abdullin Damir abd-damir': {
                        '01.07.2022': '00:00:00 - 05:00:00',  # missing
                        '02.07.2022': '00:00:00 - 05:00:00',
                        '05.07.2022': '00:00:00 - 05:00:00',
                        '06.07.2022': '00:00:00 - 05:00:00',
                        '07.07.2022': '00:00:00 - 05:00:00',
                        '08.07.2022': '00:00:00 - 05:00:00',
                        '09.07.2022': '00:00:00 - 05:00:00',
                        '12.07.2022': '00:00:00 - 05:00:00',
                        '13.07.2022': '00:00:00 - 05:00:00',
                        '14.07.2022': '00:00:00 - 05:00:00',
                        '15.07.2022': '00:00:00 - 05:00:00',
                        '16.07.2022': '00:00:00 - 05:00:00',
                        '19.07.2022': '00:00:00 - 05:00:00',
                        '20.07.2022': '00:00:00 - 05:00:00',
                        '21.07.2022': '00:00:00 - 05:00:00',
                        '22.07.2022': '00:00:00 - 05:00:00',
                        '23.07.2022': '00:00:00 - 05:00:00',
                        '26.07.2022': '00:00:00 - 05:00:00',
                        '27.07.2022': '00:00:00 - 05:00:00',
                        '28.07.2022': '00:00:00 - 05:00:00',
                        '29.07.2022': '00:00:00 - 05:00:00',
                        '30.07.2022': '00:00:00 - 05:00:00',
                        'WFM график': '5/2 (вых. сб, вс) ',
                        'WFM смещение': 1,
                        'Кадровая смена': 1,
                        'Кадровый график': '5/2 (СБ,ВС) 4Ч',
                        'Страна': 'ru',
                        'Часовой пояс': 'Asia/Krasnoyarsk',
                        'Часы': '21:00:00 - 02:00:00',
                        'Юр.лицо': 'Яндекс.Такси',
                    },
                },
            ],
            {
                'job_type': constants.JobTypes.wiki_schedule_dump.value,
                'extra': DOMAIN_CONFIG,
            },
            EXPECTED_BODY_2,
            constants.JobStatus.completed.value,
            marks=[
                pytest.mark.pgsql('workforce_management', files=['data3.sql']),
            ],
            id='first_shift_yesterday_in_utc',
        ),
        pytest.param(
            PAGE_BODY,
            {
                'yandex_uid': 'uid1',
                'login': 'abd-damir',
                'full_name': 'Abdullin Damir',
                'timezone': 'Europe/Minsk',
                'domain': 'taxi',
            },
            [
                {
                    'Abdullin Damir abd-damir': {
                        '01.06.2022': '09:00:00 - 21:00:00',
                        '02.06.2022': '09:00:00 - 21:00:00',
                        '06.06.2022': '09:00:00 - 21:00:00',
                        '07.06.2022': '09:00:00 - 21:00:00',
                        '10.06.2022': '09:00:00 - 21:00:00',
                        '11.06.2022': '09:00:00 - 21:00:00',
                        '12.06.2022': '09:00:00 - 21:00:00',
                        '15.06.2022': '09:00:00 - 21:00:00',
                        '16.06.2022': '09:00:00 - 21:00:00',
                        '20.06.2022': '09:00:00 - 21:00:00',
                        '21.06.2022': '09:00:00 - 21:00:00',
                        '24.06.2022': '09:00:00 - 21:00:00',
                        '25.06.2022': '09:00:00 - 21:00:00',
                        '26.06.2022': '09:00:00 - 21:00:00',
                        '29.06.2022': '09:00:00 - 21:00:00',
                        '30.06.2022': '09:00:00 - 21:00:00',
                        'WFM график': '7/7 ',
                        'WFM смещение': 8,
                        'Кадровая смена': 2,
                        'Кадровый график': '2/2/3-2 11Ч',
                        'Страна': 'ru',
                        'Часовой пояс': 'Europe/Minsk',
                        'Часы': '06:00:00 - 18:00:00',
                        'Юр.лицо': 'Яндекс.Такси',
                    },
                },
                {
                    'Abdullin Damir abd-damir': {
                        '01.07.2022': None,  # should be None
                        '04.07.2022': '09:00:00 - 21:00:00',
                        '05.07.2022': '09:00:00 - 21:00:00',
                        '08.07.2022': '09:00:00 - 21:00:00',
                        '09.07.2022': '09:00:00 - 21:00:00',
                        '10.07.2022': '09:00:00 - 21:00:00',
                        '13.07.2022': '09:00:00 - 21:00:00',
                        '14.07.2022': '09:00:00 - 21:00:00',
                        '18.07.2022': '09:00:00 - 21:00:00',
                        '19.07.2022': '09:00:00 - 21:00:00',
                        '22.07.2022': '09:00:00 - 21:00:00',
                        '23.07.2022': '09:00:00 - 21:00:00',
                        '24.07.2022': '09:00:00 - 21:00:00',
                        '27.07.2022': '09:00:00 - 21:00:00',
                        '28.07.2022': '09:00:00 - 21:00:00',
                        'WFM график': '7/7 ',
                        'WFM смещение': 8,
                        'Кадровая смена': 2,
                        'Кадровый график': '2/2/3-2 11Ч',
                        'Страна': 'ru',
                        'Часовой пояс': 'Europe/Minsk',
                        'Часы': '06:00:00 - 18:00:00',
                        'Юр.лицо': 'Яндекс.Такси',
                    },
                },
            ],
            {
                'job_type': constants.JobTypes.wiki_schedule_dump.value,
                'extra': DOMAIN_CONFIG,
            },
            EXPECTED_BODY_2,
            constants.JobStatus.completed.value,
            marks=[
                pytest.mark.pgsql('workforce_management', files=['data4.sql']),
            ],
            id='first_shift_holiday',
        ),
    ],
)
async def test_base_tz(
        page_body,
        cached_operator,
        expected_data,
        task_kwargs,
        expected_body,
        expected_status,
        stq3_context,
        patch,
        patch_aiohttp_session,
        response_mock,
):
    @patch(
        'workforce_management.common.jobs.setup.wiki_schedule_dump_job'
        '.WikiScheduleDumper.iter_operators_cache',
    )
    def _iter_operators_cache(*args, **kwargs):
        yield cached_operator

    await test_base(
        page_body,
        expected_data,
        task_kwargs,
        expected_body,
        expected_status,
        stq3_context,
        patch,
        patch_aiohttp_session,
        response_mock,
    )
