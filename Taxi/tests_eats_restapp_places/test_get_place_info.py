EXPECTED_RESPONSE = {
    'places': [
        {
            'place_id': 555,
            'name': '55555',
            'address_full': 'addr555',
            'entrances': [[42.1, 52.0], [43.1, 53.0]],
            'address_comment': {
                'address_comment': 'comment555',
                'type_comment': 'from_partner',
            },
            'entrances_photo': [
                'avatars.mds.yandex.net/get-eda/3807631/0d0a910ca161d'
                '055b9dbfd0518f2b242/555x555',
            ],
        },
        {
            'place_id': 444,
            'name': '44444',
            'address_full': 'addr444',
            'entrances': [[41.1, 51.0]],
            'address_comment': {
                'address_comment': 'comment444_full',
                'type_comment': 'from_partner_and_extsearch_geo',
            },
            'entrances_photo': [
                'avatars.mds.yandex.net/get-eda/3807631/0d0a910ca161d'
                '055b9dbfd0518f2b242/444x444',
            ],
        },
        {
            'place_id': 333,
            'name': '33333',
            'address_full': 'addr333',
            'entrances': [[40.1, 50.0]],
            'address_comment': {
                'address_comment': 'comment333 этаж 3',
                'type_comment': 'from_partner_and_extsearch_geo',
            },
            'entrances_photo': [
                'avatars.mds.yandex.net/get-eda/3807631/0d0a910ca161d'
                '055b9dbfd0518f2b242/333x331',
                'avatars.mds.yandex.net/get-eda/3807631/0d0a910ca161d'
                '055b9dbfd0518f2b242/333x332',
            ],
        },
        {
            'place_id': 111,
            'name': '11111',
            'address_full': 'addr111',
            'address_comment': {
                'address_comment': 'comment111',
                'type_comment': 'from_partner',
            },
            'entrances_photo': [
                'avatars.mds.yandex.net/get-eda/3807631/0d0a910ca161d'
                '055b9dbfd0518f2b242/111x111',
                'avatars.mds.yandex.net/get-eda/3807631/0d0a910ca161d'
                '055b9dbfd0518f2b242/111x112',
            ],
        },
        {
            'place_id': 222,
            'name': '22222',
            'address_full': 'addr222',
            'entrances': [],
            'address_comment': {
                'address_comment': 'comment222 этаж',
                'type_comment': 'from_partner',
            },
            'entrances_photo': [
                'avatars.mds.yandex.net/get-eda/3807631/0d0a910ca161d'
                '055b9dbfd0518f2b242/222x221',
            ],
        },
    ],
}


async def test_address_comment_200(
        mockserver, taxi_eats_restapp_places, load_binary,
):
    @mockserver.json_handler('/extsearch-geo/yandsearch')
    def _mock_extsearch(request):
        assert request.query['business_oid'] in (
            '2222',
            '3333',
            '4444',
            '5555',
        )
        assert request.query['origin'] == 'eats-restapp-place'
        assert request.query['hr'] == 'false'
        assert request.query['ms'] == 'pb'
        assert request.query['gta'] == 'll'
        assert request.query['lang'] == 'ru_RU'
        assert request.query['relev_shorten_address'] == '0'
        assert len(request.query) == 7

        bin_response = ''

        return mockserver.make_response(
            status=200,
            content_type='application/x-protobuf',
            response=bin_response,
        )

    response = await taxi_eats_restapp_places.get(
        '/internal/places/info?place_id=111,222,333,444,555',
    )

    assert response.status_code == 200
    assert response.json() == EXPECTED_RESPONSE
