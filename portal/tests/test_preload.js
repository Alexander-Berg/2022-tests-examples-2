const got = require('got');


// const url = 'http://geohelper-v122d1.wdevx.yandex.ru/geohelper/api/v1/searchapp?blocks=autoru_div&did=&experiments=district_strict_max_media_share%2Cgh_rtx_exp_searchapp%2Cstream_skippable_fragments%2Cstream_player_1788%2Cstream_picture%2Cinserts_stream_mixed%2Cmusic%2Cwith_gif%2Csplash_promo_touch%2Cyastatic_check_ru_touch%2Cfront_apphost%2Cstream_disable_personal%2Cugc%2Csport_div_card%2Cyandex_staff%2Cyandex_internal_test%2Cpg_unknown%2Ctouch_smooth_scroll_metric%2Cyalocal_custom_url%2Cmarket_api%2Cextracted_points_route%2Cplayed_games%2Cstream_personal%2Cteaser_app_bk%2Cstream_special_events%2Cstaff_new%2Cweather_sb_app%2Cclient_logger%2Ctranslator_api%2Creport_visibility_check_inline%2Ctutor_touch%2Capp_android_webcard_assist%2Cstream_send_strm_probe%2Cextracted_points_edadeal%2Clogin_touch_new%2Ctourist_blocks%2CCSPv2%2Cassist_divcard&flags=no_yskin&geoid=213&lang=ru&lat=55.753215&lon=37.622504&mordazone=ru&reqid=1600850215.38634.54357.5361&uuid=';
const url = 'http://geohelper-v122d1.wdevx.yandex.ru/geohelper/api/v1/debug_collect_urls?blocks=autoru_div&did=&experiments=district_strict_max_media_share%2Cgh_rtx_exp_searchapp%2Cstream_skippable_fragments%2Cstream_player_1788%2Cstream_picture%2Cinserts_stream_mixed%2Cmusic%2Cwith_gif%2Csplash_promo_touch%2Cyastatic_check_ru_touch%2Cfront_apphost%2Cstream_disable_personal%2Cugc%2Csport_div_card%2Cyandex_staff%2Cyandex_internal_test%2Cpg_unknown%2Ctouch_smooth_scroll_metric%2Cyalocal_custom_url%2Cmarket_api%2Cextracted_points_route%2Cplayed_games%2Cstream_personal%2Cteaser_app_bk%2Cstream_special_events%2Cstaff_new%2Cweather_sb_app%2Cclient_logger%2Ctranslator_api%2Creport_visibility_check_inline%2Ctutor_touch%2Capp_android_webcard_assist%2Cstream_send_strm_probe%2Cextracted_points_edadeal%2Clogin_touch_new%2Ctourist_blocks%2CCSPv2%2Cassist_divcard&flags=no_yskin&geoid=213&lang=ru&lat=55.753215&lon=37.622504&mordazone=ru&reqid=1600850215.38634.54357.5361&uuid=';
// const url = 'http://geohelper-v122d0.wdevx.yandex.ru/geohelper/api/v1/sa_heavy?skip_blocks=autoru_div&did=&experiments=district_strict_max_media_share%2Cgh_rtx_exp_searchapp%2Cstream_skippable_fragments%2Cstream_player_1788%2Cstream_picture%2Cinserts_stream_mixed%2Cmusic%2Cwith_gif%2Csplash_promo_touch%2Cyastatic_check_ru_touch%2Cfront_apphost%2Cstream_disable_personal%2Cugc%2Csport_div_card%2Cyandex_staff%2Cyandex_internal_test%2Cpg_unknown%2Ctouch_smooth_scroll_metric%2Cyalocal_custom_url%2Cmarket_api%2Cextracted_points_route%2Cplayed_games%2Cstream_personal%2Cteaser_app_bk%2Cstream_special_events%2Cstaff_new%2Cweather_sb_app%2Cclient_logger%2Ctranslator_api%2Creport_visibility_check_inline%2Ctutor_touch%2Capp_android_webcard_assist%2Cstream_send_strm_probe%2Cextracted_points_edadeal%2Clogin_touch_new%2Ctourist_blocks%2CCSPv2%2Cassist_divcard&flags=no_yskin&geoid=213&lang=ru&lat=55.753215&lon=37.622504&mordazone=ru&reqid=1600850215.38634.54357.5361&uuid=';

