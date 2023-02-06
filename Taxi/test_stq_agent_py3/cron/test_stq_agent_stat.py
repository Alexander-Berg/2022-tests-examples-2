# pylint: disable=redefined-outer-name
from stq_agent_py3.crontasks import stq_agent_stat
from stq_agent_py3.generated.cron import run_cron


async def test_stq_agent_stat(monkeypatch, mockserver):
    async def no_sleep(delay):
        pass

    @mockserver.json_handler('/stq-agent/queues/retrieve_alive_hosts')
    async def _retrieve_alive_hosts(request):
        return {
            'hosts': [
                {
                    'queue_name': 'processing',
                    'hosts': ['host1', 'host2', 'host3'],
                },
            ],
        }

    monkeypatch.setattr(stq_agent_stat, '_sleep', no_sleep)

    await run_cron.main(['stq_agent_py3.crontasks.stq_agent_stat', '-t', '0'])
