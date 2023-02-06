import dataclasses
from typing import Dict
from typing import Optional

import pytest


@pytest.fixture(name='logistic_dispatcher')
def mock_eats_core_eater(mockserver):
    @dataclasses.dataclass
    class Context:
        delivery_finished_at: Optional[int] = None
        from_position: Optional[Dict] = None
        to_position: Optional[Dict] = None
        logistic_group: Optional[str] = None
        status_code: int = 200
        order_id: Optional[str] = None

        def check_request(
                self,
                from_position=None,
                to_position=None,
                logistic_group=None,
                order_id=None,
        ):
            self.from_position = from_position
            self.to_position = to_position
            self.logistic_group = logistic_group
            self.order_id = order_id

        def set_response(
                self,
                status_code=200,
                delivery_finished_at=None,
                logistic_group=None,
        ):
            self.delivery_finished_at = delivery_finished_at
            self.status_code = status_code
            self.logistic_group = logistic_group

    context = Context()

    @mockserver.json_handler('/logistic-dispatcher/api/pull_dispatch/promise')
    def _mock_pull_dispatch_promise(request):
        if context.status_code != 200:
            return mockserver.make_response(status_code=context.status_code)

        if context.order_id is not None:
            assert request.json['external_order_id'] == context.order_id
        if context.from_position is not None:
            assert request.json['from'] == context.from_position
        if context.to_position is not None:
            assert request.json['to'] == context.to_position
        if context.logistic_group is not None:
            assert request.json['logistic_group'] == context.logistic_group

        return {
            'delivery_started_at': None,
            'couriers': [],
            'orders': [],
            'delivery_finished_at': context.delivery_finished_at,
        }

    return context
