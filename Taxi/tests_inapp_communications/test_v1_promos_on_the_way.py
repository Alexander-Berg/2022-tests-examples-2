import hashlib
import random

import pytest

import tests_inapp_communications.data_generators as datagen


HANDLER_PATH = '/inapp-communications/v1/promos-on-the-way'

DEFAULT_ID = '8bc1b8648a4d4b2a85d869156c5lllll'
DEFAULT_ID_2 = '8bc1b8648a4d4b2a85d869156c5llll2'

DEFAULT_YANDEX_UID = 'uid_1'
DEFAULT_USER_ID = 'user_id_1'
DEFAULT_PHONE_ID = 'phone_id_1'
DEFAULT_SUPPORTED_WIDGETS = ['toggle']
DEFAULT_TARIFF_CLASS = 'econom'
DEFAULT_POINT_A = [37.5, 55.8]  # moscow
DEFAULT_POINT_B = [30.29, 59.95]  # spb
DEFAULT_DRIVER_ID = 'driver_id'
DEFAULT_EXTRA_USER_PHONE_ID = 'extra_user_phone_id'
DEFAULT_SHARING_KEY = 'sharing_key_1'
DEFAULT_STATUS = 'driving'
DEFAULT_MEDIA_SIZE_INFO = {
    'screen_height': 1920,
    'screen_width': 1080,
    'scale': 1,
}
DEFAULT_ALTERNATIVE_TYPE = 'perfect_chain'
DEFAULT_ALT_OFFER_FINAL_DISCOUNT = 28.8
DEFAULT_CURRENCY = 'RUB'


def _build_request_body(driver=None):
    result = {
        'supported_widgets': DEFAULT_SUPPORTED_WIDGETS,
        'tariff_class': DEFAULT_TARIFF_CLASS,
        'point_a': DEFAULT_POINT_A,
        'point_b': DEFAULT_POINT_B,
        'driver_id': DEFAULT_DRIVER_ID,
        'extra_user_phone_id': DEFAULT_EXTRA_USER_PHONE_ID,
        'sharing_key': DEFAULT_SHARING_KEY,
        'status': DEFAULT_STATUS,
        'media_size_info': DEFAULT_MEDIA_SIZE_INFO,
        'alternative_type': DEFAULT_ALTERNATIVE_TYPE,
        'alt_offer_final_discount': DEFAULT_ALT_OFFER_FINAL_DISCOUNT,
    }
    if driver:
        result.update(driver)
    return result


def _build_headers(lang='ru'):
    return {
        'X-Yandex-UID': DEFAULT_YANDEX_UID,
        'X-YaTaxi-UserId': DEFAULT_USER_ID,
        'X-YaTaxi-PhoneId': DEFAULT_PHONE_ID,
        'X-Request-Language': lang,
    }


def _build_totw_promotions_exp(
        name=datagen.DEFAULT_TOTW_PROMOTIONS_EXP_NAME, zone='moscow',
):
    predicates = [
        datagen.create_eq_predicate('yandex_uid', DEFAULT_YANDEX_UID),
        datagen.create_eq_predicate('user_id', DEFAULT_USER_ID),
        datagen.create_eq_predicate('phone_id', DEFAULT_PHONE_ID),
        datagen.create_eq_predicate('tariff_class', DEFAULT_TARIFF_CLASS),
        datagen.create_eq_predicate('zone', zone),
        datagen.create_eq_predicate('driver_id', DEFAULT_DRIVER_ID),
        datagen.create_eq_predicate(
            'is_order_for_other', True, arg_type='bool',
        ),
        datagen.create_eq_predicate('status', DEFAULT_STATUS),
    ]
    return datagen.create_experiment(
        name=name,
        consumers=['totw/promotions'],
        predicates=predicates,
        value={'enabled': True},
    )


def _gen_id():
    return hashlib.sha1(str(random.random()).encode('ascii')).hexdigest()


