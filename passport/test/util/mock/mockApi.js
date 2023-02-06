/* eslint-disable max-len */

var nock = require('nock');
var data = require('./mockData.js');
const config = require('../../../configs/current');
var b = data.basic;
var s = data.sets;

const apiHost = `${config.defaults.url.protocol}://${config.defaults.url.hostname}:${config.defaults.url.port}`;

var mockApi = nock(apiHost).persist();
// var submitURL = '/1/bundle/auth/password/submit/?consumer=passport';
var submitURL = '/2/bundle/auth/password/commit_password/?consumer=passport';
var bundleSessionURL = '/1/bundle/session/?consumer=passport';

var noPolicy = nock(apiHost)
    .persist()
    .filteringRequestBody(function(path) {
        return path.replace('&policy=sessional', '').replace('&policy=long', '');
    });

mockApi.post('/1/statbox/?consumer=passport').reply(200, {
    status: 'ok'
});

mockApi
    .post('/1/bundle/auth/sso/commit/?consumer=passport', {
        saml_response: '0000',
        relay_state: '2222',
        track_id: b.trackID
    })
    .reply(200, {
        status: 'error',
        errors: ['samlresponse.invalid']
    });

mockApi
    .post('/1/bundle/auth/sso/commit/?consumer=passport', {
        saml_response: '2222',
        relay_state: '2222',
        track_id: b.trackID
    })
    .reply(200, {
        status: 'error',
        errors: ['saml_settings.invalid']
    });

mockApi
    .post('/1/bundle/auth/sso/commit/?consumer=passport', {
        saml_response: '1111',
        relay_state: '2222',
        track_id: b.trackID
    })
    .reply(200, {
        status: 'ok',
        track_id: b.trackID
    });

mockApi
    .post('/1/statbox/?consumer=passport', {
        action: 'csrf',
        mode: 'logout',
        url: '/passport?mode=logout'
    })
    .reply(200, {
        status: 'ok'
    });

mockApi
    .post('/1/statbox/?consumer=passport', {
        action: 'csrf',
        mode: 'logout',
        url: '/passport?mode=logout&yu=AAAAAA'
    })
    .reply(200, {
        status: 'ok'
    });

mockApi
    .post(bundleSessionURL, {
        track_id: b.trackID
    })
    .reply(200, {
        status: 'ok',
        track_id: b.trackID,
        cookies: [
            'Session_id="2:session"; Domain=.yandex.ru; expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/; HttpOnly',
            'sessionid2="2:sslsession"; Domain=.yandex.ru; expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/; secure; HttpOnly'
        ],
        account: {
            uid: 123456,
            person: {
                firstname: 'vasya',
                lastname: 'pupkin',
                display_name: {
                    name: 'vasya@okna.ru'
                },
                language: 'ru',
                gender: 'm',
                birthday: '1986-01-01'
            }
        }
    });

mockApi.post(submitURL, s.validLoginData).reply(200, {
    status: 'ok',
    track_id: b.trackID,
    cookies: [
        'Session_id="2:session"; Domain=.yandex.ru; expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/; HttpOnly',
        'sessionid2="2:sslsession"; Domain=.yandex.ru; expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/; secure; HttpOnly'
    ],
    account: {
        uid: 123456,
        person: {
            firstname: 'vasya',
            lastname: 'pupkin',
            display_name: {
                name: 'vasya@okna.ru'
            },
            language: 'ru',
            gender: 'm',
            birthday: '1986-01-01'
        }
    }
});

mockApi.post(submitURL, s.validLoginDataSessional).reply(200, {
    status: 'ok',
    track_id: b.trackID,
    cookies: [
        'Session_id="2:session"; Domain=.yandex.ru; expires=Tue, 19 Jan 2014 03:14:07 GMT; Path=/; HttpOnly',
        'sessionid2="2:sslsession"; Domain=.yandex.ru; expires=Tue, 19 Jan 2014 03:14:07 GMT; Path=/; secure; HttpOnly'
    ],
    account: {
        uid: 123456,
        person: {
            firstname: 'vasya',
            lastname: 'pupkin',
            display_name: {
                name: 'vasya@okna.ru'
            },
            language: 'ru',
            gender: 'm',
            birthday: '1986-01-01'
        }
    }
});

mockApi.post(submitURL, s.validLoginDataWithTrack).reply(200, {
    status: 'ok',
    track_id: b.trackID,
    cookies: [
        'Session_id="2:session"; Domain=.yandex.ru; expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/; HttpOnly',
        'sessionid2="2:sslsession"; Domain=.yandex.ru; expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/; secure; HttpOnly'
    ],
    account: {
        uid: 123456,
        person: {
            firstname: 'vasya',
            lastname: 'pupkin',
            display_name: {
                name: 'vasya@okna.ru'
            },
            language: 'ru',
            gender: 'm',
            birthday: '1986-01-01'
        }
    }
});

