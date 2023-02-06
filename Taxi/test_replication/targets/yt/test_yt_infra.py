# pylint: disable=protected-access
import pytest

from replication.targets.yt.yt_infra import monrun


@pytest.mark.now('2020-12-21T10:00:00')
@pytest.mark.config(
    REPLICATION_WEB_CTL={'runtime': {'yt_infra': {'infra_api_enabled': True}}},
)
async def test_yt_infra_monrun(replication_ctx):
    msg = await monrun._run_check(replication_ctx)
    assert msg == (
        '1; '
        '[YT Arnold] major/issue: '
        'Dynamic tables may be unavailable after recent major update to 20.3 '
        '(since around 14:24). We are investigating this issue. '
        'start_time: 21.12.2020 06:00 MSK; '
        '[YT Seneca MAN] major/maintenance '
        'start_time: 21.12.2020 05:00 MSK, '
        'finish_time: 21.12.2020 18:00 MSK'
    )
