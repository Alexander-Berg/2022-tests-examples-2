import datetime
import re
import typing

import dateutil.parser
import pytest


class StqTask(typing.NamedTuple):
    queue: str
    id: str
    args: list
    kwargs: dict
    eta: datetime.datetime

    @property
    def is_urgent(self) -> bool:
        return self.eta.timestamp() == 0.0

    @property
    def is_postponed(self) -> bool:
        return not self.is_urgent


class Agent:
    def __init__(self):
        self.tasks_queued: typing.List[StqTask] = []

    def get_tasks(
            self, queue_name: str, task_id: str = None,
    ) -> typing.List[StqTask]:

        result = []
        for task in self.tasks_queued:
            if task.queue == queue_name:
                if task_id is not None and task.id != task_id:
                    pass
                result.append(task)

        return result


@pytest.fixture(autouse=True)
def mock_stq_agent(mockserver) -> Agent:
    agent = Agent()

    @mockserver.json_handler('/stq-agent/queue')
    def stq_agent_put_task(request):
        json = request.json
        agent.tasks_queued.append(
            StqTask(
                queue=json['queue_name'],
                id=json['task_id'],
                args=json.get('args', []),
                kwargs=json.get('kwargs', {}),
                eta=dateutil.parser.parse(json['eta']),
            ),
        )
        return {}

    @mockserver.json_handler('/stq-agent/queues/api/add/', prefix=True)
    def stq_agent_add_task(request):
        queue_name = re.match(
            r'/stq-agent/queues/api/add/(\w+)', request.path,
        ).groups()[0]
        json = request.json
        agent.tasks_queued.append(
            StqTask(
                queue=queue_name,
                id=json['task_id'],
                args=json.get('args', []),
                kwargs=json.get('kwargs', {}),
                eta=dateutil.parser.parse(json['eta']),
            ),
        )
        return {}

    return agent
