async def test_update_comment(
        mockserver, taxi_eats_restapp_places, load_binary, get_info_by_place,
):
    @mockserver.json_handler('/extsearch-geo/yandsearch')
    def _mock_extsearch(request):

        if 'business_oid' in request.query:
            assert request.query['business_oid'] in (
                '2222',
                '3333',
                '4444',
                '5555',
                '6666',
                '8888',
                '9999',
            )
        else:
            assert request.query['text'] in ('111 a1', 'макдоналдс a7')
        assert request.query['origin'] == 'eats-restapp-place'
        assert request.query['hr'] == 'false'
        assert request.query['ms'] == 'pb'
        assert request.query['gta'] == 'll'
        assert request.query['lang'] == 'ru_RU'
        assert request.query['relev_shorten_address'] == '0'
        assert len(request.query) == 7

        bin_response = load_binary('response.bin')

        return mockserver.make_response(
            status=200,
            content_type='application/x-protobuf',
            response=bin_response,
        )

    await taxi_eats_restapp_places.run_periodic_task('update-comment-periodic')

    place_info1 = get_info_by_place(111)
    place_info2 = get_info_by_place(222)
    place_info3 = get_info_by_place(333)
    place_info4 = get_info_by_place(444)
    place_info5 = get_info_by_place(555)
    place_info8 = get_info_by_place(888)
    place_info9 = get_info_by_place(999)

    assert place_info1['permalink'] == '1122899103'
    assert place_info1['address_comment'] == 'comment111'
    assert (
        place_info1['full_address_comment']
        == 'comment111\nТРК "Меркурий", этаж 3'
    )
    assert place_info1['entrances'] == '[{"lon":30.204967,"lat":59.989039}]'

    assert place_info2['permalink'] is None
    assert place_info2['address_comment'] == 'comment222 этаж'
    assert place_info2['full_address_comment'] is None
    assert place_info2['entrances'] == '[{"lon":30.204967,"lat":59.989039}]'

    assert place_info3['permalink'] is None
    assert place_info3['address_comment'] == 'comment333 этаж'
    assert place_info3['full_address_comment'] is None
    assert place_info3['entrances'] == '[{"lon":30.204967,"lat":59.989039}]'

    assert place_info4['permalink'] == '1122899103'
    assert place_info4['address_comment'] == 'comment444'
    assert (
        place_info4['full_address_comment']
        == 'comment444\nТРК "Меркурий", этаж 3'
    )
    assert place_info4['entrances'] == '[{"lon":30.204967,"lat":59.989039}]'

    assert place_info5['permalink'] == '1122899103'
    assert (
        place_info5['address_comment']
        == 'comment555comment555comment555comment555comment555comment555commen'
        't555comment555comment555comment555comment555comment555comment555comm'
        'ent555comment555comment555comment555comment555comment555comment555c'
        'omment555comment555comment555comment555comme'
    )
    assert place_info5['full_address_comment'] is None
    assert place_info5['entrances'] == '[{"lon":30.204967,"lat":59.989039}]'

    assert place_info8['permalink'] == '1122899103'
    assert place_info8['address_comment'] == 'comment888'
    assert (
        place_info8['full_address_comment']
        == 'comment888\nТРК "Меркурий", этаж 3'
    )
    assert place_info8['entrances'] == '[{"lon":30.204967,"lat":59.989039}]'

    assert place_info9['permalink'] == '1122899103'
    assert place_info9['address_comment'] == 'comment999'
    assert (
        place_info9['full_address_comment']
        == 'Ориентир/Вход с улицы: со стороны фонтанки\n'
        'Торговый центр: коворкинг Практик 4 этаж\n'
        'Рядом с: ближайший вход к красному мосту\n'
        'Дополнительная информация: из лифта пол пролёта вниз'
    )
    assert place_info9['entrances'] == '[{"lon":30.204967,"lat":59.989039}]'


