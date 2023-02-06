module.exports = {
    app: {
        origin: ''
    },

    blackbox: {
        api: 'blackbox-mimino.yandex.net',
        avatarHost: 'https://avatars.mdst.yandex.net'
    },

    bunker: {
        api: 'http://bunker-api-dot.yandex.net/v1',
        version: 'latest'
    },

    csp: {
        policies: {
            'default-src': ['\'none\''],
            'script-src': ['\'unsafe-eval\'', '\'unsafe-inline\'', '%nonce%', 'mc.yandex.ru', 'social.yandex.ru'],
            'style-src': ['\'unsafe-inline\'', 'mc.yandex.ru'],
            'img-src': ['\'self\'', 'data:', 'avatars.yandex.net', 'avatars.mds.yandex.net', 'avatars.mdst.yandex.net',
                'mc.yandex.ru', 'jing.yandex-team.ru', 'ext.captcha.yandex.net'],
            'connect-src': ['\'self\'', 'mc.yandex.ru', 'mm1-bogolyubov.appmetrika-dev.haze.yandex.com',
                'mm1-bogolyubov.appmetrika-dev.haze.yandex.ru']
        }
    },

    api: {
        email: {
            url: 'https://elakov-mobmet-9539.autobeta-appmetrica.mtrs.yandex.{tld}/transport/i-demo/sendDemoLink/',
            salt: process.env.API_SALT
        }
    },

    captchaOptions: {
        apiHost: 'captcha-test.passport.yandex.net'
    }
};
