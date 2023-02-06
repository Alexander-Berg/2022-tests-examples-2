/* eslint-env es6 */
/* eslint max-len: 0 */

const domikBaseData = require('./mocks/domik.json');
const wrap = (func) => {
    return (...args) => {
        return '<div class="desk-notif__wrapper" style="margin-top: 0"><div class="desk-notif">' +
            func(...args) +
            '</div></div>';
    };
};

exports.domik = (execView) => execView('DeskNotifCard_domik', {
    name: 'domik'
}, Object.assign({}, domikBaseData));

exports.domikCounter = (execView) => execView('DeskNotifCard_domik', {
    name: 'domik'
}, Object.assign({}, domikBaseData, {
    Mail: Object.assign({}, domikBaseData.Mail, {
        count: 13
    })
}));

exports.domikCounter0 = (execView) => execView('DeskNotifCard_domik', {
    name: 'domik'
}, Object.assign({}, domikBaseData, {
    Mail: Object.assign({}, domikBaseData.Mail, {
        count: 0
    })
}));

exports.domikCounterExpanded = (execView) => execView('DeskNotifCard_domik', {
    name: 'domik'
}, Object.assign({}, domikBaseData, {
    Mail: Object.assign({}, domikBaseData.Mail, {
        count: 13, visible: 1
    })
}));

exports.domikExpanded = (execView) => execView('DeskNotifCard_domik', {
    name: 'domik'
}, Object.assign({}, domikBaseData, {
    Mail: Object.assign({}, domikBaseData.Mail, {
        visible: 1
    })
}));

exports.domikExpandedMoney = (execView) => execView('DeskNotifCard_domik', {
    name: 'domik'
}, Object.assign({}, domikBaseData, {
    Mail: Object.assign({}, domikBaseData.Mail, {
        visible: 1
    }),
    OurNotifications: [{
        'count_key': 'rub',
        'raw_hreficon': 'https://money.yandex.ru/',
        'count': '123',
        'raw_href': 'https://money.yandex.ru/',
        'style': 'money',
        'hreficon': 'https://money.yandex.ru/',
        'href': 'https://money.yandex.ru/',
        'id': 'money',
        'pos': 7,
        'sum': '0.00',
        'sign': {}
    }]
}));

exports.domikSocial = (execView) => execView('DeskNotifCard_domik', {
    name: 'domik'
}, Object.assign({}, domikBaseData, {
    Mail: Object.assign({}, domikBaseData.Mail, {
        visible: 1,
        nomailbox: 1
    })
}));

exports.domikSocialMoney = (execView) => execView('DeskNotifCard_domik', {
    name: 'domik'
}, Object.assign({}, domikBaseData, {
    Mail: Object.assign({}, domikBaseData.Mail, {
        visible: 1,
        nomailbox: 1
    }),
    OurNotifications: [{
        'count_key': 'rub',
        'raw_hreficon': 'https://money.yandex.ru/',
        'count': '123',
        'raw_href': 'https://money.yandex.ru/',
        'style': 'money',
        'hreficon': 'https://money.yandex.ru/',
        'href': 'https://money.yandex.ru/',
        'id': 'money',
        'pos': 7,
        'sum': '0.00',
        'sign': {}
    }]
}));

exports.login = (execView, {documentMods}) => {
    documentMods.push('i-ua_browser_desktop');

    return execView('DeskNotifCard_login', {
        name: 'login'
    }, Object.assign({}, domikBaseData, {
        Mail: Object.assign({}, domikBaseData.Mail, {
            Logged: 0,
            visible: 1
        })
    }));
};

exports.loginPlus = (execView, {documentMods}) => {
    documentMods.push('i-ua_browser_desktop');

    return execView('DeskNotifCard_login', {
        name: 'login'
    }, Object.assign({}, domikBaseData, {
        Mail: Object.assign({}, domikBaseData.Mail, {
            Logged: 0,
            visible: 1
        }),
        Plus: {
            show: 1,
            url: 'http://ya.ru',
            utm: ''
        },
        HomePageNoArgs: 'http://www.yandex.ru'
    }));
};