async def test_update_comment_dbl_etag(
        mockserver, taxi_eats_restapp_places, load_binary, get_info_by_place,
):
    @mockserver.json_handler('/extsearch-geo/yandsearch')
    def _mock_extsearch(request):
        if 'business_oid' in request.query:
            assert request.query['business_oid'] in (
                '2222',
                '3333',
                '4444',
                '5555',
                '6666',
                '8888',
                '9999',
            )
        else:
            assert request.query['text'] in ('111 a1', 'макдоналдс a7')
        assert request.query['origin'] == 'eats-restapp-place'
        assert request.query['hr'] == 'false'
        assert request.query['ms'] == 'pb'
        assert request.query['gta'] == 'll'
        assert request.query['lang'] == 'ru_RU'
        assert request.query['relev_shorten_address'] == '0'
        assert len(request.query) == 7

        bin_response = load_binary('response_double_etag.bin')

        return mockserver.make_response(
            status=200,
            content_type='application/x-protobuf',
            response=bin_response,
        )

    await taxi_eats_restapp_places.run_periodic_task('update-comment-periodic')

    place_info1 = get_info_by_place(111)
    place_info2 = get_info_by_place(222)
    place_info3 = get_info_by_place(333)
    place_info4 = get_info_by_place(444)
    place_info5 = get_info_by_place(555)

    assert place_info1['permalink'] == '208848543478'
    assert place_info1['address_comment'] == 'comment111'
    assert place_info1['full_address_comment'] is None
    assert place_info1['entrances'] == '[{"lon":42.88308,"lat":44.050729}]'

    assert place_info2['permalink'] is None
    assert place_info2['address_comment'] == 'comment222 этаж'
    assert place_info2['full_address_comment'] is None
    assert place_info2['entrances'] == '[{"lon":42.88308,"lat":44.050729}]'

    assert place_info3['permalink'] is None
    assert place_info3['address_comment'] == 'comment333 этаж'
    assert place_info3['full_address_comment'] is None
    assert place_info3['entrances'] == '[{"lon":42.88308,"lat":44.050729}]'

    assert place_info4['permalink'] == '208848543478'
    assert place_info4['address_comment'] == 'comment444'
    assert place_info4['full_address_comment'] is None
    assert place_info4['entrances'] == '[{"lon":42.88308,"lat":44.050729}]'

    assert place_info5['permalink'] == '208848543478'
    assert (
        place_info5['address_comment']
        == 'comment555comment555comment555comment555comment555comment555commen'
        't555comment555comment555comment555comment555comment555comment555comm'
        'ent555comment555comment555comment555comment555comment555comment555c'
        'omment555comment555comment555comment555comme'
    )
    assert place_info5['full_address_comment'] is None
    assert place_info5['entrances'] == '[{"lon":42.88308,"lat":44.050729}]'


