import pytest

from chatterbox.crontasks import tasks_monitor


async def test_predispatch_monitor_no_exc(cbox_context, loop):
    await tasks_monitor.do_stuff(cbox_context, loop)


@pytest.mark.filldb(support_chatterbox='predispatch')
async def test_predispatch_monitor(cbox_context, loop):
    with pytest.raises(tasks_monitor.TaskMonitoringError):
        await tasks_monitor.do_stuff(cbox_context, loop)


@pytest.mark.filldb(support_chatterbox='enqued')
async def test_enqued_monitor(cbox_context, loop):
    with pytest.raises(tasks_monitor.TaskMonitoringError):
        await tasks_monitor.do_stuff(cbox_context, loop)


@pytest.mark.filldb(support_chatterbox='archive_in_progress')
async def test_archive_in_progress_monitor(cbox_context, loop):
    with pytest.raises(tasks_monitor.TaskMonitoringError):
        await tasks_monitor.do_stuff(cbox_context, loop)
