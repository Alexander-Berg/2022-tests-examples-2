# pylint: disable=C5521, W0621
import pytest

from tests_reposition_matcher.utils import select_named


@pytest.mark.now('2019-09-01T00:00:00')
@pytest.mark.pgsql('reposition_matcher', files=['verdicts.sql'])
async def test_verdicts(taxi_reposition_matcher, pgsql):
    assert (
        await taxi_reposition_matcher.post(
            '/service/cron', json={'task_name': 'pgcleaner-obsolete-verdicts'},
        )
    ).status_code == 200

    rows = select_named(
        """
        SELECT verdict_id FROM state.verdicts ORDER BY
        verdict_id
        """,
        pgsql['reposition_matcher'],
    )

    assert rows == [{'verdict_id': 2}]
