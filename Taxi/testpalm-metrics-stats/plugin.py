from typing import Any


class TestpalmMetricsStats:
    def __init__(
            self, context: Any, settings: None, activations_parameters: list,
    ):
        self.new_tests_testcases = context.stats.get_counter(
            {
                'sensor': 'testpalm_metrics.collected_testcases',
                'table': 'newtests',
            },
        )

        self.ios_client_testcases = context.stats.get_counter(
            {
                'sensor': 'testpalm_metrics.collected_testcases',
                'table': 'iosclient',
            },
        )
