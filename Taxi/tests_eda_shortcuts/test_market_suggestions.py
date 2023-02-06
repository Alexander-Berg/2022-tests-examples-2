import pytest

URL = 'eda-shortcuts/v1/market-suggestions'

TITLE = 'Section'
CATEGORY_ID = 91284
CATEGORY_ID_STR = '91284'
RESOLVE_PRIME = 'resolvePrime'
RESOLVE_GO_SEARCH = 'resolveGoSearch'
IMAGE_URL = (
    '//avatars.mds.yandex.net/get-mpic/5247291/img_id6839126866688694829.jpeg/'
)
RESOLVE_PRIME_RESPONSE = {
    'results': [
        {
            'handler': RESOLVE_PRIME,
            'result': [
                {'id': 'oA', 'schema': 'showPlace'},
                {'id': 'oB', 'schema': 'showPlace'},
            ],
        },
    ],
    'collections': {
        'category': [{'id': CATEGORY_ID, 'name': TITLE}],
        'visibleEntity': [
            {'id': 've1', 'referenceEntity': 'showPlace'},
            {'id': 've2', 'referenceEntity': 'showPlace'},
        ],
        'offer': [
            {
                'id': 'oB',
                'categoryIds': [CATEGORY_ID],
                'productId': 4322,
                'titles': {'raw': 'Product B'},
                'price': {'value': 12.345, 'currency': 'USD'},
                'slug': 'sluslu',
                'pictures': [],
            },
            {
                'id': 'oA',
                'categoryIds': [CATEGORY_ID],
                'productId': 4321,
                'titles': {'raw': 'Offer A'},
                'discount': {
                    'currentPrice': {'value': 123.45, 'currency': 'RUR'},
                    'oldPrice': {'value': 1234.5, 'currency': 'RUR'},
                },
                'pictures': [],
            },
        ],
    },
}


