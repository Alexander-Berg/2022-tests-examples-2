const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('tuboUid', () => {
    const url = `${e2eUtils.baseUrl}/test/turboUid/turboUid.hbs`;
    const turboUrl = `${e2eUtils.baseUrl}/test/turboUid/turboUidInTurboPages.hbs`;
    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000);
    });
    const rnd = (Math.random() * 100).toFixed();
    const testUid = `dfd${rnd}`;
    const testCounterId = 26302566 + rnd;
    it('Correctly identifies turbo uid in artificial hit', function () {
        return this.browser
            .url(turboUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            500,
                            0,
                            options.regexp.defaultRequestRegEx,
                        );

                        const counter = new Ya.Metrika2({
                            id: options.testCounterId,
                            defer: true,
                        });
                        counter.hit('http://example.com', {
                            params: {
                                __ym: {
                                    turbo_uid: options.testUid,
                                },
                            },
                        });
                    },
                    testCounterId,
                    testUid,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const parsedResult = requests
                    .map(e2eUtils.getRequestParams)
                    .filter(({ brInfo }) => brInfo.ar);
                chai.expect(parsedResult).to.be.lengthOf(1);
                const [artHit] = parsedResult;
                chai.expect(artHit.brInfo.td).to.be.eq(`${testUid}`);
            });
    });
    it('get uid from cookes', function () {
        return this.browser
            .url(url)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        document.cookie = `_ym_turbo_uid =${options.testUid}`;
                        serverHelpers.onRequest(function (request) {
                            done(request);
                        });

                        new Ya.Metrika2(options.testCounterId);
                    },
                    testCounterId,
                    testUid,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: result }) => {
                const { brInfo } = e2eUtils.getRequestParams(result);
                chai.expect(brInfo.td).to.be.equal(testUid);
            });
    });
    it('get uid from url and set cookes', function () {
        return this.browser
            .url(`${url}?turbo_uid=${testUid}`)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.onRequest(function (request) {
                            done({
                                cookie: document.cookie.match(
                                    /_ym_turbo_uid=([^;]+)/,
                                ),
                                request,
                            });
                        });

                        new Ya.Metrika2(options.testCounterId);
                    },
                    testCounterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: { request, cookie } }) => {
                const { brInfo } = e2eUtils.getRequestParams(request);
                chai.expect(brInfo.td).to.be.equal(testUid);
                const [, cookieUid] = cookie;
                chai.expect(cookieUid).to.be.eq(testUid);
            });
    });
    it('not send uid if it doesnt exist', function () {
        return this.browser
            .url(url)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.onRequest(function (request) {
                            done(request);
                        });

                        new Ya.Metrika2(options.testCounterId);
                    },
                    testCounterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: result }) => {
                const { brInfo } = e2eUtils.getRequestParams(result);
                chai.expect(brInfo.td).to.be.not.ok;
            });
    });
});
