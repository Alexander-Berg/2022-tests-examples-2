def make_suggest_item(registration_number, name, address, carrier_type):
    return {
        'value': name,
        'unrestricted_value': 'ООО рогаИкопыта',
        'data': {
            'hid': 'abc',
            'inn': '123',
            'kpp': '123',
            'ogrn': registration_number,
            'ogrn_date': 1469998800000,
            'type': carrier_type,
            'finance': {'tax_system': 'SRP'},
            'name': {
                'full': 'рогаИкопыта',
                'short': 'рогаИкопыта',
                'full_with_opf': (
                    'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ ' 'рогаИкопыта'
                ),
                'short_with_opf': 'ООО рогаИкопыта',
            },
            'okved': '123',
            'okved_type': '2014',
            'address': address,
            'state': {
                'actuality_date': 1469998800000,
                'registration_date': 1469998800000,
                'status': 'ACTIVE',
                'liquidation_date': None,
            },
        },
    }