mockApi.post(submitURL, s.validLoginDataSessionalWithTrack).reply(200, {
    status: 'ok',
    track_id: b.trackID,
    cookies: [
        'Session_id="2:session"; Domain=.yandex.ru; expires=Tue, 19 Jan 2014 03:14:07 GMT; Path=/; HttpOnly',
        'sessionid2="2:sslsession"; Domain=.yandex.ru; expires=Tue, 19 Jan 2014 03:14:07 GMT; Path=/; secure; HttpOnly'
    ],
    account: {
        uid: 123456,
        person: {
            firstname: 'vasya',
            lastname: 'pupkin',
            display_name: {
                name: 'vasya@okna.ru'
            },
            language: 'ru',
            gender: 'm',
            birthday: '1986-01-01'
        }
    }
});

mockApi.post(submitURL, s.validPddLoginDataAlt).reply(200, {
    status: 'ok',
    track_id: b.trackID,
    cookies: [
        'Eda_id="2:session"; Domain=.yandex.ru; expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/for/okna.ru; HttpOnly'
    ],
    account: {
        uid: 123456,
        person: {
            firstname: 'vasya',
            lastname: 'pupkin',
            display_name: {
                name: 'vasya@okna.ru'
            },
            language: 'ru',
            gender: 'm',
            birthday: '1986-01-01'
        },
        domain: {
            unicode: 'okna.ru'
        }
    }
});

mockApi.post(submitURL, s.validPddLoginDataSessionalAlt).reply(200, {
    status: 'ok',
    track_id: b.trackID,
    cookies: [
        'Eda_id="2:session"; Domain=.yandex.ru; expires=Tue, 19 Jan 2014 03:14:07 GMT; Path=/for/okna.ru; HttpOnly'
    ],
    account: {
        uid: 123456,
        person: {
            firstname: 'vasya',
            lastname: 'pupkin',
            display_name: {
                name: 'vasya@okna.ru'
            },
            language: 'ru',
            gender: 'm',
            birthday: '1986-01-01'
        },
        domain: {
            unicode: 'okna.ru'
        }
    }
});
mockApi.post(submitURL, s.validPddLoginData).reply(200, {
    status: 'ok',
    track_id: b.trackID,
    cookies: [
        'Eda_id="2:session"; Domain=.yandex.ru; expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/for/okna.ru; HttpOnly'
    ],
    account: {
        uid: 123456,
        person: {
            firstname: 'vasya',
            lastname: 'pupkin',
            display_name: {
                name: 'vasya@okna.ru'
            },
            language: 'ru',
            gender: 'm',
            birthday: '1986-01-01'
        },
        domain: {
            unicode: 'okna.ru'
        }
    }
});

mockApi.post(submitURL, s.validPddLoginDataSessional).reply(200, {
    status: 'ok',
    track_id: b.trackID,
    cookies: [
        'Eda_id="2:session"; Domain=.yandex.ru; expires=Tue, 19 Jan 2014 03:14:07 GMT; Path=/for/okna.ru; HttpOnly'
    ],
    account: {
        uid: 123456,
        person: {
            firstname: 'vasya',
            lastname: 'pupkin',
            display_name: {
                name: 'vasya@okna.ru'
            },
            language: 'ru',
            gender: 'm',
            birthday: '1986-01-01'
        },
        domain: {
            unicode: 'okna.ru'
        }
    }
});

noPolicy
    .post(submitURL, {
        login: b.needCompleteLogin,
        password: b.goodPass,
        retpath: b.retpathUrl
    })
    .reply(200, {
        status: 'ok',
        track_id: b.trackID,
        account: {
            uid: 123456,
            person: {
                firstname: 'vasya',
                lastname: 'pupkin',
                display_name: {
                    name: 'vasya@okna.ru'
                },
                language: 'ru',
                gender: 'm',
                birthday: '1986-01-01'
            }
        },
        state: 'complete_autoregistered'
    });

mockApi
    .post('/1/bundle/auth/password/get_state/?consumer=passport', {
        track_id: b.trackID
    })
    .reply(200, {
        status: 'ok',
        track_id: b.trackID,
        account: {
            uid: 123456,
            person: {
                firstname: 'vasya',
                lastname: 'pupkin',
                display_name: {
                    name: 'vasya@okna.ru'
                },
                language: 'ru',
                gender: 'm',
                birthday: '1986-01-01'
            }
        },
        state: 'complete_autoregistered'
    });

mockApi
    .post('/1/bundle/auth/password/get_state/?consumer=passport', {
        track_id: b.badTrackID
    })
    .reply(200, {
        status: 'error',
        errors: ['track.not_found']
    });

noPolicy
    .post(submitURL, {
        login: b.needChangePassLogin,
        password: b.goodPass,
        retpath: b.retpathUrl
    })
    .reply(200, {
        status: 'ok',
        track_id: b.trackID,
        account: {
            uid: 123456,
            person: {
                firstname: 'vasya',
                lastname: 'pupkin',
                display_name: {
                    name: 'vasya@okna.ru'
                },
                language: 'ru',
                gender: 'm',
                birthday: '1986-01-01'
            }
        },
        state: 'change_password',
        change_password_reason: 'password_expired',
        validation_method: 'captcha'
    });