async def test_update_comment_pom(
        mockserver, taxi_eats_restapp_places, load_binary, get_info_by_place,
):
    @mockserver.json_handler('/extsearch-geo/yandsearch')
    def _mock_extsearch(request):
        if 'business_oid' in request.query:
            assert request.query['business_oid'] in (
                '2222',
                '3333',
                '4444',
                '5555',
                '6666',
                '8888',
                '9999',
            )
        else:
            assert request.query['text'] in ('111 a1', 'макдоналдс a7')
        assert request.query['origin'] == 'eats-restapp-place'
        assert request.query['hr'] == 'false'
        assert request.query['ms'] == 'pb'
        assert request.query['gta'] == 'll'
        assert request.query['lang'] == 'ru_RU'
        assert request.query['relev_shorten_address'] == '0'
        assert len(request.query) == 7

        bin_response = load_binary('response_pom.bin')

        return mockserver.make_response(
            status=200,
            content_type='application/x-protobuf',
            response=bin_response,
        )

    await taxi_eats_restapp_places.run_periodic_task('update-comment-periodic')

    place_info1 = get_info_by_place(111)
    place_info2 = get_info_by_place(222)
    place_info3 = get_info_by_place(333)
    place_info4 = get_info_by_place(444)
    place_info5 = get_info_by_place(555)

    assert place_info1['permalink'] == '62023563471'
    assert place_info1['address_comment'] == 'comment111'
    assert place_info1['full_address_comment'] == 'comment111\nпомещение 2'
    assert place_info1['entrances'] == '[{"lon":48.05122,"lat":46.3543}]'

    assert place_info2['permalink'] is None
    assert place_info2['address_comment'] == 'comment222 этаж'
    assert place_info2['full_address_comment'] is None
    assert place_info2['entrances'] == '[{"lon":48.05122,"lat":46.3543}]'

    assert place_info3['permalink'] is None
    assert place_info3['address_comment'] == 'comment333 этаж'
    assert place_info3['full_address_comment'] is None
    assert place_info3['entrances'] == '[{"lon":48.05122,"lat":46.3543}]'

    assert place_info4['permalink'] == '62023563471'
    assert place_info4['address_comment'] == 'comment444'
    assert place_info4['full_address_comment'] == 'comment444\nпомещение 2'
    assert place_info4['entrances'] == '[{"lon":48.05122,"lat":46.3543}]'

    assert place_info5['permalink'] == '62023563471'
    assert (
        place_info5['address_comment']
        == 'comment555comment555comment555comment555comment555comment555commen'
        't555comment555comment555comment555comment555comment555comment555comm'
        'ent555comment555comment555comment555comment555comment555comment555c'
        'omment555comment555comment555comment555comme'
    )
    assert (
        place_info5['full_address_comment']
        == 'comment555comment555comment555comment555comment555comment555commen'
        't555comment555comment555comment555comment555comment555comment555comm'
        'ent555comment555comment555comment555comment555comment555comment555c'
        'omment555comment555comment555comment555comme\nпом. 2'
    )
    assert place_info5['entrances'] == '[{"lon":48.05122,"lat":46.3543}]'


async def test_update_comment_digit(
        mockserver, taxi_eats_restapp_places, load_binary, get_info_by_place,
):
    @mockserver.json_handler('/extsearch-geo/yandsearch')
    def _mock_extsearch(request):
        if 'business_oid' in request.query:
            assert request.query['business_oid'] in (
                '2222',
                '3333',
                '4444',
                '5555',
                '6666',
                '8888',
                '9999',
            )
        else:
            assert request.query['text'] in ('111 a1', 'макдоналдс a7')
        assert request.query['origin'] == 'eats-restapp-place'
        assert request.query['hr'] == 'false'
        assert request.query['ms'] == 'pb'
        assert request.query['gta'] == 'll'
        assert request.query['lang'] == 'ru_RU'
        assert request.query['relev_shorten_address'] == '0'
        assert len(request.query) == 7

        bin_response = load_binary('response_digit.bin')

        return mockserver.make_response(
            status=200,
            content_type='application/x-protobuf',
            response=bin_response,
        )

    await taxi_eats_restapp_places.run_periodic_task('update-comment-periodic')

    place_info1 = get_info_by_place(111)
    place_info2 = get_info_by_place(222)
    place_info3 = get_info_by_place(333)
    place_info4 = get_info_by_place(444)
    place_info5 = get_info_by_place(555)

    assert place_info1['permalink'] == '107852018034'
    assert place_info1['address_comment'] == 'comment111'
    assert place_info1['full_address_comment'] is None
    assert place_info1['entrances'] == '[{"lon":41.909414,"lat":45.014729}]'

    assert place_info2['permalink'] is None
    assert place_info2['address_comment'] == 'comment222 этаж'
    assert place_info2['full_address_comment'] is None
    assert place_info2['entrances'] == '[{"lon":41.909414,"lat":45.014729}]'

    assert place_info3['permalink'] is None
    assert place_info3['address_comment'] == 'comment333 этаж'
    assert place_info3['full_address_comment'] is None
    assert place_info3['entrances'] == '[{"lon":41.909414,"lat":45.014729}]'

    assert place_info4['permalink'] == '107852018034'
    assert place_info4['address_comment'] == 'comment444'
    assert place_info4['full_address_comment'] is None
    assert place_info4['entrances'] == '[{"lon":41.909414,"lat":45.014729}]'

    assert place_info5['permalink'] == '107852018034'
    assert (
        place_info5['address_comment']
        == 'comment555comment555comment555comment555comment555comment555commen'
        't555comment555comment555comment555comment555comment555comment555comm'
        'ent555comment555comment555comment555comment555comment555comment555c'
        'omment555comment555comment555comment555comme'
    )
    assert place_info5['full_address_comment'] is None
    assert place_info5['entrances'] == '[{"lon":41.909414,"lat":45.014729}]'


