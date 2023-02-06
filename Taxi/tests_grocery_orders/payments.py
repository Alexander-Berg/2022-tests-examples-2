from . import models

OPERATION_TYPES = ['create', 'update', 'clear', 'cancel', 'refund', 'remove']

DEFAULT_OPERATION_ID = '1'
DEFAULT_COMPENSATION_ID = 'a2ace908-5d18-4764-8593-192a1b535514'


def get_default_payment_operations(order_id):
    return [
        models.PaymentOperation(
            order_id=order_id,
            operation_id=DEFAULT_OPERATION_ID,
            operation_type='create',
            status='requested',
            errors=[],
            items=[],
        ),
        models.PaymentOperation(
            order_id=order_id,
            operation_id=DEFAULT_OPERATION_ID,
            operation_type='update',
            status='requested',
            errors=[],
            items=[],
        ),
        models.PaymentOperation(
            order_id=order_id,
            operation_id='clear',
            operation_type='clear',
            status='requested',
            errors=[],
            items=[],
        ),
        models.PaymentOperation(
            order_id=order_id,
            operation_id=DEFAULT_OPERATION_ID,
            operation_type='cancel',
            status='requested',
            errors=[],
            items=[],
            compensation_id=DEFAULT_COMPENSATION_ID,
        ),
        models.PaymentOperation(
            order_id=order_id,
            operation_id=DEFAULT_OPERATION_ID,
            operation_type='refund',
            status='requested',
            errors=[],
            items=[],
            compensation_id=DEFAULT_COMPENSATION_ID,
        ),
        models.PaymentOperation(
            order_id=order_id,
            operation_id=DEFAULT_OPERATION_ID,
            operation_type='remove',
            status='requested',
            errors=[],
            items=[],
            compensation_id=DEFAULT_COMPENSATION_ID,
        ),
    ]


def check_last_payment_operation(
        order,
        operation_type,
        status='requested',
        total_operations_count=1,
        operation_id=None,
):
    payment_operations = order.payment_operations
    assert len(payment_operations) == total_operations_count

    if total_operations_count > 0:
        payment_operation = payment_operations[-1]

        if operation_id is not None:
            assert payment_operation.operation_id == operation_id
        else:
            if operation_type == 'clear':
                assert payment_operation.operation_id == 'clear'
            else:
                assert payment_operation.operation_id == str(
                    order.cart_version,
                )

        assert payment_operation.operation_type == operation_type
        assert payment_operation.status == status
