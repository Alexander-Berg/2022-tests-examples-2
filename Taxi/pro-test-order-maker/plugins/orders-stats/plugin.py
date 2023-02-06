from typing import Any


class OrdersStats:
    def __init__(
            self, context: Any, settings: None, activations_parameters: list,
    ):
        self.total = context.stats.get_counter({'sensor': 'orders.total'})
        self.failed = context.stats.get_counter({'sensor': 'orders.failed'})