const payload = {
    'homeparams':
        {
            'menu': {
                'alice_skills_div': {
                    'menu_list': [{
                        'text': 'Настройки ленты',
                        'action': 'opensettings://?screen=feed'
                    }, {
                        'action': 'hidecard://?topic_card_ids=alice_skills_div_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83',
                        'text': 'Скрыть карточку'
                    }]
                },
                'games_div2': {
                    'menu_list': [{'action': 'opensettings://?screen=feed', 'text': 'Настройки ленты'}, {
                        'text': 'Скрыть карточку',
                        'action': 'hidecard://?topic_card_ids=games_div2_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83'
                    }]
                },
                'sport_div': {
                    'menu_list': [{'action': 'opensettings://?screen=feed', 'text': 'Настройки ленты'}, {
                        'text': 'Скрыть карточку',
                        'action': 'hidecard://?topic_card_ids=sport_div_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83'
                    }]
                },
                'edadeal': {
                    'button_color': '#ffffffff',
                    'menu_list': [{
                        'action': 'opensettings://?screen=feed',
                        'text': 'Настройки ленты'
                    }, {
                        'action': 'hidecard://?topic_card_ids=edadeal_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83',
                        'text': 'Скрыть карточку'
                    }]
                },
                'yalocal_div2': {
                    'menu_list': [{'text': 'Настройки ленты', 'action': 'opensettings://?screen=feed'}, {
                        'text': 'Скрыть карточку',
                        'action': 'hidecard://?topic_card_ids=yalocal_div2_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83'
                    }]
                },
                'autoru_div': {
                    'menu_list': [{
                        'text': 'Настройки ленты',
                        'action': 'opensettings://?screen=feed'
                    }, {
                        'action': 'hidecard://?topic_card_ids=autoru_div_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83',
                        'text': 'Скрыть карточку'
                    }]
                },
                'topnews_div': {
                    'menu_list': [{'text': 'Настройки ленты', 'action': 'opensettings://?screen=feed'}, {
                        'text': 'Скрыть карточку',
                        'action': 'hidecard://?topic_card_ids=topnews_div_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83'
                    }]
                }
            },
            'topnews_div_title': 'Рекомендации в СМИ',
            'version': '10050000',
            'os_version': '9.0.1',
            'country': 'RU',
            'sport_div_title': '',
            'topic': {
                'edadeal': 'edadeal_card',
                'sport_div': 'sport_div_card',
                'games_div2': 'games_div2_card',
                'alice_skills_div': 'alice_skills_div_card',
                'topnews_div': 'topnews_div_card',
                'autoru_div': 'autoru_div_card',
                'yalocal_div2': 'yalocal_div2_card'
            },
            'platform': 'android',
            'layout': [{'type': 'native_banner_ad', 'heavy': 0, 'id': 'native_banner_ad'}, {'heavy': 0, 'id': 'search', 'type': 'search'}, {
                'heavy': 0,
                'id': 'topnews',
                'type': 'topnews'
            }, {'type': 'div2', 'heavy': 0, 'id': 'covid_gallery'}, {'type': 'stocks', 'heavy': 0, 'id': 'stocks'}, {
                'type': 'native_ad',
                'heavy': 0,
                'id': 'native_ad_1'
            }, {'id': 'zen', 'heavy': 0, 'type': 'zen'}, {'heavy': 0, 'id': 'native_ad_2', 'type': 'native_ad'}, {'id': 'weather', 'heavy': 0, 'type': 'weather'}, {
                'type': 'div',
                'id': 'topnews_div',
                'heavy': 1
            }, {'type': 'transportmap', 'heavy': 0, 'id': 'transportmap'}, {'id': 'teaser_appsearch', 'heavy': 0, 'type': 'teaser'}, {
                'heavy': 1,
                'id': 'yalocal_div2',
                'type': 'div2'
            }, {'type': 'div', 'heavy': 1, 'id': 'stream_mixed'}, {
                'heavy': 0,
                'id': 'tv',
                'type': 'tv'
            }, {'id': 'autoru_div', 'heavy': 1, 'type': 'div'}, {'type': 'div2', 'heavy': 1, 'id': 'games_div2'}, {'type': 'div', 'id': 'edadeal', 'heavy': 1}, {
                'type': 'afisha',
                'id': 'afisha',
                'heavy': 0
            }, {'type': 'div', 'heavy': 1, 'id': 'sport_div'}, {'id': 'services', 'heavy': 0, 'type': 'services'}, {'type': 'div', 'id': 'translator', 'heavy': 0}, {
                'heavy': 0,
                'id': 'stream',
                'type': 'div'
            }, {'id': 'alice_skills_div', 'heavy': 1, 'type': 'div'}, {'type': 'div', 'heavy': 0, 'id': 'privacy_api'}],
            'geo_country': 225,
            'games_div2_title': '',
            'yalocal_div2_title': '',
            'alice_skills_div_title': '',
            'edadeal_title': 'Скидки рядом',
            'stream_mixed_title': 'Видео',
            'autoru_div_title': '',
            'scale_factor': 1
        },
    'topnews_div': {'ttl': 300, 'type': 'div', 'id': 'topnews_div', 'is_mordanavigate': 1, 'ttv': 1200},
    'alice_skills_div': {'type': 'div', 'ttl': 300, 'ttv': 1200, 'id': 'alice_skills_div'},
    'autoru_div': {'ttv': 1200, 'id': 'autoru_div', 'is_mordanavigate': 1, 'ttl': 300, 'type': 'div'},
    'stream_mixed': {'type': 'div', 'ttl': 300, 'ttv': 1200, 'is_mordanavigate': 0, 'id': 'stream_mixed', 'ts_disabled': 0},
    'yalocal_div2': {'ttv': 1200, 'is_mordanavigate': 0, 'id': 'yalocal_div2', 'ttl': 300, 'type': 'div2'},
    'sport_div': {'type': 'div', 'ttl': 300, 'ttv': 1200, 'is_mordanavigate': 1, 'ts_disabled': 0, 'id': 'sport_div'},
    'games_div2': {'ttl': 300, 'type': 'div2', 'is_mordanavigate': 1, 'id': 'games_div2', 'ttv': 1200},
    'edadeal': {
        'ttl': 300,
        'background_color': '#399847',
        'url': 'yellowskin://?background_color=%234b9645&buttons_color=%23ffffff&omnibox_color=%23288736&status_bar_theme=dark&text_color=%23ffffff&url=https%3A%2F%2Fedadeal.ru%2Fmoskva%3Fappsearch_header%3D1%26lat%3D55.75%26lng%3D37.62%26source%3Dyandex_portal%26utm_campaign%3Dcarousel_main%26utm_content%3Dtouch%26utm_medium%3Dmain%26utm_source%3Dmorda%26utm_term%3Dmoskva',
        'ttv': 1200,
        'action_url': 'yellowskin://?background_color=%234b9645&buttons_color=%23ffffff&omnibox_color=%23288736&status_bar_theme=dark&text_color=%23ffffff&url=https%3A%2F%2Fedadeal.ru%2Fmoskva%3Fappsearch_header%3D1%26lat%3D55.75%26lng%3D37.62%26source%3Dyandex_portal%26utm_campaign%3Dcarousel_main%26utm_content%3Dtouch%26utm_medium%3Dmain%26utm_source%3Dmorda%26utm_term%3Dmoskva',
        'item_layout_kind': 'portrait',
        'id': 'edadeal',
        'type': 'div',
        'text_color': '#ffffff',
        'yellow_skin': {'status_bar_theme': 'dark', 'text_color': '#ffffff', 'omnibox_color': '#288736', 'buttons_color': '#ffffff', 'background_color': '#4b9645'},
        'action_text': 'ВСЕ СКИДКИ'
    }
};

