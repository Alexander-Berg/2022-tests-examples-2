import pytest


DEFAULT_BODY = {
    'success': True,
    'data': {
        'id': 1,
        'company_id': 7966356,
        'owner_id': {
            'id': 5809307,
            'name': (
                '\u0410\u043b\u0435\u043a\u0441\u0435\u0439 '
                '\u0412\u043e\u0439\u0442\u0435\u0445'
            ),
            'email': 'voytekh@yandex-team.ru',
            'has_pic': 1,
            'pic_hash': 'd6483a6a1ee2203b967f460b86f80560',
            'active_flag': True,
            'value': 5809307,
        },
        'name': 'Valholl',
        'open_deals_count': 0,
        'related_open_deals_count': 0,
        'closed_deals_count': 0,
        'related_closed_deals_count': 0,
        'email_messages_count': 0,
        'people_count': 0,
        'activities_count': 0,
        'done_activities_count': 0,
        'undone_activities_count': 0,
        'files_count': 0,
        'notes_count': 0,
        'followers_count': 0,
        'won_deals_count': 0,
        'related_won_deals_count': 0,
        'lost_deals_count': 0,
        'related_lost_deals_count': 0,
        'active_flag': True,
        'category_id': None,
        'picture_id': None,
        'country_code': None,
        'first_char': 'v',
        'update_time': '2021-06-30 12:50:39',
        'add_time': '2021-06-30 12:50:39',
        'visible_to': '3',
        'next_activity_date': None,
        'next_activity_time': None,
        'next_activity_id': None,
        'last_activity_id': None,
        'last_activity_date': None,
        'label': None,
        'address': None,
        'address_subpremise': None,
        'address_street_number': None,
        'address_route': None,
        'address_sublocality': None,
        'address_locality': None,
        'address_admin_area_level_1': None,
        'address_admin_area_level_2': None,
        'address_country': None,
        'address_postal_code': None,
        'address_formatted_address': None,
        'c65f1f9256993489daabf9ae850c5c6ff889dcf0': None,
        '16acb3df1deccb6aa57f352062ba676867c5dcba': None,
        'a9b0f6279821fa942793ff42f60b5b6eb961ee27': None,
        '737d2014726bd27471bd426fe1bde712f15773ce': None,
        'd1f3fd06a1353624fdfa3deb9297aed2cdd3dbdf': None,
        'b2d63d8a9a4ce926b4c3fe2989d74daac44dba6a': None,
        '5cc13eb2b4caf137fd5c9d5fd98ceaea57197fa9': None,
        'e7480ce35afd1074394d66643d39937cd806187d': None,
        '8cda0a729605af0b786b69a88ea82c2487aa2dfb': None,
        'fbc99f7699d1648bc9258bfa3972bb2118f92187': None,
        '0174d0eeea28463c7b4036aa4af6cf9398a28a09': None,
        '7f759625b61c32d403deba6af2511335cf91f75e': '3278',  # segment
        '5b564ff19d7bcdc41a2b5bbd9969a3f96d87b3b5': None,
        'b7a96ab01bae714dc1494631c69182eb71d64c47': None,  # city
        '9b0441aabed0134f967bf6b2244dc4c5770ecf7f': None,
        '5745cbdd0609734690d8dd7b8d1dc514932830b1': None,
        '1b8cf6ec97c349f4a3ac99847fc655c2140b7d8f': '3',  # country
        '1c6818cf221ce862aa0589227ac0b59566fc92d1': None,
        '43452cfa37b146980339f791a399ab96a9b20c61': None,
        'b684b6388fc93b3dfa0c7a2cc61cd5f6b3affc85': None,
        '904fc99a50db47fff9a786323f8f2480d26b029b': None,
        'cc_email': 'yandexdelivery-sandbox@pipedrivemail.com',
        'owner_name': (
            '\u0410\u043b\u0435\u043a\u0441\u0435\u0439 '
            '\u0412\u043e\u0439\u0442\u0435\u0445'
        ),
        'edit_name': True,
    },
    'related_objects': {
        'user': {
            '5809307': {
                'id': 5809307,
                'name': (
                    '\u0410\u043b\u0435\u043a\u0441\u0435\u0439 '
                    '\u0412\u043e\u0439\u0442\u0435\u0445'
                ),
                'email': 'voytekh@yandex-team.ru',
                'has_pic': 1,
                'pic_hash': 'd6483a6a1ee2203b967f460b86f80560',
                'active_flag': True,
            },
        },
    },
}


@pytest.mark.parametrize(
    'pipedrive_code, expected_code', ((201, 200), (500, 500)),
)
async def test_func_create_fake_org(
        taxi_cargo_crm, mockserver, pipedrive_code, expected_code,
):
    @mockserver.json_handler('pipedrive-api/v1/organizations')
    def _handler(request):
        body = None
        if pipedrive_code == 201:
            body = DEFAULT_BODY
        return mockserver.make_response(status=pipedrive_code, json=body)

    response = await taxi_cargo_crm.post(
        '/functions/pipedrive/organization/create',
        json={
            'name': 'Valholl',
            'visible_to': '3',
            'owner_id': 5809307,
            'country': '3',
            'city': None,
            'segment': '3278',
        },
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == {'id': 1, 'owner_id': 5809307}
