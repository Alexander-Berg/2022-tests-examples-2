from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk import environments
from sandbox.sandboxsdk import parameters as par


class EventParams(par.DictRepeater, par.SandboxStringParameter):
    name = 'event_params'
    description = 'Event params'
    default_value = ''


class SleepTime(par.SandboxIntegerParameter):
    name = 'sleep_time'
    description = 'Sleep time'
    default_value = 5 * 60


class StepHost(par.SandboxStringParameter):
    name = 'step_host'
    description = 'STEP host'
    default_value = 'https://step-sandbox1.n.yandex-team.ru'


class StatinfraTestTask(SandboxTask):
    type = 'STATINFRA_TEST_TASK'

    environment = (environments.PipEnvironment('requests'),)

    input_parameters = [SleepTime, EventParams, StepHost]

    def on_execute(self):
        import time
        import requests
        from urlparse import urljoin

        event_params = self.ctx[EventParams.name] or {}
        exec_number = int(event_params.get('exec_number', 1))

        out_numbers = []
        if exec_number < 40:
            out_numbers.append(exec_number + 1)
            if exec_number % 3 == 0:
                out_numbers.append(exec_number + 10)

            requests.post(
                urljoin(self.ctx[StepHost.name], 'api/v1/events'),
                json={
                    'events': [
                        {
                            'name': 'reset_test_event',
                            'params': {
                                'exec_number': en
                            }
                        } for en in out_numbers
                    ],
                    'source_type': 'SANDBOX_TASK',
                    'source': {
                        'task_id': self.id
                    }
                },
                verify=False
            )

        time.sleep(self.ctx[SleepTime.name])


__Task__ = StatinfraTestTask