noPolicy.post(submitURL, s.wrongPassword).reply(200, {
    status: 'error',
    track_id: b.trackID,
    errors: ['password.not_matched']
});

noPolicy.post(submitURL, s.emptyPassword).reply(200, {
    status: 'error',
    track_id: b.trackID,
    errors: ['password.empty']
});

noPolicy.post(submitURL, s.noPassword).reply(200, {
    status: 'error',
    track_id: b.trackID,
    errors: ['password.empty']
});

noPolicy.post(submitURL, s.emptyLogin).reply(200, {
    status: 'error',
    track_id: b.trackID,
    errors: ['login.empty']
});

noPolicy.post(submitURL, s.noLogin).reply(200, {
    status: 'error',
    track_id: b.trackID,
    errors: ['login.empty']
});

noPolicy.post(submitURL, s.inValidLoginData).reply(200, {
    status: 'error',
    track_id: b.trackID,
    errors: ['account.not_found']
});

noPolicy
    .post(submitURL, {
        login: b.needCaptchaLogin,
        password: b.goodPass,
        retpath: b.retpathUrl
    })
    .reply(200, {
        status: 'error',
        track_id: b.trackID,
        errors: ['captcha.required']
    });

mockApi.post('/1/captcha/generate/?consumer=passport').reply(200, {
    status: 'ok',
    image_url: 'http://u.captcha.yandex.net/image?key=40PGN6nHC5B2FLw9tP90tfR0PIRAVnwA',
    key: '40PGN6nHC5B2FLw9tP90tfR0PIRAVnwA'
});

mockApi.post('/1/captcha/generate/?consumer=passport', {voice: true}).reply(200, {
    status: 'ok',
    voice: {
        url: 'http://u.captcha.yandex.net/voice?key=40PGN6nHC5B2FLw9tP90tfR0PIRAVnwA',
        intro_url: 'http://u.captcha.yandex.net/static/intro-ru.wav'
    },
    image_url: 'http://u.captcha.yandex.net/image?key=40PGN6nHC5B2FLw9tP90tfR0PIRAVnwA',
    key: '40PGN6nHC5B2FLw9tP90tfR0PIRAVnwA'
});

mockApi.post('/1/bundle/account/register/limits/?consumer=passport').reply(200, {
    status: 'ok',
    sms_remained_count: 1,
    confirmation_remained_count: 4
});

mockApi.post('/1/track/?consumer=passport').reply(200, {
    id: b.trackID,
    status: 'ok'
});

mockApi.get(`/1/track/${b.trackID}/?consumer=passport`).reply(200, {
    id: b.trackID,
    status: 'ok'
});

mockApi.delete(`/1/track/${b.trackID}/?consumer=passport`).reply(200, {
    status: 'ok'
});

mockApi
    .post('/1/session/check/?consumer=passport', {
        track_id: b.trackID,
        session: '2:session'
    })
    .reply(200, {
        status: 'ok',
        session_is_correct: true,
        retpath: b.retpathUrl
    });

mockApi.post('/1/suggest/language/?consumer=passport').reply(200, {
    status: 'ok',
    language: 'ru'
});

mockApi
    .post('/1/captcha/check/?consumer=passport', {
        answer: b.goodCaptcha,
        display_language: 'ru',
        track_id: b.trackID
    })
    .reply(200, {
        status: 'ok',
        correct: true
    });

mockApi
    .post('/1/captcha/check/?consumer=passport', {
        answer: b.badCaptcha,
        display_language: 'ru',
        track_id: b.trackID
    })
    .reply(200, {
        status: 'ok',
        correct: false
    });

mockApi
    .post('/1/questions/?consumer=passport', {
        display_language: 'ru',
        track_id: b.trackID
    })
    .reply(200, {
        status: 'ok',
        questions: [
            {
                id: 0,
                value: 'не выбран'
            },
            {
                id: 1,
                value: 'Девичья фамилия матери'
            },
            {
                id: 2,
                value: 'Любимое блюдо'
            },
            {
                id: 3,
                value: 'Почтовый индекс родителей'
            },
            {
                id: 4,
                value: 'Дата рождения бабушки'
            },
            {
                id: 5,
                value: 'Ваше прозвище в школе'
            },
            {
                id: 6,
                value: 'Номер паспорта'
            },
            {
                id: 7,
                value: 'Пять последних цифр кред. карты'
            },
            {
                id: 8,
                value: 'Пять последних цифр ИНН'
            },
            {
                id: 9,
                value: 'Ваш любимый номер телефона'
            },
            {
                id: 99,
                value: 'Задайте собственный вопрос'
            }
        ]
    });

mockApi
    .post('/1/validation/retpath/?consumer=passport', {
        retpath: b.retpathUrl
    })
    .reply(200, {
        status: 'ok',
        retpath: b.retpathUrl
    });
