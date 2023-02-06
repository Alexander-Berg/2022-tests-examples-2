const request = require('supertest');
const cookieParser = require('cookie-parser');
const tld = require('@yandex-int/express-tld');
const express = require('express');
const {RedirectError} = require('_common/server/errors');
// eslint-disable-next-line no-unused-vars
const logger = require('_common/server/utils/logger');
const langdetect = require('../langdetect');

const MOCK_BUNKER = require('./langdetect.bunker.mock');
const MOCK_BUNKER_WITH_DOMAIN = require('./langdetectWithDomain.bunker.mock.json');

jest.mock('_common/server/utils/logger');

describe('locale middleware', () => {
    it('Должен кинуть исключение если бункера нет', () => {
        const app = createApp();

        return request(app)
            .get('/')
            .expect(500);
    });

    it('Должен кинуть исключение если не определена дефолтная страна', () => {
        const app = createApp({
            bunker: {
                countries: {
                    ...MOCK_BUNKER.countries,
                    defaultCountry: undefined
                }
            }
        });

        return request(app)
            .get('/')
            .expect(500);
    });

    it('Должен кинуть исключение если дефолтной страны нет в списке доступных', () => {
        const app = createApp({
            bunker: {
                countries: {
                    ...MOCK_BUNKER.countries,
                    defaultCountry: 'NO'
                }
            }
        });

        return request(app)
            .get('/')
            .expect(500);
    });

    it('После определения выставилась кука', () => {
        const app = createApp({
            bunker: MOCK_BUNKER,
            countryCode: ''
        });

        return request(app)
            .get('/')
            .set('accept-language', 'no')
            .expect(200, {
                isDefault: true,
                country: 'int',
                id: MOCK_BUNKER.countries.int.defaultLang,
                locale: 'en_int'
            })
            .expect(res => {
                const setCookie = res.headers['set-cookie'];

                if (!setCookie || !setCookie[0].includes('_LOCALE_')) {
                    throw new Error('cookie not set');
                }
            });
    });

    describe('Без явного запроса страны/локали', () => {
        it('Если мы не знаем страну пользователя и язык не поддерживается - выставляем дефолт', () => {
            const app = createApp({
                bunker: MOCK_BUNKER,
                countryCode: ''
            });

            return request(app)
                .get('/')
                .set('accept-language', 'no')
                .expect(200, {
                    isDefault: true,
                    country: 'int',
                    id: MOCK_BUNKER.countries.int.defaultLang,
                    locale: 'en_int'
                });
        });

        it('Если знаем страну пользователя и она поддерживается - выставляем eё', () => {
            const app = createApp({
                bunker: MOCK_BUNKER,
                countryCode: 'fi'
            });

            return request(app)
                .get('/')
                .set('accept-language', 'no')
                .expect(200, {
                    isDefault: false,
                    country: 'fi',
                    id: MOCK_BUNKER.countries.fi.defaultLang,
                    locale: 'en_fi'
                });
        });

        it('Если знаем страну пользователя и язык и они поддерживаются - выставляем их', () => {
            const app = createApp({
                bunker: MOCK_BUNKER,
                countryCode: 'fi'
            });

            return request(app)
                .get('/')
                .set('accept-language', 'fi')
                .expect(200, {
                    isDefault: false,
                    country: 'fi',
                    id: 'fi',
                    locale: 'fi_fi'
                });
        });

        it('Если знаем страну пользователя и язык задан через ?lang и они поддерживаются - выставляем их', () => {
            const app = createApp({
                bunker: MOCK_BUNKER,
                countryCode: 'fi'
            });

            return request(app)
                .get('/?lang=en')
                .set('accept-language', 'fi')
                .expect(200, {
                    isDefault: false,
                    country: 'fi',
                    id: 'en',
                    locale: 'en_fi'
                });
        });

        it('Если не знаем страну пользователя, но язык поддерживается - выставляем дефолт с языком юзера', () => {
            const app = createApp({
                bunker: MOCK_BUNKER,
                countryCode: ''
            });

            return request(app)
                .get('/')
                .set('accept-language', 'fi')
                .expect(200, {
                    isDefault: false,
                    country: 'int',
                    id: 'fi',
                    locale: 'fi_int'
                });
        });

        it('Если знаем страну пользователя, она не поддерживается - притягиваем ближайшую', () => {
            const app = createApp({
                bunker: MOCK_BUNKER,
                countryCode: 'ge',
                userCoords: {
                    lat: 8,
                    lon: -5
                }
            });

            return request(app)
                .get('/')
                .expect(200, {
                    isDefault: false,
                    country: 'ci',
                    id: 'en',
                    locale: 'en_ci'
                });
        });

        it('Если знаем страну пользователя, она не поддерживается. Ближайшая страна дальше pullRestriction - игнорируем', () => {
            const app = createApp({
                bunker: {
                    countries: {
                        ...MOCK_BUNKER.countries,
                        pullRestriction: 10
                    }
                },
                countryCode: 'ge',
                userCoords: {
                    lat: 10,
                    lon: 10
                }
            });

            return request(app)
                .get('/')
                .expect(200, {
                    isDefault: true,
                    country: 'int',
                    id: 'en',
                    locale: 'en_int'
                });
        });
    });

    describe('С явным указанием в запросе страны/локали', () => {
        it('Если запросили несуществующую страну - 404', () => {
            const app = createApp({
                bunker: MOCK_BUNKER,
                countryCode: 'fi'
            });

            return request(app)
                .get('/ru_ts')
                .set('accept-language', 'en')
                .expect(404);
        });

        it('Если в запросе есть страна и язык - отдаём их', () => {
            const app = createApp({
                bunker: MOCK_BUNKER,
                countryCode: 'NO'
            });

            return request(app)
                .get('/fr_fi')
                .set('accept-language', 'no')
                .expect(200, {
                    isDefault: false,
                    country: 'fi',
                    id: 'fr',
                    locale: 'fr_fi'
                });
        });

        it('Если в запросе есть страна, но язык не поддержживается - отдаём дефолт для страны', () => {
            const app = createApp({
                bunker: MOCK_BUNKER,
                countryCode: 'NO'
            });

            return request(app)
                .get('/tt_fi')
                .set('accept-language', 'no')
                .expect(200, {
                    isDefault: false,
                    country: 'fi',
                    id: 'en',
                    locale: 'en_fi'
                });
        });

        it('Если в запросе есть страна, но язык не поддержживается, при этом есть язык пользователя - отдаём язык пользователя для страны', () => {
            const app = createApp({
                bunker: MOCK_BUNKER,
                countryCode: 'NO'
            });

            return request(app)
                .get('/tt_fi')
                .set('accept-language', 'he')
                .expect(200, {
                    isDefault: false,
                    country: 'fi',
                    id: 'he',
                    locale: 'he_fi'
                });
        });
    });

    describe('Редиректы', () => {
        it('Если в запросе нет страны и страна пользователя поддерживается, языка нет - редирект на страну', () => {
            const app = createApp(
                {
                    bunker: MOCK_BUNKER,
                    countryCode: 'fi'
                },
                {withRedirect: true}
            );

            return request(app)
                .get('/')
                .set('accept-language', 'no')
                .expect(302)
                .expect(res => {
                    if (res.headers.location !== 'https://127.0.0.1/en_fi/') {
                        throw new Error(`wrong redirect, expect https://127.0.0.1/en_fi/ but got ${res.headers.location}`);
                    }
                });
        });

        it('Если в запросе нет страны и страна пользователя поддерживается, язык есть - редирект на страну', () => {
            const app = createApp(
                {
                    bunker: MOCK_BUNKER,
                    countryCode: 'fi'
                },
                {withRedirect: true}
            );

            return request(app)
                .get('/')
                .set('accept-language', 'fr')
                .expect(302)
                .expect(res => {
                    if (res.headers.location !== 'https://127.0.0.1/fr_fi/') {
                        throw new Error(`wrong redirect, expect https://127.0.0.1/fr_fi/ but got ${res.headers.location}`);
                    }
                });
        });

        it('Если в запросе нет страны и страна пользователя не поддерживается, язык отличается от дефолта - редирект на страну', () => {
            const app = createApp(
                {
                    bunker: MOCK_BUNKER,
                    countryCode: 'NO'
                },
                {withRedirect: true}
            );

            return request(app)
                .get('/')
                .set('accept-language', 'fr')
                .expect(302)
                .expect(res => {
                    if (res.headers.location !== 'https://127.0.0.1/fr_int/') {
                        throw new Error(`wrong redirect, expect https://127.0.0.1/fr_int/ but got ${res.headers.location}`);
                    }
                });
        });

        it('Если в запросе нет страны и страна пользователя не поддерживается, язык совпадает с дефолтом - редирект нет', () => {
            const app = createApp(
                {
                    bunker: MOCK_BUNKER,
                    countryCode: 'NO'
                },
                {withRedirect: true}
            );

            return request(app)
                .get('/')
                .set('accept-language', 'en')
                .expect(200);
        });

        it('Если в запросе нет страны и страна пользователя не поддерживается, язык не определён - редиректа нет', () => {
            const app = createApp(
                {
                    bunker: MOCK_BUNKER,
                    countryCode: 'NO'
                },
                {withRedirect: true}
            );

            return request(app)
                .get('/')
                .set('accept-language', 'no')
                .expect(200);
        });

        it('Если в запросе есть страна и язык - редиректа нет', () => {
            const app = createApp(
                {
                    bunker: MOCK_BUNKER,
                    countryCode: 'NO'
                },
                {withRedirect: true}
            );

            return request(app)
                .get('/fr_fi')
                .set('accept-language', 'no')
                .expect(200);
        });

        it('Если в запросе есть страна и язык, они дефолтные - редиректа нет', () => {
            const app = createApp(
                {
                    bunker: MOCK_BUNKER,
                    countryCode: 'NO'
                },
                {withRedirect: true}
            );

            return request(app)
                .get('/en_int')
                .set('accept-language', 'no')
                .expect(200);
        });

        it('Если в запросе есть страница - редирект на неё', () => {
            const app = createApp(
                {
                    bunker: MOCK_BUNKER,
                    countryCode: 'fi'
                },
                {withRedirect: true}
            );

            return request(app)
                .get('/index')
                .set('accept-language', 'fr')
                .expect(302)
                .expect(res => {
                    if (res.headers.location !== 'https://127.0.0.1/fr_fi/index/') {
                        throw new Error(`wrong redirect, expect https://127.0.0.1/fr_fi/index/ but got ${res.headers.location}`);
                    }
                });
        });

        it('Если в запросе есть страница, которой нет в таргете - редирект на неё + лог', () => {
            const app = createApp(
                {
                    bunker: MOCK_BUNKER,
                    countryCode: 'fi'
                },
                {withRedirect: true}
            );

            return request(app)
                .get('/nopage')
                .set('accept-language', 'fr')
                .expect(302)
                .expect(res => {
                    if (res.headers.location !== 'https://127.0.0.1/fr_fi/nopage/') {
                        throw new Error(`wrong redirect, expect https://127.0.0.1/fr_fi/nopage/ but got ${res.headers.location}`);
                    }
                });
        });
    });

    describe('Значение из куки', () => {
        const app = createApp(
            {
                bunker: MOCK_BUNKER,
                countryCode: 'no'
            },
            {withRedirect: true}
        );

        it('Если есть кука locale и она не дефолт - редирект', () => {
            return request(app)
                .get('/')
                .set('accept-language', 'no')
                .set('Cookie', ['_LOCALE_=fr_fi'])
                .expect(302)
                .expect(res => {
                    if (res.headers.location !== 'https://127.0.0.1/fr_fi/') {
                        throw new Error(`wrong redirect, expect https://127.0.0.1/fr_fi/ but got ${res.headers.location}`);
                    }
                });
        });

        it('Если есть кука locale и язык не дефолт - редирект', () => {
            return request(app)
                .get('/')
                .set('accept-language', 'no')
                .set('Cookie', ['_LOCALE_=fr_int'])
                .expect(302)
                .expect(res => {
                    if (res.headers.location !== 'https://127.0.0.1/fr_int/') {
                        throw new Error(`wrong redirect, expect https://127.0.0.1/fr_int/ but got ${res.headers.location}`);
                    }
                });
        });

        it('Если есть кука local и она дефолт - нет редиректа', () => {
            return request(app)
                .get('/')
                .set('accept-language', 'no')
                .set('Cookie', ['_LOCALE_=en_int'])
                .expect(200);
        });
    });

    describe('Настройки автодетекта', () => {
        it('Автодетект выключен', () => {
            const app = createApp({
                bunker: {
                    countries: {
                        ...MOCK_BUNKER.countries,
                        userAutodetect: false,
                        fixedRegion: 'fr_fi'
                    }
                },
                countryCode: ''
            });

            return request(app)
                .get('/')
                .set('accept-language', 'en')
                .expect(200, {
                    isDefault: false,
                    country: 'fi',
                    id: 'fr',
                    locale: 'fr_fi'
                });
        });

        it('Дефолтная страна', () => {
            const app = createApp({
                bunker: {
                    countries: {
                        ...MOCK_BUNKER.countries,
                        defaultCountry: 'fi'
                    }
                },
                countryCode: ''
            });

            return request(app)
                .get('/')
                .set('accept-language', 'en')
                .expect(200, {
                    isDefault: true,
                    country: 'fi',
                    id: 'en',
                    locale: 'en_fi'
                });
        });
    });

    describe('Определение с учетом домена', () => {
        it('Если запросили страну которая есть в списке, но недоступна на доменах - 404', () => {
            const app = createApp({
                bunker: MOCK_BUNKER_WITH_DOMAIN,
                countryCode: 'UA'
            });

            return request(app)
                .get('/ru_no')
                .set('accept-language', 'ru')
                .expect(404);
        });

        it('Страна пользователя есть на домене и язык дефолтный - выставляем их', () => {
            const app = createApp(
                {
                    bunker: MOCK_BUNKER_WITH_DOMAIN,
                    countryCode: 'KZ'
                },
                {withRedirect: true}
            );

            return request(app)
                .get('/')
                .set('accept-language', 'kk')
                .set('host', 'taxi.yandex.kz')
                .expect(200, {
                    isDefault: true,
                    country: 'kz',
                    id: 'kk',
                    locale: 'kk_kz'
                });
        });

        it('Страны пользователя нет на домене и отключен редирект на домены - выставляем дефолт для домена', () => {
            const app = createApp({
                bunker: MOCK_BUNKER_WITH_DOMAIN,
                countryCode: 'NO'
            });

            return request(app)
                .get('/')
                .set('accept-language', 'ru')
                .set('host', 'taxi.yandex.ru')
                .expect(200, {
                    isDefault: true,
                    country: 'ru',
                    id: 'ru',
                    locale: 'ru_ru'
                });
        });

        it('Страна пользователя есть на домене, язык не дефолт - редиректим с указанием локали', () => {
            const app = createApp(
                {
                    bunker: MOCK_BUNKER_WITH_DOMAIN,
                    countryCode: 'KZ'
                },
                {withRedirect: true}
            );

            return request(app)
                .get('/')
                .set('accept-language', 'ru')
                .set('host', 'taxi.yandex.kz')
                .expect(302)
                .expect(res => {
                    if (res.headers.location !== 'https://taxi.yandex.kz/ru_kz/') {
                        throw new Error(`wrong redirect, expect https://taxi.yandex.kz/ru_kz/ but got ${res.headers.location}`);
                    }
                });
        });

        it('Страна пользователя есть на домене, язык не поддерживается - выставляем дефолтный язык для страны', () => {
            const app = createApp(
                {
                    bunker: MOCK_BUNKER_WITH_DOMAIN,
                    countryCode: 'KZ'
                },
                {withRedirect: true}
            );

            return request(app)
                .get('/')
                .set('accept-language', 'no')
                .set('host', 'taxi.yandex.kz')
                .expect(200, {
                    isDefault: true,
                    country: 'kz',
                    id: 'kk',
                    locale: 'kk_kz'
                });
        });

        it('Страна не поддерживается на домене и включен редирект по доменам - редиректим на домен страны', () => {
            const app = createApp(
                {
                    bunker: {
                        ...MOCK_BUNKER_WITH_DOMAIN,
                        countries: {
                            ...MOCK_BUNKER_WITH_DOMAIN.countries,
                            enableRedirectToUserDomain: true
                        }
                    },
                    countryCode: 'RU'
                },
                {withRedirect: true}
            );

            return request(app)
                .get('/')
                .set('accept-language', 'ru')
                .set('host', 'taxi.yandex.kz')
                .expect(302)
                .expect(res => {
                    if (res.headers.location !== 'https://taxi.yandex.ru/') {
                        throw new Error(`wrong redirect, expect https://taxi.yandex.ru/ but got ${res.headers.location}`);
                    }
                });
        });

        it('Страна не подерживается сервисом и включен редирект по доменам - редиректим на дефолтный домен и страну', () => {
            const app = createApp(
                {
                    bunker: {
                        ...MOCK_BUNKER_WITH_DOMAIN,
                        countries: {
                            ...MOCK_BUNKER_WITH_DOMAIN.countries,
                            enableRedirectToUserDomain: true
                        }
                    },
                    countryCode: 'NO'
                },
                {withRedirect: true}
            );

            return request(app)
                .get('/')
                .set('accept-language', 'en')
                .set('host', 'taxi.yandex.com')
                .expect(302)
                .expect(res => {
                    if (res.headers.location !== 'https://taxi.yandex.ru/') {
                        throw new Error(`wrong redirect, expect https://taxi.yandex.ru/ but got ${res.headers.location}`);
                    }
                });
        });

        it('Страна есть на домене, но не дефолтная - редиректим на префикс', () => {
            const app = createApp(
                {
                    bunker: {
                        ...MOCK_BUNKER_WITH_DOMAIN,
                        countries: {
                            ...MOCK_BUNKER_WITH_DOMAIN.countries,
                            enableRedirectToUserDomain: true
                        }
                    },
                    countryCode: 'US'
                },
                {withRedirect: true}
            );

            return request(app)
                .get('/')
                .set('accept-language', 'en')
                .set('host', 'taxi.yandex.com')
                .expect(302)
                .expect(res => {
                    if (res.headers.location !== 'https://taxi.yandex.com/en_us/') {
                        throw new Error(`wrong redirect, expect https://taxi.yandex.com/en_us/ but got ${res.headers.location}`);
                    }
                });
        });

        it('Страна есть на домене, но язык не дефолтный - редиректим на префикс', () => {
            const app = createApp(
                {
                    bunker: {
                        ...MOCK_BUNKER_WITH_DOMAIN,
                        countries: {
                            ...MOCK_BUNKER_WITH_DOMAIN.countries,
                            enableRedirectToUserDomain: true
                        }
                    },
                    countryCode: 'AM'
                },
                {withRedirect: true}
            );

            return request(app)
                .get('/')
                .set('accept-language', 'en')
                .set('host', 'taxi.yandex.com')
                .expect(302)
                .expect(res => {
                    if (res.headers.location !== 'https://taxi.yandex.com/en_am/') {
                        throw new Error(`wrong redirect, expect https://taxi.yandex.com/en_am/ but got ${res.headers.location}`);
                    }
                });
        });

        it('Пользователь явно сменил домен, на котором нет его страны - выставляем дефолт для домена', () => {
            const app = createApp(
                {
                    bunker: {
                        countries: {
                            ...MOCK_BUNKER_WITH_DOMAIN.countries,
                            enableRedirectToUserDomain: true
                        }
                    },
                    countryCode: 'RU'
                },
                {withRedirect: true}
            );

            return request(app)
                .get('/')
                .set('accept-language', 'no')
                .set('host', 'taxi.yandex.kz')
                .set('cookie', '_forcedtld=1')
                .expect(200, {
                    isDefault: true,
                    country: 'kz',
                    id: 'kk',
                    locale: 'kk_kz'
                });
        });

        it('Если есть форс язык/страна на домене - применяем', () => {
            const app = createApp(
                {
                    bunker: {
                        ...MOCK_BUNKER_WITH_DOMAIN,
                        countries: {
                            ...MOCK_BUNKER_WITH_DOMAIN.countries,
                            enableRedirectToUserDomain: true
                        }
                    },
                    countryCode: 'RU'
                },
                {withRedirect: true}
            );

            return request(app)
                .get('/en_us/')
                .set('accept-language', 'en')
                .set('host', 'taxi.yandex.com')
                .expect(200, {
                    isDefault: false,
                    country: 'us',
                    id: 'en',
                    locale: 'en_us'
                });
        });

        it('Если есть форс язык/страна но их нет на домене - редирект', () => {
            const app = createApp(
                {
                    bunker: {
                        ...MOCK_BUNKER_WITH_DOMAIN,
                        countries: {
                            ...MOCK_BUNKER_WITH_DOMAIN.countries,
                            enableRedirectToUserDomain: true
                        }
                    },
                    countryCode: 'RU'
                },
                {withRedirect: true}
            );

            return request(app)
                .get('/ru_ru/')
                .set('accept-language', 'en')
                .set('host', 'taxi.yandex.com')
                .expect(302)
                .expect(res => {
                    if (res.headers.location !== 'https://taxi.yandex.ru/') {
                        throw new Error(`wrong redirect, expect https://taxi.yandex.ru/ but got ${res.headers.location}`);
                    }
                });
        });

        it('Притягиваем на домен - редирект', () => {
            const app = createApp(
                {
                    bunker: {
                        ...MOCK_BUNKER_WITH_DOMAIN,
                        countries: {
                            ...MOCK_BUNKER_WITH_DOMAIN.countries,
                            enableRedirectToUserDomain: true
                        }
                    },
                    countryCode: 'NO',
                    userCoords: {
                        lat: 39.495,
                        lon: -98.989
                    }
                },
                {withRedirect: true}
            );

            return request(app)
                .get('/')
                .set('accept-language', 'en')
                .set('host', 'taxi.yandex.com')
                .expect(302)
                .expect(res => {
                    if (res.headers.location !== 'https://taxi.yandex.com/en_us/') {
                        throw new Error(`wrong redirect, expect https://taxi.yandex.com/en_us/ but got ${res.headers.location}`);
                    }
                });
        });

        it('Редирект на домен с учетом дефолтной страницы', () => {
            const app = createApp(
                {
                    bunker: {
                        countries: {
                            ...MOCK_BUNKER_WITH_DOMAIN.countries,
                            enableRedirectToUserDomain: true,
                            am: {
                                ...MOCK_BUNKER_WITH_DOMAIN.countries.am,
                                defaultUrl: '/order'
                            }
                        }
                    },
                    countryCode: 'AM'
                },
                {withRedirect: true}
            );

            return request(app)
                .get('/')
                .set('accept-language', 'hy')
                .set('host', 'taxi.yandex.kz')
                .expect(302)
                .expect(res => {
                    if (res.headers.location !== 'https://taxi.yandex.com/order/') {
                        throw new Error(`wrong redirect, expect https://taxi.yandex.com/order/ but got ${res.headers.location}`);
                    }
                });
        });
    });

    function createApp(prepareData = {}, options = {}) {
        const app = express();

        app.get(
            ['/:region([a-z]{2}_[a-z]{2,3})/:page?', '/:page?'],
            [
                tld(),
                cookieParser(),
                (req, res, next) => {
                    Object.assign(req, prepareData);
                    next();
                },
                langdetect(Object.assign({bunkerPath: 'countries'}, options))
            ],
            (req, res) => {
                res.status(200).json(req.langdetect);
            }
        );

        // eslint-disable-next-line handle-callback-err
        app.use((err, req, res, next) => {
            if (err instanceof RedirectError) {
                res.status(500).json({url: err.url});
                return;
            }

            if (err.status === 404) {
                res.sendStatus(404);
                return;
            }

            // eslint-disable-next-line no-console
            // console.error(err);
            res.sendStatus(500);
        });

        return app;
    }
});
