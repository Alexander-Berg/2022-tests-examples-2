import pytest

from dashboards.generated.cron import run_cron


@pytest.mark.config(
    DASHBOARDS_GRAPHS_REPO_SETTINGS={
        'user': 'taxi',
        'repo': 'infra-cfg-graphs',
    },
    DASHBOARDS_GENERATOR_SETTINGS={'enabled': True, 'dry_run': True},
)
@pytest.mark.usefixtures('git_infra_graphs_mock')
async def test_generate_all_dashboards():
    # WARNING
    # DO NOT COMMIT ANY FILE in infra-cfg-graphs mock directory.
    # requests library is not patched and the test makes REAL requests
    # to real endpoints.
    # For local testing add config to
    # ./static/test_generate_all_dashboards/infra-cfg-graphs/grafana/*.yaml

    # if you are going to use cron_runner fixture, then you should know
    # that git_mock will not work and git clone will not be mocked
    await run_cron.main(
        ['dashboards.crontasks.generate_all_dashboards', '-t', '0'],
    )
