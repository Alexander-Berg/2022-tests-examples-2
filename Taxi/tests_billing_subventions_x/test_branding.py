import json

import pytest

HANDLE = 'v1/rules/match/'


def get_ids(response):
    match = json.loads(response.content)['match']
    return sorted([x['id'] for x in match])


# No Full Branding ::= NOT (lightbox & sticker)
# in : out (что пролезет через фильтр)
#  F : f || s || l
#  S : s || ~
#  L : l || ~
#  N : n || ~
#


@pytest.mark.parametrize(
    'driver_branding,expected',
    [
        (
            None,
            [
                'g_FullBranding',
                'g_Sticker',
                'g_Lightbox',
                'g_NoBranding',
                'g_NoFullBranding',
                'g_Null',
            ],
        ),
        (
            'full_branding',
            ['g_FullBranding', 'g_Sticker', 'g_Lightbox', 'g_Null'],
        ),
        ('sticker', ['g_Sticker', 'g_NoFullBranding', 'g_Null']),
        ('lightbox', ['g_Lightbox', 'g_NoFullBranding', 'g_Null']),
        ('no_branding', ['g_NoBranding', 'g_NoFullBranding', 'g_Null']),
    ],
)
@pytest.mark.servicetest
async def test_branding(taxi_billing_subventions_x, driver_branding, expected):
    args = {
        'reference_time': '2020-02-02T22:00:22.000Z',
        'zone_name': 'zone0',
        'time_zone': 'UTC',
        'rule_types': ['nmfg'],
    }
    if driver_branding:
        args['driver_branding'] = driver_branding

    response = await taxi_billing_subventions_x.post(HANDLE, args)
    assert response.status_code == 200
    assert get_ids(response) == sorted(expected)