exports.loginStale = (execView, {documentMods}) => {
    documentMods.push('i-ua_browser_desktop');

    return execView('DeskNotifCard_login', {
        name: 'login'
    }, Object.assign({}, domikBaseData, {
        Mail: Object.assign({}, domikBaseData.Mail, {
            Logged: 0,
            visible: 1
        }),
        'Stale_AuthInfo': {
            'UserName': {
                'l': 'asya pupkin',
                'str': 'asya pupkin',
                'f': 'v'
            },
            'display_login': 'vasya',
            'timestamp': '1512143138',
            'uid': '73855104',
            'login': 'vasya',
            'avatar_id': '0/0-0'
        },
        HomePageNoArgs: 'http://www.yandex.ru'
    }));
};

exports.loginStaleMinified = (execView) => execView('DeskNotifCard_login', {
    name: 'login'
}, Object.assign({}, domikBaseData, {
    Mail: Object.assign({}, domikBaseData.Mail, {
        Logged: 0,
        visible: 0
    }),
    'Stale_AuthInfo': {
        'UserName': {
            'l': 'asya pupkin',
            'str': 'asya pupkin',
            'f': 'v'
        },
        'display_login': 'vasya',
        'timestamp': '1512143138',
        'uid': '73855104',
        'login': 'vasya',
        'avatar_id': '0/0-0'
    },
    HomePageNoArgs: 'http://www.yandex.ru'
}));

exports.loginTT = (execView) => execView('DeskNotifCard_login', {
    name: 'login'
}, Object.assign({}, domikBaseData, {
    Locale: 'tt',
    Mail: Object.assign({}, domikBaseData.Mail, {
        Logged: 0,
        visible: 1
    }),
    HomePageNoArgs: 'http://www.yandex.ru'
}));

exports.disaster = (execView) => execView('DeskNotifCard_disaster', {
    'actions': {
        'close': '/portal/set/any/?sk=yfa481042e8b34303415cb7d93a937a0f&dntf=dstr:al:56e6'
    },
    'data': {
        'counter': 'atata',
        'domain': 'all',
        'from': '2017-06-22 03:00',
        'geos': '10000',
        'lang': 'all',
        'popup_flag': '1',
        'popup_text': 'фефеф',
        'text': 'Оперативная информация',
        'till': '2027-03-26 23:59',
        'title': 'Всё хорошо',
        'type': 'alert'
    },
    'expanded': 0,
    'name': 'disaster',
    'order': 1,
    HomePageNoArgs: 'http://www.yandex.ru'
});

exports.disasterFatal = (execView) => execView('DeskNotifCard_disaster', {
    'actions': {
        'close': '/portal/set/any/?sk=yfa481042e8b34303415cb7d93a937a0f&dntf=dstr:al:56e6'
    },
    'data': {
        'counter': 'atata',
        'domain': 'all',
        'from': '2017-06-22 03:00',
        'geos': '10000',
        'lang': 'all',
        'popup_flag': '1',
        'popup_text': 'фефеф',
        'text': 'Оперативная информация',
        'till': '2027-03-26 23:59',
        'title': 'Всё хорошо',
        'type': 'fatal'
    },
    'expanded': 0,
    'name': 'disaster',
    'order': 1
});

exports.nowcast = (execView) => execView('DeskNotifCard_nowcast', {
    'actions': {
        'close': '/portal/set/any/?sk=ydb4783baa8ed5488a0ba1d756408e4b6&dntf=ncst::'
    },
    'data': {
        'href': 'https://yandex.ru/pogoda/nowcast?lat=58.006456&lon=56.232675',
        'prec_strength': 0.25,
        'prec_type': 3,
        'state': 'ends',
        'sub_state': 'ends_35',
        'text': 'Снег закончится в течение получаса',
        'time': 1521197400
    },
    'expanded': 0,
    'name': 'nowcast',
    'order': 1
}, {});

