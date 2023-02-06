import {EnvType} from '../utils/types/common';

const ENV: EnvType = process.env.ENV as EnvType || 'testing';
const {
    /*
    * the project has several dynamic urls
    * it creates after open pull request
    * custom stand will generate custom host
    * */
    CUSTOM_HOST,
    WFM_PASSWORD,
    WFM_USERNAME,
} = process.env;

const TESTING_PASSPORT_URL = 'https://passport-test.yandex.ru';
const PASSPORT_URLS = {
    testing: TESTING_PASSPORT_URL,
};

const APP_URLS: Record<EnvType, string> = {
    testing: 'https://wfm.taxi.tst.yandex.ru',
    unstable: 'https://wfm.taxi.dev.yandex.ru',
    unstable_01: 'https://wfm-frontend-unstable-01.taxi.dev.yandex.ru',
    unstable_02: 'https://wfm-frontend-unstable-02.taxi.dev.yandex.ru',
    unstable_03: 'https://wfm-frontend-unstable-03.taxi.dev.yandex.ru',
    unstable_04: 'https://wfm-frontend-unstable-04.taxi.dev.yandex.ru',
};

export const AUTH_CONFIG = {
    PASSPORT: {
        URL: PASSPORT_URLS[ENV],
        WELCOME_PATH: '/auth/welcome',
        PROFILE_PATH: '/profile',
    },
    APP_URL: CUSTOM_HOST || APP_URLS[ENV] || '',
    CREDENTIALS: {
        USERNAME: WFM_USERNAME || 'bambuk',
        PASSWORD: WFM_PASSWORD || 'pustoy',
    },
    AQUA_ACCESS: {
        login: 'taxi-wfm-user@taxi.auto.connect-test.tk',
        secretId: 'sec-01g3nenm3nqdz31xtygqzzqhdj',
        passportHost: 'passport-test.yandex.ru',
    },
};
