const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

const tests = [
    {
        name: 'one https soket broken',
        skip: true,
        testFunction: (serverHelpers, ctx) => {
            serverHelpers.addRule(
                [
                    {
                        regex: `/watch/${ctx.counterId}`,
                        body: {
                            settings: {
                                pcs: '0',
                            },
                            userData: {},
                        },
                    },
                    {
                        regex: `/p\\?t=`,
                        scheme: 'https',
                        count: 1,
                        status: 500,
                    },
                ],
                () => {
                    Object.defineProperty(window.navigator, 'platform', {
                        value: 'android',
                    });
                    serverHelpers.collectRequests(1000);
                    new Ya.Metrika2({
                        id: ctx.counterId,
                    });
                },
            );
        },
        assertFunction: (ctx, { value: requests }) => {
            const socketRequests = requests.filter((request) => {
                return ['127.0.0.1', 'yandexmetrica.com'].includes(
                    request.headers['x-host'],
                );
            });
            const saveRequests = requests
                .filter((request) => {
                    return request.headers['x-host'] === 'mc.yandex.ru';
                })
                .map(e2eUtils.getRequestParams)
                .filter((request) => {
                    return (
                        Object.keys(request.brInfo).length && request.brInfo.di
                    );
                });
            const ports = socketRequests.map((request) => {
                return request.headers['x-port'];
            });
            chai.expect(socketRequests).to.be.lengthOf(3);
            chai.expect(ports).to.include.members(['30103', '30102', '29010']);
            chai.expect(saveRequests).to.be.lengthOf(1);
            const [saveRequest] = saveRequests;
            chai.expect(saveRequest.brInfo.dip).to.be.eq('30102');
        },
    },
    {
        name: 'http soket broken',
        skip: true,
        testFunction: (serverHelpers, ctx) => {
            serverHelpers.addRule(
                [
                    {
                        regex: `/watch/${ctx.counterId}`,
                        body: {
                            settings: {
                                pcs: '0',
                            },
                            userData: {},
                        },
                    },
                    {
                        regex: `/p\\?t=`,
                        scheme: 'http',
                        count: 2,
                        status: 500,
                    },
                ],
                () => {
                    Object.defineProperty(window.navigator, 'platform', {
                        value: 'android',
                    });
                    serverHelpers.collectRequests(1000);
                    new Ya.Metrika2({
                        id: ctx.counterId,
                    });
                },
            );
        },
        assertFunction: (ctx, { value: requests }) => {
            const socketRequests = requests.filter((request) => {
                return ['127.0.0.1', 'yandexmetrica.com'].includes(
                    request.headers['x-host'],
                );
            });
            const saveRequests = requests
                .map(e2eUtils.getRequestParams)
                .filter((request) => {
                    return (
                        Object.keys(request.brInfo).length &&
                        request.headers['x-host'] === 'mc.yandex.ru' &&
                        request.brInfo.di
                    );
                });
            const ports = socketRequests.map((request) => {
                return request.headers['x-port'];
            });
            chai.expect(socketRequests).to.be.lengthOf(3);
            chai.expect(ports).to.include.members(['30103', '30102', '29009']);
            chai.expect(saveRequests).to.be.lengthOf(1);
            const [saveRequest] = saveRequests;
            chai.expect(saveRequest.brInfo.dip).to.be.eq('30103');
        },
    },
    {
        name: 'imposible to save',
        skip: true,
        testFunction: (serverHelpers, ctx) => {
            serverHelpers.addRule(
                [
                    {
                        regex: `/watch/42822899`,
                        status: 500,
                    },
                    {
                        regex: `/watch/${ctx.counterId}`,
                        body: {
                            settings: {
                                pcs: '0',
                            },
                            userData: {},
                        },
                    },
                ],
                () => {
                    Object.defineProperty(window.navigator, 'platform', {
                        value: 'android',
                    });
                    serverHelpers.collectRequests(1000);
                    new Ya.Metrika2(ctx.counterId);
                },
            );
        },
        assertFunction: (ctx, { value: requests, extra }) => {
            const socketRequests = requests.filter((request) => {
                return ['127.0.0.1', 'yandexmetrica.com'].includes(
                    request.headers['x-host'],
                );
            });
            chai.expect(socketRequests).to.be.lengthOf(2);
            chai.expect(extra.js).to.be.lengthOf(0);
            const ports = socketRequests.map((request) => {
                return request.headers['x-port'];
            });
            chai.expect(ports).to.include.members(['30103', '30102']);
        },
    },
    {
        name: 'green path all sokets ok',
        skip: true,
        testFunction: (serverHelpers, ctx) => {
            serverHelpers.addRule(
                [
                    {
                        regex: `/watch/${ctx.counterId}`,
                        body: {
                            settings: {
                                pcs: '0',
                            },
                            userData: {},
                        },
                    },
                ],
                () => {
                    Object.defineProperty(window.navigator, 'platform', {
                        value: 'android',
                    });
                    serverHelpers.collectRequests(1000);
                    new Ya.Metrika2(ctx.counterId);
                },
            );
        },
        assertFunction: (ctx, { value: requests }) => {
            const socketRequests = requests.filter((request) => {
                return ['127.0.0.1', 'yandexmetrica.com'].includes(
                    request.headers['x-host'],
                );
            });
            chai.expect(socketRequests).to.be.lengthOf(2);
            const ports = socketRequests.map((request) => {
                return request.headers['x-port'];
            });
            chai.expect(ports).to.include.members(['30103', '30102']);
        },
    },
];

describe('deviceSync request sequence', function () {
    const baseUrl = 'https://yandex.ru/test/deviceSync/deviceSync.hbs';

    beforeEach(function () {
        return this.browser
            .url(baseUrl)
            .executeAsync(function (done) {
                localStorage.clear();
                done();
            })
            .timeoutsAsyncScript(10000);
    });
    it(// .skip
    'should find deviceSync page', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then((innerText) => {
                chai.expect(
                    'deviceSync page',
                    'check if page contains required text',
                ).to.be.equal(innerText);
            });
    });
    tests.forEach((test) => {
        if (test.skip) {
            return;
        }
        it(test.name, function () {
            const { testFunction, assertFunction } = test;
            const sessionId = Math.random().toString().slice(2);
            const ctx = {
                counterId: (Math.random() * 10000).toFixed(0),
            };
            return this.browser
                .url(`https://yandex.ru/test/deviceSync/setCookie.hbs`)
                .executeAsync(
                    (opt, done) => {
                        document.cookie = `forceIO=${opt.sessionId}; path=/; domain=.yandex.ru`;
                        done();
                    },
                    {
                        sessionId,
                    },
                )
                .url(`${baseUrl}?sessID=${sessionId}`)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb: testFunction,
                        ...ctx,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(assertFunction.bind(null, ctx));
        });
    });
});
