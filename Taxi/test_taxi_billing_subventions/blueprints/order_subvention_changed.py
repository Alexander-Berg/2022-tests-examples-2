from taxi_billing_subventions.common import converters


def model(attrs):
    data = doc_data(attrs)
    return converters.convert_to_order_subvention_changed_event(data)


def doc(attrs):
    defaults = {
        'doc_id': 4476380086,
        'kind': 'order_subvention_changed',
        'external_obj_id': 'alias_id/3c7b004a67773bb2abd2471f88feef88',
        'external_event_ref': (
            'order_subvention_changed/'
            'holded_subventions/5dde8404e871e189439afc83'
        ),
        'process_at': '2019-11-27T14:12:07.196468+00:00',
        'event_at': '2019-11-27T14:12:07.179357+00:00',
        'created': '2019-11-27T14:12:07.240823+00:00',
        'service': 'billing-orders',
        'data': doc_data(attrs.get('data', {})),
        'status': 'complete',
        'tags': ['taxi/alias_id/3c7b004a67773bb2abd2471f88feef88'],
    }
    defaults.update(attrs)
    return defaults


def doc_data(attrs):
    defaults = {
        'due': '2019-11-27T14:02:00.000000+00:00',
        'tags': ['RepositionOfferFailed'],
        'zone': 'moscow',
        'tzinfo': 'Europe/Moscow',
        'alias_id': '3c7b004a67773bb2abd2471f88feef88',
        'order_id': 'ffd6fa97095f3564af53cfbe2220571f',
        'performer': {
            'db_id': '7f74df331eb04ad78bc2ff25ff88a8f2',
            'driver_id': '643753730233_c697c5d026eb4f44b19c4464ec442acb',
            'activity_points': 100,
            'unique_driver_id': '5b056296e6c22ea26548c925',
            'available_tariff_classes': ['econom'],
            'profile_payment_type_restrictions': 'none',
        },
        'has_sticker': False,
        'has_lightbox': False,
        'tariff_class': 'econom',
        'subvention_change': {
            'amount': '168.0000',
            'currency': 'RUB',
            'amount_by_type': {'mfg': '168.0000'},
        },
        'subvention_geoareas': ['msk-tlbr'],
        'accepted_by_driver_at': '2019-11-27T13:55:52.960000+00:00',
        'closed_without_accept': False,
        'completed_by_dispatcher': False,
    }
    defaults.update(attrs)
    return defaults
