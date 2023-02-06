const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('sync cookie', function () {
    const counterId = 20302;
    let clientId;
    let resource;
    let baseUrl;
    beforeEach(function () {
        clientId = Math.random().toString().slice(2);
        resource = `test/cookieSync/cookieSync.hbs?c=${clientId}`;
        baseUrl = `https://yandex.ru/${resource}`;
        return (
            this.browser
                .timeoutsAsyncScript(15000)
                // выставляем сессионную куку на tld com tr
                // что бы прокся сложила все запросы теста в
                // одну сессию
                .url(`https://yandex.com.tr/${resource}`)
        );
    });
    it('fail with timeout', function () {
        return this.browser
            .url(baseUrl)
            .execute(function () {
                localStorage.clear();
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    counterId,
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/sync_cookie_image_check`,
                                    sleep: 5000,
                                    count: 1,
                                },
                            ],
                            () => {
                                Object.defineProperty(
                                    window.navigator,
                                    'language',
                                    {
                                        value: 'tr',
                                    },
                                );
                                document.cookie = '_ym_isad=1';
                                const min = Math.floor(Date.now() / 1000 / 60);
                                serverHelpers.collectRequests(
                                    1500,
                                    (req, done) => {
                                        done([
                                            req,
                                            JSON.stringify(localStorage),
                                            min,
                                        ]);
                                    },
                                );
                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                            },
                        );
                    },
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: [requests, ls, min] }) => {
                const hits = requests
                    .filter((req) => {
                        return req.headers['x-host'] !== 'mc.yandex.com.tr';
                    })
                    .map(e2eUtils.getRequestParams);
                const [pageView] = hits;
                chai.expect(pageView.brInfo.pv).to.be.eq('1');
                const altDomainRequests = requests.filter((req) => {
                    return req.headers['x-host'] === 'mc.yandex.com.tr';
                });
                chai.expect(altDomainRequests).to.have.lengthOf(1);
                const lsTime = JSON.parse(JSON.parse(ls)._ym_synced)['com.tr'];
                chai.expect(min - lsTime).to.be.greaterThan(1400);
            });
    });
    it('fail with error', function () {
        return this.browser
            .url(baseUrl)
            .execute(function () {
                localStorage.clear();
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    counterId,
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/sync_cookie_image_check`,
                                    status: 500,
                                    count: 1,
                                },
                            ],
                            () => {
                                Object.defineProperty(
                                    window.navigator,
                                    'language',
                                    {
                                        value: 'tr',
                                    },
                                );
                                document.cookie = '_ym_isad=1';
                                const min = Math.floor(Date.now() / 1000 / 60);
                                serverHelpers.collectRequests(
                                    1000,
                                    (req, done) => {
                                        done([
                                            req,
                                            JSON.stringify(localStorage),
                                            min,
                                        ]);
                                    },
                                );
                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                            },
                        );
                    },
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: [requests, ls, min] }) => {
                const altDomainRequests = requests.filter((req) => {
                    return req.headers['x-host'] === 'mc.yandex.com.tr';
                });
                chai.expect(altDomainRequests).to.have.lengthOf(1);
                const lsTime = JSON.parse(JSON.parse(ls)._ym_synced)['com.tr'];
                chai.expect(min - lsTime).to.be.greaterThan(1400);
                const hits = requests
                    .filter((req) => {
                        return req.headers['x-host'] !== 'mc.yandex.com.tr';
                    })
                    .map(e2eUtils.getRequestParams);
                const [pageView] = hits;
                chai.expect(pageView.brInfo.pv).to.be.eq('1');
            });
    });
    it('send requests to tld', function () {
        return this.browser
            .url(baseUrl)
            .execute(function () {
                localStorage.clear();
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    counterId,
                    cb(serverHelpers, options) {
                        Object.defineProperty(window.navigator, 'language', {
                            value: 'tr',
                        });
                        document.cookie = '_ym_isad=1';
                        const min = Math.floor(Date.now() / 1000 / 60);
                        serverHelpers.collectRequests(1000, (req, done) => {
                            done([req, JSON.stringify(localStorage), min]);
                        });
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                    },
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: [requests, lsStr, min] }) => {
                const altDomainRequests = requests.filter((req) => {
                    return req.headers['x-host'] === 'mc.yandex.com.tr';
                });
                const ls = JSON.parse(JSON.parse(lsStr)._ym_synced);
                chai.expect(altDomainRequests).to.have.lengthOf(1);
                chai.expect(ls).to.have.key('com.tr');
                const lsTime = ls['com.tr'];
                chai.expect(min - lsTime).to.be.lessThan(2);
                const hits = requests
                    .filter((req) => {
                        return req.headers['x-host'] !== 'mc.yandex.com.tr';
                    })
                    .map(e2eUtils.getRequestParams);
                const [pageView] = hits;
                chai.expect(pageView.brInfo.pv).to.be.eq('1');
            });
    });
});
