import datetime as dt


def make_daily_guarantee_db_dict(attrs):
    default_kwargs = {
        '_id': '0123456789',
        'branding_type': None,
        'class': [],
        'currency': 'RUB',
        'day_beginning_offset_in_seconds': 0,
        'dayofweek': [],
        'dayridecount': [[40]],
        'dayridecount_days': 1,
        'dayridecount_is_for_any_category': True,
        'display_in_taximeter': True,
        'end': dt.datetime(2019, 5, 11, 21),
        'group_id': 'MSK_GRNT_GROUP_ID2',
        'group_member_id': 'num_orders/10/week_days/1,2,3,4,5,6,7',
        'has_fake_counterpart': False,
        'hour': [],
        'is_bonus': True,
        'is_fake': False,
        'is_once': True,
        'kind': 'daily_guarantee',
        'driver_points': 90,
        'paymenttype': None,
        'region': 'Москва',
        'start': dt.datetime(2018, 5, 9, 21),
        'sub_commission': False,
        'sum': 1000,
        'tariffzone': ['moscow'],
        'time_zone': 'Europe/Moscow',
        'type': 'guarantee',
    }

    default_kwargs.update(attrs)
    return default_kwargs
