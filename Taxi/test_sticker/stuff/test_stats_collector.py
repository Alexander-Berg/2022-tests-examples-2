# pylint: disable=protected-access
import pytest

from sticker.generated.cron import run_cron


@pytest.mark.now('2019-01-02T09:00:00Z')
async def test_do_stuff(patch):
    @patch('taxi.clients.solomon.SolomonClient.push_data')
    async def _push_data(data, handler=None, log_extra=None):
        pass

    @patch('sticker.mail.smailik.client.get_spool_size')
    def _get_spool_size(*args):
        return 0

    await run_cron.main(['sticker.stuff.stats_collector', '-t', '0', '-d'])

    calls = _push_data.calls
    assert len(calls) == 1
    data = calls[0]['data']
    assert len(data._sensors) == 15


@pytest.mark.now('2019-01-02T09:00:00Z')
async def test_non_terminal_age(patch):
    @patch('taxi.clients.solomon.SolomonClient.push_data')
    async def _push_data(data, handler=None, log_extra=None):
        pass

    @patch('sticker.mail.smailik.client.get_spool_size')
    def _get_spool_size(*args):
        return 0

    await run_cron.main(['sticker.stuff.stats_collector', '-t', '0', '-d'])

    call = _push_data.call
    data = call['data']._sensors

    non_terminal_ages = [
        x for x in data if x['labels']['sensor'] == 'NonTerminalMaxAge'
    ]
    assert len(non_terminal_ages) == 3

    values = {x['value'] for x in non_terminal_ages}
    values.remove(0)
    age = values.pop()
    # check with range cause query based on NOW
    # and some time passed between db init and task run
    assert 1000 < age < 2000
