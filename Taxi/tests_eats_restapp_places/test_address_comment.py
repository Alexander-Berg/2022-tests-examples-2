EXPECTED_RESPONSE1 = {
    'address_comment': 'comment111',
    'type_comment': 'from_partner',
}
EXPECTED_RESPONSE2 = {
    'address_comment': 'comment222 этаж',
    'type_comment': 'from_partner',
}
EXPECTED_RESPONSE3 = {
    'address_comment': 'comment333 этаж 3',
    'type_comment': 'from_partner_and_extsearch_geo',
}
EXPECTED_RESPONSE4 = {
    'address_comment': 'comment444_full',
    'type_comment': 'from_partner_and_extsearch_geo',
}
EXPECTED_RESPONSE5 = {
    'address_comment': 'comment555',
    'type_comment': 'from_partner',
}


async def test_place_info_200(
        mockserver, taxi_eats_restapp_places, load_binary,
):
    @mockserver.json_handler('/extsearch-geo/yandsearch')
    def _mock_extsearch(request):

        bin_response = ''

        return mockserver.make_response(
            status=400,
            content_type='application/x-protobuf',
            response=bin_response,
        )

    response = await taxi_eats_restapp_places.get(
        '/internal/places/address_comment?place_id={}'.format(111),
    )

    assert response.status_code == 200
    assert response.json() == EXPECTED_RESPONSE1

    response = await taxi_eats_restapp_places.get(
        '/internal/places/address_comment?place_id={}'.format(222),
    )

    assert response.status_code == 200
    assert response.json() == EXPECTED_RESPONSE2

    response = await taxi_eats_restapp_places.get(
        '/internal/places/address_comment?place_id={}'.format(333),
    )

    assert response.status_code == 200
    assert response.json() == EXPECTED_RESPONSE3

    response = await taxi_eats_restapp_places.get(
        '/internal/places/address_comment?place_id={}'.format(444),
    )

    assert response.status_code == 200
    assert response.json() == EXPECTED_RESPONSE4

    response = await taxi_eats_restapp_places.get(
        '/internal/places/address_comment?place_id={}'.format(555),
    )

    assert response.status_code == 200
    assert response.json() == EXPECTED_RESPONSE5
