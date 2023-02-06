jest.mock('request', () => (params, callback) => callback({}));
jest.mock('got', () => ({extend: () => {}}));
jest.mock('../lib/getYaExperimentsFlags', () => (req, res, next) => next());
jest.mock('../lib/newBrokerExpFilter', () => (req, res, next) => {
    if (process.env.NEW_BROKER) {
        return next();
    }

    return next('route');
});

const querystring = require('querystring');
const supertest = require('supertest');
const url = require('url');
const config = require('../configs/current');
const originalClient = require('../lib/client');
const originalFetch = require('../lib/fetch');
const app = require('../app');

describe(`${process.env.NEW_BROKER ? 'Новый брокер' : 'Старый брокер'}`, () => {
    let broker;

    let server;

    beforeEach(() => {
        server = app.listen();
        broker = supertest.agent(server);
    });

    afterEach(() => {
        server.close();
    });

    describe('Control', () => {
        let fetch;

        beforeEach(() => {
            fetch = jest.spyOn(originalFetch, 'call');
        });

        afterEach(() => {
            fetch.mockRestore();
        });

        const apiHost = url.format(config.url);
        const frontendUrl = '://127.0.0.1/broker2';

        describe('Правильные загловки', () => {
            test('x-content-type-options', (done) => {
                broker
                    .get(`${config.path}/start?resize=true`)
                    .expect('x-content-type-options', 'nosniff')
                    .end(done);
            });

            test('x-frame-options', (done) => {
                broker
                    .get(`${config.path}/start?resize=true`)
                    .expect('x-frame-options', 'Deny')
                    .end(done);
            });

            test('strict-transport-security', (done) => {
                broker
                    .get(`${config.path}/start?resize=true`)
                    .expect('strict-transport-security', 'max-age=31536000')
                    .end(done);
            });
        });

        describe('doRequest', () => {
            ['token', 'yandex_token'].forEach((item) => {
                test(`Передает query параметры ${item} в API в body как token`, (done) => {
                    const params = {
                        token: item
                    };

                    broker.get(`${config.path}/start?${querystring.stringify(params)}`).then(() => {
                        expect(fetch).toBeCalledWith(`${apiHost}/start`, {
                            frontend_url: frontendUrl,
                            user_ip: undefined,
                            token: item
                        });

                        done();
                    });
                });
            });

            ['track', 'yandexuid', 'Session_id'].forEach((cookie) => {
                test(`Передает куку ${cookie} в API  в body`, (done) => {
                    broker
                        .get(`${config.path}/start`)
                        .set('Cookie', [`${cookie}=${cookie}`])
                        .then(() => {
                            expect(fetch).toBeCalledWith(`${apiHost}/start`, {
                                frontend_url: frontendUrl,
                                user_ip: undefined,
                                [cookie]: cookie
                            });

                            done();
                        });
                });
            });

            ['captcha_sid', 'captcha_answer'].forEach((item) => {
                test(`Передает query параметры ${item} в API в body`, (done) => {
                    const params = {
                        [item]: item
                    };

                    broker.get(`${config.path}/start?${querystring.stringify(params)}`).then(() => {
                        expect(fetch).toBeCalledWith(`${apiHost}/start`, {
                            frontend_url: frontendUrl,
                            user_ip: undefined,
                            [item]: item
                        });

                        done();
                    });
                });
            });
        });

        describe('getParams', () => {
            test('Параметр bind переименует в require_auth', (done) => {
                const params = {
                    bind: 'bind'
                };

                broker.get(`${config.path}/start?${querystring.stringify(params)}`).then(() => {
                    expect(fetch).toBeCalledWith(`${apiHost}/start?require_auth=bind`, {
                        frontend_url: frontendUrl,
                        user_ip: undefined
                    });

                    done();
                });
            });
        });

        describe('StartEntry', () => {
            test('С параметром resize не должно быть запроса в API', (done) => {
                broker.get(`${config.path}/start?resize=true`).then(() => {
                    expect(fetch).not.toBeCalled();
                    done();
                });
            });

            test('Проксирует query параметры в API', (done) => {
                const params = {
                    sid: 'sid'
                };

                broker.get(`${config.path}/start?${querystring.stringify(params)}`).then(() => {
                    expect(fetch).toBeCalledWith(`${apiHost}/start?sid=sid`, {
                        frontend_url: frontendUrl,
                        user_ip: undefined
                    });

                    done();
                });
            });

            test('Фильтрует невалидные параметры', (done) => {
                const params = {
                    application: 'application',
                    code_challenge: 'code_challenge',
                    code_challenge_method: 'code_challenge_method',
                    consumer: 'consumer',
                    display: 'display',
                    force_prompt: 'force_prompt',
                    login_hint: 'login_hint',
                    passthrough_errors: 'passthrough_errors',
                    place: 'place',
                    provider: 'provider',
                    require_auth: 'require_auth',
                    retpath: 'retpath',
                    return_brief_profile: 'return_brief_profile',
                    scope: 'scope',
                    sid: 'sid',

                    // невалидные параметры
                    some: 'query',
                    ololo: 'pepepe'
                };

                const path = `start?${querystring.stringify(params)}`;

                delete params.some;
                delete params.ololo;

                const validPath = `start?${querystring.stringify(params)}`;

                broker.get(`${config.path}/${path}`).then(() => {
                    expect(fetch).toBeCalledWith(`${apiHost}/${validPath}`, {
                        frontend_url: frontendUrl,
                        user_ip: undefined
                    });

                    done();
                });
            });
        });

        describe('AuthzInAppStartEntry', () => {
            test('С параметром resize не должно быть запроса в API', (done) => {
                broker.get(`${config.path}/authz_in_app/start?resize=true`).then(() => {
                    expect(fetch).not.toBeCalled();
                    done();
                });
            });

            test('Проксирует query параметры в API', (done) => {
                const params = {
                    application_name: 'application_name'
                };

                broker.get(`${config.path}/authz_in_app/start?${querystring.stringify(params)}`).then(() => {
                    expect(fetch).toBeCalledWith(`${apiHost}/authz_in_app/start?application_name=application_name`, {
                        frontend_url: frontendUrl,
                        user_ip: undefined
                    });

                    done();
                });
            });

            test('Фильтрует невалидные параметры', (done) => {
                const params = {
                    application_name: 'application_name',
                    code_challenge: 'code_challenge',
                    code_challenge_method: 'code_challenge_method',
                    consumer: 'consumer',
                    display: 'display',
                    passthrough_errors: 'passthrough_errors',
                    place: 'place',
                    retpath: 'retpath',
                    yandex_auth_code: 'yandex_auth_code',

                    // невалидные параметры
                    some: 'query',
                    ololo: 'pepepe'
                };

                const path = `authz_in_app/start?${querystring.stringify(params)}`;

                delete params.some;
                delete params.ololo;

                const validPath = `authz_in_app/start?${querystring.stringify(params)}`;

                broker.get(`${config.path}/${path}`).then(() => {
                    expect(fetch).toBeCalledWith(`${apiHost}/${validPath}`, {
                        frontend_url: frontendUrl,
                        user_ip: undefined
                    });

                    done();
                });
            });
        });

        describe('ReverseEntry', () => {
            test('Проксирует query параметры в API', (done) => {
                const params = {
                    consumer: 'consumer'
                };

                broker.get(`${config.path}/tw_reverse_auth_token?${querystring.stringify(params)}`).then(() => {
                    expect(fetch).toBeCalledWith(`${apiHost}/tw_reverse_auth_token?consumer=consumer`, {
                        frontend_url: frontendUrl,
                        user_ip: undefined
                    });

                    done();
                });
            });

            test('Фильтрует невалидные параметры', (done) => {
                const params = {
                    consumer: 'consumer',
                    application: 'application',
                    provider: 'provider',

                    // невалидные параметры
                    some: 'query',
                    ololo: 'pepepe'
                };

                const path = `tw_reverse_auth_token?${querystring.stringify(params)}`;

                delete params.some;
                delete params.ololo;

                const validPath = `tw_reverse_auth_token?${querystring.stringify(params)}`;

                broker.get(`${config.path}/${path}`).then(() => {
                    expect(fetch).toBeCalledWith(`${apiHost}/${validPath}`, {
                        frontend_url: frontendUrl,
                        user_ip: undefined
                    });

                    done();
                });
            });
        });

        describe('RetryEntry', () => {
            test('Проксирует query параметры в API', (done) => {
                const params = {
                    sid: 'sid'
                };

                broker.get(`${config.path}/tw_reverse_auth_token/retry?${querystring.stringify(params)}`).then(() => {
                    expect(fetch).toBeCalledWith(`${apiHost}/tw_reverse_auth_token/retry?sid=sid`, {
                        frontend_url: frontendUrl,
                        user_ip: undefined
                    });

                    done();
                });
            });

            test('Фильтрует невалидные параметры', (done) => {
                const params = {
                    application: 'application',
                    consumer: 'consumer',
                    display: 'display',
                    force_prompt: 'force_prompt',
                    login_hint: 'login_hint',
                    place: 'place',
                    provider: 'provider',
                    require_auth: 'require_auth',
                    retpath: 'retpath',
                    return_brief_profile: 'return_brief_profile',
                    scope: 'scope',
                    sid: 'sid',

                    // невалидные параметры
                    some: 'query',
                    ololo: 'pepepe'
                };

                const path = `tw_reverse_auth_token/retry?${querystring.stringify(params)}`;

                delete params.some;
                delete params.ololo;

                const validPath = `tw_reverse_auth_token/retry?${querystring.stringify(params)}`;

                broker.get(`${config.path}/${path}`).then(() => {
                    expect(fetch).toBeCalledWith(`${apiHost}/${validPath}`, {
                        frontend_url: frontendUrl,
                        user_ip: undefined
                    });

                    done();
                });
            });
        });

        ['get', 'post'].forEach((method) => {
            describe(`BindByTokenEntry ${method.toUpperCase()}`, () => {
                test('Проксирует query параметры в API', (done) => {
                    const params = {
                        provider: 'provider'
                    };

                    broker[method](`${config.path}/bind_by_token?${querystring.stringify(params)}`).then(() => {
                        expect(fetch).toBeCalledWith(`${apiHost}/bind_by_token?provider=provider`, {
                            frontend_url: frontendUrl,
                            user_ip: undefined
                        });

                        done();
                    });
                });

                ['provider_token', 'provider_token_secret'].forEach((item) => {
                    test(`Передает query параметры ${item} в API в body`, (done) => {
                        const params = {
                            [item]: item
                        };

                        broker[method](`${config.path}/bind_by_token?${querystring.stringify(params)}`).then(() => {
                            expect(fetch).toBeCalledWith(`${apiHost}/bind_by_token`, {
                                frontend_url: frontendUrl,
                                user_ip: undefined,
                                [item]: item
                            });

                            done();
                        });
                    });
                });

                test('Фильтрует невалидные параметры', (done) => {
                    const params = {
                        provider: 'provider',
                        application: 'application',
                        retpath: 'retpath',
                        place: 'place',
                        consumer: 'consumer',
                        ui_language: 'ui_language',
                        return_brief_profile: 'return_brief_profile',
                        scope: 'scope',

                        // невалидные параметры
                        some: 'query',
                        ololo: 'pepepe'
                    };

                    const path = `bind_by_token?${querystring.stringify(params)}`;

                    delete params.some;
                    delete params.ololo;

                    const validPath = `bind_by_token?${querystring.stringify(params)}`;

                    broker[method](`${config.path}/${path}`).then(() => {
                        expect(fetch).toBeCalledWith(`${apiHost}/${validPath}`, {
                            frontend_url: frontendUrl,
                            user_ip: undefined
                        });

                        done();
                    });
                });
            });
        });

        describe('AuthzInAppEntrustToAccountEntry', () => {
            ['task_id', 'token', 'code_verifier'].forEach((item) => {
                test(`Передает query параметры ${item} в API в body`, (done) => {
                    const params = {
                        [item]: item
                    };

                    broker
                        .post(`${config.path}/authz_in_app/entrust_to_account?${querystring.stringify(params)}`)
                        .then(() => {
                            expect(fetch).toBeCalledWith(`${apiHost}/authz_in_app/entrust_to_account`, {
                                frontend_url: frontendUrl,
                                user_ip: undefined,
                                [item]: item
                            });

                            done();
                        });
                });
            });

            test('Фильтрует невалидные параметры', (done) => {
                // невалидные параметры
                const params = {
                    provider: 'provider',
                    application: 'application',
                    retpath: 'retpath',
                    place: 'place',
                    consumer: 'consumer',
                    ui_language: 'ui_language',
                    return_brief_profile: 'return_brief_profile',
                    scope: 'scope',
                    some: 'query',
                    ololo: 'pepepe'
                };

                const path = `authz_in_app/entrust_to_account?${querystring.stringify(params)}`;

                broker.post(`${config.path}/${path}`).then(() => {
                    expect(fetch).toBeCalledWith(`${apiHost}/authz_in_app/entrust_to_account`, {
                        frontend_url: frontendUrl,
                        user_ip: undefined
                    });

                    done();
                });
            });
        });

        describe('BindEntry', () => {
            test(`Передает параметр allow в API в body`, (done) => {
                broker.get(`${config.path}/ololo/bind`).then(() => {
                    expect(fetch).toBeCalledWith(`${apiHost}/ololo/bind`, {
                        frontend_url: frontendUrl,
                        user_ip: undefined,
                        allow: 1
                    });

                    done();
                });
            });
        });

        describe('RedirectEntry', () => {
            test(`Проксирует в бек любые query`, (done) => {
                const params = {
                    ololo: 'pepepe',
                    sid: 'sid',
                    consumer: 'passport'
                };
                const query = querystring.stringify(params);

                broker.get(`${config.path}/redirect?${query}`).then(() => {
                    expect(fetch).toBeCalledWith(`${apiHost}/redirect?${query}`, {
                        frontend_url: frontendUrl,
                        user_ip: undefined
                    });

                    done();
                });
            });
        });
    });

    describe('AuthzInWeb', () => {
        const task_id = 'asdasdasdasdsadasdqwepodmqwpmd';
        const params = {
            consumer: 'consumer',
            application_name: 'application_name',
            retpath: 'retpath',
            flags: 'flag,flag,flag,flag'
        };
        const query = querystring.stringify(params);

        let client;

        beforeEach(() => {
            client = jest.spyOn(originalClient, 'call');
        });

        afterEach(() => {
            client.mockRestore();
        });

        describe('Start', () => {
            test('Не отправляет запрос в API без обязательных параметров', (done) => {
                broker.get(`${config.path}/authz_in_web/start`).then(() => {
                    expect(client).not.toBeCalled();
                    done();
                });
            });

            test('Проксирует параметры в API', (done) => {
                const requestParams = {
                    body: {
                        Session_id: 'Session_id',
                        application_name: params.application_name,
                        consumer: params.consumer,
                        retpath: params.retpath,
                        flags: params.flags,
                        user_ip: 'user_ip'
                    },
                    form: true,
                    method: 'POST'
                };

                broker
                    .get(`${config.path}/authz_in_web/start?${query}`)
                    .set({
                        Cookie: [`Session_id=${requestParams.body.Session_id}`],
                        'x-real-ip': requestParams.body.user_ip
                    })
                    .then(() => {
                        expect(client).toBeCalledWith('authz_in_web/start', requestParams);
                        done();
                    });
            });
        });

        describe('Callback', () => {
            test('Проксирует параметры в API', (done) => {
                const requestParams = {
                    body: {
                        Session_id: 'Session_id',
                        user_ip: 'user_ip',
                        track: 'track',
                        task_id,
                        query
                    },
                    form: true,
                    method: 'POST'
                };

                broker
                    .get(`${config.path}/authz_in_web/${task_id}/callback?${query}`)
                    .set({
                        Cookie: [`Session_id=${requestParams.body.Session_id};track=${requestParams.body.track}`],
                        'x-real-ip': requestParams.body.user_ip
                    })
                    .then(() => {
                        expect(client).toBeCalledWith('/authz_in_web/callback', requestParams);
                        done();
                    });
            });
        });

        describe('BindGet', () => {
            test('Проксирует параметры в API', (done) => {
                const requestParams = {
                    body: {
                        Session_id: 'Session_id',
                        user_ip: 'user_ip',
                        track: 'track',
                        task_id
                    },
                    form: true,
                    method: 'POST',
                    query: params
                };

                broker
                    .get(`${config.path}/authz_in_web/${task_id}/bind?${query}`)
                    .set({
                        Cookie: [`Session_id=${requestParams.body.Session_id};track=${requestParams.body.track}`],
                        'x-real-ip': requestParams.body.user_ip
                    })
                    .then(() => {
                        expect(client).toBeCalledWith('/authz_in_web/bind/submit', requestParams);
                        done();
                    });
            });
        });

        describe('BindPost', () => {
            test('Проксирует параметры в API', (done) => {
                const requestParams = {
                    body: {
                        Session_id: 'Session_id',
                        user_ip: 'user_ip',
                        track: 'track',
                        task_id
                    },
                    form: true,
                    method: 'POST',
                    query: params
                };

                broker
                    .post(`${config.path}/authz_in_web/${task_id}/bind?${query}`)
                    .set({
                        Cookie: [`Session_id=${requestParams.body.Session_id};track=${requestParams.body.track};`],
                        'x-real-ip': requestParams.body.user_ip
                    })
                    .then(() => {
                        expect(client).toBeCalledWith('/authz_in_web/bind/commit', requestParams);
                        done();
                    });
            });
        });

        describe('CollectDiagnostics', () => {
            test('Проксирует параметры в API', (done) => {
                const requestParams = {
                    body: {
                        Session_id: 'Session_id',
                        user_ip: 'user_ip',
                        track: 'track',
                        task_id
                    },
                    form: true,
                    method: 'POST',
                    query: params
                };

                broker
                    .get(`${config.path}/authz_in_web/${task_id}/collect_diagnostics?${query}`)
                    .set({
                        Cookie: [`Session_id=${requestParams.body.Session_id};track=${requestParams.body.track};`],
                        'x-real-ip': requestParams.body.user_ip
                    })
                    .then(() => {
                        expect(client).toBeCalledWith('/authz_in_web/collect_diagnostics', requestParams);
                        done();
                    });
            });
        });
    });
});
