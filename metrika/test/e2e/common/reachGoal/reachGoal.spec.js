const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('ReachGoal e2e test', function () {
    const baseUrl = 'test/reachGoal/reachGoal.hbs';
    const baseFullUrl = `${e2eUtils.baseUrl}/${baseUrl}`;
    const counterId = 26302566;

    const testGoal = 'TEST_GOAL';
    const goalUrl = `${e2eUtils.goalUrl}/${testGoal}`;
    const goalParams = {
        order_price: 1000.35,
        currency: 'RUB',
    };
    const testCtx = {
        ctx: true,
    };

    beforeEach(function () {
        return this.browser.deleteCookie().timeoutsAsyncScript(10000);
    });

    it('should send goal', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.onRequest(function (request) {
                            if (request.url.indexOf('page-url=goal') !== -1) {
                                done(request);
                            }
                        });
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        counter.reachGoal(options.testGoal);
                    },
                    counterId,
                    testGoal,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                const {
                    params,
                    brInfo,
                    counterId: reqCounterId,
                } = e2eUtils.getRequestParams(request);

                chai.expect(reqCounterId).to.be.equal(String(counterId));
                chai.expect(brInfo.ar).to.be.equal('1');
                chai.expect(params.charset).to.be.equal('utf-8');
                chai.expect(params['page-ref']).to.be.equal(baseFullUrl);
                chai.expect(params['page-url']).to.be.equal(goalUrl);
            });
    });

    it('should send goal with params', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        counter.reachGoal(options.testGoal, options.goalParams);

                        serverHelpers.onRequest(function (request) {
                            if (request.url.indexOf('page-url=goal') !== -1) {
                                done(request);
                            }
                        });
                    },
                    counterId,
                    testGoal,
                    goalParams,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                const { params, brInfo, siteInfo } =
                    e2eUtils.getRequestParams(request);

                chai.expect(siteInfo).to.be.ok;
                chai.expect(brInfo.ar).to.be.equal('1');
                chai.expect(params['page-ref']).to.be.equal(baseFullUrl);
                chai.expect(params['page-url']).to.be.equal(goalUrl);
                chai.expect(siteInfo).to.be.deep.equal(goalParams);
            });
    });

    it('should not send goal without goalName', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const requests = [];
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        counter.reachGoal();
                        counter.reachGoal('');
                        counter.reachGoal(null, options.goalParams);
                        counter.reachGoal('', options.goalParams);

                        setTimeout(function () {
                            done(requests);
                        }, 500);

                        serverHelpers.onRequest(function (request) {
                            requests.push(request);
                        });
                    },
                    counterId,
                    testGoal,
                    goalParams,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const hasGoalRequest = requests.some(({ url }) =>
                    /page-url=goal/.test(url),
                );
                chai.expect(hasGoalRequest).to.be.false;
            });
    });

    it('should use callback with ctx without params', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        const callback = function () {
                            done(this);
                        };

                        counter.reachGoal(
                            options.testGoal,
                            callback,
                            options.testCtx,
                        );
                    },
                    counterId,
                    testGoal,
                    testCtx,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: callbackGoalCtx }) => {
                chai.expect(callbackGoalCtx).to.deep.equal(testCtx);
            });
    });

    it('should use callback with ctx and params', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        const callback = function () {
                            done(this);
                        };

                        counter.reachGoal(
                            options.testGoal,
                            options.goalParams,
                            callback,
                            options.testCtx,
                        );
                    },
                    counterId,
                    testGoal,
                    goalParams,
                    testCtx,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: callbackGoalCtx }) => {
                chai.expect(callbackGoalCtx).to.deep.equal(testCtx);
            });
    });
    it('goal fail request', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            {
                                regex: 'page-url=goal',
                                count: 100,
                                status: '500',
                            },
                            function () {
                                window.navigator.sendBeacon = () => false;
                                const counter = new Ya.Metrika2({
                                    id: options.counterId,
                                });
                                serverHelpers.collectRequests(
                                    1000,
                                    function (requests, done) {
                                        const result = JSON.parse(
                                            localStorage.getItem(
                                                '_ym_retryReqs',
                                            ),
                                        );
                                        done(result);
                                    },
                                );
                                counter.reachGoal(options.testGoal);
                            },
                        );
                    },
                    counterId,
                    testGoal,
                    goalParams,
                    testCtx,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: result }) => {
                chai.expect(Object.keys(result).length).to.be.eq(
                    1,
                    'Requests length is equal 1',
                );
                return this.browser;
            })
            .refresh()
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        let firstHit = null;
                        let retryReqs = null;
                        let goalRequest = null;
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                        let timeout;
                        serverHelpers.onRequest(function (request) {
                            clearTimeout(timeout);
                            if (!firstHit) {
                                firstHit = request;
                                retryReqs = JSON.parse(
                                    localStorage.getItem('_ym_retryReqs'),
                                );
                            }
                            if (request.url.indexOf('page-url=goal') !== -1) {
                                goalRequest = request;
                            }
                            setTimeout(() => {
                                const ls = JSON.parse(
                                    localStorage.getItem('_ym_retryReqs'),
                                );
                                done([goalRequest, retryReqs, ls, firstHit]);
                            }, 500);
                        });
                    },
                    counterId,
                    testGoal,
                    goalParams,
                    testCtx,
                }),
            )
            .then(({ value: [request, retryReqs, ls, firstHit] }) => {
                const { brInfo: firstBrInfo } =
                    e2eUtils.getRequestParams(firstHit);
                const { params, brInfo } = e2eUtils.getRequestParams(request);

                const retryReqsHids = Object.keys(retryReqs).map((key) => {
                    return String(retryReqs[key].browserInfo.hid);
                });

                chai.expect(retryReqsHids).to.includes(brInfo.hid);
                chai.expect(firstBrInfo.hid).to.be.not.equal(brInfo.hid);
                chai.expect(ls).to.be.deep.equal({});
                chai.expect(brInfo.ar).to.be.equal('1', 'is Artificial hit?');
                chai.expect(params['page-ref']).to.be.equal(baseFullUrl);
                chai.expect(params['page-url']).to.be.equal(goalUrl);
            });
    });

    it(`doesn't log callback's error`, function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            500,
                            (requests, done) => {
                                done({
                                    requests,
                                    errors: getPageErrors(),
                                });
                            },
                            options.regexp.defaultRequestRegEx,
                        );
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        counter.reachGoal(options.testGoal, () => {
                            throw new Error('user error');
                        });
                    },
                    counterId,
                    testGoal,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value }) => {
                chai.expect(value.requests.length).to.be.equal(2);
                chai.expect(value.errors.usual.length).to.be.equal(1);
                chai.expect(value.errors.unhandledrejection.length).to.be.equal(
                    0,
                );
                chai.expect(value.errors.usual[0]).to.include('user error');
            });
    });
});
