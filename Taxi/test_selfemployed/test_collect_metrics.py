import pytest

from selfemployed.generated.cron import run_cron
from . import conftest


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_collect_metrics(mock_token_update, patch):
    # TODO: fix or avoid hardcode-disabled stats component and add tests
    #   as for now, let's just make sure it runs at all
    await run_cron.main(['selfemployed.crontasks.collect_metrics', '-t', '0'])
