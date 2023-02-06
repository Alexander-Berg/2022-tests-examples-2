import pytest


@pytest.mark.pgsql('taxi_exp', files=('default.sql', 'fill.sql'))
async def test_search_fallbacks(taxi_exp_client):
    response = await taxi_exp_client.get(
        '/v1/fallbacks/list/', headers={'YaTaxi-Api-Key': 'secret'},
    )
    assert response.status == 200
    body = await response.json()
    assert body['fallbacks'] == [
        {
            'closed': False,
            'consumers': ['vgw/forwarding'],
            'description': 'DESCRIPTION',
            'enabled': True,
            'is_config': False,
            'last_modified_at': 1,
            'name': 'blacklisted_phones',
            'need_turn_off': True,
            'placeholder': 'link',
            'short_description': 'Short description',
            'what_happens_when_turn_off': 'Blackout',
            'owners': [],
            'department': 'commando',
        },
        {
            'closed': False,
            'consumers': ['api_proxy_tc_3_0_paymethods'],
            'description': 'DESCRIPTION',
            'enabled': True,
            'is_config': False,
            'last_modified_at': 2,
            'name': 'country_merchant_ids',
            'need_turn_off': False,
            'placeholder': 'link',
            'short_description': 'Blah-Blah',
            'what_happens_when_turn_off': 'Crash',
            'owners': [],
        },
        {
            'closed': False,
            'consumers': [
                'protocol/routestats',
                'api_proxy_tc_3_0_paymethods',
            ],
            'description': 'DESCRIPTION',
            'enabled': True,
            'is_config': False,
            'last_modified_at': 3,
            'name': 'default_toll_roads_usage',
            'need_turn_off': False,
            'placeholder': 'link',
            'short_description': 'Nothing',
            'what_happens_when_turn_off': 'Nothing',
            'owners': ['dvasiliev', 'serg-novikov'],
        },
        {
            'closed': False,
            'consumers': ['test_consumer'],
            'description': 'DESCRIPTION - no placeholder',
            'enabled': True,
            'is_config': False,
            'last_modified_at': 6,
            'name': 'no_placeholder',
            'need_turn_off': True,
            'short_description': 'Nothing',
            'what_happens_when_turn_off': 'Nothing',
            'owners': [],
        },
        {
            'closed': False,
            'consumers': ['umlaas'],
            'description': 'DESCRIPTION',
            'enabled': True,
            'is_config': True,
            'last_modified_at': 4,
            'name': 'shortcuts_ranking_timetable',
            'need_turn_off': True,
            'placeholder': 'link',
            'short_description': 'Nothing',
            'what_happens_when_turn_off': 'Nothing',
            'owners': [],
        },
    ]

    response = await taxi_exp_client.get(
        '/v1/fallbacks/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'department': 'commando'},
    )
    assert response.status == 200
    body = await response.json()
    assert body['fallbacks'] == [
        {
            'closed': False,
            'consumers': ['vgw/forwarding'],
            'description': 'DESCRIPTION',
            'enabled': True,
            'is_config': False,
            'last_modified_at': 1,
            'name': 'blacklisted_phones',
            'need_turn_off': True,
            'placeholder': 'link',
            'short_description': 'Short description',
            'what_happens_when_turn_off': 'Blackout',
            'owners': [],
            'department': 'commando',
        },
    ]
