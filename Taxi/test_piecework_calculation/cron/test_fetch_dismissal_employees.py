import datetime

import pytest

from piecework_calculation import constants
from piecework_calculation.generated.cron import run_cron


NOW = datetime.datetime(2021, 1, 15, 11, 11, 11)


@pytest.mark.now(NOW.isoformat())
async def test_fetch_dismissal_employees(cron_context, stq):
    await run_cron.main(
        [
            'piecework_calculation.crontasks.fetch_dismissal_employees',
            '-t',
            '0',
        ],
    )
    call_args = stq.piecework_calculation_save_dismissal_rule.next_call()
    assert stq.is_empty
    assert call_args['queue'] == 'piecework_calculation_save_dismissal_rule'
    assert call_args['args'] == [
        NOW.date().strftime(constants.OEBS_DATE_FORMAT),
    ]
