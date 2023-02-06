import datetime as dt

import pytest


@pytest.mark.parametrize(
    'country_code, tariff_zone, event_at, netting_enabled, '
    'mfg_netting_enabled, mfg_geo_netting_enabled, commission_netting_enabled',
    [
        # country miss
        (
            'rus',
            'spb',
            '2022-05-01T11:00:00+03:00',
            False,
            False,
            False,
            False,
        ),
        # tariff zone miss
        (
            'azn',
            'bbb',
            '2022-05-01T11:00:00+03:00',
            False,
            False,
            False,
            False,
        ),
        # mfg and commission enabled in baku
        ('azn', 'baku', '2022-05-01T11:00:00+03:00', True, True, False, True),
        # all enabled everywhere
        ('azn', 'baku', '2022-05-11T11:00:00+03:00', True, True, True, True),
        # all disabled everywhere
        (
            'azn',
            'baku',
            '2022-05-21T11:00:00+03:00',
            False,
            False,
            False,
            False,
        ),
    ],
)
@pytest.mark.config(
    BILLING_FUNCTIONS_NETTING_CONFIG={
        'azn': [
            {
                'since': '2022-04-30T21:00:00+03:00',
                'zones': ['baku'],
                'kinds': ['mfg'],
                'netting': 'full',
                'commission_netting': True,
            },
            {
                'since': '2022-05-10T21:00:00+03:00',
                'zones': ['*'],
                'kinds': ['mfg', 'mfg_geo'],
                'netting': 'full',
                'commission_netting': True,
            },
            {
                'since': '2022-05-20T21:00:00+03:00',
                'zones': ['*'],
                'kinds': [],
                'netting': 'none',
                'commission_netting': False,
            },
        ],
    },
)
def test_netting_config(
        country_code,
        tariff_zone,
        event_at,
        netting_enabled,
        mfg_netting_enabled,
        mfg_geo_netting_enabled,
        commission_netting_enabled,
        stq3_context,
):
    netting_config = stq3_context.countries.get_netting_config(
        country_code=country_code,
        tariff_zone=tariff_zone,
        event_at=dt.datetime.fromisoformat(event_at),
    )
    assert netting_config.is_netting_enabled() is netting_enabled
    assert netting_config.is_netting('mfg') is mfg_netting_enabled
    assert netting_config.is_netting('mfg_geo') is mfg_geo_netting_enabled
    assert (
        netting_config.is_netting('subvention_commission')
        is commission_netting_enabled
    )
