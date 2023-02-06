from piecework_calculation import constants
from piecework_calculation.generated.cron import run_cron


async def test_dismissal(cron_context, mock_base_rule_processor_run):
    await run_cron.main(
        ['piecework_calculation.crontasks.dismissal', '-t', '0'],
    )
    assert mock_base_rule_processor_run.calls == [
        {
            'args': (),
            'kwargs': {'rule_type': constants.CALCULATION_RULE_DISMISSAL_TYPE},
        },
        {
            'args': (),
            'kwargs': {'rule_type': constants.CALCULATION_RULE_DISMISSAL_TYPE},
        },
        {
            'args': (),
            'kwargs': {'rule_type': constants.CALCULATION_RULE_DISMISSAL_TYPE},
        },
        {
            'args': (),
            'kwargs': {'rule_type': constants.CALCULATION_RULE_DISMISSAL_TYPE},
        },
        {
            'args': (),
            'kwargs': {'rule_type': constants.CALCULATION_RULE_DISMISSAL_TYPE},
        },
        {
            'args': (),
            'kwargs': {'rule_type': constants.CALCULATION_RULE_DISMISSAL_TYPE},
        },
        {
            'args': (),
            'kwargs': {'rule_type': constants.CALCULATION_RULE_DISMISSAL_TYPE},
        },
    ]