async def test_update_comment_lit(
        mockserver, taxi_eats_restapp_places, load_binary, get_info_by_place,
):
    @mockserver.json_handler('/extsearch-geo/yandsearch')
    def _mock_extsearch(request):
        if 'business_oid' in request.query:
            assert request.query['business_oid'] in (
                '2222',
                '3333',
                '4444',
                '5555',
                '6666',
                '8888',
                '9999',
            )
        else:
            assert request.query['text'] in ('111 a1', 'макдоналдс a7')
        assert request.query['origin'] == 'eats-restapp-place'
        assert request.query['hr'] == 'false'
        assert request.query['ms'] == 'pb'
        assert request.query['gta'] == 'll'
        assert request.query['lang'] == 'ru_RU'
        assert request.query['relev_shorten_address'] == '0'
        assert len(request.query) == 7

        bin_response = load_binary('response_lit.bin')

        return mockserver.make_response(
            status=200,
            content_type='application/x-protobuf',
            response=bin_response,
        )

    await taxi_eats_restapp_places.run_periodic_task('update-comment-periodic')

    place_info1 = get_info_by_place(111)
    place_info2 = get_info_by_place(222)
    place_info3 = get_info_by_place(333)
    place_info4 = get_info_by_place(444)
    place_info5 = get_info_by_place(555)

    assert place_info1['permalink'] == '23748463416'
    assert place_info1['address_comment'] == 'comment111'
    assert place_info1['full_address_comment'] is None
    assert place_info1['entrances'] == '[{"lon":30.010374,"lat":60.014506}]'

    assert place_info2['permalink'] is None
    assert place_info2['address_comment'] == 'comment222 этаж'
    assert place_info2['full_address_comment'] is None
    assert place_info2['entrances'] == '[{"lon":30.010374,"lat":60.014506}]'

    assert place_info3['permalink'] is None
    assert place_info3['address_comment'] == 'comment333 этаж'
    assert place_info3['full_address_comment'] is None
    assert place_info3['entrances'] == '[{"lon":30.010374,"lat":60.014506}]'

    assert place_info4['permalink'] == '23748463416'
    assert place_info4['address_comment'] == 'comment444'
    assert place_info4['full_address_comment'] is None
    assert place_info4['entrances'] == '[{"lon":30.010374,"lat":60.014506}]'

    assert place_info5['permalink'] == '23748463416'
    assert (
        place_info5['address_comment']
        == 'comment555comment555comment555comment555comment555comment555commen'
        't555comment555comment555comment555comment555comment555comment555comm'
        'ent555comment555comment555comment555comment555comment555comment555c'
        'omment555comment555comment555comment555comme'
    )
    assert place_info5['full_address_comment'] is None
    assert place_info5['entrances'] == '[{"lon":30.010374,"lat":60.014506}]'


