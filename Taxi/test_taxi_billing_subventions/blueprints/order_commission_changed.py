from taxi_billing_subventions.common import converters


def model(attrs):
    data = doc_data(attrs)
    return converters.convert_to_order_commission_changed_event(data)


def doc(attrs):
    defaults = {
        'doc_id': 0,
        'kind': 'order_commission_changed',
        'external_obj_id': 'alias_id/a93ece2f30ad573fbbb0ffe568ba7f10',
        'external_event_ref': (
            'order_commission_changed/holded_subvention_commissions/'
            '5c58439012062c72b0b2bedb'
        ),
        'process_at': '2018-11-30T19:31:35.000000+00:00',
        'event_at': '2018-11-30T19:31:35.000000+00:00',
        'created': '2018-11-30T19:31:35.000000+00:00',
        'service': 'billing-orders',
        'data': doc_data(attrs.get('data', {})),
        'status': 'new',
        'tags': [],
    }
    defaults.update(attrs)
    return defaults


def doc_data(attrs):
    defaults = {
        'due': '2018-11-30T19:31:35.000000+00:00',
        'tags': [],
        'zone': 'moscow',
        'tzinfo': 'Europe/Moscow',
        'alias_id': 'a93ece2f30ad573fbbb0ffe568ba7f10',
        'order_id': 'ebe919704422526a8b4faf1f4336ce0e',
        'performer': {
            'activity_points': 91,
            'unique_driver_id': '5a21222bd23ea6c588c8efb2',
            'db_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
            'driver_id': '643753730232_5739c79afc0f4ac8890ebb6c188d389c',
        },
        'has_sticker': False,
        'has_lightbox': False,
        'tariff_class': 'econom',
        'commission_change': {
            'amount': '379.68639820755976144',
            'currency': 'RUB',
        },
        'subvention_geoareas': ['moscow', 'test_zone_1', 'modcow'],
        'accepted_by_driver_at': '2018-11-30T19:31:35.000000+00:00',
        'closed_without_accept': False,
        'completed_by_dispatcher': False,
    }
    defaults.update(attrs)
    return defaults