const autoru_data = {"title":"Объявления на Авто.ру","tabs":[{"alias":"jekonomichnye","href":"https://search-app.auto.ru/?preset=jekonomichnye&from=search_app_morda","title":"ЭКОНОМИЧНЫЕ","offers":[{"href":"https://search-app.auto.ru/?preset=jekonomichnye&from=search_app_morda&pinned_offer_id=autoru-1100950794","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2048373/15bede4b8a75da971a02e1d969f533b8/456x342","price_rur":"1 450 000 ₽","title":"Volkswagen Touareg, 2011"},{"href":"https://search-app.auto.ru/?preset=jekonomichnye&from=search_app_morda&pinned_offer_id=autoru-1100638158","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/1973178/3ea120ba6ae6acccfe1f1c5cbfa232fb/456x342","price_rur":"660 000 ₽","title":"Hyundai Solaris, 2014"},{"href":"https://search-app.auto.ru/?preset=jekonomichnye&from=search_app_morda&pinned_offer_id=autoru-1100331668","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2165703/6c44fb67a9e0b7df3d9e1bba3a1e5f55/456x342","price_rur":"1 500 000 ₽","title":"Mercedes-Benz E-Класс, 2015"},{"href":"https://search-app.auto.ru/?preset=jekonomichnye&from=search_app_morda&pinned_offer_id=autoru-1100904478","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/1961225/78245cbdc7fd91b4503a8172a1097d4d/456x342","price_rur":"1 350 000 ₽","title":"Mercedes-Benz CLA, 2015"},{"href":"https://search-app.auto.ru/?preset=jekonomichnye&from=search_app_morda&pinned_offer_id=autoru-1100591434","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2077743/d37ffd0f7aa420d4a614f26238861dc3/456x342","price_rur":"890 000 ₽","title":"Volvo XC70, 2010"},{"href":"https://search-app.auto.ru/?preset=jekonomichnye&from=search_app_morda&pinned_offer_id=autoru-1099964240","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/1907070/d7b3dd362c5cd06145a1a847b957cb1a/456x342","price_rur":"1 370 000 ₽","title":"Toyota RAV4, 2016"},{"href":"https://search-app.auto.ru/?preset=jekonomichnye&from=search_app_morda&pinned_offer_id=autoru-1099639296","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2023570/cb2c5176bef1b245af770801af1eeda6/456x342","price_rur":"1 185 000 ₽","title":"Volkswagen Caravelle, 2012"},{"href":"https://search-app.auto.ru/?preset=jekonomichnye&from=search_app_morda&pinned_offer_id=autoru-1100194748","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/1969232/8bd378b37207f2f348bcf286d11d83ec/456x342","price_rur":"1 399 000 ₽","title":"Land Rover Range Rover Evoque, 2012"},{"href":"https://search-app.auto.ru/?preset=jekonomichnye&from=search_app_morda&pinned_offer_id=autoru-1100768270","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/1960172/4ce2b873a932df833c68d36150bd087b/456x342","price_rur":"1 390 000 ₽","title":"Renault Arkana, 2019"},{"href":"https://search-app.auto.ru/?preset=jekonomichnye&from=search_app_morda&pinned_offer_id=autoru-1100051404","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/1590523/b430f4a2c897a0220b2e358c828a993b/456x342","price_rur":"1 350 000 ₽","title":"Mercedes-Benz A-Класс AMG, 2013"}]},{"alias":"diler-auto","href":"https://search-app.auto.ru/?preset=diler-auto&from=search_app_morda","title":"ОТ ДИЛЕРОВ","offers":[{"href":"https://search-app.auto.ru/?preset=diler-auto&from=search_app_morda&pinned_offer_id=autoru-1100794854","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2159261/42900dd0206a926e73f8e1939cff824d/456x342","price_rur":"435 000 ₽","title":"Peugeot Partner, 2011"},{"href":"https://search-app.auto.ru/?preset=diler-auto&from=search_app_morda&pinned_offer_id=autoru-1099914040","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2175772/b58a26d4f844f4aebebedb3aeeea66ad/456x342","price_rur":"6 309 806 ₽","title":"Audi Q8, 2019"},{"href":"https://search-app.auto.ru/?preset=diler-auto&from=search_app_morda&pinned_offer_id=autoru-1099650338","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2195941/e1e3922f7435224eb8a7399c49e0cd4b/456x342","price_rur":"3 524 800 ₽","title":"Mercedes-Benz E-Класс, 2020"},{"href":"https://search-app.auto.ru/?preset=diler-auto&from=search_app_morda&pinned_offer_id=autoru-1099630014","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2181105/beefcd4deb0808d643b338f1bb28920c/456x342","price_rur":"1 535 000 ₽","title":"Kia Carnival, 2014"},{"href":"https://search-app.auto.ru/?preset=diler-auto&from=search_app_morda&pinned_offer_id=autoru-1100901710","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2095416/f93b0248fc4e0a1df90c0681a7d09dcc/456x342","price_rur":"469 000 ₽","title":"Chevrolet Cruze, 2014"},{"href":"https://search-app.auto.ru/?preset=diler-auto&from=search_app_morda&pinned_offer_id=autoru-1092290892","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2181286/b84e8d21cef7625c04fd52a84863302b/456x342","price_rur":"23 000 000 ₽","title":"Mercedes-Benz V-Класс, 2019"},{"href":"https://search-app.auto.ru/?preset=diler-auto&from=search_app_morda&pinned_offer_id=autoru-1099030326","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/1665854/cf8ae4dda66c0f010243ea30a133ff91/456x342","price_rur":"400 000 ₽","title":"Opel Astra, 2012"},{"href":"https://search-app.auto.ru/?preset=diler-auto&from=search_app_morda&pinned_offer_id=autoru-1100828920","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2155467/464bf4d48af41fffa83c02b5668151c3/456x342","price_rur":"6 326 900 ₽","title":"Mercedes-Benz GLE, 2020"},{"href":"https://search-app.auto.ru/?preset=diler-auto&from=search_app_morda&pinned_offer_id=autoru-1100795476","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2198235/e367a04aa47b99437e1a76da2993d05c/456x342","price_rur":"1 299 000 ₽","title":"Toyota RAV4, 2016"},{"href":"https://search-app.auto.ru/?preset=diler-auto&from=search_app_morda&pinned_offer_id=autoru-1100217704","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2074492/4ae93baa80cddbf4ca326d760872daf7/456x342","price_rur":"1 863 000 ₽","title":"Nissan Qashqai, 2020"}]},{"alias":"dizelnye","href":"https://search-app.auto.ru/?preset=dizelnye&from=search_app_morda","title":"ДИЗЕЛЬНЫЕ","offers":[{"href":"https://search-app.auto.ru/?preset=dizelnye&from=search_app_morda&pinned_offer_id=autoru-1099787444","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2101836/8cf8298970dbce54e0675d5279c67a2f/456x342","price_rur":"2 990 000 ₽","title":"Mercedes-Benz CLS, 2017"},{"href":"https://search-app.auto.ru/?preset=dizelnye&from=search_app_morda&pinned_offer_id=autoru-1100828920","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2155467/464bf4d48af41fffa83c02b5668151c3/456x342","price_rur":"6 326 900 ₽","title":"Mercedes-Benz GLE, 2020"},{"href":"https://search-app.auto.ru/?preset=dizelnye&from=search_app_morda&pinned_offer_id=autoru-1100752154","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2058473/53b5891e52c340bcba10a2a2eb332fdf/456x342","price_rur":"6 998 600 ₽","title":"Mercedes-Benz V-Класс, 2020"},{"href":"https://search-app.auto.ru/?preset=dizelnye&from=search_app_morda&pinned_offer_id=autoru-1099630014","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2181105/beefcd4deb0808d643b338f1bb28920c/456x342","price_rur":"1 535 000 ₽","title":"Kia Carnival, 2014"},{"href":"https://search-app.auto.ru/?preset=dizelnye&from=search_app_morda&pinned_offer_id=autoru-1100224560","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/1981977/cd1312e0cfde4d20502c4bc03123bd64/456x342","price_rur":"2 061 111 ₽","title":"Kia Carnival, 2017"},{"href":"https://search-app.auto.ru/?preset=dizelnye&from=search_app_morda&pinned_offer_id=autoru-1100338212","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2131711/84cb723a091dff0a1f25ceb031dee9a5/456x342","price_rur":"1 530 000 ₽","title":"BMW 6 серии, 2012"},{"href":"https://search-app.auto.ru/?preset=dizelnye&from=search_app_morda&pinned_offer_id=autoru-1100905100","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/1907787/8a09253bf9a8aa4ac4a9e45034bef6d7/456x342","price_rur":"1 485 000 ₽","title":"Mercedes-Benz GL-Класс, 2011"},{"href":"https://search-app.auto.ru/?preset=dizelnye&from=search_app_morda&pinned_offer_id=autoru-1100801676","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2037331/b896b51c9d4d7a144033fcc1dabacabb/456x342","price_rur":"3 400 000 ₽","title":"BMW X5, 2017"},{"href":"https://search-app.auto.ru/?preset=dizelnye&from=search_app_morda&pinned_offer_id=autoru-1092290892","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2181286/b84e8d21cef7625c04fd52a84863302b/456x342","price_rur":"23 000 000 ₽","title":"Mercedes-Benz V-Класс, 2019"},{"href":"https://search-app.auto.ru/?preset=dizelnye&from=search_app_morda&pinned_offer_id=autoru-1100194748","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/1969232/8bd378b37207f2f348bcf286d11d83ec/456x342","price_rur":"1 399 000 ₽","title":"Land Rover Range Rover Evoque, 2012"}]},{"alias":"vnedorogniki","href":"https://search-app.auto.ru/?preset=vnedorogniki&from=search_app_morda","title":"ВНЕДОРОЖНИКИ","offers":[{"href":"https://search-app.auto.ru/?preset=vnedorogniki&from=search_app_morda&pinned_offer_id=autoru-1100904796","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2174323/f0dbe403e1bb76c200df0b8409019d51/456x342","price_rur":"3 000 000 ₽","title":"Mercedes-Benz G-Класс AMG, 2009"},{"href":"https://search-app.auto.ru/?preset=vnedorogniki&from=search_app_morda&pinned_offer_id=autoru-1100217704","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2074492/4ae93baa80cddbf4ca326d760872daf7/456x342","price_rur":"1 863 000 ₽","title":"Nissan Qashqai, 2020"},{"href":"https://search-app.auto.ru/?preset=vnedorogniki&from=search_app_morda&pinned_offer_id=autoru-1099604336","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2161763/797c04c2814180db06348fb18775fcff/456x342","price_rur":"508 000 ₽","title":"LADA (ВАЗ) 2131 (4x4), 2018"},{"href":"https://search-app.auto.ru/?preset=vnedorogniki&from=search_app_morda&pinned_offer_id=autoru-1091873490","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2159790/10261e484d8c7a0527264a6842a38185/456x342","price_rur":"1 200 000 ₽","title":"УАЗ Hunter, 2016"},{"href":"https://search-app.auto.ru/?preset=vnedorogniki&from=search_app_morda&pinned_offer_id=autoru-1100924254","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/1994991/758515fa744680ef78bfca5fbad2e659/456x342","price_rur":"2 320 000 ₽","title":"Lexus LX, 2008"},{"href":"https://search-app.auto.ru/?preset=vnedorogniki&from=search_app_morda&pinned_offer_id=autoru-1100828920","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2155467/464bf4d48af41fffa83c02b5668151c3/456x342","price_rur":"6 326 900 ₽","title":"Mercedes-Benz GLE, 2020"},{"href":"https://search-app.auto.ru/?preset=vnedorogniki&from=search_app_morda&pinned_offer_id=autoru-1100208704","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2021936/fad7d6ea80b8e31597666b14e0c770b9/456x342","price_rur":"2 548 000 ₽","title":"Chevrolet Tahoe, 2015"},{"href":"https://search-app.auto.ru/?preset=vnedorogniki&from=search_app_morda&pinned_offer_id=autoru-1100795476","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2198235/e367a04aa47b99437e1a76da2993d05c/456x342","price_rur":"1 299 000 ₽","title":"Toyota RAV4, 2016"},{"href":"https://search-app.auto.ru/?preset=vnedorogniki&from=search_app_morda&pinned_offer_id=autoru-1100194748","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/1969232/8bd378b37207f2f348bcf286d11d83ec/456x342","price_rur":"1 399 000 ₽","title":"Land Rover Range Rover Evoque, 2012"},{"href":"https://search-app.auto.ru/?preset=vnedorogniki&from=search_app_morda&pinned_offer_id=autoru-1099693568","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/1575294/6435b50117f8f03733f4b8aa59a75f7e/456x342","price_rur":"5 000 000 ₽","title":"Audi Q8, 2018"}]},{"alias":"otlichnaja_cena","href":"https://search-app.auto.ru/?preset=otlichnaja_cena&from=search_app_morda","title":"ОТЛИЧНАЯ ЦЕНА","offers":[{"href":"https://search-app.auto.ru/?preset=otlichnaja_cena&from=search_app_morda&pinned_offer_id=autoru-1100481890","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2079997/c514b9e73a1e69717c21012e1f43e11c/456x342","price_rur":"500 000 ₽","title":"Kia Rio, 2017"},{"href":"https://search-app.auto.ru/?preset=otlichnaja_cena&from=search_app_morda&pinned_offer_id=autoru-1100623198","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2178646/2d41845804c32943312ec8b0972dc5a2/456x342","price_rur":"480 000 ₽","title":"Hyundai Solaris, 2014"},{"href":"https://search-app.auto.ru/?preset=otlichnaja_cena&from=search_app_morda&pinned_offer_id=autoru-1100930028","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2133191/f1227a0f738e08eeff8e3f6ece10d8bb/456x342","price_rur":"1 050 000 ₽","title":"Hyundai Equus, 2015"},{"href":"https://search-app.auto.ru/?preset=otlichnaja_cena&from=search_app_morda&pinned_offer_id=autoru-1100904796","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2174323/f0dbe403e1bb76c200df0b8409019d51/456x342","price_rur":"3 000 000 ₽","title":"Mercedes-Benz G-Класс AMG, 2009"},{"href":"https://search-app.auto.ru/?preset=otlichnaja_cena&from=search_app_morda&pinned_offer_id=autoru-1097710486","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2154502/fe22c89544d33c6d3c7fc66bde482061/456x342","price_rur":"635 000 ₽","title":"Nissan Teana, 2012"},{"href":"https://search-app.auto.ru/?preset=otlichnaja_cena&from=search_app_morda&pinned_offer_id=autoru-1100951964","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2154502/f2c0555fece3506ea1dce5dd401348a9/456x342","price_rur":"470 000 ₽","title":"Honda Accord, 2008"},{"href":"https://search-app.auto.ru/?preset=otlichnaja_cena&from=search_app_morda&pinned_offer_id=autoru-1100554902","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2162096/ad8c85c56dfcef49285f4fe568ca3801/456x342","price_rur":"2 200 000 ₽","title":"BMW M5, 2012"},{"href":"https://search-app.auto.ru/?preset=otlichnaja_cena&from=search_app_morda&pinned_offer_id=autoru-1099977938","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/1860524/558a31c5e834237e6bdcbbb8676cd365/456x342","price_rur":"1 169 000 ₽","title":"Mercedes-Benz E-Класс, 2015"},{"href":"https://search-app.auto.ru/?preset=otlichnaja_cena&from=search_app_morda&pinned_offer_id=autoru-1099812278","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2004588/d338b45ec832c29e5ec3e7335c37c487/456x342","price_rur":"370 000 ₽","title":"Chery Tiggo (T11), 2014"},{"href":"https://search-app.auto.ru/?preset=otlichnaja_cena&from=search_app_morda&pinned_offer_id=autoru-1100338212","image_url":"https://avatars.mds.yandex.net/get-autoru-vos/2131711/84cb723a091dff0a1f25ceb031dee9a5/456x342","price_rur":"1 530 000 ₽","title":"BMW 6 серии, 2012"}]}]};

payload.blocks = {autoru_div: autoru_data};

got.post(url, {json: payload, responseType: 'json'})
    .then(({body}) => body)
    .then(result => {
        console.log(result);
    });