exports.nowcastMap = (execView) => '<style>' +
    '.desk-notif-card__nowcast-map{background-image: none !important;}' +
    '</style>' + execView('DeskNotifCard_nowcast', {
    'actions': {
        'close': '/portal/set/any/?sk=ydb4783baa8ed5488a0ba1d756408e4b6&dntf=ncst::'
    },
    'data': {
        'href': 'https://yandex.ru/pogoda/nowcast?lat=58.006456&lon=56.232675',
        'prec_strength': 0.25,
        'prec_type': 3,
        'state': 'ends',
        'sub_state': 'ends_35',
        'text': 'Снег закончится в течение получаса',
        'time': 1521197400,
        'static_map_url': '[% mockSvg %]'
    },
    'expanded': 0,
    'name': 'nowcast',
    'order': 1
}, {
    Weather_map: {
        geo_valid: 1
    },
    GeoDetection: {
        lat: 12,
        lon: 34
    },
    Timestamp: 1234
});

exports.rates = (execView) => execView('DeskNotifCard_rates', {
    'actions': {
        'close': '/portal/set/any/?sk=yfa481042e8b34303415cb7d93a937a0f&dntf=rate:1:72fb'
    },
    'data': {
        'Xivadata': {
            'ch': 'XDATA.stocks',
            'dt': 1337,
            'key': '1_10000',
            'ts': 1521234000
        },
        'alt': 'курс ЦБ РФ на 17/03',
        'alt_template': 'курс ЦБ РФ на %d',
        'datetime_full': '17/03',
        'delta': '+0,47',
        'delta_raw': '0.47',
        'history': [
            '57.4942',
            '57.0188',
            '56.9372',
            '56.9359',
            '56.6122',
            '56.8011',
            '56.5041'
        ],
        'href': 'https://news.yandex.ru/quotes/1.html',
        'id': '1',
        'is_hot': '1',
        'short_caps': '<c>USD</c>',
        'symbol': '$',
        'text': 'USD ЦБ',
        'value': '57,49'
    },
    'expanded': 0,
    'name': 'rates',
    'order': 2
});

exports.traffic = (execView) => execView('DeskNotifCard_traffic', {
    'actions': {
        'close': '/portal/set/any/?sk=yfa481042e8b34303415cb7d93a937a0f&dntf=traf::c1bc'
    },
    'data': {
        'plain': {
            'geo': '213',
            'html': 'С 00:00 11 ноября до 00:00 12 ноября будет перекрыто движение в районе стадиона «Лужники» в связи с проведением матча Россия – Аргентина',
            'info_id': 'tmmgnk',
            'popup': '1',
            'reason': 'Матч Россия – Аргентина',
            'subtitle': '',
            'text': 'Перекрытия движения в районе «Лужников» завтра',
            'url': 'https://yandex.ru/maps/213/moscow/?um=constructor%3A3c3d15999c0b3afce7db1bad40ccac6a40178f7a7e2d0e811a4fe7980528976d&source=constructorLink&mode=usermaps&ll=37.571249%2C55.733498&z=13',
            'url_img': 'https://yastatic.net/morda-logo/i/disaster/11nov_moscow.jpg'
        }
    },
    'expanded': 0,
    'name': 'traffic',
    'order': 1
});

exports.route = (execView) => `<script>
    window.mocks = {
        route: ${JSON.stringify(require('./mocks/route.json'))},
        routeInverse: ${JSON.stringify(require('./mocks/route_inverse.json'))}
    };

    var oldAjax = $.ajax;
    $.ajax = function (opts) {
        if (opts.url.indexOf('geohelper') > -1) {
            if (opts.url.indexOf('points=37.6409923652344') > -1) {
                return $.Deferred().resolve(window.mocks.route);
            } else {
                return $.Deferred().resolve(window.mocks.routeInverse);
            }
        }
        return oldAjax.apply(this, arguments);
    };

    home.now = function () {
        return new Date();
    };
</script>` + execView('DeskNotifCard_route', {
    'actions': {
        'ban': '/portal/set/any/?sk=yfa481042e8b34303415cb7d93a937a0f&dntf=rout:*:',
        'close': '/portal/set/any/?sk=yfa481042e8b34303415cb7d93a937a0f&dntf=rout::7caa'
    },
    'data': require('./mocks/points.json'),
    'expanded': 0,
    'name': 'route',
    'order': 2
}, {
    GeohelperHost: 'yandex.ru',
    Locale: 'ru',
    MordaZone: 'ru'
});

