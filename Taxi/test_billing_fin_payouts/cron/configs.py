BILLING_FIN_PAYOUTS_SKIP_NETTING_SERVICES = [
    {
        'start': '1999-01-01T00:00:00.000000+00:00',
        'end': '2099-01-01T00:00:00.000000+00:00',
        'services': [650, 668, 672, 697, 718, 1122, 1124, 1130],
    },
]

BILLING_FIN_PAYOUTS_PRODUCT_WITH_VAT = [
    {
        'start': '1999-01-01T00:00:00.000000+00:00',
        'end': '2099-01-01T00:00:00.000000+00:00',
        'product_with_vat_list': [
            'coupon',
            'subvention',
            'coupon_plus',
            'coupon_plus_scooter',
        ],
    },
]


BILLING_FIN_PAYOUTS_VAT_RATE = [
    {
        'firm_name': 'YATAXI',
        'firm_id': 13,
        'country_settings': [
            {
                'country_name': 'RU',
                'region_id': 225,
                'rate_settings': [
                    {
                        'start': '1999-01-01T00:00:00+00:00',
                        'end': '2021-09-15T00:00:00+00:00',
                        'rate': '18.00',
                    },
                    {
                        'start': '2021-09-15T00:00:00+00:00',
                        'end': '2099-01-01T00:00:00+00:00',
                        'rate': '20.00',
                    },
                ],
            },
            {
                'country_name': 'KAZ',
                'region_id': 145,
                'rate_settings': [
                    {
                        'start': '1999-01-01T00:00:00+00:00',
                        'end': '2021-09-15T00:00:00+00:00',
                        'rate': '5.00',
                    },
                    {
                        'start': '2021-09-15T00:00:00+00:00',
                        'end': '2099-01-01T00:00:00+00:00',
                        'rate': '10.00',
                    },
                ],
            },
        ],
    },
    {
        'firm_name': 'YANDEX',
        'firm_id': 1,
        'country_settings': [
            {
                'country_name': 'RU',
                'region_id': 225,
                'rate_settings': [
                    {
                        'start': '1999-01-01T00:00:00+00:00',
                        'end': '2021-09-15T00:00:00+00:00',
                        'rate': '18.00',
                    },
                    {
                        'start': '2021-09-15T00:00:00+00:00',
                        'end': '2099-01-01T00:00:00+00:00',
                        'rate': '20.00',
                    },
                ],
            },
            {
                'country_name': 'KAZ',
                'region_id': 145,
                'rate_settings': [
                    {
                        'start': '1999-01-01T00:00:00+00:00',
                        'end': '2021-09-15T00:00:00+00:00',
                        'rate': '5.00',
                    },
                    {
                        'start': '2021-09-15T00:00:00+00:00',
                        'end': '2099-01-01T00:00:00+00:00',
                        'rate': '10.00',
                    },
                ],
            },
        ],
    },
]


BILLING_FIN_PAYOUTS_NETTING_SETTINGS = [
    {
        'firm_name': 'YATAXI',
        'firm_id': 13,
        'country_settings': [
            {
                'country_name': 'RU',
                'region_id': 225,
                'netting_settings': [
                    {
                        'start': '1999-01-01T00:00:00+00:00',
                        'end': '2021-09-15T00:00:00+00:00',
                        'services': [111, 128, 124],
                    },
                    {
                        'start': '2021-09-15T00:00:00+00:00',
                        'end': '2099-01-01T00:00:00+00:00',
                        'services': [111, 128, 124, 1161],
                    },
                ],
            },
        ],
    },
]


BILLING_FIN_PAYOUTS_AGENT_REWARD_SETTINGS = [
    {
        'firm_name': 'YATAXI',
        'firm_id': 13,
        'country_settings': [
            {
                'country_name': 'RU',
                'region_id': 225,
                'reward_settings': [
                    {
                        'start': '1999-01-01T00:00:00+00:00',
                        'end': '2021-09-15T00:00:00+00:00',
                        'enabled': False,
                    },
                    {
                        'start': '2021-09-15T00:00:00+00:00',
                        'end': '2099-01-01T00:00:00+00:00',
                        'enabled': True,
                    },
                ],
            },
        ],
    },
]

BILLING_FIN_PAYOUTS_PGAAS_QOS = [
    {'__default__': {'attempts': 3, 'timeout-ms': 500}},
]
