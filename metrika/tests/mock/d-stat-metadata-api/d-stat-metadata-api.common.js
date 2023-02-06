BEM.decl('d-stat-metadata-api', null, {
    getSegmentsTree: function () {
        //in vim :. !curl 'http://mtback01et.yandex.ru:8082/stat/v1/metadata/user_and_common_segments?user_type=manager&interface=1&lang=ru&request_domain=ru&uid_real=134224088&uid=134224088' 2>/dev/null | jq .
        /*jshint ignore: start*/
        /*jscs:disable*/
        return {
          "common_segments": [
            {
              "name": "Источники",
              "type": "menu",
              "id": "sources",
              "chld": [
                {
                  "name": "Последний источник",
                  "type": "menu",
                  "id": "sources_last",
                  "chld": [
                    {
                      "name": "Тип источника",
                      "full_name": "Тип последнего источника",
                      "type": "list",
                      "dim": "ym:s:trafficSource",
                      "id": "TrafficSource",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits"
                    },
                    {
                      "name": "Рекламная система",
                      "full_name": "Последняя рекламная система",
                      "type": "list",
                      "dim": "ym:s:advEngine",
                      "wv_dim": "ym:s:WVAdvEngine",
                      "id": "AdvEngine",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits"
                    },
                    {
                      "name": "Поисковая система",
                      "full_name": "Последняя поисковая система",
                      "type": "path",
                      "dim": "ym:s:searchEngineRoot",
                      "id": "SearchEngineRoot",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "dims": [
                        "ym:s:searchEngineRoot",
                        "ym:s:searchEngine"
                      ]
                    },
                    {
                      "name": "Поисковая фраза",
                      "full_name": "Последняя поисковая фраза",
                      "type": "multiline",
                      "dim": "ym:s:searchPhrase",
                      "id": "SearchPhrase",
                      "table": "visits",
                      "permission_scope": "private",
                      "count_metric": "ym:s:visits"
                    },
                    {
                      "name": "Переходы с сайтов",
                      "full_name": "Последние переходы с сайтов",
                      "type": "multiline",
                      "dim": "ym:s:referalSource",
                      "id": "ReferalSource",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits"
                    },
                    {
                      "name": "Социальные сети",
                      "full_name": "Последние социальные сети",
                      "type": "list",
                      "dim": "ym:s:socialNetwork",
                      "id": "SocialNetwork",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits"
                    },
                    {
                      "name": "Группа соц. сети",
                      "full_name": "Последняя группа соц. сети",
                      "type": "multiline",
                      "dim": "ym:s:socialNetworkProfile",
                      "id": "SocialNetworkProfile",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits"
                    },
                    {
                      "name": "Директ",
                      "type": "menu",
                      "id": "direct_last",
                      "chld": [
                        {
                          "name": "Кампания",
                          "type": "list",
                          "dim": "ym:s:lastDirectClickOrder",
                          "wv_dim": "ym:s:WVLastDirectClickOrder",
                          "id": "LastDirectClickOrder",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits",
                          "values_filter_dims": [
                            "ym:s:lastDirectClickOrderName",
                            "ym:s:lastDirectID"
                          ]
                        },
                        {
                          "name": "Группа объявлений",
                          "type": "list",
                          "dim": "ym:s:lastDirectBannerGroup",
                          "wv_dim": "ym:s:WVLastDirectBannerGroup",
                          "id": "LastDirectBannerGroup",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Тип площадки",
                          "type": "list",
                          "dim": "ym:s:lastDirectPlatformType",
                          "wv_dim": "ym:s:WVLastDirectPlatformType",
                          "id": "LastDirectPlatformType",
                          "table": "visits",
                          "advanced": true,
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Площадка",
                          "type": "list",
                          "dim": "ym:s:lastDirectPlatform",
                          "wv_dim": "ym:s:WVLastDirectPlatform",
                          "id": "LastDirectPlatform",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Поисковая фраза",
                          "type": "multiline",
                          "dim": "ym:s:lastDirectSearchPhrase",
                          "wv_dim": "ym:s:directSearchPhraseShort",
                          "id": "LastDirectSearchPhrase",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Объявление Яндекс.Директа",
                          "type": "list",
                          "dim": "ym:s:lastDirectClickBanner",
                          "id": "LastDirectClickBanner",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits",
                          "values_filter_dims": [
                            "ym:s:lastDirectClickBannerName",
                            "ym:s:lastDirectBanner"
                          ]
                        },
                        {
                          "name": "Текст объявления",
                          "type": "list",
                          "dim": "ym:s:lastDirectBannerText",
                          "wv_dim": "ym:s:WVLastDirectBannerText",
                          "id": "LastDirectBannerText",
                          "table": "visits",
                          "advanced": true,
                          "permission_scope": "internal",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Тип условия подбора объявления",
                          "type": "list",
                          "dim": "ym:s:lastDirectConditionType",
                          "wv_dim": "ym:s:WVLastDirectConditionType",
                          "id": "LastDirectConditionType",
                          "table": "visits",
                          "advanced": true,
                          "permission_scope": "internal",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Условие подбора объявления",
                          "type": "list",
                          "dim": "ym:s:lastDirectPhraseOrCond",
                          "wv_dim": "ym:s:WVLastDirectCondition",
                          "id": "LastDirectPhraseOrCond",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits"
                        }
                      ]
                    },
                    {
                      "name": "Дисплей",
                      "type": "menu",
                      "id": "display_last",
                      "chld": [
                        {
                          "name": "Номер заказа Яндекс.Дисплея",
                          "type": "list",
                          "dim": "ym:s:lastDisplayCampaign",
                          "id": "LastDisplayCampaign",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits"
                        }
                      ]
                    },
                    {
                      "name": "Метки",
                      "type": "menu",
                      "id": "tags_last",
                      "chld": [
                        {
                          "name": "from",
                          "type": "multiline",
                          "dim": "ym:s:lastFrom",
                          "id": "LastFrom",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "UTM: source",
                          "type": "multiline",
                          "dim": "ym:s:lastUTMSource",
                          "id": "LastUTMSource",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "UTM: medium",
                          "type": "multiline",
                          "dim": "ym:s:lastUTMMedium",
                          "id": "LastUTMMedium",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "UTM: campaign",
                          "type": "multiline",
                          "dim": "ym:s:lastUTMCampaign",
                          "id": "LastUTMCampaign",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "UTM: content",
                          "type": "multiline",
                          "dim": "ym:s:lastUTMContent",
                          "id": "LastUTMContent",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "UTM: term",
                          "type": "multiline",
                          "dim": "ym:s:lastUTMTerm",
                          "id": "LastUTMTerm",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Openstat: service",
                          "type": "multiline",
                          "dim": "ym:s:lastOpenstatService",
                          "id": "LastOpenstatService",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Openstat: campaign",
                          "type": "multiline",
                          "dim": "ym:s:lastOpenstatCampaign",
                          "id": "LastOpenstatCampaign",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Openstat: ad",
                          "type": "multiline",
                          "dim": "ym:s:lastOpenstatAd",
                          "id": "LastOpenstatAd",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Openstat: source",
                          "type": "multiline",
                          "dim": "ym:s:lastOpenstatSource",
                          "id": "LastOpenstatSource",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Наличие GCLID",
                          "type": "bool",
                          "dim": "ym:s:lastHasGCLID",
                          "id": "LastHasGCLID",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits",
                          "yes_label": "Есть",
                          "no_label": "Нет"
                        }
                      ]
                    }
                  ]
                },
                {
                  "name": "Первый источник",
                  "type": "menu",
                  "id": "sources_first",
                  "chld": [
                    {
                      "name": "Тип источника",
                      "full_name": "Тип первого источника",
                      "type": "list",
                      "dim": "ym:s:firstTrafficSource",
                      "id": "FirstTrafficSource",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits"
                    },
                    {
                      "name": "Рекламная система",
                      "full_name": "Первая рекламная система",
                      "type": "list",
                      "dim": "ym:s:firstAdvEngine",
                      "wv_dim": "ym:s:WVFirstAdvEngine",
                      "id": "FirstAdvEngine",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits"
                    },
                    {
                      "name": "Поисковая система",
                      "full_name": "Первая поисковая система",
                      "type": "path",
                      "dim": "ym:s:firstSearchEngineRoot",
                      "id": "FirstSearchEngineRoot",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "dims": [
                        "ym:s:firstSearchEngineRoot",
                        "ym:s:firstSearchEngine"
                      ]
                    },
                    {
                      "name": "Поисковая фраза",
                      "full_name": "Первая поисковая фраза",
                      "type": "multiline",
                      "dim": "ym:s:firstSearchPhrase",
                      "id": "FirstSearchPhrase",
                      "table": "visits",
                      "permission_scope": "private",
                      "count_metric": "ym:s:visits"
                    },
                    {
                      "name": "Переходы с сайтов",
                      "full_name": "Первые переходы с сайтов",
                      "type": "multiline",
                      "dim": "ym:s:firstReferalSource",
                      "id": "FirstReferalSource",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits"
                    },
                    {
                      "name": "Социальные сети",
                      "full_name": "Первые социальные сети",
                      "type": "list",
                      "dim": "ym:s:firstSocialNetwork",
                      "id": "FirstSocialNetwork",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits"
                    },
                    {
                      "name": "Группа соц. сети",
                      "full_name": "Первая группа соц. сети",
                      "type": "multiline",
                      "dim": "ym:s:firstSocialNetworkProfile",
                      "id": "FirstSocialNetworkProfile",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits"
                    },
                    {
                      "name": "Директ",
                      "type": "menu",
                      "id": "direct_first",
                      "chld": [
                        {
                          "name": "Кампания",
                          "type": "list",
                          "dim": "ym:s:firstDirectClickOrder",
                          "wv_dim": "ym:s:WVFirstDirectClickOrder",
                          "id": "FirstDirectClickOrder",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits",
                          "values_filter_dims": [
                            "ym:s:firstDirectClickOrderName",
                            "ym:s:firstDirectID"
                          ]
                        },
                        {
                          "name": "Группа объявлений",
                          "type": "list",
                          "dim": "ym:s:firstDirectBannerGroup",
                          "wv_dim": "ym:s:WVFirstDirectBannerGroup",
                          "id": "FirstDirectBannerGroup",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Тип площадки",
                          "type": "list",
                          "dim": "ym:s:firstDirectPlatformType",
                          "wv_dim": "ym:s:WVFirstDirectPlatformType",
                          "id": "FirstDirectPlatformType",
                          "table": "visits",
                          "advanced": true,
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Площадка",
                          "type": "list",
                          "dim": "ym:s:firstDirectPlatform",
                          "wv_dim": "ym:s:WVFirstDirectPlatform",
                          "id": "FirstDirectPlatform",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Поисковая фраза",
                          "type": "multiline",
                          "dim": "ym:s:firstDirectSearchPhrase",
                          "wv_dim": "ym:s:directSearchPhraseShort",
                          "id": "FirstDirectSearchPhrase",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Объявление Яндекс.Директа",
                          "type": "list",
                          "dim": "ym:s:firstDirectClickBanner",
                          "id": "FirstDirectClickBanner",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits",
                          "values_filter_dims": [
                            "ym:s:firstDirectClickBannerName",
                            "ym:s:firstDirectBanner"
                          ]
                        },
                        {
                          "name": "Текст объявления",
                          "type": "list",
                          "dim": "ym:s:firstDirectBannerText",
                          "wv_dim": "ym:s:WVFirstDirectBannerText",
                          "id": "FirstDirectBannerText",
                          "table": "visits",
                          "advanced": true,
                          "permission_scope": "internal",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Тип условия подбора объявления",
                          "type": "list",
                          "dim": "ym:s:firstDirectConditionType",
                          "wv_dim": "ym:s:WVFirstDirectConditionType",
                          "id": "FirstDirectConditionType",
                          "table": "visits",
                          "advanced": true,
                          "permission_scope": "internal",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Условие подбора объявления",
                          "type": "list",
                          "dim": "ym:s:firstDirectPhraseOrCond",
                          "wv_dim": "ym:s:WVFirstDirectCondition",
                          "id": "FirstDirectPhraseOrCond",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits"
                        }
                      ]
                    },
                    {
                      "name": "Дисплей",
                      "type": "menu",
                      "id": "display_first",
                      "chld": [
                        {
                          "name": "Номер заказа Яндекс.Дисплея",
                          "type": "list",
                          "dim": "ym:s:firstDisplayCampaign",
                          "id": "FirstDisplayCampaign",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits"
                        }
                      ]
                    },
                    {
                      "name": "Метки",
                      "type": "menu",
                      "id": "tags_first",
                      "chld": [
                        {
                          "name": "from",
                          "type": "multiline",
                          "dim": "ym:s:firstFrom",
                          "id": "FirstFrom",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "UTM: source",
                          "type": "multiline",
                          "dim": "ym:s:firstUTMSource",
                          "id": "FirstUTMSource",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "UTM: medium",
                          "type": "multiline",
                          "dim": "ym:s:firstUTMMedium",
                          "id": "FirstUTMMedium",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "UTM: campaign",
                          "type": "multiline",
                          "dim": "ym:s:firstUTMCampaign",
                          "id": "FirstUTMCampaign",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "UTM: content",
                          "type": "multiline",
                          "dim": "ym:s:firstUTMContent",
                          "id": "FirstUTMContent",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "UTM: term",
                          "type": "multiline",
                          "dim": "ym:s:firstUTMTerm",
                          "id": "FirstUTMTerm",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Openstat: service",
                          "type": "multiline",
                          "dim": "ym:s:firstOpenstatService",
                          "id": "FirstOpenstatService",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Openstat: campaign",
                          "type": "multiline",
                          "dim": "ym:s:firstOpenstatCampaign",
                          "id": "FirstOpenstatCampaign",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Openstat: ad",
                          "type": "multiline",
                          "dim": "ym:s:firstOpenstatAd",
                          "id": "FirstOpenstatAd",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Openstat: source",
                          "type": "multiline",
                          "dim": "ym:s:firstOpenstatSource",
                          "id": "FirstOpenstatSource",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Наличие GCLID",
                          "type": "bool",
                          "dim": "ym:s:firstHasGCLID",
                          "id": "FirstHasGCLID",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits",
                          "yes_label": "Есть",
                          "no_label": "Нет"
                        }
                      ]
                    }
                  ]
                },
                {
                  "name": "Последний значимый источник",
                  "type": "menu",
                  "id": "sources_last_sign",
                  "chld": [
                    {
                      "name": "Тип источника",
                      "full_name": "Тип последнего значимого источника",
                      "type": "list",
                      "dim": "ym:s:lastSignTrafficSource",
                      "id": "LastSignTrafficSource",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits"
                    },
                    {
                      "name": "Рекламная система",
                      "full_name": "Последняя значимая рекламная система",
                      "type": "list",
                      "dim": "ym:s:lastSignAdvEngine",
                      "wv_dim": "ym:s:WVLastSignAdvEngine",
                      "id": "LastSignAdvEngine",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits"
                    },
                    {
                      "name": "Поисковая система",
                      "full_name": "Последняя значимая поисковая система",
                      "type": "path",
                      "dim": "ym:s:lastSignSearchEngineRoot",
                      "id": "LastSignSearchEngineRoot",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "dims": [
                        "ym:s:lastSignSearchEngineRoot",
                        "ym:s:lastSignSearchEngine"
                      ]
                    },
                    {
                      "name": "Поисковая фраза",
                      "full_name": "Последняя значимая поисковая фраза",
                      "type": "multiline",
                      "dim": "ym:s:lastSignSearchPhrase",
                      "id": "LastSignSearchPhrase",
                      "table": "visits",
                      "permission_scope": "private",
                      "count_metric": "ym:s:visits"
                    },
                    {
                      "name": "Переходы с сайтов",
                      "full_name": "Последние значимые переходы с сайтов",
                      "type": "multiline",
                      "dim": "ym:s:lastSignReferalSource",
                      "id": "LastSignReferalSource",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits"
                    },
                    {
                      "name": "Социальные сети",
                      "full_name": "Последние значимые социальные сети",
                      "type": "list",
                      "dim": "ym:s:lastSignSocialNetwork",
                      "id": "LastSignSocialNetwork",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits"
                    },
                    {
                      "name": "Группа соц. сети",
                      "full_name": "Последняя значимая группа соц. сети",
                      "type": "multiline",
                      "dim": "ym:s:lastSignSocialNetworkProfile",
                      "id": "LastSignSocialNetworkProfile",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits"
                    },
                    {
                      "name": "Директ",
                      "type": "menu",
                      "id": "direct_last_sign",
                      "chld": [
                        {
                          "name": "Кампания",
                          "type": "list",
                          "dim": "ym:s:lastSignDirectClickOrder",
                          "wv_dim": "ym:s:WVLastSignDirectClickOrder",
                          "id": "LastSignDirectClickOrder",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits",
                          "values_filter_dims": [
                            "ym:s:lastSignDirectClickOrderName",
                            "ym:s:lastSignDirectID"
                          ]
                        },
                        {
                          "name": "Группа объявлений",
                          "type": "list",
                          "dim": "ym:s:lastSignDirectBannerGroup",
                          "wv_dim": "ym:s:WVLastSignDirectBannerGroup",
                          "id": "LastSignDirectBannerGroup",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Тип площадки",
                          "type": "list",
                          "dim": "ym:s:lastSignDirectPlatformType",
                          "wv_dim": "ym:s:WVLastSignDirectPlatformType",
                          "id": "LastSignDirectPlatformType",
                          "table": "visits",
                          "advanced": true,
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Площадка",
                          "type": "list",
                          "dim": "ym:s:lastSignDirectPlatform",
                          "wv_dim": "ym:s:WVLastSignDirectPlatform",
                          "id": "LastSignDirectPlatform",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Поисковая фраза",
                          "type": "multiline",
                          "dim": "ym:s:lastSignDirectSearchPhrase",
                          "wv_dim": "ym:s:directSearchPhraseShort",
                          "id": "LastSignDirectSearchPhrase",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Объявление Яндекс.Директа",
                          "type": "list",
                          "dim": "ym:s:lastSignDirectClickBanner",
                          "id": "LastSignDirectClickBanner",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits",
                          "values_filter_dims": [
                            "ym:s:lastSignDirectClickBannerName",
                            "ym:s:lastSignDirectBanner"
                          ]
                        },
                        {
                          "name": "Текст объявления",
                          "type": "list",
                          "dim": "ym:s:lastSignDirectBannerText",
                          "wv_dim": "ym:s:WVLastSignDirectBannerText",
                          "id": "LastSignDirectBannerText",
                          "table": "visits",
                          "advanced": true,
                          "permission_scope": "internal",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Тип условия подбора объявления",
                          "type": "list",
                          "dim": "ym:s:lastSignDirectConditionType",
                          "wv_dim": "ym:s:WVLastSignDirectConditionType",
                          "id": "LastSignDirectConditionType",
                          "table": "visits",
                          "advanced": true,
                          "permission_scope": "internal",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Условие подбора объявления",
                          "type": "list",
                          "dim": "ym:s:lastSignDirectPhraseOrCond",
                          "wv_dim": "ym:s:WVLastSignDirectCondition",
                          "id": "LastSignDirectPhraseOrCond",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits"
                        }
                      ]
                    },
                    {
                      "name": "Дисплей",
                      "type": "menu",
                      "id": "display_last_sign",
                      "chld": [
                        {
                          "name": "Номер заказа Яндекс.Дисплея",
                          "type": "list",
                          "dim": "ym:s:lastSignDisplayCampaign",
                          "id": "LastSignDisplayCampaign",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits"
                        }
                      ]
                    },
                    {
                      "name": "Метки",
                      "type": "menu",
                      "id": "tags_last_sign",
                      "chld": [
                        {
                          "name": "from",
                          "type": "multiline",
                          "dim": "ym:s:lastSignFrom",
                          "id": "LastSignFrom",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "UTM: source",
                          "type": "multiline",
                          "dim": "ym:s:lastSignUTMSource",
                          "id": "LastSignUTMSource",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "UTM: medium",
                          "type": "multiline",
                          "dim": "ym:s:lastSignUTMMedium",
                          "id": "LastSignUTMMedium",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "UTM: campaign",
                          "type": "multiline",
                          "dim": "ym:s:lastSignUTMCampaign",
                          "id": "LastSignUTMCampaign",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "UTM: content",
                          "type": "multiline",
                          "dim": "ym:s:lastSignUTMContent",
                          "id": "LastSignUTMContent",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "UTM: term",
                          "type": "multiline",
                          "dim": "ym:s:lastSignUTMTerm",
                          "id": "LastSignUTMTerm",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Openstat: service",
                          "type": "multiline",
                          "dim": "ym:s:lastSignOpenstatService",
                          "id": "LastSignOpenstatService",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Openstat: campaign",
                          "type": "multiline",
                          "dim": "ym:s:lastSignOpenstatCampaign",
                          "id": "LastSignOpenstatCampaign",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Openstat: ad",
                          "type": "multiline",
                          "dim": "ym:s:lastSignOpenstatAd",
                          "id": "LastSignOpenstatAd",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Openstat: source",
                          "type": "multiline",
                          "dim": "ym:s:lastSignOpenstatSource",
                          "id": "LastSignOpenstatSource",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits"
                        },
                        {
                          "name": "Наличие GCLID",
                          "type": "bool",
                          "dim": "ym:s:lastSignHasGCLID",
                          "id": "LastSignHasGCLID",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits",
                          "yes_label": "Есть",
                          "no_label": "Нет"
                        }
                      ]
                    }
                  ]
                },
                {
                  "name": "Маркет, поисковая фраза",
                  "type": "multiline",
                  "dim": "ym:s:marketSearchPhrase",
                  "wv_dim": "ym:s:WVMarketSearchPhrase",
                  "id": "MarketSearchPhrase",
                  "table": "visits",
                  "permission_scope": "private",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Реферер",
                  "type": "url",
                  "dim": "ym:s:referer",
                  "id": "referer",
                  "table": "visits",
                  "advanced": true,
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "host_dim": "ym:s:refererDomain",
                  "path_dim": "ym:s:refererPathFull"
                },
                {
                  "name": "Внешний реферер",
                  "type": "url",
                  "dim": "ym:s:externalReferer",
                  "id": "external_referer",
                  "table": "visits",
                  "advanced": true,
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "host_dim": "ym:s:externalRefererDomain",
                  "path_dim": "ym:s:externalRefererPathFull"
                }
              ]
            },
            {
              "name": "Поведение",
              "type": "menu",
              "id": "behaviour",
              "chld": [
                {
                  "name": "Просмотр",
                  "type": "menu",
                  "id": "hits",
                  "chld": [
                    {
                      "name": "Просмотр URL",
                      "type": "url",
                      "dim": "ym:pv:URL",
                      "id": "URL",
                      "table": "hits",
                      "permission_scope": "common",
                      "count_metric": "ym:pv:pageviews",
                      "host_dim": "ym:pv:URLDomain",
                      "path_dim": "ym:pv:URLPathFull"
                    },
                    {
                      "name": "Заголовок",
                      "type": "multiline",
                      "dim": "ym:pv:title",
                      "id": "Title",
                      "table": "hits",
                      "permission_scope": "common",
                      "count_metric": "ym:pv:pageviews"
                    },
                    {
                      "name": "Реферер просмотра",
                      "type": "url",
                      "dim": "ym:pv:referer",
                      "id": "Referer",
                      "table": "hits",
                      "permission_scope": "common",
                      "count_metric": "ym:pv:pageviews",
                      "host_dim": "ym:pv:refererDomain",
                      "path_dim": "ym:pv:refererPathFull"
                    }
                  ]
                },
                {
                  "name": "Загрузки",
                  "type": "menu",
                  "id": "downloads",
                  "chld": [
                    {
                      "name": "Загрузка файла",
                      "type": "url",
                      "dim": "ym:dl:downloadURL",
                      "id": "DownloadURL",
                      "table": "downloads",
                      "permission_scope": "common",
                      "count_metric": "ym:dl:pageviews",
                      "host_dim": "ym:dl:downloadURLDomain",
                      "path_dim": "ym:dl:downloadURLPathFull"
                    },
                    {
                      "name": "Страница загрузки",
                      "type": "url",
                      "dim": "ym:dl:pageURL",
                      "id": "PageURL",
                      "table": "downloads",
                      "permission_scope": "common",
                      "count_metric": "ym:dl:pageviews",
                      "host_dim": "ym:dl:pageURLDomain",
                      "path_dim": "ym:dl:pageURLPathFull"
                    }
                  ]
                },
                {
                  "name": "Внешний переход",
                  "type": "multiline",
                  "dim": "ym:el:externalLink",
                  "id": "ExternalLink",
                  "table": "external_links",
                  "permission_scope": "common",
                  "count_metric": "ym:el:pageviews"
                },
                {
                  "name": "Достижение цели",
                  "type": "goals",
                  "dim": "ym:s:goal",
                  "id": "Goal",
                  "table": "visits",
                  "permission_scope": "private",
                  "count_metric": "ym:s:visits",
                  "filter_template": "ym:s:goal<goal_id>IsReached=='Yes'",
                  "dimension_template": "ym:s:goal<goal_id>IsReached"
                },
                {
                  "name": "Глубина просмотра",
                  "type": "number",
                  "dim": "ym:s:pageViews",
                  "id": "PageViews",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Время на сайте",
                  "type": "number",
                  "dim": "ym:s:visitDuration",
                  "wv_dim": "ym:s:visitDurationShort",
                  "id": "VisitDuration",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "units": [
                    {
                      "label": "секунды",
                      "x": 1
                    },
                    {
                      "label": "минуты",
                      "x": 60
                    }
                  ]
                },
                {
                  "name": "Отказы",
                  "type": "bool",
                  "dim": "ym:s:bounce",
                  "id": "Bounce",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "yes_label": "Отказ",
                  "no_label": "Не отказ",
                  "label_style": "display_none"
                },
                {
                  "name": "Страница входа",
                  "type": "url",
                  "dim": "ym:s:startURL",
                  "id": "StartURL",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "host_dim": "ym:s:startURLDomain",
                  "path_dim": "ym:s:startURLPathFull"
                },
                {
                  "name": "Страница выхода",
                  "type": "url",
                  "dim": "ym:s:endURL",
                  "id": "EndURL",
                  "table": "visits",
                  "advanced": true,
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "host_dim": "ym:s:endURLDomain",
                  "path_dim": "ym:s:endURLPathFull"
                },
                {
                  "name": "Параметры визита",
                  "type": "params",
                  "dim": "ym:s:paramsLevel1",
                  "id": "ParamsLevel1",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "dims": [
                    "ym:s:paramsLevel1",
                    "ym:s:paramsLevel2",
                    "ym:s:paramsLevel3",
                    "ym:s:paramsLevel4",
                    "ym:s:paramsLevel5",
                    "ym:s:paramsLevel6",
                    "ym:s:paramsLevel7",
                    "ym:s:paramsLevel8",
                    "ym:s:paramsLevel9",
                    "ym:s:paramsLevel10"
                  ],
                  "dim_value_double": "ym:s:paramsValueDouble",
                  "no_quantifier": false
                },
                {
                  "name": "Час посещения",
                  "type": "number",
                  "dim": "ym:s:hour",
                  "id": "Hour",
                  "table": "visits",
                  "advanced": true,
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Доменная зона cookie",
                  "type": "list",
                  "dim": "ym:pv:cookieDomainZone",
                  "id": "CookieDomainZone",
                  "table": "hits",
                  "advanced": true,
                  "permission_scope": "internal",
                  "count_metric": "ym:pv:pageviews"
                }
              ]
            },
            {
              "name": "История",
              "type": "menu",
              "id": "history",
              "chld": [
                {
                  "name": "Новый/вернувшийся посетитель",
                  "type": "bool",
                  "dim": "ym:s:isNewUser",
                  "id": "IsNewUser",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "yes_label": "Новый посетитель",
                  "no_label": "Вернувшийся посетитель",
                  "label_style": "display_none"
                },
                {
                  "name": "Номер визита",
                  "type": "number",
                  "dim": "ym:s:userVisits",
                  "id": "UserVisits",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Время c первого визита",
                  "type": "number",
                  "dim": "ym:s:daysSinceFirstVisit",
                  "id": "DaysSinceFirstVisit",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "units": [
                    {
                      "label": "дни",
                      "x": 1
                    },
                    {
                      "label": "недели",
                      "x": 7
                    },
                    {
                      "label": "месяцы",
                      "x": 30
                    }
                  ]
                },
                {
                  "name": "Время c предыдущего визита",
                  "type": "number",
                  "dim": "ym:s:daysSincePreviousVisit",
                  "id": "DaysSincePreviousVisit",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "units": [
                    {
                      "label": "дни",
                      "x": 1
                    },
                    {
                      "label": "недели",
                      "x": 7
                    },
                    {
                      "label": "месяцы",
                      "x": 30
                    }
                  ]
                },
                {
                  "name": "Дата предыдущего визита",
                  "type": "date",
                  "dim": "ym:s:previousVisitDate",
                  "id": "PreviousVisitDate",
                  "table": "visits",
                  "advanced": true,
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Среднее время между визитами",
                  "type": "number",
                  "dim": "ym:s:userVisitsPeriod",
                  "id": "UserVisitsPeriod",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "units": [
                    {
                      "label": "дни",
                      "x": 1
                    },
                    {
                      "label": "недели",
                      "x": 7
                    },
                    {
                      "label": "месяцы",
                      "x": 30
                    }
                  ]
                }
              ]
            },
            {
              "name": "Вебвизор",
              "type": "menu",
              "id": "webvisor",
              "restricted": "webvisor",
              "chld": [
                {
                  "name": "Просмотренное",
                  "type": "bool",
                  "dim": "ym:s:webVisorViewed",
                  "id": "WebVisorViewed",
                  "table": "visits",
                  "restricted": "webvisor",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "yes_label": "Да",
                  "no_label": "Нет"
                },
                {
                  "name": "Избранное",
                  "type": "bool",
                  "dim": "ym:s:webVisorSelected",
                  "id": "WebVisorSelected",
                  "table": "visits",
                  "restricted": "webvisor",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "yes_label": "Да",
                  "no_label": "Нет"
                },
                {
                  "name": "Активность",
                  "type": "number",
                  "dim": "ym:s:webVisorActivity",
                  "id": "WebVisorActivity",
                  "table": "visits",
                  "restricted": "webvisor",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Визиты выбранного пользователя",
                  "type": "uid",
                  "dim": "ym:s:userIDHash",
                  "id": "UserIDHash",
                  "table": "visits",
                  "restricted": "webvisor",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Фраза",
                  "type": "multiline",
                  "dim": "ym:s:searchPhraseAll",
                  "wv_dim": "ym:s:searchPhraseAll",
                  "id": "SearchPhraseAll",
                  "table": "visits",
                  "restricted": "webvisor",
                  "permission_scope": "private",
                  "count_metric": "ym:s:visits"
                }
              ]
            },
            {
              "name": "География",
              "type": "menu",
              "id": "geo",
              "chld": [
                {
                  "name": "Местоположение",
                  "type": "path",
                  "dim": "ym:s:regionCountry",
                  "id": "RegionCountry",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "dims": [
                    "ym:s:regionCountry",
                    "ym:s:regionArea",
                    "ym:s:regionCity"
                  ],
                  "concat": " \u2192 "
                },
                {
                  "name": "Размер города",
                  "type": "list",
                  "dim": "ym:s:regionCitySize",
                  "id": "RegionCitySize",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Часовой пояс",
                  "type": "list",
                  "dim": "ym:s:clientTimeZone",
                  "id": "ClientTimeZone",
                  "table": "visits",
                  "advanced": true,
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Язык браузера",
                  "type": "list",
                  "dim": "ym:s:browserLanguage",
                  "id": "BrowserLanguage",
                  "table": "visits",
                  "advanced": true,
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Страна браузера",
                  "type": "list",
                  "dim": "ym:s:browserCountry",
                  "id": "BrowserCountry",
                  "table": "visits",
                  "advanced": true,
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                }
              ]
            },
            {
              "name": "Технологии",
              "type": "menu",
              "id": "technology",
              "chld": [
                {
                  "name": "Устройство",
                  "type": "path",
                  "dim": "ym:s:deviceCategory",
                  "id": "DeviceCategory",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "dims": [
                    "ym:s:deviceCategory",
                    "ym:s:mobilePhone",
                    "ym:s:mobilePhoneModel"
                  ]
                },
                {
                  "name": "Операционные системы",
                  "type": "tree",
                  "dim": "ym:s:operatingSystemRoot",
                  "id": "OperatingSystemRoot",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "dims": [
                    "ym:s:operatingSystemRoot",
                    "ym:s:operatingSystem"
                  ]
                },
                {
                  "name": "Браузеры",
                  "type": "tree",
                  "dim": "ym:s:browser",
                  "id": "Browser",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "dims": [
                    "ym:s:browser",
                    "ym:s:browserAndVersionMajor"
                  ]
                },
                {
                  "name": "Технологии браузеров",
                  "type": "menu",
                  "id": "browser",
                  "chld": [
                    {
                      "name": "Движок браузера",
                      "type": "path",
                      "dim": "ym:s:browserEngine",
                      "id": "BrowserEngine",
                      "table": "visits",
                      "advanced": true,
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "dims": [
                        "ym:s:browserEngine",
                        "ym:s:browserEngineVersion1"
                      ]
                    },
                    {
                      "name": "Наличие блокировщиков рекламы",
                      "type": "bool",
                      "dim": "ym:s:hasAdBlocker",
                      "id": "HasAdBlocker",
                      "table": "visits",
                      "advanced": true,
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "yes_label": "Блокировка включена",
                      "no_label": "Блокировка выключена"
                    },
                    {
                      "name": "Поддержка Flash",
                      "type": "bool",
                      "dim": "ym:s:flashEnabled",
                      "id": "FlashEnabled",
                      "table": "visits",
                      "advanced": true,
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "yes_label": "Flash включен",
                      "no_label": "Flash выключен"
                    },
                    {
                      "name": "Поддержка cookies",
                      "type": "bool",
                      "dim": "ym:s:cookieEnabled",
                      "id": "CookieEnabled",
                      "table": "visits",
                      "advanced": true,
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "yes_label": "Cookies включены",
                      "no_label": "Cookies выключены"
                    },
                    {
                      "name": "Поддержка Javascript",
                      "type": "bool",
                      "dim": "ym:s:javascriptEnabled",
                      "id": "JavascriptEnabled",
                      "table": "visits",
                      "advanced": true,
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "yes_label": "Javascript включен",
                      "no_label": "Javascript выключен"
                    },
                    {
                      "name": "Поддержка SilverLight",
                      "type": "bool",
                      "dim": "ym:s:silverlightEnabled",
                      "id": "SilverlightEnabled",
                      "table": "visits",
                      "advanced": true,
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "yes_label": "SilverLight включен",
                      "no_label": "SilverLight выключен"
                    }
                  ]
                },
                {
                  "name": "IP",
                  "type": "multiline",
                  "dim": "ym:s:ipAddress",
                  "id": "IpAddress",
                  "table": "visits",
                  "permission_scope": "private",
                  "count_metric": "ym:s:visits",
                  "disable_suggest": true
                },
                {
                  "name": "Экран",
                  "type": "menu",
                  "id": "screen",
                  "chld": [
                    {
                      "name": "Соотношение сторон",
                      "type": "list",
                      "dim": "ym:s:screenFormat",
                      "id": "ScreenFormat",
                      "table": "visits",
                      "advanced": true,
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits"
                    },
                    {
                      "name": "Глубина цвета",
                      "type": "list",
                      "dim": "ym:s:screenColors",
                      "id": "ScreenColors",
                      "table": "visits",
                      "advanced": true,
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits"
                    },
                    {
                      "name": "Ориентация экрана",
                      "type": "list",
                      "dim": "ym:s:screenOrientation",
                      "id": "ScreenOrientation",
                      "table": "visits",
                      "advanced": true,
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits"
                    },
                    {
                      "name": "Логическое разрешение экрана",
                      "type": "path",
                      "dim": "ym:s:screenWidth",
                      "id": "logical_resolution",
                      "table": "visits",
                      "advanced": true,
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "dims": [
                        "ym:s:screenWidth",
                        "ym:s:screenHeight"
                      ],
                      "concat": "x"
                    },
                    {
                      "name": "Физическое разрешение экрана",
                      "type": "path",
                      "dim": "ym:s:physicalScreenWidth",
                      "id": "PhysicalScreenWidth",
                      "table": "visits",
                      "advanced": true,
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "dims": [
                        "ym:s:physicalScreenWidth",
                        "ym:s:physicalScreenHeight"
                      ],
                      "concat": "x"
                    },
                    {
                      "name": "Размер окна",
                      "type": "path",
                      "dim": "ym:s:windowClientWidth",
                      "id": "WindowClientWidth",
                      "table": "visits",
                      "advanced": true,
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "dims": [
                        "ym:s:windowClientWidth",
                        "ym:s:windowClientHeight"
                      ],
                      "concat": "x"
                    }
                  ]
                }
              ]
            },
            {
              "name": "Электронная коммерция",
              "type": "menu",
              "id": "ecommerce",
              "chld": [
                {
                  "name": "Категория товара",
                  "type": "path",
                  "dim": "ym:s:productCategoryLevel1",
                  "id": "ProductCategoryLevel1",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "dims": [
                    "ym:s:productCategoryLevel1",
                    "ym:s:productCategoryLevel2",
                    "ym:s:productCategoryLevel3",
                    "ym:s:productCategoryLevel4",
                    "ym:s:productCategoryLevel5"
                  ]
                },
                {
                  "name": "ID товара",
                  "type": "list",
                  "dim": "ym:s:productID",
                  "id": "ProductID",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Название товара",
                  "type": "list",
                  "dim": "ym:s:productName",
                  "id": "ProductName",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Бренд",
                  "type": "list",
                  "dim": "ym:s:productBrand",
                  "id": "ProductBrand",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Стоимость единицы товара",
                  "type": "number",
                  "dim": "ym:s:productPrice",
                  "id": "ProductPrice",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Промокод товара",
                  "type": "list",
                  "dim": "ym:s:productCoupon",
                  "id": "ProductCoupon",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "ID товаров в корзине",
                  "type": "list",
                  "dim": "ym:s:productIDCart",
                  "id": "ProductIDCart",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Товары в корзине",
                  "type": "list",
                  "dim": "ym:s:productNameCart",
                  "id": "ProductNameCart",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Бренды в корзине",
                  "type": "list",
                  "dim": "ym:s:productBrandCart",
                  "id": "ProductBrandCart",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "ID заказанных товаров",
                  "type": "list",
                  "dim": "ym:s:PProductID",
                  "id": "PProductID",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Заказанные товары",
                  "type": "list",
                  "dim": "ym:s:PProductName",
                  "id": "PProductName",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Бренды заказанных товаров",
                  "type": "list",
                  "dim": "ym:s:PProductBrand",
                  "id": "PProductBrand",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Промокод покупки",
                  "type": "list",
                  "dim": "ym:s:purchaseCoupon",
                  "id": "PurchaseCoupon",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Сумма покупки",
                  "type": "number",
                  "dim": "ym:s:purchaseRevenue",
                  "id": "PurchaseRevenue",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Заказы в визите",
                  "type": "bool",
                  "dim": "ym:s:purchaseExistsVisit",
                  "id": "PurchaseExistsVisit",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "yes_label": "Есть",
                  "no_label": "Нет"
                },
                {
                  "name": "Доход визита",
                  "type": "number",
                  "dim": "ym:s:purchaseRevenueVisit",
                  "id": "PurchaseRevenueVisit",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Количество покупок в визите",
                  "type": "number",
                  "dim": "ym:s:purchaseCountVisit",
                  "id": "PurchaseCountVisit",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Товаров просмотрено в визите",
                  "type": "number",
                  "dim": "ym:s:impressionCountVisit",
                  "id": "ImpressionCountVisit",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits"
                }
              ]
            },
            {
              "name": "Только для Яндекса",
              "type": "menu",
              "id": "internal",
              "chld": [
                {
                  "name": "Номер счетчика",
                  "type": "list",
                  "dim": "ym:s:counterID",
                  "id": "CounterID",
                  "table": "visits",
                  "advanced": true,
                  "permission_scope": "internal",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Порядковый номер счетчика",
                  "type": "list",
                  "dim": "ym:s:counterIDSerial",
                  "id": "CounterIDSerial",
                  "table": "visits",
                  "advanced": true,
                  "permission_scope": "internal",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Тип счетчика",
                  "type": "list",
                  "dim": "ym:s:counterClass",
                  "id": "CounterClass",
                  "table": "visits",
                  "advanced": true,
                  "permission_scope": "internal",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Механизм привязки клика",
                  "type": "list",
                  "dim": "ym:s:clickCounterIDMatchType",
                  "id": "ClickCounterIDMatchType",
                  "table": "visits",
                  "advanced": true,
                  "permission_scope": "internal",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Идентификатор посетителя (uid)",
                  "type": "multiline",
                  "dim": "ym:s:userIDString",
                  "id": "UserIDString",
                  "table": "visits",
                  "advanced": true,
                  "permission_scope": "internal",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "Наличие AWAPSCLID",
                  "type": "bool",
                  "dim": "ym:s:hasYACLID",
                  "id": "HasYACLID",
                  "table": "visits",
                  "advanced": true,
                  "permission_scope": "internal",
                  "count_metric": "ym:s:visits",
                  "yes_label": "Есть",
                  "no_label": "Нет"
                },
                {
                  "name": "Наличие DirectCLID",
                  "type": "bool",
                  "dim": "ym:s:hasYDCLID",
                  "id": "HasYDCLID",
                  "table": "visits",
                  "advanced": true,
                  "permission_scope": "internal",
                  "count_metric": "ym:s:visits",
                  "yes_label": "Есть",
                  "no_label": "Нет"
                },
                {
                  "name": "Наличие MarketCLID",
                  "type": "bool",
                  "dim": "ym:s:hasYMCLID",
                  "id": "HasYMCLID",
                  "table": "visits",
                  "advanced": true,
                  "permission_scope": "internal",
                  "count_metric": "ym:s:visits",
                  "yes_label": "Есть",
                  "no_label": "Нет"
                },
                {
                  "name": "Сайт Яндекса",
                  "type": "bool",
                  "dim": "ym:s:isYandex",
                  "id": "IsYandex",
                  "table": "visits",
                  "advanced": true,
                  "permission_scope": "internal",
                  "count_metric": "ym:s:visits",
                  "yes_label": "Да",
                  "no_label": "Нет"
                },
                {
                  "name": "IP exact",
                  "type": "multiline",
                  "dim": "ym:s:ip",
                  "id": "Ip",
                  "table": "visits",
                  "advanced": true,
                  "permission_scope": "internal",
                  "count_metric": "ym:s:visits",
                  "disable_suggest": true
                },
                {
                  "name": "CLID",
                  "type": "list",
                  "dim": "ym:s:CLID",
                  "id": "CLID",
                  "table": "visits",
                  "advanced": true,
                  "permission_scope": "internal",
                  "count_metric": "ym:s:visits"
                },
                {
                  "name": "IP сеть",
                  "type": "menu",
                  "id": "network",
                  "chld": [
                    {
                      "name": "IPv4",
                      "type": "multiline",
                      "dim": "ym:s:ip4",
                      "id": "Ip4",
                      "table": "visits",
                      "advanced": true,
                      "permission_scope": "internal",
                      "count_metric": "ym:s:visits",
                      "disable_suggest": true
                    },
                    {
                      "name": "IPv6",
                      "type": "multiline",
                      "dim": "ym:s:ip6",
                      "id": "Ip6",
                      "table": "visits",
                      "advanced": true,
                      "permission_scope": "internal",
                      "count_metric": "ym:s:visits",
                      "disable_suggest": true
                    },
                    {
                      "name": "IP-сеть Яндекса",
                      "type": "bool",
                      "dim": "ym:s:inYandexRegion",
                      "id": "InYandexRegion",
                      "table": "visits",
                      "advanced": true,
                      "permission_scope": "internal",
                      "count_metric": "ym:s:visits",
                      "yes_label": "Да",
                      "no_label": "Нет"
                    }
                  ]
                }
              ]
            },
            {
              "name": "Директ - расходы",
              "type": "menu",
              "id": "clicks",
              "chld": [
                {
                  "name": "Первый источник",
                  "type": "menu",
                  "id": "direct_clicks_first",
                  "chld": [
                    {
                      "name": "Кампания",
                      "type": "list",
                      "dim": "ym:ad:firstDirectOrder",
                      "id": "FirstDirectOrder",
                      "table": "advertising",
                      "permission_scope": "common",
                      "count_metric": "ym:ad:clicks",
                      "values_filter_dims": [
                        "ym:ad:firstDirectOrderName",
                        "ym:ad:firstDirectID"
                      ]
                    },
                    {
                      "name": "Тип площадки",
                      "type": "list",
                      "dim": "ym:ad:firstDirectPlatformType",
                      "id": "FirstDirectPlatformType",
                      "table": "advertising",
                      "advanced": true,
                      "permission_scope": "private",
                      "count_metric": "ym:ad:clicks"
                    },
                    {
                      "name": "Площадка",
                      "type": "list",
                      "dim": "ym:ad:firstDirectPlatform",
                      "id": "FirstDirectPlatform",
                      "table": "advertising",
                      "permission_scope": "private",
                      "count_metric": "ym:ad:clicks"
                    },
                    {
                      "name": "Группа объявлений",
                      "type": "list",
                      "dim": "ym:ad:firstDirectBannerGroup",
                      "id": "FirstDirectBannerGroup",
                      "table": "advertising",
                      "permission_scope": "private",
                      "count_metric": "ym:ad:clicks"
                    },
                    {
                      "name": "Поисковая фраза",
                      "type": "multiline",
                      "dim": "ym:ad:firstDirectSearchPhrase",
                      "id": "FirstDirectSearchPhrase",
                      "table": "advertising",
                      "permission_scope": "common",
                      "count_metric": "ym:ad:clicks"
                    },
                    {
                      "name": "Объявление Яндекс.Директа",
                      "type": "list",
                      "dim": "ym:ad:firstDirectBanner",
                      "id": "FirstDirectBanner",
                      "table": "advertising",
                      "permission_scope": "common",
                      "count_metric": "ym:ad:clicks",
                      "values_filter_dims": [
                        "ym:ad:firstDirectBannerName",
                        "ym:ad:firstDirectBannerID"
                      ]
                    },
                    {
                      "name": "Текст объявления",
                      "type": "list",
                      "dim": "ym:ad:firstDirectBannerText",
                      "id": "FirstDirectBannerText",
                      "table": "advertising",
                      "advanced": true,
                      "permission_scope": "internal",
                      "count_metric": "ym:ad:clicks"
                    },
                    {
                      "name": "Тип условия подбора объявления",
                      "type": "list",
                      "dim": "ym:ad:firstDirectConditionType",
                      "id": "FirstDirectConditionType",
                      "table": "advertising",
                      "advanced": true,
                      "permission_scope": "internal",
                      "count_metric": "ym:ad:clicks"
                    },
                    {
                      "name": "Условие подбора объявления",
                      "type": "list",
                      "dim": "ym:ad:firstDirectPhraseOrCond",
                      "id": "FirstDirectPhraseOrCond",
                      "table": "advertising",
                      "permission_scope": "common",
                      "count_metric": "ym:ad:clicks"
                    }
                  ]
                },
                {
                  "name": "Последний источник",
                  "type": "menu",
                  "id": "direct_clicks_last",
                  "chld": [
                    {
                      "name": "Кампания",
                      "type": "list",
                      "dim": "ym:ad:lastDirectOrder",
                      "id": "LastDirectOrder",
                      "table": "advertising",
                      "permission_scope": "common",
                      "count_metric": "ym:ad:clicks",
                      "values_filter_dims": [
                        "ym:ad:lastDirectOrderName",
                        "ym:ad:lastDirectID"
                      ]
                    },
                    {
                      "name": "Тип площадки",
                      "type": "list",
                      "dim": "ym:ad:lastDirectPlatformType",
                      "id": "LastDirectPlatformType",
                      "table": "advertising",
                      "advanced": true,
                      "permission_scope": "private",
                      "count_metric": "ym:ad:clicks"
                    },
                    {
                      "name": "Площадка",
                      "type": "list",
                      "dim": "ym:ad:lastDirectPlatform",
                      "id": "LastDirectPlatform",
                      "table": "advertising",
                      "permission_scope": "private",
                      "count_metric": "ym:ad:clicks"
                    },
                    {
                      "name": "Группа объявлений",
                      "type": "list",
                      "dim": "ym:ad:lastDirectBannerGroup",
                      "id": "LastDirectBannerGroup",
                      "table": "advertising",
                      "permission_scope": "private",
                      "count_metric": "ym:ad:clicks"
                    },
                    {
                      "name": "Поисковая фраза",
                      "type": "multiline",
                      "dim": "ym:ad:lastDirectSearchPhrase",
                      "id": "LastDirectSearchPhrase",
                      "table": "advertising",
                      "permission_scope": "common",
                      "count_metric": "ym:ad:clicks"
                    },
                    {
                      "name": "Объявление Яндекс.Директа",
                      "type": "list",
                      "dim": "ym:ad:lastDirectBanner",
                      "id": "LastDirectBanner",
                      "table": "advertising",
                      "permission_scope": "common",
                      "count_metric": "ym:ad:clicks",
                      "values_filter_dims": [
                        "ym:ad:lastDirectBannerName",
                        "ym:ad:lastDirectBannerID"
                      ]
                    },
                    {
                      "name": "Текст объявления",
                      "type": "list",
                      "dim": "ym:ad:lastDirectBannerText",
                      "id": "LastDirectBannerText",
                      "table": "advertising",
                      "advanced": true,
                      "permission_scope": "internal",
                      "count_metric": "ym:ad:clicks"
                    },
                    {
                      "name": "Тип условия подбора объявления",
                      "type": "list",
                      "dim": "ym:ad:lastDirectConditionType",
                      "id": "LastDirectConditionType",
                      "table": "advertising",
                      "advanced": true,
                      "permission_scope": "internal",
                      "count_metric": "ym:ad:clicks"
                    },
                    {
                      "name": "Условие подбора объявления",
                      "type": "list",
                      "dim": "ym:ad:lastDirectPhraseOrCond",
                      "id": "LastDirectPhraseOrCond",
                      "table": "advertising",
                      "permission_scope": "common",
                      "count_metric": "ym:ad:clicks"
                    }
                  ]
                },
                {
                  "name": "Последний значимый источник",
                  "type": "menu",
                  "id": "direct_clicks_lastsign",
                  "chld": [
                    {
                      "name": "Кампания",
                      "type": "list",
                      "dim": "ym:ad:lastSignDirectOrder",
                      "id": "LastSignDirectOrder",
                      "table": "advertising",
                      "permission_scope": "common",
                      "count_metric": "ym:ad:clicks",
                      "values_filter_dims": [
                        "ym:ad:lastSignDirectOrderName",
                        "ym:ad:lastSignDirectID"
                      ]
                    },
                    {
                      "name": "Тип площадки",
                      "type": "list",
                      "dim": "ym:ad:lastSignDirectPlatformType",
                      "id": "LastSignDirectPlatformType",
                      "table": "advertising",
                      "advanced": true,
                      "permission_scope": "private",
                      "count_metric": "ym:ad:clicks"
                    },
                    {
                      "name": "Площадка",
                      "type": "list",
                      "dim": "ym:ad:lastSignDirectPlatform",
                      "id": "LastSignDirectPlatform",
                      "table": "advertising",
                      "permission_scope": "private",
                      "count_metric": "ym:ad:clicks"
                    },
                    {
                      "name": "Группа объявлений",
                      "type": "list",
                      "dim": "ym:ad:lastSignDirectBannerGroup",
                      "id": "LastSignDirectBannerGroup",
                      "table": "advertising",
                      "permission_scope": "private",
                      "count_metric": "ym:ad:clicks"
                    },
                    {
                      "name": "Поисковая фраза",
                      "type": "multiline",
                      "dim": "ym:ad:lastSignDirectSearchPhrase",
                      "id": "LastSignDirectSearchPhrase",
                      "table": "advertising",
                      "permission_scope": "common",
                      "count_metric": "ym:ad:clicks"
                    },
                    {
                      "name": "Объявление Яндекс.Директа",
                      "type": "list",
                      "dim": "ym:ad:lastSignDirectBanner",
                      "id": "LastSignDirectBanner",
                      "table": "advertising",
                      "permission_scope": "common",
                      "count_metric": "ym:ad:clicks",
                      "values_filter_dims": [
                        "ym:ad:lastSignDirectBannerName",
                        "ym:ad:lastSignDirectBannerID"
                      ]
                    },
                    {
                      "name": "Текст объявления",
                      "type": "list",
                      "dim": "ym:ad:lastSignDirectBannerText",
                      "id": "LastSignDirectBannerText",
                      "table": "advertising",
                      "advanced": true,
                      "permission_scope": "internal",
                      "count_metric": "ym:ad:clicks"
                    },
                    {
                      "name": "Тип условия подбора объявления",
                      "type": "list",
                      "dim": "ym:ad:lastSignDirectConditionType",
                      "id": "LastSignDirectConditionType",
                      "table": "advertising",
                      "advanced": true,
                      "permission_scope": "internal",
                      "count_metric": "ym:ad:clicks"
                    },
                    {
                      "name": "Условие подбора объявления",
                      "type": "list",
                      "dim": "ym:ad:lastSignDirectPhraseOrCond",
                      "id": "LastSignDirectPhraseOrCond",
                      "table": "advertising",
                      "permission_scope": "common",
                      "count_metric": "ym:ad:clicks"
                    }
                  ]
                },
                {
                  "name": "Аудитория",
                  "type": "menu",
                  "id": "audience_clicks",
                  "chld": [
                    {
                      "name": "Интересы",
                      "type": "list",
                      "dim": "ym:ad:interest",
                      "id": "Interest",
                      "table": "advertising",
                      "permission_scope": "common",
                      "count_metric": "ym:ad:clicks"
                    },
                    {
                      "name": "Местоположение",
                      "type": "path",
                      "dim": "ym:ad:regionCountry",
                      "id": "RegionCountry",
                      "table": "advertising",
                      "permission_scope": "common",
                      "count_metric": "ym:ad:clicks",
                      "dims": [
                        "ym:ad:regionCountry",
                        "ym:ad:regionArea",
                        "ym:ad:regionCity"
                      ],
                      "concat": " \u2192 "
                    },
                    {
                      "name": "Размер города",
                      "type": "list",
                      "dim": "ym:ad:regionCitySize",
                      "id": "RegionCitySize",
                      "table": "advertising",
                      "permission_scope": "common",
                      "count_metric": "ym:ad:clicks"
                    }
                  ]
                },
                {
                  "name": "Технологии",
                  "type": "menu",
                  "id": "technology_clicks",
                  "chld": [
                    {
                      "name": "IP",
                      "type": "multiline",
                      "dim": "ym:ad:ipAddress",
                      "id": "IpAddress",
                      "table": "advertising",
                      "permission_scope": "private",
                      "count_metric": "ym:ad:clicks",
                      "disable_suggest": true
                    },
                    {
                      "name": "IP (точный)",
                      "type": "multiline",
                      "dim": "ym:ad:ip",
                      "id": "Ip",
                      "table": "advertising",
                      "advanced": true,
                      "permission_scope": "internal",
                      "count_metric": "ym:ad:clicks",
                      "disable_suggest": true
                    },
                    {
                      "name": "IPv4 (точный)",
                      "type": "multiline",
                      "dim": "ym:ad:ip4",
                      "id": "Ip4",
                      "table": "advertising",
                      "advanced": true,
                      "permission_scope": "internal",
                      "count_metric": "ym:ad:clicks",
                      "disable_suggest": true
                    },
                    {
                      "name": "IPv6 (точный)",
                      "type": "multiline",
                      "dim": "ym:ad:ip6",
                      "id": "Ip6",
                      "table": "advertising",
                      "advanced": true,
                      "permission_scope": "internal",
                      "count_metric": "ym:ad:clicks",
                      "disable_suggest": true
                    },
                    {
                      "name": "IP-сеть Яндекса",
                      "type": "bool",
                      "dim": "ym:ad:inYandexRegion",
                      "id": "InYandexRegion",
                      "table": "advertising",
                      "advanced": true,
                      "permission_scope": "internal",
                      "count_metric": "ym:ad:clicks",
                      "yes_label": "Да",
                      "no_label": "Нет"
                    }
                  ]
                }
              ]
            }
          ],
          "usercentric_segments": [
            {
              "name": "Характеристики",
              "type": "menu",
              "id": "characteristics",
              "chld": [
                {
                  "name": "Пол",
                  "type": "list",
                  "dim": "ym:u:gender",
                  "id": "Gender",
                  "table": "users_visits",
                  "permission_scope": "common",
                  "count_metric": "ym:u:users",
                  "filter_type": "attr",
                  "user_dim": "ym:u:userID"
                },
                {
                  "name": "Возраст",
                  "type": "list",
                  "dim": "ym:u:ageInterval",
                  "id": "AgeInterval",
                  "table": "users_visits",
                  "permission_scope": "common",
                  "count_metric": "ym:u:users",
                  "filter_type": "attr",
                  "user_dim": "ym:u:userID"
                },
                {
                  "name": "Роботность",
                  "type": "bool",
                  "dim": "ym:s:isRobot",
                  "id": "IsRobot",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "filter_type": "attr",
                  "user_dim": "ym:s:specialUser",
                  "yes_label": "Роботы",
                  "no_label": "Люди"
                },
                {
                  "name": "География",
                  "type": "menu",
                  "id": "geo",
                  "chld": [
                    {
                      "name": "Местоположение",
                      "type": "path",
                      "dim": "ym:s:regionCountry",
                      "id": "RegionCountry",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "filter_type": "event",
                      "user_dim": "ym:s:specialUser",
                      "special_date_dim": "ym:s:specialDefaultDate",
                      "dims": [
                        "ym:s:regionCountry",
                        "ym:s:regionArea",
                        "ym:s:regionCity"
                      ],
                      "concat": " \u2192 "
                    },
                    {
                      "name": "Размер города",
                      "type": "list",
                      "dim": "ym:s:regionCitySize",
                      "id": "RegionCitySize",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "filter_type": "event",
                      "user_dim": "ym:s:specialUser",
                      "special_date_dim": "ym:s:specialDefaultDate"
                    },
                    {
                      "name": "Часовой пояс",
                      "type": "list",
                      "dim": "ym:s:clientTimeZone",
                      "id": "ClientTimeZone",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "filter_type": "event",
                      "user_dim": "ym:s:specialUser",
                      "special_date_dim": "ym:s:specialDefaultDate"
                    },
                    {
                      "name": "Язык браузера",
                      "type": "list",
                      "dim": "ym:s:browserLanguage",
                      "id": "BrowserLanguage",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "filter_type": "event",
                      "user_dim": "ym:s:specialUser",
                      "special_date_dim": "ym:s:specialDefaultDate"
                    },
                    {
                      "name": "Страна браузера",
                      "type": "list",
                      "dim": "ym:s:browserCountry",
                      "id": "BrowserCountry",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "filter_type": "event",
                      "user_dim": "ym:s:specialUser",
                      "special_date_dim": "ym:s:specialDefaultDate"
                    }
                  ]
                },
                {
                  "name": "Интересы",
                  "type": "list",
                  "dim": "ym:u:interest",
                  "id": "Interest",
                  "table": "users_visits",
                  "permission_scope": "common",
                  "count_metric": "ym:u:users",
                  "filter_type": "attr",
                  "user_dim": "ym:u:userID"
                },
                {
                  "name": "Дата первого визита",
                  "type": "date",
                  "dim": "ym:u:userFirstVisitDate",
                  "id": "UserFirstVisitDate",
                  "table": "users_visits",
                  "permission_scope": "common",
                  "count_metric": "ym:u:users",
                  "filter_type": "attr",
                  "user_dim": "ym:u:userID"
                },
                {
                  "name": "Дней на сайте",
                  "type": "number",
                  "dim": "ym:u:daysSinceFirstVisitOneBased",
                  "id": "DaysSinceFirstVisitOneBased",
                  "table": "users_visits",
                  "permission_scope": "common",
                  "count_metric": "ym:u:users",
                  "filter_type": "attr",
                  "user_dim": "ym:u:userID"
                },
                {
                  "name": "Параметры пользователей",
                  "type": "params",
                  "dim": "ym:up:paramsLevel1",
                  "id": "up",
                  "table": "user_param",
                  "permission_scope": "internal",
                  "count_metric": "ym:up:params",
                  "filter_type": "attr",
                  "user_dim": "ym:up:userID",
                  "dims": [
                    "ym:up:paramsLevel1",
                    "ym:up:paramsLevel2",
                    "ym:up:paramsLevel3",
                    "ym:up:paramsLevel4",
                    "ym:up:paramsLevel5"
                  ],
                  "dim_value_double": "ym:up:paramsValueDouble",
                  "no_quantifier": true
                }
              ]
            },
            {
              "name": "Метрики",
              "type": "menu",
              "id": "metrics",
              "chld": [
                {
                  "name": "Количество визитов",
                  "type": "number",
                  "dim": "ym:u:userVisits",
                  "id": "UserVisits",
                  "table": "users_visits",
                  "permission_scope": "common",
                  "count_metric": "ym:u:users",
                  "filter_type": "metric",
                  "user_dim": "ym:u:userID",
                  "special_date_dim": "ym:u:specialDefaultDate"
                },
                {
                  "name": "Количество просмотров",
                  "type": "number",
                  "dim": "ym:u:pageViews",
                  "id": "PageViews",
                  "table": "users_visits",
                  "permission_scope": "common",
                  "count_metric": "ym:u:users",
                  "filter_type": "metric",
                  "user_dim": "ym:u:userID",
                  "special_date_dim": "ym:u:specialDefaultDate"
                },
                {
                  "name": "Суммарное время на сайте",
                  "type": "number",
                  "dim": "ym:u:totalVisitsDuration",
                  "id": "TotalVisitsDuration",
                  "table": "users_visits",
                  "permission_scope": "common",
                  "count_metric": "ym:u:users",
                  "filter_type": "metric",
                  "user_dim": "ym:u:userID",
                  "special_date_dim": "ym:u:specialDefaultDate",
                  "units": [
                    {
                      "label": "секунды",
                      "x": 1
                    },
                    {
                      "label": "минуты",
                      "x": 60
                    }
                  ]
                },
                {
                  "name": "Количество достижений цели",
                  "type": "goals",
                  "dim": "ym:u:goalReaches",
                  "id": "GoalReaches",
                  "table": "users_visits",
                  "permission_scope": "private",
                  "count_metric": "ym:u:visits",
                  "filter_type": "metric",
                  "user_dim": "ym:u:userID",
                  "special_date_dim": "ym:u:specialDefaultDate",
                  "filter_template": "ym:u:goal<goal_id>Reaches",
                  "dimension_template": "ym:u:goal<goal_id>Reaches"
                },
                {
                  "name": "Количество целевых визитов",
                  "type": "goals",
                  "dim": "ym:u:goalVisits",
                  "id": "GoalVisits",
                  "table": "users_visits",
                  "permission_scope": "private",
                  "count_metric": "ym:u:visits",
                  "filter_type": "metric",
                  "user_dim": "ym:u:userID",
                  "special_date_dim": "ym:u:specialDefaultDate",
                  "filter_template": "ym:u:goal<goal_id>Visits",
                  "dimension_template": "ym:u:goal<goal_id>Visits"
                }
              ]
            },
            {
              "name": "Источники",
              "type": "menu",
              "id": "sources",
              "chld": [
                {
                  "name": "Первый источник трафика",
                  "type": "menu",
                  "id": "sources_first",
                  "chld": [
                    {
                      "name": "Тип источника",
                      "full_name": "Тип первого источника",
                      "type": "list",
                      "dim": "ym:u:firstTrafficSource",
                      "id": "FirstTrafficSource",
                      "table": "users_visits",
                      "permission_scope": "common",
                      "count_metric": "ym:u:users",
                      "filter_type": "attr",
                      "user_dim": "ym:u:userID"
                    },
                    {
                      "name": "Рекламная система",
                      "full_name": "Первая рекламная система",
                      "type": "list",
                      "dim": "ym:u:firstAdvEngine",
                      "id": "FirstAdvEngine",
                      "table": "users_visits",
                      "permission_scope": "common",
                      "count_metric": "ym:u:users",
                      "filter_type": "attr",
                      "user_dim": "ym:u:userID"
                    },
                    {
                      "name": "Поисковая система",
                      "full_name": "Первая поисковая система",
                      "type": "path",
                      "dim": "ym:u:firstSearchEngineRoot",
                      "id": "FirstSearchEngineRoot",
                      "table": "users_visits",
                      "permission_scope": "common",
                      "count_metric": "ym:u:users",
                      "filter_type": "attr",
                      "user_dim": "ym:u:userID",
                      "dims": [
                        "ym:u:firstSearchEngineRoot",
                        "ym:u:firstSearchEngine"
                      ]
                    },
                    {
                      "name": "Поисковая фраза",
                      "full_name": "Первая поисковая фраза",
                      "type": "multiline",
                      "dim": "ym:u:firstSearchPhrase",
                      "id": "FirstSearchPhrase",
                      "table": "users_visits",
                      "permission_scope": "private",
                      "count_metric": "ym:u:users",
                      "filter_type": "attr",
                      "user_dim": "ym:u:userID"
                    },
                    {
                      "name": "Переходы с сайтов",
                      "full_name": "Первые переходы с сайтов",
                      "type": "multiline",
                      "dim": "ym:u:firstReferalSource",
                      "id": "FirstReferalSource",
                      "table": "users_visits",
                      "permission_scope": "common",
                      "count_metric": "ym:u:users",
                      "filter_type": "attr",
                      "user_dim": "ym:u:userID"
                    },
                    {
                      "name": "Социальные сети",
                      "full_name": "Первые социальные сети",
                      "type": "list",
                      "dim": "ym:u:firstSocialNetwork",
                      "id": "FirstSocialNetwork",
                      "table": "users_visits",
                      "permission_scope": "common",
                      "count_metric": "ym:u:users",
                      "filter_type": "attr",
                      "user_dim": "ym:u:userID"
                    },
                    {
                      "name": "Группа соц. сети",
                      "full_name": "Первая группа соц. сети",
                      "type": "multiline",
                      "dim": "ym:u:firstSocialNetworkProfile",
                      "id": "FirstSocialNetworkProfile",
                      "table": "users_visits",
                      "permission_scope": "common",
                      "count_metric": "ym:u:users",
                      "filter_type": "attr",
                      "user_dim": "ym:u:userID"
                    },
                    {
                      "name": "Директ",
                      "type": "menu",
                      "id": "direct_first",
                      "chld": [
                        {
                          "name": "Кампания",
                          "type": "list",
                          "dim": "ym:u:firstDirectClickOrder",
                          "id": "FirstDirectClickOrder",
                          "table": "users_visits",
                          "permission_scope": "private",
                          "count_metric": "ym:u:users",
                          "filter_type": "attr",
                          "user_dim": "ym:u:userID"
                        },
                        {
                          "name": "Группа объявлений",
                          "type": "list",
                          "dim": "ym:u:firstDirectBannerGroup",
                          "id": "FirstDirectBannerGroup",
                          "table": "users_visits",
                          "permission_scope": "private",
                          "count_metric": "ym:u:users",
                          "filter_type": "attr",
                          "user_dim": "ym:u:userID"
                        },
                        {
                          "name": "Тип площадки",
                          "type": "list",
                          "dim": "ym:u:firstDirectPlatformType",
                          "id": "FirstDirectPlatformType",
                          "table": "users_visits",
                          "permission_scope": "private",
                          "count_metric": "ym:u:users",
                          "filter_type": "attr",
                          "user_dim": "ym:u:userID"
                        },
                        {
                          "name": "Площадка",
                          "type": "list",
                          "dim": "ym:u:firstDirectPlatform",
                          "id": "FirstDirectPlatform",
                          "table": "users_visits",
                          "permission_scope": "private",
                          "count_metric": "ym:u:users",
                          "filter_type": "attr",
                          "user_dim": "ym:u:userID"
                        },
                        {
                          "name": "Поисковая фраза",
                          "type": "multiline",
                          "dim": "ym:u:firstDirectSearchPhrase",
                          "id": "FirstDirectSearchPhrase",
                          "table": "users_visits",
                          "permission_scope": "private",
                          "count_metric": "ym:u:users",
                          "filter_type": "attr",
                          "user_dim": "ym:u:userID"
                        },
                        {
                          "name": "Текст объявления",
                          "type": "list",
                          "dim": "ym:u:firstDirectBannerText",
                          "id": "FirstDirectBannerText",
                          "table": "users_visits",
                          "permission_scope": "internal",
                          "count_metric": "ym:u:users",
                          "filter_type": "attr",
                          "user_dim": "ym:u:userID"
                        },
                        {
                          "name": "Тип условия подбора объявления",
                          "type": "list",
                          "dim": "ym:u:firstDirectConditionType",
                          "id": "FirstDirectConditionType",
                          "table": "users_visits",
                          "permission_scope": "internal",
                          "count_metric": "ym:u:users",
                          "filter_type": "attr",
                          "user_dim": "ym:u:userID"
                        },
                        {
                          "name": "Условие подбора объявления",
                          "type": "list",
                          "dim": "ym:u:firstDirectPhraseOrCond",
                          "id": "FirstDirectPhraseOrCond",
                          "table": "users_visits",
                          "permission_scope": "private",
                          "count_metric": "ym:u:users",
                          "filter_type": "attr",
                          "user_dim": "ym:u:userID"
                        }
                      ]
                    },
                    {
                      "name": "Дисплей",
                      "type": "menu",
                      "id": "display_first",
                      "chld": [
                        {
                          "name": "Номер заказа Яндекс.Дисплея",
                          "type": "list",
                          "dim": "ym:u:firstDisplayCampaign",
                          "id": "FirstDisplayCampaign",
                          "table": "users_visits",
                          "permission_scope": "private",
                          "count_metric": "ym:u:users",
                          "filter_type": "attr",
                          "user_dim": "ym:u:userID"
                        }
                      ]
                    },
                    {
                      "name": "Метки",
                      "type": "menu",
                      "id": "tags_first",
                      "chld": [
                        {
                          "name": "from",
                          "type": "multiline",
                          "dim": "ym:u:firstFrom",
                          "id": "FirstFrom",
                          "table": "users_visits",
                          "permission_scope": "common",
                          "count_metric": "ym:u:users",
                          "filter_type": "attr",
                          "user_dim": "ym:u:userID"
                        },
                        {
                          "name": "UTM: source",
                          "type": "multiline",
                          "dim": "ym:u:firstUTMSource",
                          "id": "FirstUTMSource",
                          "table": "users_visits",
                          "permission_scope": "common",
                          "count_metric": "ym:u:users",
                          "filter_type": "attr",
                          "user_dim": "ym:u:userID"
                        },
                        {
                          "name": "UTM: medium",
                          "type": "multiline",
                          "dim": "ym:u:firstUTMMedium",
                          "id": "FirstUTMMedium",
                          "table": "users_visits",
                          "permission_scope": "common",
                          "count_metric": "ym:u:users",
                          "filter_type": "attr",
                          "user_dim": "ym:u:userID"
                        },
                        {
                          "name": "UTM: campaign",
                          "type": "multiline",
                          "dim": "ym:u:firstUTMCampaign",
                          "id": "FirstUTMCampaign",
                          "table": "users_visits",
                          "permission_scope": "common",
                          "count_metric": "ym:u:users",
                          "filter_type": "attr",
                          "user_dim": "ym:u:userID"
                        },
                        {
                          "name": "UTM: content",
                          "type": "multiline",
                          "dim": "ym:u:firstUTMContent",
                          "id": "FirstUTMContent",
                          "table": "users_visits",
                          "permission_scope": "common",
                          "count_metric": "ym:u:users",
                          "filter_type": "attr",
                          "user_dim": "ym:u:userID"
                        },
                        {
                          "name": "UTM: term",
                          "type": "multiline",
                          "dim": "ym:u:firstUTMTerm",
                          "id": "FirstUTMTerm",
                          "table": "users_visits",
                          "permission_scope": "common",
                          "count_metric": "ym:u:users",
                          "filter_type": "attr",
                          "user_dim": "ym:u:userID"
                        },
                        {
                          "name": "Openstat: service",
                          "type": "multiline",
                          "dim": "ym:u:firstOpenstatService",
                          "id": "FirstOpenstatService",
                          "table": "users_visits",
                          "permission_scope": "common",
                          "count_metric": "ym:u:users",
                          "filter_type": "attr",
                          "user_dim": "ym:u:userID"
                        },
                        {
                          "name": "Openstat: campaign",
                          "type": "multiline",
                          "dim": "ym:u:firstOpenstatCampaign",
                          "id": "FirstOpenstatCampaign",
                          "table": "users_visits",
                          "permission_scope": "common",
                          "count_metric": "ym:u:users",
                          "filter_type": "attr",
                          "user_dim": "ym:u:userID"
                        },
                        {
                          "name": "Openstat: ad",
                          "type": "multiline",
                          "dim": "ym:u:firstOpenstatAd",
                          "id": "FirstOpenstatAd",
                          "table": "users_visits",
                          "permission_scope": "common",
                          "count_metric": "ym:u:users",
                          "filter_type": "attr",
                          "user_dim": "ym:u:userID"
                        },
                        {
                          "name": "Openstat: source",
                          "type": "multiline",
                          "dim": "ym:u:firstOpenstatSource",
                          "id": "FirstOpenstatSource",
                          "table": "users_visits",
                          "permission_scope": "common",
                          "count_metric": "ym:u:users",
                          "filter_type": "attr",
                          "user_dim": "ym:u:userID"
                        },
                        {
                          "name": "Наличие GCLID",
                          "type": "bool",
                          "dim": "ym:u:firstHasGCLID",
                          "id": "FirstHasGCLID",
                          "table": "users_visits",
                          "permission_scope": "common",
                          "count_metric": "ym:u:users",
                          "filter_type": "attr",
                          "user_dim": "ym:u:userID",
                          "yes_label": "Есть",
                          "no_label": "Нет"
                        }
                      ]
                    }
                  ]
                },
                {
                  "name": "Один из источников трафика",
                  "type": "menu",
                  "id": "sources_last",
                  "chld": [
                    {
                      "name": "Тип источника",
                      "full_name": "Тип одного из источников",
                      "type": "list",
                      "dim": "ym:s:trafficSource",
                      "id": "TrafficSource",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "filter_type": "event",
                      "user_dim": "ym:s:specialUser",
                      "special_date_dim": "ym:s:specialDefaultDate"
                    },
                    {
                      "name": "Рекламная система",
                      "full_name": "Одна из рекламных систем",
                      "type": "list",
                      "dim": "ym:s:advEngine",
                      "id": "AdvEngine",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "filter_type": "event",
                      "user_dim": "ym:s:specialUser",
                      "special_date_dim": "ym:s:specialDefaultDate"
                    },
                    {
                      "name": "Поисковая система",
                      "full_name": "Одна из поисковых систем",
                      "type": "path",
                      "dim": "ym:s:searchEngineRoot",
                      "id": "SearchEngineRoot",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "filter_type": "event",
                      "user_dim": "ym:s:specialUser",
                      "special_date_dim": "ym:s:specialDefaultDate",
                      "dims": [
                        "ym:s:searchEngineRoot",
                        "ym:s:searchEngine"
                      ]
                    },
                    {
                      "name": "Поисковая фраза",
                      "full_name": "Одна из поисковых фраз",
                      "type": "multiline",
                      "dim": "ym:s:searchPhrase",
                      "id": "SearchPhrase",
                      "table": "visits",
                      "permission_scope": "private",
                      "count_metric": "ym:s:visits",
                      "filter_type": "event",
                      "user_dim": "ym:s:specialUser",
                      "special_date_dim": "ym:s:specialDefaultDate"
                    },
                    {
                      "name": "Переходы с сайтов",
                      "full_name": "Один из переходов с сайтов",
                      "type": "multiline",
                      "dim": "ym:s:referalSource",
                      "id": "ReferalSource",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "filter_type": "event",
                      "user_dim": "ym:s:specialUser",
                      "special_date_dim": "ym:s:specialDefaultDate"
                    },
                    {
                      "name": "Социальные сети",
                      "full_name": "Одна из социальных сетей",
                      "type": "list",
                      "dim": "ym:s:socialNetwork",
                      "id": "SocialNetwork",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "filter_type": "event",
                      "user_dim": "ym:s:specialUser",
                      "special_date_dim": "ym:s:specialDefaultDate"
                    },
                    {
                      "name": "Группа соц. сети",
                      "full_name": "Одна из групп соц.сетей",
                      "type": "multiline",
                      "dim": "ym:s:socialNetworkProfile",
                      "id": "SocialNetworkProfile",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "filter_type": "event",
                      "user_dim": "ym:s:specialUser",
                      "special_date_dim": "ym:s:specialDefaultDate"
                    },
                    {
                      "name": "Директ",
                      "type": "menu",
                      "id": "direct",
                      "chld": [
                        {
                          "name": "Одна из кампаний",
                          "type": "list",
                          "dim": "ym:s:directClickOrder",
                          "id": "DirectClickOrder",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits",
                          "filter_type": "event",
                          "user_dim": "ym:s:specialUser",
                          "special_date_dim": "ym:s:specialDefaultDate"
                        },
                        {
                          "name": "Одна из групп объявлений",
                          "type": "list",
                          "dim": "ym:s:directBannerGroup",
                          "id": "DirectBannerGroup",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits",
                          "filter_type": "event",
                          "user_dim": "ym:s:specialUser",
                          "special_date_dim": "ym:s:specialDefaultDate"
                        },
                        {
                          "name": "Один из типов площадок",
                          "type": "list",
                          "dim": "ym:s:directPlatformType",
                          "id": "DirectPlatformType",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits",
                          "filter_type": "event",
                          "user_dim": "ym:s:specialUser",
                          "special_date_dim": "ym:s:specialDefaultDate"
                        },
                        {
                          "name": "Одна из площадок",
                          "type": "list",
                          "dim": "ym:s:directPlatform",
                          "id": "DirectPlatform",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits",
                          "filter_type": "event",
                          "user_dim": "ym:s:specialUser",
                          "special_date_dim": "ym:s:specialDefaultDate"
                        },
                        {
                          "name": "Одна из поисковых фраз",
                          "type": "multiline",
                          "dim": "ym:s:directSearchPhrase",
                          "id": "DirectSearchPhrase",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits",
                          "filter_type": "event",
                          "user_dim": "ym:s:specialUser",
                          "special_date_dim": "ym:s:specialDefaultDate"
                        },
                        {
                          "name": "Один из текстов объявлений",
                          "type": "list",
                          "dim": "ym:s:directBannerText",
                          "id": "DirectBannerText",
                          "table": "visits",
                          "permission_scope": "internal",
                          "count_metric": "ym:s:visits",
                          "filter_type": "event",
                          "user_dim": "ym:s:specialUser",
                          "special_date_dim": "ym:s:specialDefaultDate"
                        },
                        {
                          "name": "Один из типов условий подбора объявления",
                          "type": "list",
                          "dim": "ym:s:directConditionType",
                          "id": "DirectConditionType",
                          "table": "visits",
                          "permission_scope": "internal",
                          "count_metric": "ym:s:visits",
                          "filter_type": "event",
                          "user_dim": "ym:s:specialUser",
                          "special_date_dim": "ym:s:specialDefaultDate"
                        },
                        {
                          "name": "Одно из условий подбора объявления",
                          "type": "list",
                          "dim": "ym:s:directPhraseOrCond",
                          "id": "DirectPhraseOrCond",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits",
                          "filter_type": "event",
                          "user_dim": "ym:s:specialUser",
                          "special_date_dim": "ym:s:specialDefaultDate"
                        }
                      ]
                    },
                    {
                      "name": "Дисплей",
                      "type": "menu",
                      "id": "display_last",
                      "chld": [
                        {
                          "name": "Номер заказа Яндекс.Дисплея",
                          "type": "list",
                          "dim": "ym:s:lastDisplayCampaign",
                          "id": "LastDisplayCampaign",
                          "table": "visits",
                          "permission_scope": "private",
                          "count_metric": "ym:s:visits",
                          "filter_type": "event",
                          "user_dim": "ym:s:specialUser",
                          "special_date_dim": "ym:s:specialDefaultDate"
                        }
                      ]
                    },
                    {
                      "name": "Метки",
                      "type": "menu",
                      "id": "tags",
                      "chld": [
                        {
                          "name": "from",
                          "type": "multiline",
                          "dim": "ym:s:from",
                          "id": "From",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits",
                          "filter_type": "event",
                          "user_dim": "ym:s:specialUser",
                          "special_date_dim": "ym:s:specialDefaultDate"
                        },
                        {
                          "name": "UTM: source",
                          "type": "multiline",
                          "dim": "ym:s:UTMSource",
                          "id": "UTMSource",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits",
                          "filter_type": "event",
                          "user_dim": "ym:s:specialUser",
                          "special_date_dim": "ym:s:specialDefaultDate"
                        },
                        {
                          "name": "UTM: medium",
                          "type": "multiline",
                          "dim": "ym:s:UTMMedium",
                          "id": "UTMMedium",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits",
                          "filter_type": "event",
                          "user_dim": "ym:s:specialUser",
                          "special_date_dim": "ym:s:specialDefaultDate"
                        },
                        {
                          "name": "UTM: campaign",
                          "type": "multiline",
                          "dim": "ym:s:UTMCampaign",
                          "id": "UTMCampaign",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits",
                          "filter_type": "event",
                          "user_dim": "ym:s:specialUser",
                          "special_date_dim": "ym:s:specialDefaultDate"
                        },
                        {
                          "name": "UTM: content",
                          "type": "multiline",
                          "dim": "ym:s:UTMContent",
                          "id": "UTMContent",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits",
                          "filter_type": "event",
                          "user_dim": "ym:s:specialUser",
                          "special_date_dim": "ym:s:specialDefaultDate"
                        },
                        {
                          "name": "UTM: term",
                          "type": "multiline",
                          "dim": "ym:s:UTMTerm",
                          "id": "UTMTerm",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits",
                          "filter_type": "event",
                          "user_dim": "ym:s:specialUser",
                          "special_date_dim": "ym:s:specialDefaultDate"
                        },
                        {
                          "name": "Openstat: service",
                          "type": "multiline",
                          "dim": "ym:s:openstatService",
                          "id": "OpenstatService",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits",
                          "filter_type": "event",
                          "user_dim": "ym:s:specialUser",
                          "special_date_dim": "ym:s:specialDefaultDate"
                        },
                        {
                          "name": "Openstat: campaign",
                          "type": "multiline",
                          "dim": "ym:s:openstatCampaign",
                          "id": "OpenstatCampaign",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits",
                          "filter_type": "event",
                          "user_dim": "ym:s:specialUser",
                          "special_date_dim": "ym:s:specialDefaultDate"
                        },
                        {
                          "name": "Openstat: ad",
                          "type": "multiline",
                          "dim": "ym:s:openstatAd",
                          "id": "OpenstatAd",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits",
                          "filter_type": "event",
                          "user_dim": "ym:s:specialUser",
                          "special_date_dim": "ym:s:specialDefaultDate"
                        },
                        {
                          "name": "Openstat: source",
                          "type": "multiline",
                          "dim": "ym:s:openstatSource",
                          "id": "OpenstatSource",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits",
                          "filter_type": "event",
                          "user_dim": "ym:s:specialUser",
                          "special_date_dim": "ym:s:specialDefaultDate"
                        },
                        {
                          "name": "Наличие GCLID",
                          "type": "bool",
                          "dim": "ym:s:hasGCLID",
                          "id": "HasGCLID",
                          "table": "visits",
                          "permission_scope": "common",
                          "count_metric": "ym:s:visits",
                          "filter_type": "event",
                          "user_dim": "ym:s:specialUser",
                          "special_date_dim": "ym:s:specialDefaultDate",
                          "yes_label": "Есть",
                          "no_label": "Нет"
                        }
                      ]
                    }
                  ]
                }
              ]
            },
            {
              "name": "Технологии",
              "type": "menu",
              "id": "technology",
              "chld": [
                {
                  "name": "Устройство",
                  "type": "path",
                  "dim": "ym:s:deviceCategory",
                  "id": "DeviceCategory",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "filter_type": "event",
                  "user_dim": "ym:s:specialUser",
                  "special_date_dim": "ym:s:specialDefaultDate",
                  "dims": [
                    "ym:s:deviceCategory",
                    "ym:s:mobilePhone",
                    "ym:s:mobilePhoneModel"
                  ]
                },
                {
                  "name": "Операционные системы",
                  "type": "tree",
                  "dim": "ym:s:operatingSystemRoot",
                  "id": "OperatingSystemRoot",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "filter_type": "event",
                  "user_dim": "ym:s:specialUser",
                  "special_date_dim": "ym:s:specialDefaultDate",
                  "dims": [
                    "ym:s:operatingSystemRoot",
                    "ym:s:operatingSystem"
                  ]
                },
                {
                  "name": "Браузеры",
                  "type": "tree",
                  "dim": "ym:s:browser",
                  "id": "Browser",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "filter_type": "event",
                  "user_dim": "ym:s:specialUser",
                  "special_date_dim": "ym:s:specialDefaultDate",
                  "dims": [
                    "ym:s:browser",
                    "ym:s:browserAndVersionMajor"
                  ]
                },
                {
                  "name": "Технологии браузеров",
                  "type": "menu",
                  "id": "browser",
                  "chld": [
                    {
                      "name": "Движок браузера",
                      "type": "path",
                      "dim": "ym:s:browserEngine",
                      "id": "BrowserEngine",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "filter_type": "event",
                      "user_dim": "ym:s:specialUser",
                      "special_date_dim": "ym:s:specialDefaultDate",
                      "dims": [
                        "ym:s:browserEngine",
                        "ym:s:browserEngineVersion1"
                      ]
                    },
                    {
                      "name": "Наличие блокировщиков рекламы",
                      "type": "bool",
                      "dim": "ym:s:hasAdBlocker",
                      "id": "HasAdBlocker",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "filter_type": "event",
                      "user_dim": "ym:s:specialUser",
                      "special_date_dim": "ym:s:specialDefaultDate",
                      "yes_label": "Блокировка включена",
                      "no_label": "Блокировка выключена"
                    },
                    {
                      "name": "Поддержка Flash",
                      "type": "bool",
                      "dim": "ym:s:flashEnabled",
                      "id": "FlashEnabled",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "filter_type": "event",
                      "user_dim": "ym:s:specialUser",
                      "special_date_dim": "ym:s:specialDefaultDate",
                      "yes_label": "Flash включен",
                      "no_label": "Flash выключен"
                    },
                    {
                      "name": "Поддержка cookies",
                      "type": "bool",
                      "dim": "ym:s:cookieEnabled",
                      "id": "CookieEnabled",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "filter_type": "event",
                      "user_dim": "ym:s:specialUser",
                      "special_date_dim": "ym:s:specialDefaultDate",
                      "yes_label": "Cookies включены",
                      "no_label": "Cookies выключены"
                    },
                    {
                      "name": "Поддержка Javascript",
                      "type": "bool",
                      "dim": "ym:s:javascriptEnabled",
                      "id": "JavascriptEnabled",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "filter_type": "event",
                      "user_dim": "ym:s:specialUser",
                      "special_date_dim": "ym:s:specialDefaultDate",
                      "yes_label": "Javascript включен",
                      "no_label": "Javascript выключен"
                    },
                    {
                      "name": "Поддержка SilverLight",
                      "type": "bool",
                      "dim": "ym:s:silverlightEnabled",
                      "id": "SilverlightEnabled",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "filter_type": "event",
                      "user_dim": "ym:s:specialUser",
                      "special_date_dim": "ym:s:specialDefaultDate",
                      "yes_label": "SilverLight включен",
                      "no_label": "SilverLight выключен"
                    }
                  ]
                },
                {
                  "name": "IP",
                  "type": "multiline",
                  "dim": "ym:s:ipAddress",
                  "id": "IpAddress",
                  "table": "visits",
                  "permission_scope": "private",
                  "count_metric": "ym:s:visits",
                  "filter_type": "event",
                  "user_dim": "ym:s:specialUser",
                  "special_date_dim": "ym:s:specialDefaultDate",
                  "disable_suggest": true
                },
                {
                  "name": "Экран",
                  "type": "menu",
                  "id": "screen",
                  "chld": [
                    {
                      "name": "Соотношение сторон",
                      "type": "list",
                      "dim": "ym:s:screenFormat",
                      "id": "ScreenFormat",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "filter_type": "event",
                      "user_dim": "ym:s:specialUser",
                      "special_date_dim": "ym:s:specialDefaultDate"
                    },
                    {
                      "name": "Глубина цвета",
                      "type": "list",
                      "dim": "ym:s:screenColors",
                      "id": "ScreenColors",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "filter_type": "event",
                      "user_dim": "ym:s:specialUser",
                      "special_date_dim": "ym:s:specialDefaultDate"
                    },
                    {
                      "name": "Ориентация экрана",
                      "type": "list",
                      "dim": "ym:s:screenOrientation",
                      "id": "ScreenOrientation",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "filter_type": "event",
                      "user_dim": "ym:s:specialUser",
                      "special_date_dim": "ym:s:specialDefaultDate"
                    },
                    {
                      "name": "Логическое разрешение экрана",
                      "type": "path",
                      "dim": "ym:s:screenWidth",
                      "id": "logical_resolution",
                      "table": "visits",
                      "permission_scope": "common",
                      "count_metric": "ym:s:visits",
                      "filter_type": "event",
                      "user_dim": "ym:s:specialUser",
                      "special_date_dim": "ym:s:specialDefaultDate",
                      "dims": [
                        "ym:s:screenWidth",
                        "ym:s:screenHeight"
                      ],
                      "concat": "x"
                    }
                  ]
                }
              ]
            },
            {
              "name": "Поведение",
              "type": "menu",
              "id": "behaviour",
              "chld": [
                {
                  "name": "Страница входа",
                  "type": "url",
                  "dim": "ym:s:startURL",
                  "id": "StartURL",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "filter_type": "event",
                  "user_dim": "ym:s:specialUser",
                  "special_date_dim": "ym:s:specialDefaultDate",
                  "host_dim": "ym:s:startURLDomain",
                  "path_dim": "ym:s:startURLPathFull"
                },
                {
                  "name": "Просмотр URL",
                  "type": "url",
                  "dim": "ym:pv:URL",
                  "id": "URL",
                  "table": "hits",
                  "permission_scope": "common",
                  "count_metric": "ym:pv:pageviews",
                  "filter_type": "event",
                  "user_dim": "ym:pv:specialUser",
                  "special_date_dim": "ym:pv:specialDefaultDate",
                  "host_dim": "ym:pv:URLDomain",
                  "path_dim": "ym:pv:URLPathFull"
                },
                {
                  "name": "Параметры визита",
                  "type": "params",
                  "dim": "ym:s:paramsLevel1",
                  "id": "ParamsLevel1",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "filter_type": "event",
                  "user_dim": "ym:s:specialUser",
                  "special_date_dim": "ym:s:specialDefaultDate",
                  "dims": [
                    "ym:s:paramsLevel1",
                    "ym:s:paramsLevel2",
                    "ym:s:paramsLevel3",
                    "ym:s:paramsLevel4",
                    "ym:s:paramsLevel5",
                    "ym:s:paramsLevel6",
                    "ym:s:paramsLevel7",
                    "ym:s:paramsLevel8",
                    "ym:s:paramsLevel9",
                    "ym:s:paramsLevel10"
                  ],
                  "dim_value_double": "ym:s:paramsValueDouble",
                  "no_quantifier": false
                },
                {
                  "name": "Загрузка файла",
                  "type": "url",
                  "dim": "ym:dl:downloadURL",
                  "id": "DownloadURL",
                  "table": "downloads",
                  "permission_scope": "common",
                  "count_metric": "ym:dl:pageviews",
                  "filter_type": "event",
                  "user_dim": "ym:dl:specialUser",
                  "special_date_dim": "ym:dl:specialDefaultDate",
                  "host_dim": "ym:dl:downloadURLDomain",
                  "path_dim": "ym:dl:downloadURLPathFull"
                },
                {
                  "name": "Внешний переход",
                  "type": "multiline",
                  "dim": "ym:el:externalLink",
                  "id": "ExternalLink",
                  "table": "external_links",
                  "permission_scope": "common",
                  "count_metric": "ym:el:pageviews",
                  "filter_type": "event",
                  "user_dim": "ym:el:specialUser",
                  "special_date_dim": "ym:el:specialDefaultDate"
                },
                {
                  "name": "Дата визита",
                  "type": "date",
                  "dim": "ym:s:date",
                  "id": "Date",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "filter_type": "event",
                  "user_dim": "ym:s:specialUser",
                  "special_date_dim": "ym:s:specialDefaultDate"
                }
              ]
            },
            {
              "name": "Электронная коммерция",
              "type": "menu",
              "id": "ecommerce",
              "chld": [
                {
                  "name": "Товаров просмотрено",
                  "type": "number",
                  "dim": "ym:u:productViews",
                  "id": "ProductViews",
                  "table": "users_visits",
                  "permission_scope": "common",
                  "count_metric": "ym:u:users",
                  "filter_type": "metric",
                  "user_dim": "ym:u:userID",
                  "special_date_dim": "ym:u:specialDefaultDate"
                },
                {
                  "name": "Количество покупок",
                  "type": "number",
                  "dim": "ym:u:purchaseNumber",
                  "id": "PurchaseNumber",
                  "table": "users_visits",
                  "permission_scope": "common",
                  "count_metric": "ym:u:users",
                  "filter_type": "metric",
                  "user_dim": "ym:u:userID",
                  "special_date_dim": "ym:u:specialDefaultDate"
                },
                {
                  "name": "Товаров куплено",
                  "type": "number",
                  "dim": "ym:u:productsBought",
                  "id": "ProductsBought",
                  "table": "users_visits",
                  "permission_scope": "common",
                  "count_metric": "ym:u:users",
                  "filter_type": "metric",
                  "user_dim": "ym:u:userID",
                  "special_date_dim": "ym:u:specialDefaultDate"
                },
                {
                  "name": "Суммарный доход",
                  "type": "number",
                  "dim": "ym:u:userRevenue",
                  "id": "UserRevenue",
                  "table": "users_visits",
                  "permission_scope": "common",
                  "count_metric": "ym:u:users",
                  "filter_type": "metric",
                  "user_dim": "ym:u:userID",
                  "special_date_dim": "ym:u:specialDefaultDate"
                },
                {
                  "name": "Просмотр товара",
                  "type": "list",
                  "dim": "ym:s:productImpression",
                  "id": "ProductImpression",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "filter_type": "event",
                  "user_dim": "ym:s:specialUser",
                  "special_date_dim": "ym:s:specialDefaultDate"
                },
                {
                  "name": "Просмотр товара из категории",
                  "type": "path",
                  "dim": "ym:s:impressionProductCategoryLevel1",
                  "id": "ImpressionProductCategoryLevel1",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "filter_type": "event",
                  "user_dim": "ym:s:specialUser",
                  "special_date_dim": "ym:s:specialDefaultDate",
                  "dims": [
                    "ym:s:impressionProductCategoryLevel1",
                    "ym:s:impressionProductCategoryLevel2",
                    "ym:s:impressionProductCategoryLevel3",
                    "ym:s:impressionProductCategoryLevel4",
                    "ym:s:impressionProductCategoryLevel5"
                  ]
                },
                {
                  "name": "Покупка товара",
                  "type": "list",
                  "dim": "ym:s:productPurchase",
                  "id": "ProductPurchase",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "filter_type": "event",
                  "user_dim": "ym:s:specialUser",
                  "special_date_dim": "ym:s:specialDefaultDate"
                },
                {
                  "name": "Покупка товара из категории",
                  "type": "path",
                  "dim": "ym:s:purchaseProductCategoryLevel1",
                  "id": "PurchaseProductCategoryLevel1",
                  "table": "visits",
                  "permission_scope": "common",
                  "count_metric": "ym:s:visits",
                  "filter_type": "event",
                  "user_dim": "ym:s:specialUser",
                  "special_date_dim": "ym:s:specialDefaultDate",
                  "dims": [
                    "ym:s:purchaseProductCategoryLevel1",
                    "ym:s:purchaseProductCategoryLevel2",
                    "ym:s:purchaseProductCategoryLevel3",
                    "ym:s:purchaseProductCategoryLevel4",
                    "ym:s:purchaseProductCategoryLevel5"
                  ]
                }
              ]
            }
          ]
        };
        /*jshint ignore: end*/
        /*jscs:enable*/
    }
});
