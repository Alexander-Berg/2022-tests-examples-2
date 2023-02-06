import * as csp from 'express-csp-header';

import common from './common';
import type { Config } from './types';

const config: Config & typeof common = {
    ...common,
    environment: 'testing',
    chat: {
        env: 'development',
    },
    metrika: {
        id: '30479502',
    },
    backend: {
        ...common.backend,
        url: 'https://ohio-backend-test.so.yandex.net',
    },
    billsBackend: {
        ...common.billsBackend,
        url: 'https://test.bills.pay.yandex.ru',
    },
    payments: {
        ...common.payments,
        url: 'https://payments-test.mail.yandex.net',
    },
    images: {
        ...common.images,
        avatarHost: '//avatars.mdst.yandex.net',
    },
    csp: {
        ...common.csp,
        'img-src': [
            ...common.csp['img-src'],
            'avatars.mdst.yandex.net',
            'https://test.pay.yandex.ru',
        ],
        'connect-src': [
            ...common.csp['connect-src'],
            `https://api.passport-test.yandex.${csp.TLD}`,
            'https://test.pay.yandex.ru',
        ],
        'frame-src': [...common.csp['frame-src'], 'https://test.pay.yandex.ru'],
        'script-src': [...common.csp['script-src'], 'https://test.pay.yandex.ru'],
    },
    yandexPay: {
        scriptSrc: 'https://test.pay.yandex.ru/sdk/v1/pay.js',
        merchantId: '18b3b6ac-6d17-41ff-ad6a-cbed3775c3e3',
        merchantName: 'passport-bills',
        gateway: 'yandex-trust',
        gatewayId: 'oplatagosuslug',
        env: 'TESTING',
    },
};

export default config;