@pytest.mark.translations(
    tariff={
        'currency.rub': {'ru': 'руб', 'en': 'rub'},
        'currency.usd': {'ru': 'usd', 'en': 'usd'},
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency_sign.rub': {'ru': '₽'},
    },
)
@pytest.mark.parametrize(
    'accept_language, formatted_large_num, scale, image_suffixes'
    ', cache_seconds',
    [
        pytest.param('ru', '1234', 1.5, ('180x240', '8hq'), 0, id='ru'),
        pytest.param(
            'ru', '1234', 10, ('900x1200', '9hq'), 10, id='max',
        ),  # use maximum resolution as we can
        pytest.param(
            'ru', '1234', 0.1, ('50x50', '1hq'), 30, id='min',
        ),  # use minimum resolution even if it's bigger than requested
        pytest.param(
            'en;q=1, ru-US;q=0.9',
            '1,234',
            1.5,
            ('180x240', '8hq'),
            60,
            id='en',
        ),
    ],
)
@pytest.mark.parametrize(
    'request_body, expected_fapi_request, cache_key, fapi_response, '
    'expected_collections, expected_title',
    [
        pytest.param(
            {'limit': 3},
            [
                'resolveDJUniversalProducts',
                {
                    'params': [
                        {
                            'djPlace': 'go_express_retargeting_block',
                            'numdoc': 3,
                            'page': 1,
                            'puid': '4073058016',
                        },
                    ],
                },
            ],
            '|'.join(
                (
                    '{"params":['
                    '{"djPlace":"go_express_retargeting_block",'
                    '"puid":"4073058016","numdoc":3,"page":1}'
                    ']}',
                    'q:deviceid:AM-DEV',
                    'q:name:resolveDJUniversalProducts',
                    'q:uuid:AM-UUID',
                    'h:Content-Type:application/json',
                    'h:X-Region-Id:100697',
                    'h:api-platform:WEDROID',
                ),
            ),
            {
                'results': [
                    {
                        'handler': 'resolveDJUniversalProducts',
                        'result': 'nert3xwq6tf',
                    },
                ],
                'djResult': [
                    {
                        'id': 'nert3xwq6tf',
                        'title': 'Section',
                        'visibleEntityIds': ['veB', 'veA'],
                    },
                ],
            },
            [{'id': 'nert3xwq6tf', 'items': ['oB', 'oA'], 'title': 'Section'}],
            'Section',
            id='compatibility',
        ),
        pytest.param(
            {
                'collections': [
                    {
                        'id': 'cA',
                        'name': 'resolveDJUniversalProducts',
                        'param': {'numdoc': 3},
                    },
                    {
                        'id': 'cB',
                        'name': 'resolveDJUniversalProducts',
                        'param': {
                            'djPlace': 'go_express_retargeting_block',
                            'numdoc': 3,
                            'page': 1,
                            'puid': '4073058016',
                        },
                    },
                ],
            },
            [
                'resolveDJUniversalProducts,resolveDJUniversalProducts',
                {
                    'params': [
                        {'numdoc': 3},
                        {
                            'djPlace': 'go_express_retargeting_block',
                            'numdoc': 3,
                            'page': 1,
                            'puid': '4073058016',
                        },
                    ],
                },
            ],
            '|'.join(
                (
                    '{"params":['
                    '{"numdoc":3},'
                    '{"djPlace":"go_express_retargeting_block",'
                    '"numdoc":3,"page":1,"puid":"4073058016"}'
                    ']}',
                    'q:deviceid:AM-DEV',
                    (
                        'q:name:resolveDJUniversalProducts'
                        ',resolveDJUniversalProducts'
                    ),
                    'q:uuid:AM-UUID',
                    'h:Content-Type:application/json',
                    'h:X-Region-Id:100697',
                    'h:api-platform:WEDROID',
                ),
            ),
            {
                'results': [
                    {
                        'handler': 'resolveDJUniversalProducts',
                        'result': 'nert3xwq6tf',
                    },
                    {
                        'handler': 'resolveDJUniversalProducts',
                        'result': 'nert3xwq6tf2',
                    },
                ],
                'djResult': [
                    {'id': 'nert3xwq6tf', 'visibleEntityIds': ['veB', 'veA']},
                    {
                        'id': 'nert3xwq6tf2',
                        'title': 'Section 2',
                        'visibleEntityIds': ['veB'],
                    },
                ],
            },
            [
                {'id': 'cA', 'items': ['oB', 'oA']},
                {'id': 'cB', 'title': 'Section 2', 'items': ['oB']},
            ],
            None,
            id='multi-collection',
        ),
        pytest.param(
            {'limit': 2, 'tags': ['flowers', 'some-tag']},
            [
                RESOLVE_PRIME,
                {
                    'params': [
                        {
                            'hid': [91284],
                            'billingZone': 'default',
                            'filter-express-delivery': '1',
                            'count': 2,
                        },
                    ],
                },
            ],
            '|'.join(
                (
                    '{"params":['
                    '{"hid":[91284],"billingZone":"default",'
                    '"filter-express-delivery":"1","count":2}'
                    ']}',
                    'q:deviceid:AM-DEV',
                    'q:name:resolvePrime',
                    'q:uuid:AM-UUID',
                    'h:Content-Type:application/json',
                    'h:X-Region-Id:100697',
                    'h:api-platform:WEDROID',
                ),
            ),
            None,
            [{'id': CATEGORY_ID_STR, 'items': ['oB', 'oA'], 'title': TITLE}],
            TITLE,
            id='products_by_category',
        ),
        pytest.param(
            {'tags': ['new-api'], 'point_a': [37, 55]},
            [
                RESOLVE_GO_SEARCH,
                {
                    'params': [
                        {
                            'nid': [222],
                            'billingZone': 'default',
                            'filter-express-delivery': '1',
                            'count': 5,
                        },
                    ],
                },
            ],
            '|'.join(
                (
                    '{"params":['
                    '{"nid":[222],"billingZone":"default",'
                    '"filter-express-delivery":"1","count":5}'
                    ']}',
                    'q:deviceid:AM-DEV',
                    'q:gps:37.000000,55.000000',
                    'q:name:resolveGoSearch',
                    'q:uuid:AM-UUID',
                    'h:Content-Type:application/json',
                    'h:X-Region-Id:100697',
                    'h:api-platform:WEDROID',
                ),
            ),
            None,
            [{'id': CATEGORY_ID_STR, 'items': ['oB', 'oA'], 'title': TITLE}],
            TITLE,
            id='products_by_category_new_api',
        ),
        pytest.param(
            {'tags': ['new-api-all-products'], 'point_a': [37, 55]},
            [
                RESOLVE_GO_SEARCH,
                {
                    'params': [
                        {
                            'nid': [222],
                            'billingZone': 'default',
                            'filter-express-delivery': '0',
                            'count': 5,
                            'returnAllProducts': True,
                        },
                    ],
                },
            ],
            '|'.join(
                (
                    '{"params":['
                    '{"nid":[222],"billingZone":"default",'
                    '"filter-express-delivery":"0","count":5,'
                    '"returnAllProducts":true}]}',
                    'q:deviceid:AM-DEV',
                    'q:gps:37.000000,55.000000',
                    'q:name:resolveGoSearch',
                    'q:uuid:AM-UUID',
                    'h:Content-Type:application/json',
                    'h:X-Region-Id:100697',
                    'h:api-platform:WEDROID',
                ),
            ),
            None,
            [{'id': CATEGORY_ID_STR, 'items': ['oB', 'oA'], 'title': TITLE}],
            TITLE,
            id='products_by_category_new_api_all_products',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_market_express_suggestions.json')
async def test_simple(
        taxi_eda_shortcuts,
        mockserver,
        taxi_config,
        load_json,
        accept_language,
        formatted_large_num,
        scale,
        image_suffixes,
        cache_seconds,
        request_body,
        expected_fapi_request,
        cache_key,
        fapi_response,
        expected_collections,
        expected_title,
):
    caching_enabled = cache_seconds > 0
    taxi_config.set_values(
        {
            'EDA_SHORTCUTS_MARKET_SUGGESTIONS': {
                'cache_seconds': cache_seconds,
                'enabled': caching_enabled,
            },
        },
    )

    await taxi_eda_shortcuts.invalidate_caches()

    cache = {}

    is_category_suggestion = expected_fapi_request[0] in {
        RESOLVE_PRIME,
        RESOLVE_GO_SEARCH,
    }

    @mockserver.json_handler('/api-cache/v1/cached-value/market-suggestions')
    async def _api_cache_mock(request):
        nonlocal cache
        assert request.query == {'key': cache_key}
        key = request.query['key']
        if request.method == 'GET':
            cached = cache.get(key)
            if cached:
                return mockserver.make_response(cached, status=200)
            return mockserver.make_response(status=404)
        if request.method == 'PUT':
            assert (
                request.headers['Cache-Control'] == f'max-age={cache_seconds}'
            )
            bytes_body = request.get_data()
            cache[key] = bytes_body

    @mockserver.json_handler('/market-ipa-internal/api/v1')
    def _market_ipa_internal_mock(request):
        expected_query = {
            'name': expected_fapi_request[0],
            'deviceid': 'AM-DEV',
            'uuid': 'AM-UUID',
        }
        if 'point_a' in request_body:
            lon, lat = request_body['point_a']
            expected_query['gps'] = f'{lon:.6f},{lat:.6f}'
        assert request.query == expected_query
        assert request.json == expected_fapi_request[1]
        if is_category_suggestion:
            picture = load_json('resolvePrimeResponsePicture.json')
            response = RESOLVE_PRIME_RESPONSE
            response['collections']['offer'][0]['pictures'] = [picture]
            response['collections']['offer'][1]['pictures'] = [picture]
            return response

        example = load_json('resolveDJUniversalProducts.json')
        return {
            'results': fapi_response['results'],
            'collections': {
                'djResult': fapi_response['djResult'],
                'visibleEntity': [
                    {
                        'id': 'veA',
                        'referenceEntity': 'showPlace',
                        'showPlaceId': 'ospA',
                        'offerShowPlaceId': 'xx',
                    },
                    {
                        'id': 'veB',
                        'referenceEntity': 'offerShowPlace',
                        'showPlaceId': 'xx',
                        'offerShowPlaceId': 'ospB',
                    },
                    {
                        'id': 'veC',
                        'referenceEntity': 'productShowPlace',
                        'productShowPlaceId': 'pspC',
                    },
                ],
                'product': [
                    {'id': 4321, 'description': 'bla-bla'},
                    {
                        'id': 4322,
                        'description': 'la-la-la',
                        'titles': {'raw': 'Product B'},
                        'slug': 'sluslu',
                    },
                ],
                'offer': [
                    {
                        'id': 'oA',
                        'productId': 4321,
                        'pictures': [
                            {
                                'original': {
                                    'namespace': 'marketpic',
                                    'groupId': 312,
                                    'key': 'pikA',
                                },
                            },
                        ],
                        'titles': {'raw': 'Offer A'},
                        'discount': {
                            'currentPrice': {
                                'value': 123.45,
                                'currency': 'RUR',
                            },
                            'oldPrice': {'value': 1234.5, 'currency': 'RUR'},
                        },
                    },
                    {
                        'id': 'oB',
                        'productId': 4322,
                        'pictures': [
                            {
                                'original': {
                                    'namespace': 'mpic',
                                    'groupId': 313,
                                    'key': 'pikB',
                                },
                            },
                        ],
                        'modelAwareTitles': {'raw': 'Offer Bma'},
                        'titles': {'raw': 'Offer Bt'},
                        'price': {'value': 12.345, 'currency': 'USD'},
                    },
                ],
                'showPlace': [{'id': 'ospA', 'offerId': 'oA'}],
                'offerShowPlace': [
                    {
                        'id': 'ospB',
                        'entity': 'offerShowPlace',
                        'offerId': 'oB',
                    },
                ],
                'productShowPlace': [],
                'knownThumbnail': example['knownThumbnail'],
                'thumbnail': example['thumbnail'],
            },
        }

    body = {
        'api_platform': 'WEDROID',
        'region_id': 100697,
        'media_size_info': {'scale': scale},
        'image_size': 144,
    }
    body.update(request_body)
    headers = {
        'Accept-Language': accept_language,
        'X-Yandex-UID': '4073058016',
        'X-AppMetrica-UUID': 'AM-UUID',
        'X-AppMetrica-DeviceId': 'AM-DEV',
    }
    response = await taxi_eda_shortcuts.post(URL, headers=headers, json=body)
    assert response.status_code == 200

    expected_json = {
        'collections': expected_collections,
        'suggestions': [
            {
                'id': 'oB',
                'image_url': (
                    IMAGE_URL + image_suffixes[0]
                    if is_category_suggestion
                    else 'mpic/313/pikB/' + image_suffixes[1]
                ),
                'title': 'Product B',
                'price': {
                    'formatted': '12 ₽',
                    'value': '12',
                    'currency': 'RUB',  # TODO: add currency support on demand
                },
                'product': {'id': 4322, 'slug': 'sluslu'},
            },
            {
                'id': 'oA',
                'image_url': (
                    IMAGE_URL + image_suffixes[0]
                    if is_category_suggestion
                    else 'marketpic/312/pikA/' + image_suffixes[0]
                ),
                'title': 'Offer A',
                'price': {
                    'formatted': '123 ₽',
                    'value': '123',
                    'currency': 'RUB',
                },
                'price_before_discount': {
                    'formatted': formatted_large_num + ' ₽',
                    'value': formatted_large_num,
                    'currency': 'RUB',
                },
                'product': {'id': 4321},
            },
        ],
    }
    if expected_title:
        expected_json['title'] = expected_title
    assert response.json() == expected_json

    response2 = await taxi_eda_shortcuts.post(URL, headers=headers, json=body)
    assert response2.json() == response.json()

    if caching_enabled:
        assert _api_cache_mock.times_called == 3
        assert _market_ipa_internal_mock.times_called == 1
    else:
        assert _api_cache_mock.times_called == 0
        assert _market_ipa_internal_mock.times_called == 2
