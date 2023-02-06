const draw = req => (execView, {documentMods}) => {
    documentMods.push('i-ua_browser_desktop');
    let ajaxMock = '';
    if (req.unread) {
        ajaxMock = `<script>
                var server = window.server = sinon.fakeServer.create();
                server.respondImmediately = true;
                server.respondWith(/^https:\\/\\/yandex\\.ru\\/bell/, JSON.stringify({unviewed_count: 15, services: {}}));
            </script>`;
    } else {
        ajaxMock = '<script>sinon.stub($, \'ajax\').returns(new $.Deferred().promise());</script>';
    }
    return `${ajaxMock}
<script>
BEM.DOM.decl('notifier', {
    count: function () {
    }
});
</script>
<style>
.rows__row_main{margin-left:0 !important;}
</style>
<div class="wrapper" style="width:100%">${execView.withReq('Xproc', execView('Headline', req), req)}</div>`;
};

const baseData = {
    JSON: {
        common: {
            language: 'ru'
        }
    },
    LanguageChooserInFooter: [],
    BigCityName: 'Москва',
    HomePageNoArgs: 'https://yandex.ru',
    MordaZone: 'ru',
    Local: {
        hour: '12',
        min: '34'
    },
    BigDay: '17',
    BigMonth: 'декабря',
    BigWday: 'четверг'
};

const plusData = {
    Plus: {
        show: 1,
        promo: {
            menu: {
                text: 'Плюс-инус',
                url: '//ya.ru'
            }
        }
    }
};

const notifierData = {
    Logged: 1,
    Bell: {
        show: 1
    }
};

const notifierUnreadData = {
    Logged: 1,
    Bell: {
        show: 1
    },
    unread: 1
};

const marketData = {
    Logged: 1,
    MarketCart: {
        totalCount: 0,
        icon_url: '//',
        show: 1
    }
};

const marketUnreadData = {
    Logged: 1,
    MarketCart: {
        totalCount: 9,
        icon_url: '//',
        show: 1
    }
};

const redirData = {
    redirLink: {
        show: 1,
        textType: 'ua',
        domain: 'ua',
        url: '//ya.ru'
    }
};

const langData = {
    JSON: {
        common: {
            language: 'ru'
        }
    },
    LanguageChooserInFooter: [
        {
            'locale': 'uk',
            'href': 'https://yandex.ua/?lang=uk&sk=yea5cdf5c2b9f2a8ffc36705bef53d33c',
            'selected': '',
            'lang': 'ua'
        },
        {
            'lang': 'ru',
            'locale': 'ru',
            'selected': '1',
            'href': 'https://yandex.ua/?lang=ru&sk=yea5cdf5c2b9f2a8ffc36705bef53d33c'
        }
    ]
};

const switchData = {
    switch_type: {
        url: '//ya.ru'
    }
};

const setHomeData = {
    SetHome: {
        show: 1
    },
    set_start_page_link: '//ya.ru',
    BrowserDesc: {
        OSFamily: 'Windows'
    },
    Chrome: 36,
    options: {}
};

const allData = {
    ...baseData,
    MordaZone: 'ru',
    ...plusData,
    ...notifierData,
    ...redirData,
    ...langData,
    ...switchData,
    ...marketData
};

const allUnreadData = {
    ...baseData,
    MordaZone: 'ru',
    ...plusData,
    ...notifierUnreadData,
    ...redirData,
    ...langData,
    ...switchData,
    ...marketUnreadData
};

const setHome = {
    ...baseData,
    ...setHomeData
};

exports.simple = draw(baseData);
exports.simpleDark = draw({...baseData, Skin: 'night'});
exports.setHome = draw(setHome);
exports.setHomeDark = draw({...setHome, Skin: 'night'});
exports.all = draw(allData);
exports.allUnread = draw(allUnreadData);
exports.allDark = draw({...allData, Skin: 'night'});
exports.allUnreadDark = draw({...allUnreadData, Skin: 'night'});