exports.weather = (execView) => execView('DeskNotifCard_weather', {
    'actions': {
        'close': '/portal/set/any/?sk=yfa481042e8b34303415cb7d93a937a0f&dntf=wthr:i:3602'
    },
    'data': {
        'icon': 'ovc_-sn',
        'text': 'посмотреть погоду на карте',
        'url': 'https://yandex.ru/pogoda/maps/temperature?from=ya-widget-link&origin=maps-temperature&source=ya-widget-link',
        'portal_icon': 'alert'
    },
    'expanded': 0,
    'name': 'weather',
    'order': 1
}, {});

const promoMock = require('./mocks/promo');
const promoBgMock = require('./mocks/promo_bg');
exports.promo = (execView) => execView('DeskNotifCard_promo', promoMock, {});
exports['promo-bg'] = (execView) => execView('DeskNotifCard_promo', promoBgMock, {});

const etrainsMock = require('./mocks/etrains.json');
exports.etrains = execView => execView('DeskNotifCard_etrains', etrainsMock);

const etrainsTunedMock = require('./mocks/etrainsTuned.json');
exports.etrainsTuned = execView => `
<script>
var oldAjax = $.ajax;
$.ajax = function (opts) {
    if (opts.url.indexOf('next_trains') > -1) {
        opts.success.call(opts.context, ${JSON.stringify(require('./mocks/etrainsTunedResponse.json'))});
        return;
    }
    return oldAjax.apply(this, arguments);
};
</script>
` + execView('DeskNotifCard_etrains', etrainsTunedMock);

const marketResponses = require('./mocks/marketResponses.js');

[
    'marketSingleItem',
    'marketManyItems',
    'marketManyItemsButStaled',
    'marketFlashDiscountMoreHour',
    'marketFlashDiscountMoreHalfHour',
    'marketFlashDiscountMoreTenMin',
    'marketFlashDiscountMoreFiveMin',
    'marketFlashDiscountLessFourMin',
    'marketSingleItem',
    'marketManyItems',
    'marketPromocodeSingle',
    'marketPromocodeMax',
    'marketPromocodeSeveral',
    'marketCoupon',
    'marketCouponWithEnd',
    'marketCouponWithManyItems',
    'marketCouponWithEndWithManyItems',
    'marketCartPromoItemsDiscount',
    'marketCartPromoItemsDiscountWithManyItems',
    'marketPromoPriceDrop',
    'marketPromoPriceDropManyItems'
].forEach(key => {
    exports[key] = execView => execView.withReq('DeskNotifCard_market', {
        actions: {
            close: 'https://yandex.ru/portal/set/any/?sk=ubc71aa508bdc90f6c08805a07dde6d07&dntf=market::'
        },
        expanded: 0,
        name: 'market',
        order: 7
    }, {
        GeohelperHost: 'yandex.ru',
        GeoID: '213',
        Requestid: '1616422139.00000.1111.2222',
        MarketCart: Object.assign({
            show: 1,
            url: 'https://pokupki.market.yandex.ru/my/cart?clid=904'
        }, marketResponses[key])
    });
});

const covidGraphMock = require('./mocks/covidGraph.json');
exports.covidGraph = execView => execView('DeskNotifCard_covid', covidGraphMock);

const covidHistogramMock = require('./mocks/covidHistogram.json');
exports.covidHistogram = execView => execView('DeskNotifCard_covid', covidHistogramMock);

const covidPromoData = Object.assign({}, covidHistogramMock.data, {
    promo: {
        counter: 'vacine',
        icon: '',
        icon_skin: '',
        items: [
            {
                counter: 'vacine',
                icon: '',
                icon_skin: '',
                text: 'О вакцинации',
                url: 'https://yandex.ru/covid19/stat?geoId=225&sectionId=vaccinations-questions?utm=main_big'
            },
            {
                counter: 'qr',
                icon: 'https://yastatic.net/s3/home/covid/speed/promo/qr-l.svg',
                icon_skin: 'https://yastatic.net/s3/home/covid/speed/promo/qr-d.svg',
                text: null,
                tooltip_text: 'Получить QR-код',
                url: 'https://yandex.ru/promo/searchapp/covid/qr?utm_source=big&utm_medium=landing&utm_campaign=landing_covid_qr'
            }
        ],
        text: 'О вакцинации',
        url: 'https://yandex.ru/covid19/stat?geoId=225&sectionId=vaccinations-questions?utm=main_big'
    }
});
exports.covidPromo = execView => execView('DeskNotifCard_covid', Object.assign({}, covidHistogramMock, {data: covidPromoData}));

