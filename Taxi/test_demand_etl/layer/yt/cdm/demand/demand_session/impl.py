from copy import deepcopy

from nile.processing.record import Record

COMMON_ATTRIBUTES = dict(
    phone_pd_id='7987654321',
    user_id='foo',
    source_lat=39.3436,
    source_lon=72.8776
)
PIN_ATTRIBUTES = dict(
    event_type='pin',
    sort_order=0,
    tariff_zone='qwerty',
    surge_value=1.,
    estimated_waiting_sec=60.,
    **COMMON_ATTRIBUTES
)
OFFER_ATTRIBUTES = dict(
    event_type='offer',
    sort_order=1,
    **COMMON_ATTRIBUTES
)
ORDER_ATTRIBUTES = dict(
    event_type='order',
    sort_order=2,
    order_application_platform='android',
    success_order_flg=False,
    multiorder_flg=False,
    **COMMON_ATTRIBUTES
)
SESSION_ATTRIBUTES = dict(
    phone_pd_id='7987654321',
    user_id_list=['foo'],
    first_event_lat=39.3436,
    first_event_lon=72.8776,
    last_event_lat=39.3436,
    last_event_lon=72.8776,
    last_tariff_zone='qwerty',
    multiorder_flg=False,
    pin_list=[],
    offer_list=[],
    order_list=[],
    break_reason='timeout',
    first_surge_value=1.,
    last_surge_value=1.,
    first_waiting_time_sec=60.,
    last_waiting_time_sec=60.,
)


def create_default_record(default_args):
    def _record(**kwargs):
        attributes = deepcopy(default_args)
        attributes.update(**kwargs)
        return Record(**attributes)
    return _record

pin_record = create_default_record(PIN_ATTRIBUTES)
offer_record = create_default_record(OFFER_ATTRIBUTES)
order_record = create_default_record(ORDER_ATTRIBUTES)
session_record = create_default_record(SESSION_ATTRIBUTES)
