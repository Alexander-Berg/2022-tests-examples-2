import datetime as dt

from taxi_billing_subventions.common import intervals
from taxi_billing_subventions.common import models


def doc(attrs):
    default_kwargs = {
        'unique_driver_id': '111111111111111111111111',
        'db_id': 'db_id',
        'clid': 'clid',
        'driver_uuid': 'uuid',
        'time_interval': intervals.closed_open(
            dt.datetime(2019, 11, 19, tzinfo=dt.timezone.utc),
            dt.datetime(2019, 11, 19, 0, 0, 1, tzinfo=dt.timezone.utc),
        ),
        'geoarea_activities': [],
        'activity_points': 100.0,
        'profile_payment_type_restrictions': (
            models.ProfilePaymentTypeRestrictions.NONE
        ),
        'tags': frozenset(),
        'available_tariff_classes': frozenset(['econom']),
        'rule_types': [],
    }
    default_kwargs.update(attrs)
    return models.doc.DriverGeoareaActivity(**default_kwargs)
