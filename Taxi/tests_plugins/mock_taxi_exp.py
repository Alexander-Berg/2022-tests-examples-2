import json

import pytest


class TaxiExpMock:
    MAX_KWARGS_SEND_RETRIES = 3

    def __init__(self):
        self.consumer_kwargs_send_calls = {}

    def inc_kwargs_send(self, consumer):
        if consumer not in self.consumer_kwargs_send_calls:
            self.consumer_kwargs_send_calls[consumer] = 0

        self.consumer_kwargs_send_calls[consumer] += 1

        assert (
            self.consumer_kwargs_send_calls[consumer]
            <= self.MAX_KWARGS_SEND_RETRIES
        )

    def kwargs_sends_by_consumer(self, consumer):
        return self.consumer_kwargs_send_calls.get(consumer, 0)


@pytest.fixture(autouse=True)
def mock_taxi_exp(experiments3, mockserver):
    experiments = TaxiExpMock()

    @mockserver.json_handler('/experiments3-upstream/v1/consumers/kwargs/')
    def _handler_send_kwargs_info(request):
        req = json.loads(request.get_data(as_text=True))
        assert 'consumer' in req
        assert 'kwargs' in req
        experiments.inc_kwargs_send(req['consumer'])
        return {}

    return experiments
