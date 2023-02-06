import pytest

import tests_inapp_communications.data_generators as datagen

STORIES_PATH = '/4.0/stories'

DEFAULT_YANDEX_UID = 'uid_1'
DEFAULT_USER_ID = 'user_id_1'
DEFAULT_PHONE_ID = 'phone_id_1'

DEFAULT_ID = '8bc1b8648a4d4b2a85d869156c5lllll'


def _build_request(context, order_id=None, location=None):
    body = {'order_id': order_id, 'context': context, 'location': location}
    return dict((k, v) for k, v in body.items() if v is not None)


def _build_query(context, order_id=None):
    return {'order_id': order_id, 'context': context}


def _build_headers(accept_language='ru-RU', pass_flags=None):
    return {
        'X-Yandex-UID': DEFAULT_YANDEX_UID,
        'X-YaTaxi-UserId': DEFAULT_USER_ID,
        'X-YaTaxi-PhoneId': DEFAULT_PHONE_ID,
        'Accept-Language': accept_language,
        'User-Agent': 'android',
        'X-Remote-IP': '2.60.0.0',  # ru ip
        'X-YaTaxi-Pass-Flags': pass_flags,
    }


async def _check_stories_response(
        taxi_inapp_communications, body, query, headers, expected_response,
):
    response_post = await taxi_inapp_communications.post(
        STORIES_PATH, json=body, headers=headers,
    )
    response_get = await taxi_inapp_communications.get(
        STORIES_PATH, params=query, headers=headers,
    )

    assert response_post.status_code == 200
    assert response_get.status_code == 200

    assert response_post.json() == expected_response
    assert response_get.json() == expected_response


def _add_stories_by_countries_config(
        taxi_config,
        context,
        ids=None,
        country=None,
        langs=None,
        country_includes=None,
        country_excludes=None,
):
    value = {context: {'__all__': ids or []}}

    if any([country_includes, country_excludes]) and not all([country, langs]):
        raise ValueError('incorrect arguments')

    if all([country, langs]):
        value[context][country] = {
            lang: {
                'include': (
                    country_includes.get(lang, []) if country_includes else []
                ),
                'exclude': (
                    country_excludes.get(lang, []) if country_excludes else []
                ),
            }
            for lang in langs
        }

    taxi_config.set(STORIES_BY_COUNTRIES_WITH_LOCALE=value)


def _add_cashback_stories_exp(
        experiments3,
        stories=None,
        plus_stories=None,
        no_plus_stories=None,
        cashback_plus_stories=None,
):
    experiments3.add_experiment(
        **datagen.create_experiment(
            name='cashback_stories',
            consumers=['stories/stories'],
            predicates=[
                datagen.create_eq_predicate('yandex_uid', DEFAULT_YANDEX_UID),
                datagen.create_eq_predicate('user_id', DEFAULT_USER_ID),
                datagen.create_eq_predicate('phone_id', DEFAULT_PHONE_ID),
            ],
            value={
                'stories': stories or [],
                'plus_stories': plus_stories,
                'no_plus_stories': no_plus_stories,
                'cashback_plus_stories': cashback_plus_stories,
            },
        ),
    )


def _add_superapp_stories_exp(experiments3, context, ids, zone=None):
    predicates = [
        datagen.create_eq_predicate('yandex_uid', DEFAULT_YANDEX_UID),
        datagen.create_eq_predicate('user_id', DEFAULT_USER_ID),
        datagen.create_eq_predicate('phone_id', DEFAULT_PHONE_ID),
    ]

    if zone is not None:
        predicates.append(datagen.create_eq_predicate('zone_name', zone))

    experiments3.add_experiment(
        **datagen.create_experiment(
            name='superapp_stories',
            consumers=['stories/stories'],
            predicates=predicates,
            value={context: {'stories': [{'id': id} for id in ids]}},
        ),
    )


