# pylint: disable=redefined-outer-name

from hiring_st.generated.cron import run_cron


async def test_graphite():
    await run_cron.main(['hiring_st.crontasks.graphite', '-t', '0', '-d'])
