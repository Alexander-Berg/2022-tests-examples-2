const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

export const counterIdSpecial = 42080444;
export const counterIdRandom = 12345;
export const counterIdSave = 42822899;

describe('deviceSync', function () {
    const baseUrl = 'https://yandex.ru/test/deviceSync/deviceSync.hbs';
    const notYandexUrl = 'https://example.com/test/deviceSync/deviceSync.hbs';
    const turboUrl = 'http://yandex.ru/test/deviceSync/deviceSyncTurbo.hbs';

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000);
    });

    it('should find deviceSync page', function () {
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

    it('should be no device request if not a mobile platform', function () {
        const counterId = counterIdRandom;
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/${options.counterId}`,
                                    count: 2,
                                    body: {
                                        settings: {
                                            pcs: '0',
                                        },
                                        userData: {},
                                    },
                                },
                                {
                                    regex: `/watch/${options.counterIdSave}`,
                                    count: 1,
                                    status: '200',
                                },
                                {
                                    regex: `/user_storage_set`,
                                    count: 1,
                                    status: '200',
                                },
                            ],
                            function () {
                                serverHelpers.collectRequests(2000);
                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                            },
                        );
                    },
                    counterId,
                    counterIdSave,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                chai.expect(
                    requests.filter((request) =>
                        request.url.match(new RegExp(`/watch/${counterId}`)),
                    ).length,
                    `should exchange data with /watch/${counterId}`,
                ).not.equal(0);
                chai.expect(
                    requests.filter((request) =>
                        request.url.match(
                            new RegExp(
                                `/watch/${counterIdSave}|user_storage_set`,
                            ),
                        ),
                    ).length,
                    `should send no requests to /watch/${counterIdSave} or user_storage_set`,
                ).equal(0);
            });
    });

    it(`should be no requests to user_storage_set and /watch/${counterIdSave} if localStorage.ds < currentTime`, function () {
        const counterId = counterIdSpecial;
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/${options.counterId}`,
                                    count: 2,
                                    body: {
                                        settings: {
                                            pcs: '0',
                                        },
                                        userData: {
                                            ds: 11111111111111111,
                                        },
                                    },
                                },
                                {
                                    regex: `/watch/${options.counterIdSave}`,
                                    count: 1,
                                    status: '200',
                                },
                                {
                                    regex: `/user_storage_set`,
                                    count: 1,
                                    status: '200',
                                },
                            ],
                            function () {
                                serverHelpers.collectRequests(2000);
                                Object.defineProperty(
                                    window.navigator,
                                    'platform',
                                    { value: 'android' },
                                );
                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                            },
                        );
                    },
                    counterId,
                    counterIdSave,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                chai.expect(
                    requests.filter((request) =>
                        request.url.match(new RegExp(`/watch/${counterId}`)),
                    ).length,
                    `should exchange data with /watch/${counterId}`,
                ).not.equal(0);
                chai.expect(
                    requests.filter((request) =>
                        request.url.match(
                            new RegExp(
                                `/watch/${counterIdSave}|user_storage_set`,
                            ),
                        ),
                    ).length,
                    `should send no requests to /watch/${counterIdSave} or user_storage_set`,
                ).equal(0);
            });
    });
    it.skip('get info from sync domain', function () {
        return this.browser
            .url(
                'https://yandexmetrica.com:30103/test/deviceSync/deviceSync.hbs',
            )
            .getText('body')
            .then((innerText) => {
                chai.expect(
                    'deviceSync page',
                    'check if page contains required text',
                ).to.be.equal(innerText);
            });
    });

    it('should request device at yandex if platform is Android', function () {
        const counterId = counterIdSpecial;
        const sessionId = Math.random().toString().slice(2);
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
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/${options.counterId}`,
                                    count: 2,
                                    body: {
                                        settings: {
                                            pcs: '0',
                                        },
                                        userData: {
                                            ds: 0,
                                        },
                                    },
                                },
                                {
                                    regex: `/watch/${options.counterIdSave}`,
                                    count: 1,
                                    status: '200',
                                },
                                {
                                    regex: `/user_storage_set`,
                                    count: 1,
                                    status: '200',
                                },
                            ],
                            function () {
                                serverHelpers.collectRequests(2000);
                                Object.defineProperty(
                                    window.navigator,
                                    'platform',
                                    { value: 'android' },
                                );
                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                            },
                        );
                    },
                    counterId,
                    counterIdSave,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                chai.expect(
                    requests.filter((request) =>
                        request.url.match(new RegExp(`/watch/${counterId}`)),
                    ).length,
                    `should exchange data with /watch/${counterId}`,
                ).not.equal(0);
                const saveRequests = requests.filter((request) =>
                    request.url.match(
                        new RegExp(`/watch/${counterIdSave}.+data-from-device`),
                    ),
                );
                chai.expect(
                    saveRequests.length,
                    `should send data to /watch/${counterIdSave} with text from local server`,
                ).not.equal(0);
                chai.expect(
                    requests.filter((request) =>
                        request.url.match(new RegExp(`/user_storage_set`)),
                    ).length,
                    `should send data to user_storage_set`,
                ).not.equal(0);
            });
    });

    it('should request device at non-yandex domains independent of random', function () {
        const counterId = counterIdSpecial;
        return this.browser
            .url(notYandexUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/${options.counterId}`,
                                    count: 2,
                                    body: {
                                        settings: {
                                            pcs: '0',
                                        },
                                        userData: {
                                            ds: 0,
                                        },
                                    },
                                },
                                {
                                    regex: `/watch/${options.counterIdSave}`,
                                    count: 1,
                                    status: '200',
                                },
                                {
                                    regex: `/user_storage_set`,
                                    count: 1,
                                    status: '200',
                                },
                            ],
                            function () {
                                serverHelpers.collectRequests(2000);
                                Math.random = () => 0.01;
                                Object.defineProperty(
                                    window.navigator,
                                    'platform',
                                    { value: 'android' },
                                );
                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                            },
                        );
                    },
                    counterId,
                    counterIdSave,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                chai.expect(
                    requests.filter((request) =>
                        request.url.match(new RegExp(`/watch/${counterId}`)),
                    ).length,
                    `should exchange data with /watch/${counterId}`,
                ).not.equal(0);
                const saveRequests = requests.filter((request) =>
                    request.url.match(
                        new RegExp(`/watch/${counterIdSave}.+data-from-device`),
                    ),
                );
                chai.expect(
                    saveRequests.length,
                    `should send data to /watch/${counterIdSave} with text from local server`,
                ).not.equal(0);
                const [parsedReq] = saveRequests.map(e2eUtils.getRequestParams);
                chai.expect(parsedReq.brInfo.hid).is.not.empty;
                chai.expect(parseInt(parsedReq.brInfo.dit, 10)).is.gte(0);
                chai.expect(
                    requests.filter((request) =>
                        request.url.match(new RegExp(`/user_storage_set`)),
                    ).length,
                    `should send data to user_storage_set`,
                ).not.equal(0);
            });
    });

    it('should not request device on rsya counters', function () {
        const counterId = counterIdSpecial;
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/${options.counterId}`,
                                    count: 2,
                                    body: {
                                        settings: {
                                            pcs: '0',
                                        },
                                        userData: {
                                            ds: 0,
                                        },
                                    },
                                },
                            ],
                            function () {
                                serverHelpers.collectRequests(2000);
                                Object.defineProperty(
                                    window.navigator,
                                    'platform',
                                    { value: 'android' },
                                );
                                new Ya.Metrika2({
                                    id: options.counterId,
                                    type: 1,
                                });
                            },
                        );
                    },
                    counterId,
                    counterIdSave,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                chai.expect(
                    requests.filter((request) =>
                        request.url.match(new RegExp(`/p?t=`)),
                    ).length,
                    'do not send requests to localhost on rsya counters',
                ).equal(0);
            });
    });

    it('should send request device at non-yandex domains random independed', function () {
        const counterId = counterIdSpecial;
        return this.browser
            .url(notYandexUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/${options.counterId}`,
                                    count: 2,
                                    body: {
                                        settings: {
                                            pcs: '0',
                                        },
                                        userData: {
                                            ds: 0,
                                        },
                                    },
                                },
                                {
                                    regex: `/watch/${options.counterIdSave}`,
                                    count: 1,
                                    status: '200',
                                },
                                {
                                    regex: `/user_storage_set`,
                                    count: 1,
                                    status: '200',
                                },
                            ],
                            function () {
                                serverHelpers.collectRequests(2000);
                                Math.random = () => 0.2;
                                Object.defineProperty(
                                    window.navigator,
                                    'platform',
                                    { value: 'android' },
                                );
                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                            },
                        );
                    },
                    counterId,
                    counterIdSave,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                chai.expect(
                    requests.filter((request) =>
                        request.url.match(new RegExp(`/watch/${counterId}`)),
                    ).length,
                    `should exchange data with /watch/${counterId}`,
                ).not.equal(0);
                chai.expect(
                    requests.filter((request) =>
                        request.url.match(
                            new RegExp(`/watch/${counterIdSave}`),
                        ),
                    ).length,
                    `should not send data to /watch/${counterIdSave}`,
                ).equal(1);
                chai.expect(
                    requests.filter((request) =>
                        request.url.match(new RegExp(`/user_storage_set`)),
                    ).length,
                    `should not send data to user_storage_set`,
                ).equal(1);
            });
    });

    it('should only write to a console once', function () {
        const counterId = counterIdSpecial;
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/${options.counterId}`,
                                    count: 2,
                                    body: {
                                        settings: {
                                            pcs: '0',
                                        },
                                        userData: {
                                            ds: 0,
                                        },
                                    },
                                },
                                {
                                    regex: `/watch/${options.counterIdSave}`,
                                    count: 1,
                                    status: '500',
                                },
                                {
                                    regex: `/user_storage_set`,
                                    count: 1,
                                    status: '500',
                                },
                            ],
                            function () {
                                serverHelpers.collectRequests(2000);
                                Object.defineProperty(
                                    window.navigator,
                                    'platform',
                                    { value: 'android' },
                                );
                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                            },
                        );
                    },
                    counterId,
                    counterIdSave,
                }),
            )
            .then(e2eUtils.handleDebugConsole(this.browser))
            .then((consoleMessages) => {
                chai.expect(consoleMessages.length).equal(1);
            });
    });

    it('turboapp should save device state when online', function () {
        const counterId = counterIdSpecial;
        return this.browser
            .deleteCookie()
            .url(turboUrl)
            .execute(() => {
                window.yandex = {
                    navigator: {
                        sendPersistentBeacon(url) {
                            window.onRequest({ url });
                        },
                    },
                    private: {
                        user: {
                            getRegion: () => Promise.resolve(true),
                        },
                    },
                };
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/${options.counterId}`,
                                    count: 2,
                                    body: {
                                        settings: {
                                            pcs: '0',
                                        },
                                        userData: {
                                            ds: 0,
                                        },
                                    },
                                },
                                {
                                    regex: `/watch/${options.counterIdSave}`,
                                    count: 1,
                                    status: '200',
                                },
                                {
                                    regex: `/user_storage_set`,
                                    count: 1,
                                    status: '200',
                                },
                            ],
                            function () {
                                serverHelpers.collectRequests(2000);
                                const requests = [];
                                serverHelpers.onRequest(function (request) {
                                    requests.push(request);
                                });
                                window.onRequest = (url) => {
                                    requests.push(url);
                                    if (url.url.match('user_storage_set')) {
                                        done(requests);
                                    }
                                };
                                Object.defineProperty(
                                    window.navigator,
                                    'platform',
                                    { value: 'android' },
                                );
                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                            },
                        );
                    },
                    counterId,
                    counterIdSave,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                chai.expect(
                    requests.filter((request) =>
                        request.url.match(new RegExp(`/watch/${counterId}`)),
                    ).length,
                    `should exchange data with /watch/${counterId}`,
                ).not.equal(0);
                chai.expect(
                    requests.filter((request) =>
                        request.url.match(
                            new RegExp(`/watch/${counterIdSave}`),
                        ),
                    ).length,
                    `should send data to /watch/${counterIdSave}`,
                ).not.equal(0);
                chai.expect(
                    requests.filter((request) => {
                        const res = request.url.match(
                            new RegExp(`/user_storage_set`),
                        );
                        if (res) {
                            chai.expect(request.url).to.not.include('ti(');
                        }
                        return res;
                    }).length,
                    `should  send data to user_storage_set`,
                ).not.equal(0);
            });
    });

    it('turboapp should not save device state when offline', function () {
        const counterId = counterIdSpecial;
        return this.browser
            .deleteCookie()
            .url(turboUrl)
            .execute(() => {
                window.yandex = {
                    navigator: {
                        sendPersistentBeacon(url) {
                            window.onRequest({ url });
                        },
                    },
                    private: {
                        user: {
                            getRegion: () => Promise.resolve(true),
                        },
                    },
                };
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/${options.counterId}`,
                                    count: 2,
                                    body: {
                                        settings: {
                                            pcs: '0',
                                        },
                                        userData: {
                                            ds: 0,
                                        },
                                    },
                                },
                                {
                                    regex: `/watch/${options.counterIdSave}`,
                                    count: 1,
                                    status: '200',
                                },
                                {
                                    regex: `/user_storage_set`,
                                    count: 1,
                                    status: '200',
                                },
                            ],
                            function () {
                                const requests = [];
                                serverHelpers.onRequest(function (request) {
                                    requests.push(request);
                                    if (requests.length > 3) {
                                        done(requests);
                                    }
                                });
                                window.onRequest = (url) => {
                                    requests.push(url);
                                    if (requests.length > 3) {
                                        done(requests);
                                    }
                                };
                                setTimeout(() => {
                                    done(requests);
                                }, 1000);
                                Object.defineProperty(
                                    window.navigator,
                                    'platform',
                                    { value: 'android' },
                                );
                                Object.defineProperty(
                                    window.navigator,
                                    'onLine',
                                    { value: false },
                                );
                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                            },
                        );
                    },
                    counterId,
                    counterIdSave,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                chai.expect(
                    requests.filter((request) =>
                        request.url.match(new RegExp(`/watch/${counterId}`)),
                    ).length,
                    `should not exchange data with /watch/${counterId}`,
                ).equal(0);
                chai.expect(
                    requests.filter((request) =>
                        request.url.match(
                            new RegExp(`/watch/${counterIdSave}`),
                        ),
                    ).length,
                    `should not send data to /watch/${counterIdSave}`,
                ).equal(0);
            });
    });
});
