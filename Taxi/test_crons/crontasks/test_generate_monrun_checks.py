# pylint: disable=protected-access
from crons.crontasks import generate_monrun_checks


async def test_generate_monrun_checks(cron_context):
    dev_teams = await generate_monrun_checks._collect_teams(cron_context)
    assert dev_teams == ['platform', 'taxidata']
    entry = generate_monrun_checks._monrun_entry(
        team_name='platform',
        python_path='/testsuite/lib/python3.7',
        python_bin='/testsuite/bin/python3.7',
    )
    assert entry.splitlines() == [
        '[taxi-cron-fails-platform]',
        'type=taxi',
        (
            'command=PYTHONPATH="/testsuite/lib/python3.7" '
            '/testsuite/bin/python3.7 -m '
            'crons.generated.cron.run_monrun taxi-cron-fails-platform '
            'crons.monrun_checks.cron_fails '
            '--dev-team platform'
        ),
        'execution_interval=60',
    ]
