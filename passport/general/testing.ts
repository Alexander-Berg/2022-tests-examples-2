import common from './common';

import type { Config } from './types';

const config: Config = {
    ...common,
    environment: 'testing',
    metrika: {
        id: '69331741',
    },
    blackbox: {
        host: 'blackbox-test.yandex.net',
    },
    passport: {
        baseUrl: 'https://passport-test.yandex.ru',
    },
    passportAPI: {
        ...common.passportAPI,
        baseUrl: 'http://127.0.0.1:6000',
        host: 'passport-test-internal.yandex.ru',
    },
    socialAPI: {
        ...common.socialAPI,
        baseUrl: 'https://api.social-test.yandex.ru',
        frontendUrl: 'https://social-test.yandex.ru',
        host: 'api.social-test.yandex.ru',
    },
    documentsAPI: {
        ...common.documentsAPI,
        baseUrl: 'https://documents-test.pers.yandex.net',
        host: 'documents-test.pers.yandex.net',
    },
    avatar: {
        ...common.avatar,
        url: common.avatar.url.replace('mds', 'mdst'),
    },
    cloud: {
        ...common.cloud,
        baseUrl: 'https://cloud-api.dst.yandex.net:8443',
    },
    geo: {
        ...common.geo,
        baseUrl: 'http://addrs-testing.search.yandex.net/search/stable',
    },
    csp: {
        ...common.csp,
        'img-src': (common.csp as ANY)['img-src'].map((rule: string) => rule.replace('mds', 'mdst')),
    },
    oauthUrl: 'https://oauth-test.yandex.ru',
};

export default config;
