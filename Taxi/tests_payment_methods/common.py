import dataclasses


@dataclasses.dataclass
class CallsCount:
    reschedule: int = 0
    get_fields: int = 0
    transactions: int = 0
    send_event: int = 0


@dataclasses.dataclass
class InvoiceState:
    status: str = 'hold-failed'
    is_operations_in_progress: bool = False
    is_transactions_in_progress: bool = False
    is_not_found: bool = False
