const got = require('got');

const host = 'geohelper-v122d1.wdevx.yandex.ru';

const url = `http://${host}/geohelper/api/v1/searchapp?blocks=market_cart&did=&experiments=with_gif%2Capp_android_webcard_assist%2Cgh_rtx_exp_searchapp%2Cstream_skippable_fragments%2Clogin_touch_new%2Cweather_sb_app%2Cstream_player_1788%2Cassist_divcard%2Ctourist_blocks%2Cfront_apphost%2Ctutor_touch%2Cinserts_stream_mixed%2Cmusic%2Creport_visibility_check_inline%2Cteaser_app_bk%2Cclient_logger%2Cyalocal_custom_url%2Cstream_special_events%2Cyastatic_check_ru_touch%2Cextracted_points_edadeal%2Cplayed_games%2Cextracted_points_route%2Cugc%2Csport_div_card%2Cstream_picture%2Cmarket_api%2Cwith_plus%2Csplash_promo_touch%2Ctouch_smooth_scroll_metric%2CCSPv2%2Cstream_disable_personal%2Ctranslator_api%2Cyandex_internal_test%2Cpg_unknown%2Cstream_send_strm_probe%2Cyandex_staff%2Cstream_personal&flags=no_yskin&geoid=213&lang=ru&lat=55.753215&lon=37.622504&mordazone=ru&reqid=1608901247.91406.54357.21724&uuid=`;