async def test_update_comment_double(
        mockserver, taxi_eats_restapp_places, load_binary, get_info_by_place,
):
    @mockserver.json_handler('/extsearch-geo/yandsearch')
    def _mock_extsearch(request):

        if 'business_oid' in request.query:
            assert request.query['business_oid'] in (
                '2222',
                '3333',
                '4444',
                '5555',
                '6666',
                '8888',
                '9999',
            )
        else:
            assert request.query['text'] in ('111 a1', 'макдоналдс a7')

        assert request.query['origin'] == 'eats-restapp-place'
        assert request.query['hr'] == 'false'
        assert request.query['ms'] == 'pb'
        assert request.query['gta'] == 'll'
        assert request.query['lang'] == 'ru_RU'
        assert request.query['relev_shorten_address'] == '0'
        assert len(request.query) == 7

        bin_response = load_binary('response_double.bin')

        return mockserver.make_response(
            status=200,
            content_type='application/x-protobuf',
            response=bin_response,
        )

    await taxi_eats_restapp_places.run_periodic_task('update-comment-periodic')

    place_info1 = get_info_by_place(111)
    place_info2 = get_info_by_place(222)
    place_info3 = get_info_by_place(333)
    place_info4 = get_info_by_place(444)
    place_info5 = get_info_by_place(555)
    place_info6 = get_info_by_place(666)

    assert place_info1['permalink'] == '158130001261'
    assert place_info1['address_comment'] == 'comment111'
    assert (
        place_info1['full_address_comment'] == 'comment111\nсо стороны Волги'
    )
    assert place_info1['entrances'] == '[{"lon":44.518919,"lat":48.700467}]'

    assert place_info2['permalink'] is None
    assert place_info2['address_comment'] == 'comment222 этаж'
    assert place_info2['full_address_comment'] is None
    assert place_info2['entrances'] == '[{"lon":44.518919,"lat":48.700467}]'

    assert place_info3['permalink'] is None
    assert place_info3['address_comment'] == 'comment333 этаж'
    assert place_info3['full_address_comment'] is None
    assert place_info3['entrances'] == '[{"lon":44.518919,"lat":48.700467}]'

    assert place_info4['permalink'] == '158130001261'
    assert place_info4['address_comment'] == 'comment444'
    assert (
        place_info4['full_address_comment'] == 'comment444\nсо стороны Волги'
    )
    assert place_info4['entrances'] == '[{"lon":44.518919,"lat":48.700467}]'

    assert place_info5['permalink'] == '158130001261'
    assert (
        place_info5['address_comment']
        == 'comment555comment555comment555comment555comment555comment555commen'
        't555comment555comment555comment555comment555comment555comment555comm'
        'ent555comment555comment555comment555comment555comment555comment555c'
        'omment555comment555comment555comment555comme'
    )
    assert place_info5['full_address_comment'] is None
    assert place_info5['entrances'] == '[{"lon":44.518919,"lat":48.700467}]'

    assert place_info6['permalink'] == '158130001261'
    assert place_info6['address_comment'] == ' Со стороны Волги!!!'
    assert place_info6['full_address_comment'] is None
    assert place_info6['entrances'] == '[{"lon":44.518919,"lat":48.700467}]'


async def test_update_comment_multi(
        mockserver, taxi_eats_restapp_places, load_binary, get_info_by_place,
):
    @mockserver.json_handler('/extsearch-geo/yandsearch')
    def _mock_extsearch(request):

        if 'business_oid' in request.query:
            assert request.query['business_oid'] in (
                '2222',
                '3333',
                '4444',
                '5555',
                '6666',
                '8888',
                '9999',
            )
        else:
            assert request.query['text'] in ('111 a1', 'макдоналдс a7')
        assert request.query['origin'] == 'eats-restapp-place'
        assert request.query['hr'] == 'false'
        assert request.query['ms'] == 'pb'
        assert request.query['gta'] == 'll'
        assert request.query['lang'] == 'ru_RU'
        assert request.query['relev_shorten_address'] == '0'
        assert len(request.query) == 7

        bin_response = load_binary('response_multi.bin')

        return mockserver.make_response(
            status=200,
            content_type='application/x-protobuf',
            response=bin_response,
        )

    await taxi_eats_restapp_places.run_periodic_task('update-comment-periodic')

    place_info = get_info_by_place(777)

    assert place_info['permalink'] == '1084300497'
    assert place_info['address_comment'] == 'comment777'
    assert place_info['full_address_comment'] == 'comment777\nэтаж 1'
    assert place_info['entrances'] == '[{"lon":30.147428,"lat":59.994313}]'
