/* jscs:disable */
/* jshint ignore: start */
BEM.decl('d-counter', null, {

    get: function () {
        return {
            "id" : 101024,
            "status" : "Active",
            "owner_login" : "sendflowers-amf",
            "code_status" : "CS_OK",
            "name" : "AMF - международная сеть доставки цветов",
            "site" : "sendflowers.ru",
            "type" : "simple",
            "favorite" : 0,
            "goals" : [ {
              "id" : 2899978,
              "name" : "Вход в корзину",
              "type" : "url",
              "is_retargeting" : 1,
              "prev_goal_id" : 0,
              "flag" : "basket",
              "conditions" : [ {
                "type" : "exact",
                "url" : "www.sendflowers.ru/cart.phtml"
              } ],
              "class" : 1
            }, {
              "id" : 3290299,
              "name" : "Оформление интерьеров",
              "type" : "url",
              "is_retargeting" : 1,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "exact",
                "url" : "http://www.sendflowers.ru/rus/info/2009.html"
              } ],
              "class" : 0
            }, {
              "id" : 4105168,
              "name" : "8 марта 2014. 101 тюльпан",
              "type" : "action",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "exact",
                "url" : "080314BASKET101"
              } ],
              "class" : 0
            }, {
              "id" : 4105171,
              "name" : "8 марта 2014. 51 тюльпан",
              "type" : "action",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "exact",
                "url" : "080314BASKET51"
              } ],
              "class" : 0
            }, {
              "id" : 4105174,
              "name" : "8 марта 2014. Заказали обратный звонок",
              "type" : "action",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "exact",
                "url" : "080314CALLME"
              } ],
              "class" : 1
            }, {
              "id" : 5133665,
              "name" : "корзина воронка",
              "type" : "step",
              "is_retargeting" : 0,
              "steps" : [ {
                "id" : 5133668,
                "name" : "корзина",
                "type" : "url",
                "is_retargeting" : 0,
                "prev_goal_id" : 0,
                "conditions" : [ {
                  "type" : "contain",
                  "url" : "cart.phtml"
                } ],
                "class" : 1
              }, {
                "id" : 5133671,
                "name" : "адрес",
                "type" : "url",
                "is_retargeting" : 0,
                "prev_goal_id" : 5133668,
                "conditions" : [ {
                  "type" : "contain",
                  "url" : "shipping/"
                } ],
                "class" : 1
              }, {
                "id" : 5133674,
                "name" : "оплата",
                "type" : "url",
                "is_retargeting" : 0,
                "prev_goal_id" : 5133671,
                "conditions" : [ {
                  "type" : "contain",
                  "url" : "/cart/payment/"
                } ],
                "class" : 1
              }, {
                "id" : 5133677,
                "name" : "подтверждение заказа",
                "type" : "url",
                "is_retargeting" : 0,
                "prev_goal_id" : 5133674,
                "conditions" : [ {
                  "type" : "contain",
                  "url" : "/cart/confirm/"
                } ],
                "class" : 1
              }, {
                "id" : 5133680,
                "name" : "оплата",
                "type" : "url",
                "is_retargeting" : 0,
                "prev_goal_id" : 5133677,
                "conditions" : [ {
                  "type" : "contain",
                  "url" : "/completed"
                } ],
                "class" : 1
              } ],
              "class" : 1
            }, {
              "id" : 5232020,
              "name" : "Обратный звонок",
              "type" : "step",
              "is_retargeting" : 0,
              "steps" : [ {
                "id" : 5232023,
                "name" : "Заказать об.зв.",
                "type" : "url",
                "is_retargeting" : 0,
                "prev_goal_id" : 0,
                "conditions" : [ {
                  "type" : "action",
                  "url" : "ORDER1"
                } ],
                "class" : 0
              }, {
                "id" : 5232026,
                "name" : "отправили",
                "type" : "url",
                "is_retargeting" : 0,
                "prev_goal_id" : 5232023,
                "conditions" : [ {
                  "type" : "action",
                  "url" : "ORDER2"
                } ],
                "class" : 0
              } ],
              "class" : 0
            }, {
              "id" : 6799211,
              "name" : "Новый год",
              "type" : "url",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "contain",
                "url" : "new_year"
              } ],
              "class" : 0
            }, {
              "id" : 5231966,
              "name" : "Оформление интерьеров",
              "type" : "step",
              "is_retargeting" : 0,
              "steps" : [ {
                "id" : 5231969,
                "name" : "отправить заявку",
                "type" : "url",
                "is_retargeting" : 0,
                "prev_goal_id" : 0,
                "conditions" : [ {
                  "type" : "action",
                  "url" : "ORDER5"
                } ],
                "class" : 0
              }, {
                "id" : 5231972,
                "name" : "отправили",
                "type" : "url",
                "is_retargeting" : 0,
                "prev_goal_id" : 5231969,
                "conditions" : [ {
                  "type" : "action",
                  "url" : "ORDER6"
                } ],
                "class" : 0
              } ],
              "class" : 0
            }, {
              "id" : 5231948,
              "name" : "Быстрый заказ",
              "type" : "step",
              "is_retargeting" : 0,
              "steps" : [ {
                "id" : 5231951,
                "name" : "Быстрый заказ",
                "type" : "url",
                "is_retargeting" : 0,
                "prev_goal_id" : 0,
                "conditions" : [ {
                  "type" : "action",
                  "url" : "ORDER3"
                } ],
                "class" : 0
              }, {
                "id" : 5231954,
                "name" : "Оформить заказ",
                "type" : "url",
                "is_retargeting" : 0,
                "prev_goal_id" : 5231951,
                "conditions" : [ {
                  "type" : "action",
                  "url" : "ORDER4"
                } ],
                "class" : 0
              } ],
              "class" : 0
            }, {
              "id" : 3290296,
              "name" : "Оформление к Новому году",
              "type" : "url",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "exact",
                "url" : "http://www.sendflowers.ru/rus/info/1604.html"
              } ],
              "class" : 0
            }, {
              "id" : 3176764,
              "name" : "Свадьба",
              "type" : "url",
              "is_retargeting" : 1,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "contain",
                "url" : "wedding"
              } ],
              "class" : 1
            }, {
              "id" : 2899981,
              "name" : "Покупка - оплата наличными курьеру",
              "type" : "url",
              "is_retargeting" : 1,
              "prev_goal_id" : 0,
              "flag" : "order",
              "conditions" : [ {
                "type" : "contain",
                "url" : "AMFset[CustomerOrderNumber]"
              } ],
              "class" : 1
            }, {
              "id" : 3176497,
              "name" : "Все посетители",
              "type" : "number",
              "is_retargeting" : 1,
              "depth" : 2,
              "class" : 0
            }, {
              "id" : 3176500,
              "name" : "Просмотр 3 страниц сайта",
              "type" : "number",
              "is_retargeting" : 1,
              "depth" : 3,
              "class" : 1
            }, {
              "id" : 5231957,
              "name" : "Свадьба",
              "type" : "step",
              "is_retargeting" : 0,
              "steps" : [ {
                "id" : 5231960,
                "name" : "Отправить заявку",
                "type" : "url",
                "is_retargeting" : 0,
                "prev_goal_id" : 0,
                "conditions" : [ {
                  "type" : "action",
                  "url" : "ORDER7"
                } ],
                "class" : 0
              }, {
                "id" : 5231963,
                "name" : "Отправили",
                "type" : "url",
                "is_retargeting" : 0,
                "prev_goal_id" : 5231960,
                "conditions" : [ {
                  "type" : "action",
                  "url" : "ORDER8"
                } ],
                "class" : 0
              } ],
              "class" : 0
            }, {
              "id" : 3176503,
              "name" : "Посетили корзину",
              "type" : "url",
              "is_retargeting" : 1,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "contain",
                "url" : "/cart"
              } ],
              "class" : 1
            }, {
              "id" : 3176557,
              "name" : "Интересовались букетами",
              "type" : "url",
              "is_retargeting" : 1,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "contain",
                "url" : "bouquets"
              } ],
              "class" : 0
            }, {
              "id" : 3176575,
              "name" : "Интересовались композициями",
              "type" : "url",
              "is_retargeting" : 1,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "contain",
                "url" : "arrangement"
              } ],
              "class" : 0
            }, {
              "id" : 3176578,
              "name" : "Интересовались корзинами",
              "type" : "url",
              "is_retargeting" : 1,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "contain",
                "url" : "baskets"
              } ],
              "class" : 0
            }, {
              "id" : 3176581,
              "name" : "Интересовались подарками",
              "type" : "url",
              "is_retargeting" : 1,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "contain",
                "url" : "presents"
              } ],
              "class" : 0
            }, {
              "id" : 7526146,
              "name" : "14 февраля",
              "type" : "url",
              "is_retargeting" : 1,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "contain",
                "url" : "february"
              } ],
              "class" : 1
            }, {
              "id" : 7989291,
              "name" : "8 марта",
              "type" : "url",
              "is_retargeting" : 1,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "contain",
                "url" : "march"
              } ],
              "class" : 1
            }, {
              "id" : 13846275,
              "name" : "нет изображений",
              "type" : "action",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "exact",
                "url" : "NOIMAGE"
              } ],
              "class" : 1
            }, {
              "id" : 13860200,
              "name" : "Ошибка 404",
              "type" : "action",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "exact",
                "url" : "ERROR404"
              } ],
              "class" : 0
            }, {
              "id" : 13860205,
              "name" : "Ошибка 500",
              "type" : "action",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "exact",
                "url" : "ERROR500"
              } ],
              "class" : 0
            }, {
              "id" : 13860210,
              "name" : "Ошибка неизвестна",
              "type" : "action",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "exact",
                "url" : "ERRORUNKNOWN"
              } ],
              "class" : 0
            }, {
              "id" : 17202110,
              "name" : "Переход на страницу контактов",
              "type" : "url",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "contain",
                "url" : "/rus/firmennye-salony/"
              } ],
              "class" : 0
            }, {
              "id" : 17202210,
              "name" : "Переход на страницу \"О компании\"",
              "type" : "url",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "contain",
                "url" : "/rus/info/kompaniya/"
              } ],
              "class" : 0
            }, {
              "id" : 17202215,
              "name" : "Переход на страницу \"Скидки\"",
              "type" : "url",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "contain",
                "url" : "/rus/skidki/"
              } ],
              "class" : 0
            }, {
              "id" : 17202220,
              "name" : "Переход на страницу \"Гарантия качества\"",
              "type" : "url",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "contain",
                "url" : "/rus/kachestvo/"
              } ],
              "class" : 0
            }, {
              "id" : 17202225,
              "name" : "Переход на страницу \"Напомнить о дате\"",
              "type" : "url",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "contain",
                "url" : "/rus/info/napominanie/"
              } ],
              "class" : 0
            }, {
              "id" : 17202230,
              "name" : "Переход на страницу отзывов",
              "type" : "url",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "contain",
                "url" : "/rus/info/1013.html"
              } ],
              "class" : 0
            }, {
              "id" : 17202235,
              "name" : "Отправка отзыва или жалобы",
              "type" : "url",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "contain",
                "url" : "/rus/info/90.html"
              } ],
              "class" : 0
            }, {
              "id" : 17500490,
              "name" : "SEO. Подписка на новости",
              "type" : "action",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "exact",
                "url" : "SUBSCRIBE_NEWS"
              } ],
              "class" : 0
            }, {
              "id" : 17501485,
              "name" : "SEO. Быстрый заказ",
              "type" : "action",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "exact",
                "url" : "FAST_ORDER"
              } ],
              "class" : 0
            }, {
              "id" : 17501490,
              "name" : "SEO. Форма похвалить",
              "type" : "action",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "exact",
                "url" : "FORM_COMPLIMENT"
              } ],
              "class" : 0
            }, {
              "id" : 17501495,
              "name" : "SEO. Форма пожаловаться",
              "type" : "action",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "exact",
                "url" : "FORM_COMPLAIN"
              } ],
              "class" : 0
            }, {
              "id" : 17501600,
              "name" : "SEO. Рекомендации в корзине",
              "type" : "action",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "exact",
                "url" : "RECOMMENDATION_BASKET"
              } ],
              "class" : 0
            }, {
              "id" : 17501605,
              "name" : "SEO. Рекомендации на карточке товара",
              "type" : "action",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "exact",
                "url" : "RECOMMENDATION_ARTICLE"
              } ],
              "class" : 0
            }, {
              "id" : 17644590,
              "name" : "Нажата \"Наверх\"",
              "type" : "action",
              "is_retargeting" : 0,
              "prev_goal_id" : 0,
              "conditions" : [ {
                "type" : "exact",
                "url" : "CLICK_GO_TOP"
              } ],
              "class" : 0
            } ],
            "filters" : [ {
              "id" : 3327789,
              "attr" : "uniq_id",
              "type" : "me",
              "value" : "",
              "action" : "exclude",
              "status" : "active",
              "serial" : 0,
              "with_subdomains" : 0
            }, {
              "id" : 3327792,
              "attr" : "url",
              "type" : "contain",
              "value" : "backdoor.amf.ru",
              "action" : "exclude",
              "status" : "active",
              "serial" : 0,
              "with_subdomains" : 0
            }, {
              "id" : 3294371,
              "attr" : "client_ip",
              "type" : "equal",
              "value" : "195.68.142.35",
              "action" : "exclude",
              "status" : "active",
              "serial" : 0,
              "with_subdomains" : 0
            }, {
              "id" : 3294374,
              "attr" : "client_ip",
              "type" : "equal",
              "value" : "195.68.187.10",
              "action" : "exclude",
              "status" : "active",
              "serial" : 0,
              "with_subdomains" : 0
            }, {
              "id" : 3294377,
              "attr" : "client_ip",
              "type" : "equal",
              "value" : "62.113.107.2",
              "action" : "exclude",
              "status" : "active",
              "serial" : 0,
              "with_subdomains" : 0
            }, {
              "id" : 3294380,
              "attr" : "client_ip",
              "type" : "equal",
              "value" : "95.128.227.99",
              "action" : "exclude",
              "status" : "active",
              "serial" : 0,
              "with_subdomains" : 0
            }, {
              "id" : 3641586,
              "attr" : "referer",
              "type" : "contain",
              "value" : "b-motor.ru",
              "action" : "exclude",
              "status" : "active",
              "serial" : 0,
              "with_subdomains" : 0
            }, {
              "id" : 3641622,
              "attr" : "referer",
              "type" : "contain",
              "value" : "9157481813.ru",
              "action" : "exclude",
              "status" : "active",
              "serial" : 0,
              "with_subdomains" : 0
            }, {
              "id" : 3641625,
              "attr" : "referer",
              "type" : "contain",
              "value" : "ruskweb.ru",
              "action" : "exclude",
              "status" : "active",
              "serial" : 0,
              "with_subdomains" : 0
            }, {
              "id" : 3641628,
              "attr" : "referer",
              "type" : "contain",
              "value" : "semalt.com",
              "action" : "exclude",
              "status" : "active",
              "serial" : 0,
              "with_subdomains" : 0
            }, {
              "id" : 3641631,
              "attr" : "referer",
              "type" : "contain",
              "value" : "buttons-for-website.com",
              "action" : "exclude",
              "status" : "active",
              "serial" : 0,
              "with_subdomains" : 0
            }, {
              "id" : 3641634,
              "attr" : "referer",
              "type" : "contain",
              "value" : "b-motor.info",
              "action" : "exclude",
              "status" : "active",
              "serial" : 0,
              "with_subdomains" : 0
            }, {
              "id" : 3641643,
              "attr" : "referer",
              "type" : "contain",
              "value" : "ilovepetya.com",
              "action" : "exclude",
              "status" : "active",
              "serial" : 0,
              "with_subdomains" : 0
            }, {
              "id" : 3641646,
              "attr" : "referer",
              "type" : "contain",
              "value" : "topsites.me",
              "action" : "exclude",
              "status" : "active",
              "serial" : 0,
              "with_subdomains" : 0
            }, {
              "id" : 3641649,
              "attr" : "referer",
              "type" : "contain",
              "value" : "darodar.ru",
              "action" : "exclude",
              "status" : "active",
              "serial" : 0,
              "with_subdomains" : 0
            }, {
              "id" : 3641652,
              "attr" : "referer",
              "type" : "contain",
              "value" : "iskalko.ru",
              "action" : "exclude",
              "status" : "active",
              "serial" : 0,
              "with_subdomains" : 0
            }, {
              "id" : 3641655,
              "attr" : "client_ip",
              "type" : "equal",
              "value" : "78.110.60.230",
              "action" : "exclude",
              "status" : "active",
              "serial" : 0,
              "with_subdomains" : 0
            }, {
              "id" : 3641658,
              "attr" : "client_ip",
              "type" : "equal",
              "value" : "78.110.59.177",
              "action" : "exclude",
              "status" : "active",
              "serial" : 0,
              "with_subdomains" : 0
            }, {
              "id" : 3641661,
              "attr" : "client_ip",
              "type" : "equal",
              "value" : "205.164.14.88",
              "action" : "exclude",
              "status" : "active",
              "serial" : 0,
              "with_subdomains" : 0
            }, {
              "id" : 3641664,
              "attr" : "client_ip",
              "type" : "equal",
              "value" : "78.110.50.109",
              "action" : "exclude",
              "status" : "active",
              "serial" : 0,
              "with_subdomains" : 0
            }, {
              "id" : 3645210,
              "attr" : "referer",
              "type" : "contain",
              "value" : "cityadspix.com",
              "action" : "exclude",
              "status" : "active",
              "serial" : 0,
              "with_subdomains" : 0
            } ],
            "operations" : [ {
              "id" : 8775,
              "action" : "merge_https_and_http",
              "attr" : "url",
              "value" : "",
              "status" : "disabled",
              "serial" : 21
            } ],
            "grants" : [ {
              "user_login" : "sendflower2",
              "perm" : "view",
              "created_at" : "2014-09-17T11:53:20+03:00",
              "comment" : "Demis SEO"
            }, {
              "user_login" : "itprojects-amf",
              "perm" : "view",
              "created_at" : "2015-08-14T16:47:44+03:00",
              "comment" : "IT Projects"
            }, {
              "user_login" : "o100012",
              "perm" : "edit",
              "created_at" : "2009-10-07T10:05:49+03:00",
              "comment" : "Станислав Котомкин"
            }, {
              "user_login" : "lam-pam-pam",
              "perm" : "view",
              "created_at" : "2011-10-14T13:35:31+03:00",
              "comment" : "Алексей Сланчевский"
            }, {
              "user_login" : "imedia-sendflowers",
              "perm" : "edit",
              "created_at" : "2014-07-18T09:49:38+03:00",
              "comment" : "Аккаунт на Директе"
            }, {
              "user_login" : "victorino",
              "perm" : "view",
              "created_at" : "2015-07-21T15:40:18+03:00",
              "comment" : ""
            }, {
              "user_login" : "seoamf2016",
              "perm" : "view",
              "created_at" : "2015-12-07T15:51:52+03:00",
              "comment" : ""
            }, {
              "user_login" : "rusnec",
              "perm" : "view",
              "created_at" : "2015-05-27T17:22:40+03:00",
              "comment" : "просьба Пласковицкой Марии"
            }, {
              "user_login" : "sdd3",
              "perm" : "view",
              "created_at" : "2015-10-07T12:10:53+03:00",
              "comment" : ""
            }, {
              "user_login" : "romanenkosb",
              "perm" : "view",
              "created_at" : "2014-10-20T12:22:31+03:00",
              "comment" : "просьба Зверевой Юли"
            }, {
              "user_login" : "silverplate",
              "perm" : "view",
              "created_at" : "2015-02-25T13:18:54+03:00",
              "comment" : "silverplate@yandex.ru"
            }, {
              "user_login" : "umbrellaagency2014",
              "perm" : "edit",
              "created_at" : "2015-06-15T11:26:06+03:00",
              "comment" : "просьба Пласковицкой Марии"
            }, {
              "user_login" : "amf.adw.direct",
              "perm" : "view",
              "created_at" : "2015-12-07T15:51:42+03:00",
              "comment" : ""
            }, {
              "user_login" : "191919@mail.ru",
              "perm" : "view",
              "created_at" : "2015-06-02T18:15:04+03:00",
              "comment" : ""
            }, {
              "user_login" : "kam4atkin",
              "perm" : "edit",
              "created_at" : "2015-10-05T17:25:25+03:00",
              "comment" : "Камчаткин Никита"
            }, {
              "user_login" : "ingatenew",
              "perm" : "view",
              "created_at" : "2015-02-05T15:45:34+03:00",
              "comment" : "Ingate"
            }, {
              "user_login" : "flowersmetrika",
              "perm" : "view",
              "created_at" : "2015-11-10T19:02:40+03:00",
              "comment" : "Nick B"
            }, {
              "user_login" : "itagency",
              "perm" : "view",
              "created_at" : "2015-02-12T11:40:38+03:00",
              "comment" : "IT-Agency"
            } ],
            "webvisor" : {
              "urls" : "",
              "arch_enabled" : 0,
              "arch_type" : "none",
              "load_player_type" : "on_your_behalf"
            },
            "code_options" : {
              "async" : 1,
              "informer" : {
                "enabled" : 0,
                "type" : "ext",
                "size" : 3,
                "indicator" : "pageviews",
                "color_start" : "FFFFFFFF",
                "color_end" : "EFEFEFFF",
                "color_text" : 0,
                "color_arrow" : 1
              },
              "visor" : 1,
              "ut" : 0,
              "track_hash" : 1,
              "xml_site" : 0,
              "clickmap" : 1,
              "in_one_line" : 0,
              "ecommerce" : 0,
              "ecommerce_object" : "dataLayer"
            },
            "create_time" : "2008-08-25T16:49:51+03:00",
            "partner_id" : 0,
            "update_time" : "2015-08-19 11:18:43",
            "code" : "\n<!-- Yandex.Metrika counter -->\n<script type=\"text/javascript\">\n    (function (d, w, c) {\n        (w[c] = w[c] || []).push(function() {\n            try {\n                w.yaCounter101024 = new Ya.Metrika({id:101024,webvisor:true\n,trackHash:true\n,clickmap:true});\n\n            } catch(e) { }\n        });\n\n        var n = d.getElementsByTagName(\"script\")[0],\n                s = d.createElement(\"script\"),\n                f = function () { n.parentNode.insertBefore(s, n); };\n        s.type = \"text/javascript\";\n        s.async = true;\n        s.src = (d.location.protocol == \"https:\" ? \"https:\" : \"http:\") + \"//mc.yandex.ru/metrika/watch.js\";\n\n        if (w.opera == \"[object Opera]\") {\n            d.addEventListener(\"DOMContentLoaded\", f, false);\n        } else { f(); }\n    })(document, window, \"yandex_metrika_callbacks\");\n</script>\n<noscript><div><img src=\"//mc.yandex.ru/watch/101024\" style=\"position:absolute; left:-9999px;\" alt=\"\" /></div></noscript>\n<!-- /Yandex.Metrika counter -->\n\n\n",
            "monitoring" : {
              "enable_monitoring" : 1,
              "emails" : [ "jevstratova@amf.ru", "jzvereva@amf.ru", "internet@amf.ru", "sn@amf.ru", "vgabdullin@amf.ru" ],
              "sms_allowed" : 0,
              "enable_sms" : 0,
              "sms_time" : "8-19;8-19;8-19;8-19;8-19;8-19;8-19",
              "phones" : [ ],
              "possible_phones" : [ ]
            },
            "filter_robots" : 1,
            "time_zone_name" : "Europe/Moscow",
            "time_zone_offset" : 180,
            "currency" : "RUB",
            "visit_threshold" : 1800,
            "rating_options" : {
              "enabled" : 0,
              "category_id" : 0
            },
            "max_goals" : 200,
            "max_operations" : 30,
            "max_filters" : 30
          };
    }

});