const teaser = require('./mocks/teaser.json');
const teaserDataWide = Object.assign({}, teaser.data, {title1: 'Умная колонка для вашего дома', text1: 'С бесплатной подпиской Плюс Мульти'});
const teaserDataTitle2 = Object.assign({}, teaser.data, {title2: 'умная колонка'});
const teaserDataText2 = Object.assign({}, teaser.data, {text2: 'оформить проще простого'});
const teaserDataTitle2Text2 = Object.assign({}, teaser.data, {title2: 'умная колонка', text2: 'оформить проще простого'});
const teaserDataNoDescription = Object.assign({}, teaser.data, {title2: 'умная колонка', text1: ''});

exports.teaser = (execView) => execView('DeskNotifCard_teaser', Object.assign({}, teaser));
exports.teaserNoDescription = (execView) => execView('DeskNotifCard_teaser', Object.assign({}, teaser, {data: teaserDataNoDescription}));
exports.teaserWide = (execView) => execView('DeskNotifCard_teaser', Object.assign({}, teaser, {data: teaserDataWide}));
exports.teaserTitle2 = (execView) => execView('DeskNotifCard_teaser', Object.assign({}, teaser, {data: teaserDataTitle2}));
exports.teaserText2 = (execView) => execView('DeskNotifCard_teaser', Object.assign({}, teaser, {data: teaserDataText2}));
exports.teaserTitle2Text2 = (execView) => execView('DeskNotifCard_teaser', Object.assign({}, teaser, {data: teaserDataTitle2Text2}));

const teaserRedesign = require('./mocks/teaser_redesign.json');
const teaserDataRedesignDefault = Object.assign({}, teaserRedesign.data, {button_text: '', button_color: ''});
const teaserDataRedesignLight = Object.assign({}, teaserRedesign.data, {button_text: 'Берем?', button_color: '#bbeab4'});
const teaserDataRedesignDark = Object.assign({}, teaserRedesign.data, {button_text: 'Берем?', button_color: '#2a6595'});

exports.teaserRedesign = (execView) => execView('DeskNotifCard_teaser', Object.assign({}, teaserRedesign));
exports.teaserRedesignDefault = (execView) => execView('DeskNotifCard_teaser', Object.assign({}, teaserRedesign, {data: teaserDataRedesignDefault}));
exports.teaserRedesignLight = (execView) => execView('DeskNotifCard_teaser', Object.assign({}, teaserRedesign, {data: teaserDataRedesignLight}));
exports.teaserRedesignDark = (execView) => execView('DeskNotifCard_teaser', Object.assign({}, teaserRedesign, {data: teaserDataRedesignDark}));

const plusCard = {
    name: 'plus-wallet',
    actions: {
        'close': '/close'
    },
    data: {
        href: '/plus.url'
    }
};

exports.plusWalletNoBalanceNoPlus = (execView) => execView('DeskNotifCard_plusWallet', plusCard, {
    Plus: {
        show: 1,
        is_active: false,
        local_currency: 'RUB',
        balances: []
    }
});
exports.plusWalletBalanceNoPlus = (execView) => execView('DeskNotifCard_plusWallet', plusCard, {
    Plus: {
        show: 1,
        is_active: false,
        local_currency: 'RUB',
        local_amount: '123',
        balances: [
            {
                amount: 123,
                currency: 'RUB'
            }
        ]
    }
});
exports.plusWalletNoBalancePlus = (execView) => execView('DeskNotifCard_plusWallet', plusCard, {
    Plus: {
        show: 1,
        is_active: true,
        local_currency: 'RUB',
        balances: []
    }
});
exports.plusWalletBalancePlus = (execView) => execView('DeskNotifCard_plusWallet', plusCard, {
    Plus: {
        show: 1,
        is_active: true,
        local_currency: 'RUB',
        local_amount: '123',
        balances: [
            {
                amount: 123,
                currency: 'RUB'
            }
        ]
    }
});

for (const data in module.exports) {
    module.exports[data] = wrap(module.exports[data]);
}
