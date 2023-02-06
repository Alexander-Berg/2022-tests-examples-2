var Mock = require('./mock');

var comEn = 'com_lang_en',
    comId = 'com_lang_id',
    auth = 'auth',
    newTabInformers = 'geminiNewTabInformers',
    authLong = 'auth_long',
    comtrDate = 'comtr_date',
    comtrTraffic = 'comtr_traffic',
    comtrNoTraffic = 'comtr_no_traffic',
    tvVideo = 'geminiTvVideo',
    ffStocks = 'ffStocks',
    ffTraffic = 'ffTraffic',
    ffWeather = 'ffWeather',
    tvStocks = 'geminiTvStocks',
    tvWeather = 'geminiTvWeather',
    tvTraffic = 'geminiTvTraffic',
    tvTopNews = 'geminiTvTopNews',
    tvTv = 'geminiTvTv',
    services404 = 'ruServices404',
    ExampleGramps = 'ExampleGramps',
    grampsLogIn = 'GrampsLogIn',
    grampsTeaserNone = 'GrampsTeaserNone',
    trafficT = 'trafficT',
    wrongDate = 'wrong_date',
    logIn = 'auth_long',
    longCity = 'longCity',
    weatherCloudy = 'weatherCloudy',
    kylorenSkinTouch = 'kylorenSkinTouch',
    servicesTouch = 'servicesTouch',
    videoTouch = 'videoTouch',
    longNewsForTouch = 'longNewsForTouch',
    comtrDistPopup = 'comtr_distpop',
    tSpecial = 'touchSpecial',
    NoExps = 'noExps',
    tAeroexpress = 'aero_departure12',
    tTimeShift = 'geminiTouchTimeshift',
    tBridges = 'bridges',
    dMulti = 'multiV14',
    spokUa = 'spokUa',
    spokEn = 'spokEn',
    spokRu = 'spokRu',
    spokDate = 'spok_date',
    spokNews = 'spok_news',
    spokWeather = 'spok_weather',
    v14StaleLogin = 'geminiV14StaleLogin',
    v14AuthSocial = 'geminiV14AuthSocial',
    v14ThemePromo = 'geminiV14ThemePromo',
    v14Tv = 'geminiV14Tv',
    v14GeoBlock = 'geminiV14GeoBlock',
    v14NoNotif = 'v14_no_notif',
    v14Example = 'geminiV14Example',
    v14Services = 'geminiV14Services',
    v14Traffic = 'geminiV14Traffic',
    v14TopNews = 'geminiV14TopNews',
    v14Auth = 'geminiV14Auth',
    v14Weather = 'geminiV14Weather',
    v14Afisha = 'geminiV14Afisha';

