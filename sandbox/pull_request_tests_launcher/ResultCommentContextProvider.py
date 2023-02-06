import logging

import requests
import sandbox.common.types.task as ctt
from sandbox import sdk2
from sandbox.common.utils import get_task_link

# from https://a.yandex-team.ru/arcadia/sandbox/ui/src/less/index.less?rev=r9516480#L2635
STATUS_COLOR = {
    "break": "#fea929",
    "draft": "#b28060",
    "deleting": "#b28060",
    "deleted": "#b28060",
    "queue": "#ababab",
    "enqueuing": "#ababab",
    "enqueued": "#ababab",
    "stopping": "#ababab",
    "temporary": "#ababab",
    "wait": "#ababab",
    "unknown": "#ababab",
    "preparing": "#1DAFF0",
    "assigned": "#1DAFF0",
    "executing": "#1DAFF0",
    "finishing": "#1DAFF0",
    "watching": "#1DAFF0",
    "suspending": "#1DAFF0",
    "suspended": "#1DAFF0",
    "finish": "#18A651",
    "success": "#18A651",
    "releasing": "#18A651",
    "released": "#18A651",
    "finished": "#18A651",
    "expired": "#FD0D1B",
    "not_released": "#FD0D1B",
    "failure": "#FD0D1B",
    "no_res": "#FD0D1B",
    "exception": "#FD0D1B",
    "timeout": "#FD0D1B",
    "stopped": "#FD0D1B",
    "broken": "#FD0D1B",
    "not_ready": "#f7bf41",
}


def get_result_comment_context(tasks):
    launcher_tasks = sdk2.task.Task.find(id=tasks.keys()).limit(100)
    tasks = [_get_launcher_info(tasks[str(launcher_task.id)], launcher_task) for launcher_task in launcher_tasks]
    width = {
        "name": max(_calculate_width_for_runner(lambda r: r["name"], tasks), len("Build task")),
        "status": max(
            _calculate_width_for_runner(lambda r: r["status"]["text"], tasks),
            _calculate_width(lambda t: t["buildTask"]["status"]["text"] if t["buildTask"] else "", tasks),
        ),
        "result": _calculate_width_for_runner(
            lambda r: "{} / {}".format(r["result"]["passed"], r["result"]["total"]), tasks
        ),
        "allure": 6,
        "duration": _calculate_width_for_runner(lambda r: r["duration"] or "", tasks),
    }
    return dict(tasks=tasks, width=width)


def _calculate_width_for_runner(displayed_text, tasks):
    return max([max([len(displayed_text(runner)) for runner in task["runners"]] or [0]) for task in tasks] or [0])


def _calculate_width(displayed_text, tasks):
    return max([len(displayed_text(task)) for task in tasks] or [0])


def _get_launcher_info(name, launcher_task):
    runners = [(label, launcher_task.find(id=task_id).first())
               for (label, task_id) in sorted(launcher_task.Context.test_task_ids.items())]
    return {
        "name": name,
        "link": get_task_link(launcher_task.id),
        "status": _get_task_status(launcher_task),
        "runners": [_get_runner_info(label, runner_task) for (label, runner_task) in runners],
        "buildTask": _get_build_task_info(launcher_task.find(id=launcher_task.Context.build_task_id).first()),
        "duration": _get_task_duration_time(launcher_task),
    }


def _get_build_task_info(task):
    is_success = task.status in ctt.Status.Group.SUCCEED
    return {
        "link": get_task_link(task.id),
        "status": _get_task_status(task),
    } if not is_success else None


def _get_runner_info(label, runner_task):
    return {
        "name": _get_runner_title(label),
        "link": get_task_link(runner_task.id),
        "status": _get_task_status(runner_task),
        "result": _get_runner_statistic(runner_task),
        "allureLink": _get_runner_allure_url(runner_task),
        "duration": _get_task_duration_time(runner_task),
    }


def _get_task_status(task):
    return dict(text=task.status, color=STATUS_COLOR[task.status.lower()] or "#AFAFAF")


def _get_runner_title(label):
    if ':' in label:
        label = label[label.index(':') + 2:]
    return label


def _get_runner_statistic(task):
    if task is None:
        return dict(passed="NAN", total="NAN")
    resource_url = sdk2.Resource.find(id=task.Context.artifacts_resource_id).first().http_proxy
    try:
        statistic = requests.get('{}/reports/allure/widgets/summary.json'.format(resource_url)).json()['statistic']
        return dict(passed=statistic['passed'], total=statistic['total'])
    except Exception as e:
        logging.warning("Failed get statistics for task {}: {}".format(task.id, str(e)))
        return dict(passed="NAN", total="NAN")


def _get_runner_allure_url(task):
    if task is None:
        return None
    resource = sdk2.Resource.find(id=task.Context.artifacts_resource_id).first()
    if resource is None:
        return None
    return '{}/reports/allure/index.html'.format(resource.http_proxy)


def _get_task_duration_time(task):
    if task is None:
        return None
    try:
        return str(task.updated - task.created).split(".")[0]
    except Exception:
        logging.exception("Failed to get duration time for task {}".format(task.id))
        return None