def _gen_stories(with_mediatags=False):
    return [
        datagen.create_promotions_story(
            DEFAULT_ID,
            name='legit',
            active=True,
            story_context='totw',
            zones=['rus'],
            with_mediatags=with_mediatags,
        ),
        datagen.create_promotions_story(
            DEFAULT_ID_2,
            name='match_all',
            active=True,
            story_context='totw',
            zones=[],
            with_mediatags=with_mediatags,
        ),
        datagen.create_promotions_story(
            _gen_id(),
            name='not_active',
            active=False,
            story_context='totw',
            zones=['rus'],
            with_mediatags=with_mediatags,
        ),
        datagen.create_promotions_story(
            _gen_id(),
            name='not_in_zone',
            active=True,
            story_context='totw',
            zones=['unk'],
            with_mediatags=with_mediatags,
        ),
        datagen.create_promotions_story(
            _gen_id(),
            name='no_context',
            active=True,
            zones=['rus'],
            with_mediatags=with_mediatags,
        ),
        datagen.create_promotions_story(
            _gen_id(),
            name='not_totw_context',
            active=True,
            story_context='grocery',
            zones=['rus'],
            with_mediatags=with_mediatags,
        ),
    ]


def _create_stories_response(stories):
    return {
        'match': {'views': ['ask_feedback', 'transporting']},
        'type': 'stories',
        'stories': stories,
    }


def _sort_stories(stories):
    return sorted(stories, key=lambda story: story['name'])


def _sort_response(response):
    response['legacy_stories']['stories'] = _sort_stories(
        response['legacy_stories']['stories'],
    )

    return response


def _create_response(stories, banners):
    stories = _sort_stories(stories)

    return {
        'legacy_stories': _create_stories_response(stories),
        'promotions': {
            'banners': {'items': banners},
            'promoblocks': {'items': []},
        },
        'notifications': {},
    }


def _create_keyset_totw_notifications():
    result = datagen.DEFAULT_BACKEND_PROMOTIONS
    result.update(
        {
            'order_cancel_notification.title_with_name': {
                'ru': 'Водитель %(short_name)s уже едет к вам',
            },
            'order_cancel_notification.title_without_name': {
                'ru': 'Водитель уже едет к вам',
            },
            'order_cancel_notification.text': {
                'ru': (
                    'Если сейчас отменить, '
                    'поиск новой машины может быть дольше'
                ),
            },
            'order_cancel_notification.cancel_button.text': {
                'ru': 'Отменить поездку',
            },
            'order_cancel_notification.do_nothing_button.text': {
                'ru': 'Подождать водителя',
            },
            'order_cancen_notification.icon.accessibility_with_rating': {
                'ru': 'Фото водителя, рейтинг %(rating)s',
            },
            'order_cancen_notification.icon.accessibility_no_rating': {
                'ru': 'Фото водителя',
            },
        },
    )
    return result