module.exports = {
    touch: {
        yaru: {
            default: new Mock('default', [NoExps]),
        },
        ru: {
            default: new Mock('default', [NoExps, longNewsForTouch]),
            tTraffic: new Mock('traffic_block', [trafficT, NoExps]),
            wrongDate: new Mock('wrong_date_popup', [wrongDate, trafficT, weatherCloudy, NoExps]),
            complexity: new Mock('static_blocks', [trafficT, weatherCloudy, longNewsForTouch, NoExps]),
            specialNew: new Mock('special_new', [tSpecial, NoExps]),
            logIn: new Mock('long_login', [logIn, NoExps]),
            logInLongCity: new Mock('long_login&city', [logIn, longCity, NoExps]),
            services: new Mock('services', [servicesTouch, NoExps]),
            timeshift: new Mock('timeshift', [tTimeShift, NoExps]),
            bridges: new Mock('bridges', [tBridges, NoExps]),
            video: new Mock('video', [videoTouch, NoExps]),
            news: new Mock('news', [longNewsForTouch, NoExps]),
            aeroexpress: new Mock('aeroexpress', [tAeroexpress, NoExps]),
            kylorenDefault: new Mock('kyloren_default', [kylorenSkinTouch, NoExps, longNewsForTouch]),
            kylorenSpecialNew: new Mock('special_new, kyloren', [tSpecial, kylorenSkinTouch, NoExps]),
            kylorenLogIn: new Mock('long_login, kyloren', [logIn, kylorenSkinTouch, NoExps]),
            kylorenLogInLongCity: new Mock('long_login&city, kyloren', [logIn, longCity, kylorenSkinTouch, NoExps]),
            kylorenServices: new Mock('services, kyloren', [kylorenSkinTouch, servicesTouch, NoExps]),
            kylorenTimeshift: new Mock('timeshift, kyloren', [tTimeShift, kylorenSkinTouch, NoExps]),
            kylorenBridges: new Mock('bridges, kyloren', [tBridges, kylorenSkinTouch, NoExps]),
            kylorenVideo: new Mock('video, kyloren', [kylorenSkinTouch, videoTouch, NoExps]),
            kylorenNews: new Mock('news, kyloren', [kylorenSkinTouch, longNewsForTouch, NoExps]),
            kylorenAeroexpress: new Mock('aeroexpress, kyloren', [tAeroexpress, kylorenSkinTouch, NoExps])
        },
        comTr: {
            default: new Mock('default', [NoExps]),
            tr: new Mock('date', [comtrDate]),
            auth: new Mock('auth', [auth, comtrTraffic, comtrDate]),
            auth_long: new Mock('auth_long', [authLong, comtrDate]),
            traffic: new Mock('with_traffic', [comtrTraffic, NoExps]),
            no_traffic: new Mock('without_traffic', [comtrNoTraffic, NoExps])
        },
        com: {
            default: new Mock('default', [NoExps]),
            en: new Mock('en', [comEn]),
            id: new Mock('id', [comId]),
            auth_en: new Mock('en_auth', [comEn, auth]),
            auth_id: new Mock('id_auth', [comId, auth]),
            auth_long: new Mock('en_auth_long', [comEn, authLong])
        },
        all: {
            default: new Mock('default', [NoExps])
        },
        embed: {
            default: new Mock('default', [NoExps])
        },
        spok: {
            default: new Mock('default', [NoExps]),
            langEn: new Mock('en', [spokEn]),
            langUa: new Mock('ua', [spokUa]),
            langRu: new Mock('ru', [spokRu]),
            authRu: new Mock('ru_auth', [spokRu, auth, spokDate]),
            authUa: new Mock('ua_auth', [spokUa, auth, spokDate]),
            authEn: new Mock('en_auth', [spokEn, auth, spokDate]),
            authLongRu: new Mock('ru_auth_long', [spokRu, authLong, spokDate]),
            authLongUa: new Mock('ua_auth_long', [spokUa, authLong, spokDate]),
            authLongEn: new Mock('en_auth_long', [spokEn, authLong, spokDate]),
            news: new Mock('news', [spokNews]),
            weather: new Mock('weather', [spokWeather])
        },
        tune: {
            default: new Mock('default')
        }
    },
    tv: {
        default: new Mock('default', [NoExps]),
        video: new Mock('video', [tvVideo]),
        topNews: new Mock('topnews', [tvTopNews]),
        tv: new Mock('tv', [tvTv]),
        informers: new Mock('informers', [tvTraffic, tvWeather, tvStocks])
    },
    desktop: {
        v14: {
            default: new Mock('default', [NoExps, v14NoNotif]),
            example: new Mock('example', [v14Example]),
            staleLogin: new Mock('stale_login', [v14StaleLogin]),
            authSocial: new Mock('auth_social', [v14AuthSocial]),
            dMulti: new Mock('multi_login_v14', [dMulti, NoExps, v14NoNotif]),
            themePromo: new Mock('theme_promo', [v14ThemePromo]),
            services: new Mock('services', [v14Services]),
            afisha: new Mock('afisha', [v14Afisha]),
            geoBlock: new Mock('geo_block', [v14GeoBlock]),
            weather: new Mock('weather', [v14Weather]),
            tv: new Mock('tv', [v14Tv]),
            auth: new Mock('auth', [v14Auth]),
            topNews: new Mock('top_news', [v14TopNews]),
            traffic: new Mock('traffic', [v14Traffic])
        },
        gramps: {
            default: new Mock('default', [NoExps]),
            exampleGramps: new Mock('example_for_gramps', [ExampleGramps]),
            logInGramps: new Mock('login_domik', [grampsLogIn]),
            teaserNoneGramps: new Mock('no_teaser_gramps', [grampsTeaserNone])
        },
        '404': {
            default: new Mock('default', [NoExps]),
            services404: new Mock('ru_404_Services', [services404])
        },
        yaru: {
            default: new Mock('default', [NoExps])
        },
        spok: {
            langEn: new Mock('en', [spokEn]),
            langUa: new Mock('ua', [spokUa]),
            langRu: new Mock('ru', [spokRu]),
            authRu: new Mock('ru_auth', [spokRu, auth]),
            authUa: new Mock('ua_auth', [spokUa, auth]),
            authEn: new Mock('en_auth', [spokEn, auth]),
            authLongRu: new Mock('ru_auth_long', [spokRu, authLong]),
            authLongUa: new Mock('ua_auth_long', [spokUa, authLong]),
            authLongEn: new Mock('en_auth_long', [spokEn, authLong])
        },
        all: {
            default: new Mock('default', [NoExps])
        },
        pumpkin: {
            default: new Mock('default')
        },
        ff: {
            default: new Mock('default', [NoExps]),
            ffInformers: new Mock('ff_informers', [ffStocks, ffTraffic, ffWeather])
        },
        comTr: {
            default: new Mock('default', [NoExps]),
            tr: new Mock('date', [comtrDate, NoExps]),
            auth: new Mock('auth', [auth, comtrTraffic, comtrDate, NoExps]),
            auth_long: new Mock('auth_long', [authLong, comtrDate, NoExps]),
            traffic: new Mock('with_traffic', [comtrTraffic, NoExps]),
            no_traffic: new Mock('without_traffic', [comtrNoTraffic, NoExps]),
            dist_popup: new Mock('dist_popup', [comtrDistPopup, NoExps])
        },
        com: {
            default: new Mock('default', [NoExps]),
            en: new Mock('en', [comEn]),
            id: new Mock('id', [comId]),
            auth_en: new Mock('en_auth', [comEn, auth]),
            auth_id: new Mock('id_auth', [comId, auth]),
            auth_long: new Mock('en_auth_long', [comEn, authLong])
        },
        chromenewtab: {
            default: new Mock('default', [NoExps]),
            informers: new Mock('informers', [NoExps, newTabInformers])
        },
        tune: {
            default: new Mock('default')
        }
    }
};
