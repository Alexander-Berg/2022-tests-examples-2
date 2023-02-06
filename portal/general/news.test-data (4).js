/* eslint max-len: 0 */

const simple = (execView, params) => {
    let req = {
        JSON: {
            common: {}
        },
        Local: {
            hour: '00',
            min: '00'
        },
        MordaZone: 'ru',
        Topnews: require('./mocks/simple.json')
    };

    if (params && params.personal) {
        req.Topnews = Object.assign({}, req.Topnews, {tabs: req.Topnews.tabs.concat([require('./mocks/personal-tab.json')])});
    }

    const bodyStyles = `
        <style>
            .news-test-wrapper {
                padding-top: 5px;
                padding-left: 45px;
            }
        </style>`;

    return ((params && params.before) || '') + bodyStyles + `
        <div class="news-test-wrapper">
            <div class="container__first">
                <div class="col_td_0">
                    ${execView('News', req)}
                </div>
            </div>
        </div>`;
};

exports.simple = (execView) => simple(execView);

exports.extraPopup = (execView, params) => {
    let req = {
        JSON: {
            common: {}
        },
        Local: {
            hour: '00',
            min: '00'
        },
        MordaZone: 'ru',
        ab_flags: {
            topnews_extra: {
                value: 1
            }
        },
        Topnews: require('./mocks/extra-popup.json')
    };

    if (params && params.personal) {
        req.Topnews = Object.assign({}, req.Topnews, {tabs: req.Topnews.tabs.concat([require('./mocks/personal-tab.json')])});
    }

    const bodyStyles = `
        <style>
            .news-test-wrapper {
                padding-top: 5px;
                padding-left: 45px;
                width: 605px
            }
        </style>`;

    return ((params && params.before) || '') + bodyStyles + `
        <div class="news-test-wrapper">
            <div class="container__first">
                <div class="col_td_0">
                    ${execView('News', req)}
                </div>
            </div>
        </div>`;
};

exports.personal = (execView) => {
    const fakeServer = `<script>
        var server = window.server = sinon.fakeServer.create();

        server.respondImmediately = true;

        server.respondWith(/https:\\/\\/news.yandex.ru\\/api\\/v2\\/rubric/, [200, {'Content-Type': 'application/json'}, JSON.stringify(${JSON.stringify(require('./mocks/personal.json'))})]);
    </script>`;

    return simple(execView, {
        before: fakeServer,
        personal: 1
    });
};

exports.personalFallback = (execView) => {
    const fakeServer = `<script>
        var server = window.server = sinon.fakeServer.create();

        server.respondImmediately = true;

        server.respondWith(/https:\\/\\/news.yandex.ru\\/api\\/v2\\/rubric/, [404, {}, '']);
    </script>`;

    return simple(execView, {
        before: fakeServer,
        personal: 1
    });
};

exports.hotAnimated = (execView) => {
    let req = {
        JSON: {
            common: {}
        },
        Local: {
            hour: '00',
            min: '00'
        },
        MordaZone: 'ru',
        Topnews: require('./mocks/hot-animated.json')
    };

    const bodyStyles = `
        <style>
            .news-test-wrapper {
                padding-top: 5px;
                padding-left: 45px;
            }
        </style>`;

    return bodyStyles + `
        <div class="news-test-wrapper">
            <div class="container__first">
                <div class="col_td_0">
                    ${execView('News', req)}
                </div>
            </div>
        </div>`;
};

exports.special = (execView) => {
    let req = {
        JSON: {
            common: {}
        },
        Local: {
            hour: '00',
            min: '00'
        },
        MordaZone: 'ru',
        Topnews: require('./mocks/special.json')
    };

    const bodyStyles = `
        <style>
            .news-test-wrapper {
                padding-top: 5px;
                padding-left: 45px;
            }
        </style>`;

    return bodyStyles + `
        <div class="news-test-wrapper">
            <div class="container__first">
                <div class="col_td_0">
                    ${execView('News', req)}
                </div>
            </div>
        </div>`;
};

exports.covid = (execView) => {
    let req = {
        JSON: {
            common: {}
        },
        Local: {
            hour: '00',
            min: '00'
        },
        MordaZone: 'ru',
        Topnews: require('./mocks/covid.json')
    };

    const bodyStyles = `
        <style>
            .news-test-wrapper {
                padding-left: 45px;
                padding-top: 5px;
            }
        </style>`;

    return bodyStyles + `
        <div class="news-test-wrapper">
            <div class="container__first">
                <div class="col_td_0">
                    ${execView('News', req)}
                </div>
            </div>
        </div>`;
};

exports.disclaimer = (execView) => {
    let req = {
        JSON: {
            common: {}
        },
        Local: {
            hour: '00',
            min: '00'
        },
        MordaZone: 'ru',
        Topnews: require('./mocks/disclaimer.json')
    };

    const bodyStyles = `
        <style>
            .news-test-wrapper {
                padding-left: 45px;
                padding-top: 5px;
            }
        </style>`;

    return bodyStyles + `
        <div class="news-test-wrapper">
            <div class="container__first">
                <div class="col_td_0">
                    ${execView('News', req)}
                </div>
            </div>
        </div>`;
};

exports.disclaimerCustomIcon = (execView) => {
    let req = {
        JSON: {
            common: {}
        },
        Local: {
            hour: '00',
            min: '00'
        },
        MordaZone: 'ru',
        Topnews: require('./mocks/disclaimer-custom.json')
    };

    const bodyStyles = `
        <style>
            .news-test-wrapper {
                padding-left: 45px;
                padding-top: 5px;
            }
        </style>`;

    return bodyStyles + `
        <div class="news-test-wrapper">
            <div class="container__first">
                <div class="col_td_0">
                    ${execView('News', req)}
                </div>
            </div>
        </div>`;
};


exports.degradation = (execView) => {
    let req = {
        JSON: {
            common: {}
        },
        MordaZone: 'ru',
        ab_flags: {
            news_degradation: {
                value: 1
            }
        },
        Topnews: require('./mocks/degradation.json')
    };

    const bodyStyles = `
        <style>
            .news-test-wrapper {
                padding-left: 45px;
                padding-top: 5px;
            }
        </style>`;

    return bodyStyles + `
        <div class="news-test-wrapper">
            <div class="container__first media-grid">
                <div class="col_td_0  media-grid__media-content-main ">
                    ${execView('News', req)}
                </div>
            </div>
        </div>`;
};