const payload = {
    "games_div2": {"type": "div2", "ttl": 300, "is_mordanavigate": 1, "ttv": 1200, "id": "games_div2"},
    "topnews_div": {"is_mordanavigate": 1, "ttv": 1200, "type": "div", "ttl": 300, "id": "topnews_div"},
    "alice_skills_div": {"ttv": 1200, "type": "div", "ttl": 300, "id": "alice_skills_div"},
    "general_div2": {"type": "div2", "ttl": 300, "is_mordanavigate": 0, "ttv": 1200, "id": "general_div2"},
    "market_div2": {"is_mordanavigate": 0, "ttv": 1200, "ttl": 300, "type": "div2", "id": "market_div2"},
    "market_cart": {"is_mordanavigate": 0, "ttv": 1200, "ttl": 300, "type": "div2", "id": "market_div2"},
    "sport_div": {"id": "sport_div", "ts_disabled": 0, "is_mordanavigate": 1, "ttv": 1200, "ttl": 300, "type": "div"},
    "autoru_div": {"id": "autoru_div", "type": "div", "ttl": 300, "is_mordanavigate": 1, "ttv": 1200},
    "yalocal_div2": {"id": "yalocal_div2", "ttv": 1200, "is_mordanavigate": 0, "type": "div2", "ttl": 300},
    "stream_mixed": {
        "ttv": 1200,
        "is_mordanavigate": 0,
        "ts_disabled": 0,
        "type": "div",
        "ttl": 300,
        "id": "stream_mixed"
    },
    "homeparams": {
        "general_div2_title": "",
        "market_div2_title": "",
        "sport_div_title": "",
        "autoru_div_title": "",
        "alice_skills_div_title": "",
        "topnews_div_title": "Рекомендации в СМИ",
        "scale_factor": 1,
        "geo_country": 225,
        "country": "RU",
        "menu": {
            "yalocal_div2": {
                "menu_list": [{
                    "text": "Настройки ленты",
                    "action": "opensettings://?screen=feed"
                }, {
                    "text": "Скрыть карточку",
                    "action": "hidecard://?topic_card_ids=yalocal_div2_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83"
                }]
            },
            "sport_div": {
                "menu_list": [{
                    "text": "Настройки ленты",
                    "action": "opensettings://?screen=feed"
                }, {
                    "text": "Скрыть карточку",
                    "action": "hidecard://?topic_card_ids=sport_div_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83"
                }]
            },
            "autoru_div": {
                "menu_list": [{
                    "text": "Настройки ленты",
                    "action": "opensettings://?screen=feed"
                }, {
                    "text": "Скрыть карточку",
                    "action": "hidecard://?topic_card_ids=autoru_div_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83"
                }]
            },
            "topnews_div": {
                "menu_list": [{
                    "text": "Настройки ленты",
                    "action": "opensettings://?screen=feed"
                }, {
                    "text": "Скрыть карточку",
                    "action": "hidecard://?topic_card_ids=topnews_div_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83"
                }]
            },
            "games_div2": {
                "menu_list": [{
                    "action": "opensettings://?screen=feed",
                    "text": "Настройки ленты"
                }, {
                    "text": "Скрыть карточку",
                    "action": "hidecard://?topic_card_ids=games_div2_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83"
                }]
            },
            "general_div2": {
                "menu_list": [{
                    "text": "Настройки ленты",
                    "action": "opensettings://?screen=feed"
                }, {
                    "text": "Скрыть карточку",
                    "action": "hidecard://?topic_card_ids=general_div2_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83"
                }]
            },
            "alice_skills_div": {
                "menu_list": [{
                    "action": "opensettings://?screen=feed",
                    "text": "Настройки ленты"
                }, {
                    "action": "hidecard://?topic_card_ids=alice_skills_div_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83",
                    "text": "Скрыть карточку"
                }]
            },
            "market_div2": {
                "menu_list": [{
                    "text": "Настройки ленты",
                    "action": "opensettings://?screen=feed"
                }, {
                    "text": "Скрыть карточку",
                    "action": "hidecard://?topic_card_ids=market_div2_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83"
                }]
            }
        },
        "layout": [{"id": "search", "type": "search", "heavy": 0}, {
            "heavy": 0,
            "type": "div2",
            "id": "nowcast"
        }, {"id": "topnews", "heavy": 0, "type": "topnews"}, {
            "id": "covid_gallery",
            "type": "div2",
            "heavy": 0
        }, {"type": "div2", "heavy": 1, "id": "market_div2"}, {
            "type": "native_ad",
            "heavy": 0,
            "id": "native_ad_1"
        }, {"type": "div2", "heavy": 1, "id": "general_div2"}, {"id": "zen", "heavy": 0, "type": "zen"}, {
            "heavy": 0,
            "type": "native_ad",
            "id": "native_ad_2"
        }, {"id": "weather", "type": "weather", "heavy": 0}, {
            "id": "topnews_div",
            "type": "div",
            "heavy": 1
        }, {"type": "teaser", "heavy": 0, "id": "teaser_appsearch"}, {
            "heavy": 1,
            "type": "div2",
            "id": "yalocal_div2"
        }, {
            "type": "div",
            "heavy": 1,
            "id": "stream_mixed"
        }, {"id": "games_div2", "type": "div2", "heavy": 1}, {
            "heavy": 1,
            "type": "div",
            "id": "autoru_div"
        }, {"id": "alice_skills_div", "type": "div", "heavy": 1}, {
            "id": "translator",
            "type": "div",
            "heavy": 0
        }, {"type": "div", "heavy": 1, "id": "sport_div"}, {
            "type": "transportmap",
            "heavy": 0,
            "id": "transportmap"
        }, {"id": "privacy_api", "type": "div", "heavy": 0}],
        "stream_mixed_title": "Видео",
        "topic": {
            "alice_skills_div": "alice_skills_div_card",
            "market_div2": "market_div2_card",
            "general_div2": "general_div2_card",
            "games_div2": "games_div2_card",
            "topnews_div": "topnews_div_card",
            "autoru_div": "autoru_div_card",
            "sport_div": "sport_div_card",
            "yalocal_div2": "yalocal_div2_card"
        },
        "yalocal_div2_title": "",
        "version": "10100000",
        "games_div2_title": "",
        "platform": "android",
        "os_version": "10.0.1"
    }
};


got.post(url, {
    json: payload,
    responseType: 'json',
    decompress: false,
    headers: {}
})
    // got.post(url, {json: payload, responseType: 'json'})
    .then(({body}) => body)
    .then(result => {
        console.log(result);
    })
    .catch(error => {
        console.log('ERROR:');
        console.log(error);
    });
