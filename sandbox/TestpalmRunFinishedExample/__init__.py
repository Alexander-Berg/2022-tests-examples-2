import logging

from sandbox import sdk2


class TestpalmRunFinishedExample(sdk2.Task):
    class Parameters(sdk2.Task.Parameters):
        step_events = sdk2.parameters.String('STEP events parameters', description='STEP events parameters as json string')

    def on_enqueue(self):
        step_events = eval(self.Parameters.step_events)
        template = '<a href="https://testpalm.yandex-team.ru/{project_id}">{project_id}</a> {event_name}'
        for step_event in step_events:
            self.Parameters.description = template.format(
                project_id=step_event['params']['project_id'],
                event_name=step_event['name'],
            )

    def on_execute(self):
        step_events = eval(self.Parameters.step_events)
        for step_event in step_events:
            logging.info(step_event['params']['project_id'])
