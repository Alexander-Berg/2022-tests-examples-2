exports.simple = function (execView) {
    return '<div style="display: inline-block; vertical-align: top; margin-left: 100px;">' + execView('Domik2', {}, {
        Mail: {
            '2fa': 0,
            LiteUser: null,
            Logged: 0,
            NoAuthReason: 'no-session',
            auth_host: 'passport.yandex.ru',
            banner: null,
            href: 'https://mail.yandex.ru/',
            nomailbox: null,
            processed: 1,
            promo_button: {
                color: 'blue',
                counter: 'zavesti',
                domain: 'ru',
                geo: '10000',
                lang: 'ru',
                text: 'завести почту',
                url: 'https://mail.yandex.ru/?origin=home_soc_ru'
            },
            promo_disk_v12: {
                counter: 'diskpromo',
                domain: 'ru',
                geo: '10000',
                geo_exclude: '977',
                lang: 'ru',
                text: '10 ГБ на Диске',
                url: 'https://disk.yandex.ru/?auth&source=main-nonlogin'
            },
            show: 1,
            visible: 1,
            visible_configured: 0,
            visible_set_off: 'https://yandex.ru/portal/set/any/?sk=y6d73bfd676fab30a6685fa6da1d32193&empty=1&mv=1',
            visible_set_on: 'https://yandex.ru/portal/set/any/?sk=y6d73bfd676fab30a6685fa6da1d32193&empty=1&mv=0',
            expanded: 1
        },
        AuthInfo: {
            users: []
        },
        Passport: {
            host: 'passport.yandex.ru',
            path: 'passport.yandex.ru/passport',
            register_url: 'https://passport.yandex.ru/registration?mode=register&retpath=https%3A%2F%2Fmail.yandex.ru&origin=passport_auth2reg&mda=0',
            social_host: 'social.yandex.ru',
            url: 'https://passport.yandex.ru/passport?mda=0'
        },
        MordaZone: 'ru',
        SocialProvidersList: [
            {
                code: 'vk',
                display_name: 'ВКонтакте',
                enabled: 1,
                id: '1',
                primary: 1
            },
            {
                code: 'fb',
                display_name: 'Facebook',
                enabled: 1,
                id: '2',
                primary: 1
            },
            {
                code: 'tw',
                display_name: 'Twitter',
                enabled: 1,
                id: '3',
                primary: 1
            },
            {
                code: 'mr',
                display_name: 'Mail.ru',
                enabled: 1,
                id: '4',
                primary: 0
            },
            {
                code: 'gg',
                display_name: 'Google',
                enabled: 1,
                id: '5',
                primary: 0
            },
            {
                code: 'ok',
                display_name: 'Одноклассники',
                enabled: 1,
                id: '6',
                primary: 0
            }
        ],
        JSON: {
            mail: {
                expanded: 1
            },
            authInfo: {
            },
            passportHost: 'https://passport.yandex.ru'
        }
    }) + '</div>';
};
