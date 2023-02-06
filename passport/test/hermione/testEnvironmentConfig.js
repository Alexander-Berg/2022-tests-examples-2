const DEV_PORT = process.env.PORT || process.env.npm_package_config_port || 3000;

const PASSPORT_GUARD_HOSTS = {
    dev: `passportdev.yandex.${process.env.TEST_TLD}`,
    test: `passport-test.yandex.${process.env.TEST_TLD}`,
    rc: `passport-rc.yandex.${process.env.TEST_TLD}`,
    prod: `passport.yandex.${process.env.TEST_TLD}`
};

const PASSPORT_FRONTEND_HOSTS = {
    dev: `https://${DEV_PORT}.passportdev.yandex.${process.env.TEST_TLD}`,
    test: `https://passport-test.yandex.${process.env.TEST_TLD}`,
    rc: `https://passport-rc.yandex.${process.env.TEST_TLD}`,
    prod: `https://passport.yandex.${process.env.TEST_TLD}`,
    'team-test': 'not_implemented',
    team: 'not_implemented'
};

const PASSPORT_INTERNAL_HOSTS = {
    dev: 'https://0-internal.passportdev.yandex.ru',
    test: 'https://passport-test-internal.yandex.ru',
    rc: 'https://passport-rc-internal.yandex.ru',
    prod: 'https://passport-internal.yandex.ru',
    'team-test': 'not_implemented',
    team: 'not_implemented'
};

const BLACKBOX_HOSTS = {
    dev: 'https://pass-test.yandex.ru/blackbox/',
    test: 'https://pass-test.yandex.ru/blackbox/',
    rc: 'https://blackbox-mimino.yandex.net/blackbox/',
    prod: 'https://blackbox-mimino.yandex.net/blackbox/',
    'team-test': 'not_implemented',
    team: 'not_implemented'
};

const TUS_ENVS = {
    dev: 'test',
    test: 'test',
    rc: 'prod',
    prod: 'prod',
    'team-test': 'team-test',
    team: 'team'
};

function isProd() {
    return process.env.TEST_ENV === 'prod';
}
function isRc() {
    return process.env.TEST_ENV === 'rc';
}

function getPassportFrontendHost() {
    return PASSPORT_FRONTEND_HOSTS[process.env.HOST_ENV || process.env.TEST_ENV];
}

function getPassportFrontendDomain() {
    return PASSPORT_GUARD_HOSTS[process.env.HOST_ENV || process.env.TEST_ENV];
}

function getPassportInternalHost() {
    return PASSPORT_INTERNAL_HOSTS[process.env.TEST_ENV];
}

function getBlackboxHost() {
    return BLACKBOX_HOSTS[process.env.TEST_ENV];
}

function getTusEnvironment() {
    return TUS_ENVS[process.env.TEST_ENV];
}

// TODO: завести passport-web-tests, получить гранты, добавить в qa-proxy, добавить в секретницу
const PASSPORT_API_CONSUMER = 'kopusha';
const QA_PROXY_HOST = 'https://passport-qa-proxy.yandex.net:8888';

module.exports = {
    isProd,
    isRc,
    getPassportFrontendHost,
    getPassportFrontendDomain,
    getPassportInternalHost,
    getBlackboxHost,
    getTusEnvironment,
    PASSPORT_API_CONSUMER,
    QA_PROXY_HOST
};