@pytest.mark.geoareas(filename='db_geoareas.json')
@pytest.mark.tariffs(filename='db_tariffs.json')
@pytest.mark.translations(
    client_messages=datagen.DEFAULT_CLIENT_MESSAGES,
    backend_promotions=datagen.DEFAULT_BACKEND_PROMOTIONS,
)
@pytest.mark.parametrize(
    'with_mediatags',
    [
        pytest.param(False, id='without_mediatags'),
        pytest.param(True, id='with_mediatags'),
    ],
)
async def test_totw_legacy_stories(
        taxi_inapp_communications, mockserver, with_mediatags,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return datagen.create_promotions_response(
            _gen_stories(with_mediatags=with_mediatags),
        )

    response = await taxi_inapp_communications.post(
        HANDLER_PATH,
        json={'point_a': [37.62, 55.75], 'tariff_class': 'econom'},
        headers=_build_headers(),
    )
    assert response.status_code == 200
    assert response.headers['Cache-Control'] == 'max-age=300'
    stories = [
        datagen.create_old_story(
            DEFAULT_ID_2, 'ru', active=True, name='match_all',
        ),
        datagen.create_old_story(DEFAULT_ID, 'ru', active=True, name='legit'),
    ]

    assert _sort_response(response.json()) == _create_response(stories, [])


@pytest.mark.geoareas(filename='db_geoareas.json')
@pytest.mark.tariffs(filename='db_tariffs.json')
@pytest.mark.translations(
    client_messages=datagen.DEFAULT_CLIENT_MESSAGES,
    backend_promotions=datagen.DEFAULT_BACKEND_PROMOTIONS,
)
@pytest.mark.parametrize('lang', ['ru', 'en'])
async def test_totw_banners_mapping(
        taxi_inapp_communications, mockserver, experiments3, lang,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return datagen.create_promotions_response(
            totw_banners=[datagen.create_promotions_totw_banner('id1')],
        )

    experiments3.add_experiment(**_build_totw_promotions_exp())

    await taxi_inapp_communications.invalidate_caches()

    response = await taxi_inapp_communications.post(
        HANDLER_PATH,
        json=_build_request_body(),
        headers=_build_headers(lang=lang),
    )
    assert response.status_code == 200
    assert response.headers['Cache-Control'] == 'max-age=300'

    totw_banners = response.json()['promotions']['banners']['items']

    assert len(totw_banners) == 1
    assert totw_banners[0] == datagen.create_inapp_totw_banner(
        'id1', locale=lang,
    )


@pytest.mark.geoareas(filename='db_geoareas.json')
@pytest.mark.tariffs(filename='db_tariffs.json')
@pytest.mark.translations(
    client_messages=datagen.DEFAULT_CLIENT_MESSAGES,
    backend_promotions=datagen.DEFAULT_BACKEND_PROMOTIONS,
)
async def test_totw_banners_order(
        taxi_inapp_communications, mockserver, experiments3,
):

    promotions_totw_banners = [
        datagen.create_promotions_totw_banner(f'id{i}', priority=i)
        for i in range(10)
    ]

    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return datagen.create_promotions_response(
            totw_banners=promotions_totw_banners,
        )

    experiments3.add_experiment(**_build_totw_promotions_exp())

    await taxi_inapp_communications.invalidate_caches()

    response = await taxi_inapp_communications.post(
        HANDLER_PATH, json=_build_request_body(), headers=_build_headers(),
    )
    assert response.status_code == 200
    assert response.headers['Cache-Control'] == 'max-age=300'

    totw_banners = response.json()['promotions']['banners']['items']

    assert len(totw_banners) == len(promotions_totw_banners)

    priorities = [totw_banner['priority'] for totw_banner in totw_banners]

    assert priorities == sorted(priorities)[::-1]


@pytest.mark.geoareas(filename='db_geoareas.json')
@pytest.mark.tariffs(filename='db_tariffs.json')
@pytest.mark.translations(
    client_messages=datagen.DEFAULT_CLIENT_MESSAGES,
    backend_promotions=datagen.DEFAULT_BACKEND_PROMOTIONS,
)
async def test_totw_banners_exp_matching(
        taxi_inapp_communications, mockserver, experiments3,
):
    custom_exp_name = 'custom_exp'

    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return datagen.create_promotions_response(
            totw_banners=[
                datagen.create_promotions_totw_banner(
                    'id0', experiment=custom_exp_name,
                ),
                datagen.create_promotions_totw_banner('id1'),
                datagen.create_promotions_totw_banner(
                    'id2', experiment=custom_exp_name,
                ),
            ],
        )

    experiments3.add_experiment(**_build_totw_promotions_exp())
    experiments3.add_experiment(
        **_build_totw_promotions_exp(name=custom_exp_name, zone='sbp'),
    )

    await taxi_inapp_communications.invalidate_caches()

    response = await taxi_inapp_communications.post(
        HANDLER_PATH, json=_build_request_body(), headers=_build_headers(),
    )
    assert response.status_code == 200
    assert response.headers['Cache-Control'] == 'max-age=300'

    totw_banners = response.json()['promotions']['banners']['items']

    assert len(totw_banners) == 1
    assert totw_banners[0] == datagen.create_inapp_totw_banner('id1')


@pytest.mark.config(
    INAPP_SHARING_PROMOTIONS_SETTINGS={
        'enabled': True,
        'sources': ['promotions', 'config'],
        'tariff_classes': ['econom'],
        'sharing_with_family_promotion_id': (
            'id_family_promoblock_from_promotions_1'
        ),
    },
    INAPP_FAMILY_PROMOBLOCK_HARDCODE={
        'id': 'id_family_promoblock',
        'meta_type': 'family_promo_block',
        'supported_classes': ['econom', 'comfort', 'comfortplus'],
        'options': {'priority': 7},
        'title': {
            'items': [
                {
                    'color': '#000000',
                    'font_size': 10,
                    'text': 'totw_family_share_promoblock.title',
                    'type': 'text',
                    'is_tanker_key': True,
                },
                {
                    'color': '#000000',
                    'font_size': 10,
                    'text': 'просто текст',
                    'type': 'text',
                    'is_tanker_key': False,
                },
            ],
        },
        'text': {
            'items': [
                {
                    'color': '#000000',
                    'font_size': 10,
                    'text': 'totw_family_share_promoblock.text',
                    'type': 'text',
                    'is_tanker_key': True,
                },
                {
                    'color': '#000000',
                    'font_size': 10,
                    'text': 'просто текст',
                    'type': 'text',
                    'is_tanker_key': False,
                },
            ],
        },
        'widgets': {
            'toggle': {
                'is_selected': False,
                'option_on': {
                    'text': {
                        'items': [
                            {
                                'color': '#000000',
                                'font_size': 10,
                                'text': 'totw_family_share_promoblock.text',
                                'type': 'text',
                                'is_tanker_key': True,
                            },
                            {
                                'color': '#000000',
                                'font_size': 10,
                                'text': 'просто текст',
                                'type': 'text',
                                'is_tanker_key': False,
                            },
                        ],
                    },
                    'title': {
                        'items': [
                            {
                                'color': '#000000',
                                'font_size': 10,
                                'text': 'totw_family_share_promoblock.title',
                                'type': 'text',
                                'is_tanker_key': True,
                            },
                            {
                                'color': '#000000',
                                'font_size': 10,
                                'text': 'просто текст',
                                'type': 'text',
                                'is_tanker_key': False,
                            },
                        ],
                    },
                    'actions': [],
                },
                'option_off': {
                    'text': {
                        'items': [
                            {
                                'color': '#000000',
                                'font_size': 10,
                                'text': 'totw_family_share_promoblock.text',
                                'type': 'text',
                                'is_tanker_key': True,
                            },
                            {
                                'color': '#000000',
                                'font_size': 10,
                                'text': 'просто текст',
                                'type': 'text',
                                'is_tanker_key': False,
                            },
                        ],
                    },
                    'title': {
                        'items': [
                            {
                                'color': '#000000',
                                'font_size': 10,
                                'text': 'totw_family_share_promoblock.title',
                                'type': 'text',
                                'is_tanker_key': True,
                            },
                            {
                                'color': '#000000',
                                'font_size': 10,
                                'text': 'просто текст',
                                'type': 'text',
                                'is_tanker_key': False,
                            },
                        ],
                    },
                    'actions': [],
                },
            },
        },
        'show_policy': {'max_show_count': 3, 'max_widget_usage_count': 1},
        'configuration': {'type': 'list'},
    },
    INAPP_ALT_WAITING_PROMOTION_SETTINGS={
        'enabled': True,
        'alt_waiting_promotion_id': 'id_alt_waiting_promoblock',
    },
)
@pytest.mark.geoareas(filename='db_geoareas.json')
@pytest.mark.tariffs(filename='db_tariffs.json')
@pytest.mark.translations(
    client_messages=datagen.DEFAULT_CLIENT_MESSAGES,
    backend_promotions=datagen.DEFAULT_BACKEND_PROMOTIONS,
    tariff={
        'currency_sign.rub': {'ru': '₽'},
        'currency_sign.usd': {'ru': '$', 'en': '$'},
    },
)
@pytest.mark.experiments3(
    filename='exp3_inapp_sharing_with_family_enabled.json',
)
@pytest.mark.experiments3(filename='exp3_inapp_alt_waiting_info_panel.json')
async def test_totw_promoblocks(
        taxi_inapp_communications, mockserver, load_json, experiments3,
):
    experiments3.add_experiment(**_build_totw_promotions_exp())

    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return datagen.create_promotions_response(
            promos_on_summary=[
                datagen.create_promotions_promoblock(
                    promoblock_id='id_family_promoblock_from_promotions_1',
                    priority=5,
                    widgets=['toggle'],
                ),
                datagen.create_promotions_promoblock(
                    promoblock_id='id_alt_waiting_promoblock',
                    experiment='alt_waiting_info_panel',
                    text_items=[
                        {
                            'color': '#000000',
                            'font_size': 10,
                            'text': 'totw_promoblock_alt_waiting.text',
                            'type': 'text',
                            'is_tanker_key': False,
                        },
                    ],
                    title_items=[
                        {
                            'color': '#000000',
                            'font_size': 10,
                            'text': 'totw_promoblock_alt_waiting.title',
                            'type': 'text',
                            'is_tanker_key': False,
                        },
                    ],
                    priority=6,
                    widgets=['attributed_text'],
                ),
                datagen.create_promotions_promoblock(
                    promoblock_id='another_totw_promoblock',
                    priority=9,
                    widgets=['toggle'],
                ),
                datagen.create_promotions_promoblock(
                    promoblock_id='unsupported_totw_promoblock',
                    priority=11,
                    widgets=['toggle', 'attributed_text'],
                ),
            ],
        )

    calls_count = 0

    @mockserver.json_handler('/order-route-sharing/v1/sharing_info')
    def _mock_order_route_sharing(request):
        nonlocal calls_count
        calls_count += 1
        return {
            'phone_ids': [],
            'family_info': {'sharing_on': True, 'admin_name': 'Admin'},
        }

    headers = _build_headers()
    headers.update({'X-Ya-Family-Role': 'user'})
    response = await taxi_inapp_communications.post(
        HANDLER_PATH, json=_build_request_body(), headers=headers,
    )
    assert response.status_code == 200
    assert calls_count == 1

    totw_promoblocks = response.json()['promotions']['promoblocks']['items']
    assert totw_promoblocks == load_json('response_totw_promoblocks.json')


@pytest.mark.translations(
    client_messages=datagen.DEFAULT_CLIENT_MESSAGES,
    backend_promotions=_create_keyset_totw_notifications(),
)
@pytest.mark.parametrize(
    'driver,filename',
    [
        pytest.param(
            None,
            'response_totw_order_cancel_notification_without_driver.json',
        ),
        pytest.param(
            {
                'driver': {
                    'rating': '4.97',
                    'short_name': 'Михаил',
                    'pictures': {'avatar_image': {'url': 'https://icon.url'}},
                },
            },
            'response_totw_order_cancel_notification_with_driver.json',
        ),
        pytest.param(
            {
                'driver': {
                    'short_name': 'Михаил',
                    'pictures': {'avatar_image': {'url': 'https://icon.url'}},
                },
            },
            'response_totw_order_cancel_notification_with_driver_cut.json',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_order_cancel_notification.json')
async def test_totw_notifications(
        taxi_inapp_communications, load_json, driver, filename,
):

    headers = _build_headers()
    response = await taxi_inapp_communications.post(
        HANDLER_PATH, json=_build_request_body(driver=driver), headers=headers,
    )
    assert response.status_code == 200

    assert 'order_cancel_notification' in response.json()['notifications']
    totw_promoblocks = response.json()['notifications'][
        'order_cancel_notification'
    ]

    assert totw_promoblocks == load_json(filename)
