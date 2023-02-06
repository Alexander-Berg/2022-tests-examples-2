import datetime
import typing

from . import consts


def make_operation(
        operation_type: str = consts.OPERATION_TYPE,
        priority: int = consts.OPERATION_PRIORITY,
):
    return dict(
        operation_type=operation_type,
        operation_id=consts.OPERATION_ID,
        priority=priority,
    )


def make_item(item_id, amount, **kwargs):
    return dict(item_id=item_id, amount=amount, **kwargs)


def make_payment_items(items, payment_type='card'):
    return dict(items=items, payment_type=payment_type)


def to_debt_collector_items(payment_items):
    return dict(total=payment_items, debt=payment_items)


def make_time_table_strategy(times: typing.List[datetime.datetime], **kwargs):
    return dict(
        strategy=dict(
            kind='time_table',
            metadata=dict(schedule=[it.isoformat() for it in times]),
        ),
        **kwargs,
    )


def make_reason(reason_code=consts.DEBT_REASON_CODE):
    return dict(code=reason_code, metadata={})
