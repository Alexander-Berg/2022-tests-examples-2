import datetime
import typing

import pytest
import requests


class STQService:
    def __init__(self):
        self.host = None

    def set_host(self, host: str):
        self.host = host

    def post_task(
            self, queue_name: str, kwargs: typing.Dict, task_id: str,
    ) -> None:
        eta = datetime.datetime.utcnow() + datetime.timedelta(seconds=3)
        response = requests.post(
            url=f'{self.host}/queue',
            json={
                'queue_name': queue_name,
                'task_id': task_id,
                'args': [],
                'kwargs': kwargs,
                'eta': eta.strftime('%Y-%m-%dT%H:%M:%SZ'),
            },
        )

        assert response.status_code == 200
        assert response.json() == {}

    def get_queue_stat(self, queue_name: str) -> typing.Dict:
        response = requests.post(
            url=f'{self.host}/queues/stats',
            json={'queues': [queue_name], 'metrics': []},
        )

        assert response.status_code == 200
        return response.json()

    def payment_confirmed_task(self, order_id: str) -> None:
        self.post_task(
            queue_name='eda_order_processing_payment_events_callback',
            kwargs={
                'order_id': order_id,
                'action': 'purchase',
                'status': 'confirmed',
                'revision': order_id + '_1',
            },
            task_id=f'test_task_id_{order_id}',
        )

    def payment_canceled_task(self, order_id: str) -> None:
        self.post_task(
            queue_name='eda_order_processing_payment_events_callback',
            kwargs={
                'order_id': order_id,
                'action': 'cancel',
                'status': 'rejected',
                'revision': order_id + '_1',
            },
            task_id=f'test_task_id_{order_id}',
        )


@pytest.fixture
def stq():
    return STQService()
