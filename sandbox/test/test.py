from sandbox.projects.ads.nirvana_regular_process.lib import NirvanaRegularProcess, empty_process_state
from sandbox.projects.common.juggler.jclient import to_juggler_service_name
import sandbox.common.rest
import datetime
import sys
import pathlib2
import yatest.common
import pytest
import logging
import dateutil.tz


@pytest.yield_fixture(scope='module', autouse=True)
def local_sandbox():
    with sandbox.common.rest.DispatchedClient as c:
        logging.info('use fixture!')
        yield c(lambda **kws: sandbox.common.rest.Client(base_url='http://localhost:123456/', total_wait=0.001, **kws))


def ts():
    return int((datetime.datetime(2018, 1, 1, tzinfo=dateutil.tz.gettz("Europe/Moscow"))
                                    - datetime.datetime(1970, 1, 1, tzinfo=dateutil.tz.gettz("UTC"))).total_seconds())


TASK_ID = 1


def create_task(start, **kws):
    global TASK_ID
    task_id = TASK_ID
    TASK_ID += 1
    args = dict(
        parent=None,
        period=3600,
        start_time=start,
        end_time=start + 3600 * 24,
        cmd_template='''{binary} '{{"workflow_id": "workflow_{timestamp}"}}' ''',
    )
    args.update(kws)

    import sandbox.common.types.task as ctt
    state = {}
    state.update({'input_parameters': args, 'id': task_id, 'type': 'NIRVANA_REGULAR_PROCESS', 'status': ctt.Status.EXECUTING, 'author': 'robert', 'owner': 'PAULSON', 'context': {}})
    return NirvanaRegularProcess.restore(state)


def launch(task, process_state, **kws):
    check_cmd = kws.get('check_cmd', 'Y_PYTHON_ENTRY_POINT=sandbox.projects.ads.nirvana_regular_process.test.lib:running_operation ' + sys.executable)

    return task.do_job(process_state, '/bin/echo', check_cmd, 'some_file', 'some_config_file', process_id=1, now=datetime.datetime(2018, 1, 3, tzinfo=dateutil.tz.gettz("Europe/Moscow")),
                       log_path=pathlib2.Path(yatest.common.output_path()))


def test_failed_while_launching():
    new_state, flows = launch(create_task(ts(), cmd_template='{binary} 123'), empty_process_state())
    return new_state, flows.to_dict()


def test_successfully_launched():
    task = create_task(ts())
    new_state, flows = launch(task, empty_process_state())
    return new_state, flows.to_dict(), task.get_short_message(flows)


def test_do_nothing():
    state = empty_process_state()
    state['last_time'] = ts() + 3600 * 24
    new_state, flows = launch(create_task(ts()), state)
    return new_state, flows.to_dict()


@pytest.mark.parametrize(
    'status',
    ['running', 'failed', 'successed']
)
def test_check_states(status):
    state = empty_process_state()
    state['last_time'] = ts() + 3600 * 24
    state['graphs_to_watch'] = [
        {
            "attempt": 0,
            "first_launch_time": ts(),
            "timestamp": ts() - 3600,
            "workflow_id": "workflow_123"
        },
    ]
    if status == 'failed':
        func = 'failed_operation'
    elif status == 'successed':
        func = 'successed_operation'
    elif status == 'running':
        func = 'running_operation'
    check_cmd = 'Y_PYTHON_ENTRY_POINT=sandbox.projects.ads.nirvana_regular_process.test.lib:%s %s' % (func, sys.executable)
    new_state, flows = launch(create_task(ts()), state, check_cmd=check_cmd)
    return new_state, flows.to_dict()


@pytest.mark.parametrize(
    'running_count,failed_count,successed_count', [
        [0, 0, 0],
        [3, 3, 3],
        [3, 3, 0],
        [3, 0, 0],
        [10, 0, 0],
        [0, 10, 0],
    ]
)
def test_launch_limited(running_count, failed_count, successed_count):
    state = empty_process_state()
    state['graphs_to_watch'] = [
        {
            "attempt": 0,
            "first_launch_time": ts(),
            "timestamp": ts() - 3600 * (i + 1),
            "workflow_id": wid
        }
        for i, wid in enumerate(
            ['failed_%s' % i for i in xrange(failed_count)] +
            ['successed_%s' % i for i in xrange(successed_count)] +
            ['running_%s' % i for i in xrange(running_count)]
        )
    ]

    check_cmd = 'Y_PYTHON_ENTRY_POINT=sandbox.projects.ads.nirvana_regular_process.test.lib:status %s' % sys.executable
    new_state, flows = launch(create_task(ts(), max_count_of_running_flows=7), state, check_cmd=check_cmd)

    def looks_like_running(wid):
        return wid is not None and ('running_' in wid or 'workflow_' in wid)
    assert len([g for g in new_state['graphs_to_watch'] if looks_like_running(g.get('workflow_id'))]) == max(7, running_count)
    assert len(new_state['graphs_to_watch']) == running_count + failed_count + 25
    return new_state, flows.to_dict()


def test_no_worklow_id():
    state = empty_process_state()
    state['last_time'] = ts() + 3600 * 24
    state['graphs_to_watch'] = [
        {
            "attempt": 0,
            "first_launch_time": ts(),
            "timestamp": ts(),
        }
    ]
    new_state, flows = launch(create_task(ts()), state)
    return new_state, flows.to_dict()


def test_to_juggler():
    assert to_juggler_service_name('ml_engine_task_behav/new_age/vw_cpc_action.yaml') == 'ml_engine_task_behav/new_age/vw_cpc_action.yaml'
    assert to_juggler_service_name('ml_engine_task_behav://new_age/vw_cpc_action.yaml') == 'ml_engine_task_behav_//new_age/vw_cpc_action.yaml'
