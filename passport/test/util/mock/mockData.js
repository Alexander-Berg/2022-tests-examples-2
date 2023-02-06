var basic = {
    retpathUrl: 'http://yandex.ru/',

    goodLogin: 'good.login',
    goodPddLogin: 'good.login@okna.ru',
    badLogin: 'bad.login',
    needCompleteLogin: 'need.complete.login',
    needChangePassLogin: 'need.changepass.login',
    needCaptchaLogin: 'need.captcha.login',

    goodPass: 'good.password1234567',
    badPass: 'bad.password1234567',
    trackID: '0000000000000000000000000000000000',
    badTrackID: '1000000000000000000000000000000000',
    goodCaptcha: 'CAPTCHA',
    badCaptcha: 'AHCTPAC'
};

var sets = {
    validLoginData: {
        login: basic.goodLogin,
        password: basic.goodPass,
        retpath: basic.retpathUrl,
        policy: 'long'
    },

    validLoginDataWithTrack: {
        login: basic.goodLogin,
        password: basic.goodPass,
        retpath: basic.retpathUrl,
        track_id: basic.trackID,
        policy: 'long'
    },

    validPddLoginData: {
        login: basic.goodPddLogin,
        password: basic.goodPass,
        retpath: basic.retpathUrl,
        policy: 'long',
        is_pdd: '1'
    },

    validPddLoginDataAlt: {
        login: basic.goodPddLogin,
        password: basic.goodPass,
        retpath: basic.retpathUrl,
        policy: 'long'
    },

    validLoginDataSessional: {
        login: basic.goodLogin,
        password: basic.goodPass,
        retpath: basic.retpathUrl,
        policy: 'sessional'
    },

    validLoginDataSessionalWithTrack: {
        login: basic.goodLogin,
        password: basic.goodPass,
        retpath: basic.retpathUrl,
        track_id: basic.trackID,
        policy: 'sessional'
    },

    validPddLoginDataSessional: {
        login: basic.goodPddLogin,
        password: basic.goodPass,
        retpath: basic.retpathUrl,
        policy: 'sessional',
        is_pdd: '1'
    },

    validPddLoginDataSessionalAlt: {
        login: basic.goodPddLogin,
        password: basic.goodPass,
        retpath: basic.retpathUrl,
        policy: 'sessional'
    },

    inValidLoginData: {
        login: basic.badLogin,
        password: basic.badPass,
        retpath: basic.retpathUrl
    },

    emptyLogin: {
        login: '',
        password: basic.goodPass,
        retpath: basic.retpathUrl
    },

    noLogin: {
        password: basic.goodPass,
        retpath: basic.retpathUrl
    },

    wrongPassword: {
        login: basic.goodLogin,
        password: basic.badPass,
        retpath: basic.retpathUrl
    },

    emptyPassword: {
        login: basic.goodLogin,
        password: '',
        retpath: basic.retpathUrl
    },

    noPassword: {
        login: basic.goodLogin,
        retpath: basic.retpathUrl
    },

    loginDataWithGoodCaptcha: {
        login: basic.goodLogin,
        password: basic.goodPass,
        retpath: basic.retpathUrl,
        captcha_answer: basic.goodCaptcha
    },

    loginDataWithBadCaptcha: {
        login: basic.goodLogin,
        password: basic.goodPass,
        retpath: basic.retpathUrl,
        captcha_answer: basic.badCaptcha
    }
};

var headers = {
    'x-real-ip': '0.0.0.0',
    'x-real-scheme': 'https',
    host: 'passport.yandex.ru',
    'user-agent': 'supertest',
    cookie: 'yandexuid=0123456789'
};

exports.basic = basic;
exports.sets = sets;
exports.headers = headers;
