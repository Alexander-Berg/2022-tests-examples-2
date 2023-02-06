# pylint: disable=redefined-outer-name
from stq_agent_py3.generated.cron import run_cron


async def test_cleanup_stq(mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/stq-agent/queues/list')
    async def stq_agent_list_stqs(request):
        return {'queues': ['queue1', 'queue2']}

    # pylint: disable=unused-variable
    @mockserver.json_handler('/stq-agent/queues/api/cleanup')
    async def stq_agent_cleanup_stq(request):
        return {}

    await run_cron.main(['stq_agent_py3.crontasks.cleanup_stq', '-t', '0'])