@pytest.mark.translations(client_messages=datagen.DEFAULT_CLIENT_MESSAGES)
@pytest.mark.parametrize(
    'context', ['eats', 'grocery', 'cashback', 'safety_center'],
)
@pytest.mark.parametrize('lang', ['ru', 'en'])
async def test_get_stories(
        taxi_inapp_communications,
        mockserver,
        experiments3,
        taxi_config,
        context,
        lang,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return datagen.create_promotions_response(
            [datagen.create_promotions_story(DEFAULT_ID)],
        )

    _add_stories_by_countries_config(taxi_config, context, ids=[DEFAULT_ID])
    _add_cashback_stories_exp(experiments3, stories=[DEFAULT_ID])
    _add_superapp_stories_exp(experiments3, context, ids=[DEFAULT_ID])

    await taxi_inapp_communications.invalidate_caches()

    expected_stories_response = datagen.create_stories_response(
        [datagen.create_old_story(DEFAULT_ID, lang)],
    )

    await _check_stories_response(
        taxi_inapp_communications,
        _build_request(context),
        _build_query(context),
        _build_headers(lang),
        expected_stories_response,
    )


@pytest.mark.translations(client_messages=datagen.DEFAULT_CLIENT_MESSAGES)
async def test_stories_by_countries_logic(
        taxi_inapp_communications,
        mockserver,
        taxi_config,
        context='safety_center',
        lang='ru',
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return datagen.create_promotions_response(
            [datagen.create_promotions_story(f'id{i}') for i in range(7)],
        )

    _add_stories_by_countries_config(
        taxi_config,
        context,
        ids=['id3', 'id1', 'id2'],
        country='rus',
        langs=[lang],
        country_includes={lang: ['id1', 'id5', 'id6']},
        country_excludes={lang: ['id2', 'id6']},
    )

    await taxi_inapp_communications.invalidate_caches()

    expected_stories_response = datagen.create_stories_response(
        [
            datagen.create_old_story('id1', lang),
            datagen.create_old_story('id5', lang),
            datagen.create_old_story('id3', lang),
        ],
    )

    await _check_stories_response(
        taxi_inapp_communications,
        _build_request(context),
        _build_query(context),
        _build_headers(lang),
        expected_stories_response,
    )


@pytest.mark.translations(client_messages=datagen.DEFAULT_CLIENT_MESSAGES)
@pytest.mark.parametrize(
    'config_langs,request_lang',
    [
        pytest.param(['ru', 'en'], 'ru', id='same_locale_and_lang_ok'),
        pytest.param(['ru', 'en'], 'en', id='same_locale_and_lang_en_ok'),
        pytest.param(['ru'], 'en', id='diff_locale_and_lang_ru_fallback'),
        pytest.param(['ru'], 'wrong', id='wrong_lang_ru_fallback'),
    ],
)
@pytest.mark.config(STORIES_SERVICE={'default_locale': 'ru'})
async def test_stories_by_locale_logic(
        taxi_inapp_communications,
        mockserver,
        taxi_config,
        config_langs,
        request_lang,
        context='safety_center',
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return datagen.create_promotions_response(
            [datagen.create_promotions_story(f'id{i}') for i in range(7)],
        )

    includes = {lang: ['id1', 'id5', 'id6'] for lang in config_langs}
    excludes = {lang: ['id2', 'id6'] for lang in config_langs}

    _add_stories_by_countries_config(
        taxi_config,
        context,
        ids=['id3', 'id1', 'id2'],
        country='rus',
        langs=config_langs,
        country_includes=includes,
        country_excludes=excludes,
    )

    await taxi_inapp_communications.invalidate_caches()

    expected_stories_response = datagen.create_stories_response(
        [
            datagen.create_old_story('id1', request_lang),
            datagen.create_old_story('id5', request_lang),
            datagen.create_old_story('id3', request_lang),
        ],
    )

    await _check_stories_response(
        taxi_inapp_communications,
        _build_request(context),
        _build_query(context),
        _build_headers(request_lang),
        expected_stories_response,
    )


@pytest.mark.translations(client_messages=datagen.DEFAULT_CLIENT_MESSAGES)
async def test_country_detection_by_order(
        taxi_inapp_communications,
        mockserver,
        order_archive_mock,
        taxi_config,
        context='safety_center',
        lang='ru',
):
    order_id = 'order_id_1'
    zone = 'london'

    order_archive_mock.set_order_proc(
        {
            '_id': order_id,
            'order': {
                '_id': order_id,
                'nz': zone,
                'user_id': DEFAULT_USER_ID,
                'user_uid': DEFAULT_YANDEX_UID,
                'user_locale': '',
            },
        },
    )

    @mockserver.json_handler('/taxi-tariffs/v1/tariff_settings/bulk_retrieve')
    def _mock_tariffs_bulk_retrieve(request):
        return {
            'zones': [
                {
                    'zone': request.query['zone_names'].split(',')[0],
                    'tariff_settings': {'country': 'gbr'},
                },
            ],
        }

    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return datagen.create_promotions_response(
            [datagen.create_promotions_story(DEFAULT_ID)],
        )

    _add_stories_by_countries_config(
        taxi_config,
        context,
        country='gbr',
        langs=[lang],
        country_includes={lang: [DEFAULT_ID]},
    )

    await taxi_inapp_communications.invalidate_caches()

    expected_stories_response = datagen.create_stories_response(
        [datagen.create_old_story(DEFAULT_ID, lang)],
    )

    await _check_stories_response(
        taxi_inapp_communications,
        _build_request(context, order_id=order_id),
        _build_query(context, order_id=order_id),
        _build_headers(lang),
        expected_stories_response,
    )

    assert order_archive_mock.order_proc_retrieve.has_calls
    order_proc_req = order_archive_mock.order_proc_retrieve.next_call()[
        'request'
    ]
    assert order_proc_req.json['id'] == order_id

    assert _mock_tariffs_bulk_retrieve.has_calls
    tariffs_req = _mock_tariffs_bulk_retrieve.next_call()['request']
    assert zone == tariffs_req.query['zone_names'].split(',')[0]


@pytest.mark.translations(client_messages=datagen.DEFAULT_CLIENT_MESSAGES)
async def test_stories_by_countries_filtering(
        taxi_inapp_communications,
        mockserver,
        experiments3,
        taxi_config,
        context='cashback',
        lang='ru',
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return datagen.create_promotions_response(
            [datagen.create_promotions_story(f'id{i}') for i in range(5)],
        )

    _add_stories_by_countries_config(
        taxi_config, context, ids=['id3', 'id1', 'id4'],
    )
    _add_cashback_stories_exp(experiments3, stories=['id1', 'id2', 'id3'])

    await taxi_inapp_communications.invalidate_caches()

    expected_stories_response = datagen.create_stories_response(
        [
            datagen.create_old_story('id1', lang),
            datagen.create_old_story('id3', lang),
        ],
    )

    await _check_stories_response(
        taxi_inapp_communications,
        _build_request(context),
        _build_query(context),
        _build_headers(lang),
        expected_stories_response,
    )


@pytest.mark.translations(client_messages=datagen.DEFAULT_CLIENT_MESSAGES)
@pytest.mark.parametrize('context', ['eats', 'grocery'])
async def test_superapp_stories_order(
        taxi_inapp_communications,
        mockserver,
        experiments3,
        context,
        lang='ru',
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return datagen.create_promotions_response(
            [datagen.create_promotions_story(f'id{i}') for i in range(4)],
        )

    ids = ['id3', 'id1', 'id2']

    _add_superapp_stories_exp(experiments3, context, ids=ids)

    await taxi_inapp_communications.invalidate_caches()

    expected_stories_response = datagen.create_stories_response(
        [datagen.create_old_story(story_id, lang) for story_id in ids],
    )

    await _check_stories_response(
        taxi_inapp_communications,
        _build_request(context),
        _build_query(context),
        _build_headers(lang),
        expected_stories_response,
    )


@pytest.mark.geoareas(filename='db_geoareas.json')
@pytest.mark.tariffs(filename='db_tariffs.json')
@pytest.mark.translations(client_messages=datagen.DEFAULT_CLIENT_MESSAGES)
@pytest.mark.parametrize('context', ['eats', 'grocery'])
@pytest.mark.parametrize(
    'zone_name, location', [('moscow', [37.5, 55.8]), ('spb', [30.29, 59.95])],
)
async def test_superapp_stories_zone_kwarg(
        taxi_inapp_communications,
        mockserver,
        experiments3,
        context,
        zone_name,
        location,
        lang='ru',
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return datagen.create_promotions_response(
            [datagen.create_promotions_story(DEFAULT_ID)],
        )

    _add_superapp_stories_exp(
        experiments3, context, ids=[DEFAULT_ID], zone=zone_name,
    )

    await taxi_inapp_communications.invalidate_caches()

    response_post = await taxi_inapp_communications.post(
        STORIES_PATH,
        json=_build_request(context, location=location),
        headers=_build_headers(lang),
    )

    assert response_post.status_code == 200
    assert response_post.json() == datagen.create_stories_response(
        [datagen.create_old_story(DEFAULT_ID, lang)],
    )


@pytest.mark.translations(client_messages=datagen.DEFAULT_CLIENT_MESSAGES)
@pytest.mark.parametrize(
    'pass_flags,expected_ids',
    [
        pytest.param(
            '',
            ['no_plus_id_1', 'no_plus_id_2', 'common_id_1', 'common_id_2'],
            id='no-passport-flags',
        ),
        pytest.param(
            'portal,pdd',
            ['no_plus_id_1', 'no_plus_id_2', 'common_id_1', 'common_id_2'],
            id='no-ya-plus',
        ),
        pytest.param(
            'phonish,ya-plus',
            ['ya_plus_id_1', 'ya_plus_id_2', 'common_id_1', 'common_id_2'],
            id='has-ya-plus',
        ),
        pytest.param(
            'portal,cashback-plus',
            [
                'cashback_plus_id_1',
                'cashback_plus_id_2',
                'common_id_1',
                'common_id_2',
            ],
            id='has-cashback-plus',
        ),
        pytest.param(
            'portal,ya-plus,cashback-plus',
            [
                'cashback_plus_id_1',
                'cashback_plus_id_2',
                'common_id_1',
                'common_id_2',
            ],
            id='has-cashback-plus-and-ya-plus',
        ),
    ],
)
async def test_cashback_stories_logic(
        taxi_inapp_communications,
        mockserver,
        experiments3,
        pass_flags,
        expected_ids,
        all_ids=(
            'id',
            'common_id_1',
            'common_id_2',
            'no_plus_id_1',
            'no_plus_id_2',
            'ya_plus_id_1',
            'ya_plus_id_2',
            'cashback_plus_id_1',
            'cashback_plus_id_2',
        ),
        context='cashback',
        lang='ru',
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return datagen.create_promotions_response(
            [
                datagen.create_promotions_story(story_id)
                for story_id in all_ids
            ],
        )

    _add_cashback_stories_exp(
        experiments3,
        stories=['common_id_1', 'common_id_2'],
        plus_stories=['ya_plus_id_1', 'ya_plus_id_2'],
        no_plus_stories=['no_plus_id_1', 'no_plus_id_2'],
        cashback_plus_stories=['cashback_plus_id_1', 'cashback_plus_id_2'],
    )

    await taxi_inapp_communications.invalidate_caches()

    expected_stories_response = datagen.create_stories_response(
        [
            datagen.create_old_story(story_id, lang)
            for story_id in expected_ids
        ],
    )

    await _check_stories_response(
        taxi_inapp_communications,
        _build_request(context),
        _build_query(context),
        _build_headers(lang, pass_flags=pass_flags),
        expected_stories_response,
    )


@pytest.mark.translations(client_messages=datagen.DEFAULT_CLIENT_MESSAGES)
async def test_story_not_found(
        taxi_inapp_communications,
        mockserver,
        taxi_config,
        context='business_account',
        lang='ru',
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return datagen.create_promotions_response(
            [datagen.create_promotions_story('id2')],
        )

    _add_stories_by_countries_config(taxi_config, context, ids=['id1', 'id2'])

    await taxi_inapp_communications.invalidate_caches()

    expected_stories_response = datagen.create_stories_response(
        [datagen.create_old_story('id2', lang)],
    )

    await _check_stories_response(
        taxi_inapp_communications,
        _build_request(context),
        _build_query(context),
        _build_headers(lang),
        expected_stories_response,
    )


@pytest.mark.translations(client_messages=datagen.DEFAULT_CLIENT_MESSAGES)
@pytest.mark.parametrize(
    'user_lang, story_locale', [('ru', 'ru'), ('en', 'en'), ('fr', 'ru')],
)
async def test_stories_localization(
        taxi_inapp_communications,
        mockserver,
        taxi_config,
        user_lang,
        story_locale,
        context='safety_center',
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return datagen.create_promotions_response(
            [datagen.create_promotions_story(DEFAULT_ID)],
        )

    _add_stories_by_countries_config(taxi_config, context, ids=[DEFAULT_ID])

    await taxi_inapp_communications.invalidate_caches()

    expected_stories_response = datagen.create_stories_response(
        [datagen.create_old_story(DEFAULT_ID, story_locale)],
    )

    await _check_stories_response(
        taxi_inapp_communications,
        _build_request(context),
        _build_query(context),
        _build_headers(user_lang),
        expected_stories_response,
    )


# skip story due to localization failure exception
@pytest.mark.translations(client_messages=datagen.DEFAULT_CLIENT_MESSAGES)
async def test_default_locale_not_found(
        taxi_inapp_communications,
        mockserver,
        taxi_config,
        user_lang='cz',
        default_locale='fr',
        context='safety_center',
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return datagen.create_promotions_response(
            [datagen.create_promotions_story(DEFAULT_ID)],
        )

    _add_stories_by_countries_config(taxi_config, context, ids=[DEFAULT_ID])

    taxi_config.set(STORIES_SERVICE={'default_locale': default_locale})

    await taxi_inapp_communications.invalidate_caches()

    expected_stories_response = datagen.create_stories_response([])

    await _check_stories_response(
        taxi_inapp_communications,
        _build_request(context),
        _build_query(context),
        _build_headers(user_lang),
        expected_stories_response,
    )
