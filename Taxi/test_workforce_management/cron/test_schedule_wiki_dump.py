import typing as tp

import pytest

from workforce_management.common.jobs.setup import wiki_schedule_dump_job
from workforce_management.generated.cron import run_cron

WFM_DOMAIN = 'taxi'
WIKI_PATH = f'/{WFM_DOMAIN}/workgraph'
S3_PREFIX = 'hr_schedule'

DEFAULT_CONFIG: tp.Dict[str, tp.Any] = {
    'enabled': False,
    'domains': [],
    'timezone': 'Europe/Moscow',
    'wiki_title': 'Графики сотрудников',
    'wiki_path': '',
}

DOMAIN_CONFIG: tp.Dict[str, tp.Any] = {
    'enabled': True,
    'domains': [WFM_DOMAIN],
    'wiki_path': WIKI_PATH,
}


@pytest.mark.now('2020-07-20T00:00:00')
@pytest.mark.config(
    WORKFORCE_MANAGEMENT_SCHEDULE_WIKI_DUMP_SETTINGS={
        wiki_schedule_dump_job.DEFAULT_CONFIG_KEY: DEFAULT_CONFIG,
        S3_PREFIX: DOMAIN_CONFIG,
    },
)
@pytest.mark.parametrize(
    'expected_kwargs',
    [
        pytest.param(
            {
                'extra': {
                    **DEFAULT_CONFIG,
                    **DOMAIN_CONFIG,
                    's3_prefix': S3_PREFIX,
                },
            },
        ),
    ],
)
async def test_base(expected_kwargs, stq):
    await run_cron.main(
        ['workforce_management.crontasks.wiki_schedule_dump', '-t', '0'],
    )

    task = stq.workforce_management_setup_jobs.next_call()
    for field, expected_value in expected_kwargs.items():
        assert task['kwargs'][field] == expected_value
