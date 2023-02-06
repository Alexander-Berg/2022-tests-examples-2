import {EnvType} from '../utils/types/common';

const ENV: EnvType = process.env.ENV as EnvType || 'unstable';
const {
    /*
    * the project has several dynamic urls
    * it creates after open pull request
    * custom stand will generate custom host
    * */
    CUSTOM_HOST,
    PASSWORD,
    USERNAME,
} = process.env;

const TESTING_PASSPORT_URL = 'https://passport-test.yandex.ru';
const PASSPORT_URLS = {
    testing: TESTING_PASSPORT_URL,
};

const APP_URLS: Record<EnvType, string> = {
    testing: 'https://atlas.taxi.tst.yandex-team.ru',
    unstable: 'https://atlas-unstable.taxi.tst.yandex-team.ru',
};


export const AUTH_CONFIG = {
    PASSPORT: {
        URL: PASSPORT_URLS[ENV],
        WELCOME_PATH: '/auth/welcome',
        PROFILE_PATH: '/profile',
    },
    APP_URL: CUSTOM_HOST || APP_URLS[ENV] || '',
    CREDENTIALS: {
        USERNAME: USERNAME || 'bambuk',
        PASSWORD: PASSWORD || 'pustoy',
    },
    AQUA_ACCESS: {
        login: 'robot-crm-tester@yandex-team.ru',
        secretId: 'sec-01f8fhb9z1jpag1erx7wngq9g5',
        passportHost: 'passport.yandex-team.ru',
    },
};
