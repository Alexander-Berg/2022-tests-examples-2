from taxi_billing_subventions.common import models


def doc(attrs: dict) -> models.doc.ShiftEnded:
    default_kwargs: dict = {
        'shift': None,
        'subscription_ref': None,
        'driver_work_mode': 'orders',
        'rule_data': None,
        'active_contracts': [],
    }
    default_kwargs.update(attrs)
    return models.doc.ShiftEnded(**default_kwargs)  # type: ignore
